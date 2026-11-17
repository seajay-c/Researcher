import json
import re
from datetime import date
from pathlib import Path

from . import rank, store
from .config import Config
from .llm import estimate_tokens
from .log import get_logger
from .mcp_tools import ToolError

PROMPTS = Path(__file__).parent / "prompts"
CITE = re.compile(r"\[(\d+)\]")
MDLINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HEADING = re.compile(r"^\s*#{1,6}\s+(.+?)\s*#*\s*$", re.M)
MAX_GATHER_TURNS = 40
MAX_NUDGES = 2
MAX_FAILS = 3  # consecutive tool failures per step before a failure line; SRS-FR-009
log = get_logger("agent")


def load_prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text()


def fill(name: str, **values) -> str:
    # str.replace, not str.format: the prompts contain literal JSON braces
    text = load_prompt(name).replace("{today}", date.today().isoformat())
    for k, v in values.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def _emitter(state: dict, on_event):
    def emit(event: str, **data):
        log.info(event, extra={"task": state["id"], **data})
        if on_event:
            on_event({"event": event, "task": state["id"], **data})
    return emit


def _parse_queries(text: str | None) -> list[str] | None:
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        qs = json.loads(m.group(0))["queries"] if m else None
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
    qs = [q.strip() for q in qs if isinstance(q, str) and q.strip()] if isinstance(qs, list) else []
    return qs or None


def _format_chunks(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{c['n']}] {c['text']}" for c in chunks) or "(no saved sources)"


def clean_citations(text: str, state: dict, emit) -> str:
    valid = {s["n"] for s in state["sources"]}
    def fix(m):
        if int(m.group(1)) in valid:
            return m.group(0)
        emit("bad_citation", n=int(m.group(1)))
        return ""
    return CITE.sub(fix, text)


def _trim(msgs: list[dict], tools: list[dict], budget: int) -> None:
    """Replace older tool results with "[trimmed]" until the request is under 80% of the budget."""
    tool_idx = [i for i, m in enumerate(msgs) if m["role"] == "tool" and m["content"] != "[trimmed]"]
    for i in tool_idx[:-1]:  # keep the newest result
        if estimate_tokens(msgs, tools) <= 0.8 * budget:
            return
        msgs[i]["content"] = "[trimmed]"


def _progress(state: dict, cfg: Config) -> str:
    return f"{len(state['sources'])} sources saved, target {cfg.min_sources}-{cfg.max_sources}"


async def _run_call(call: dict, specs: dict, folder: Path, state: dict, tools, cfg: Config, emit,
                    seen: dict | None = None) -> tuple[str, str]:
    """Validate and execute one model tool call. Returns (result_text, outcome) with outcome in ok|fail|invalid|skip|dup."""
    name = call["name"]
    if name not in specs:
        emit("invalid_tool_call", tool=name, error="unknown tool")
        return f"Error: unknown tool '{name}'. Available tools: {', '.join(specs)}.", "invalid"
    try:
        args = json.loads(call["arguments"] or "{}")
        if not isinstance(args, dict):
            raise ValueError("arguments must be a JSON object")
    except (json.JSONDecodeError, ValueError) as e:
        emit("invalid_tool_call", tool=name, error=f"bad JSON: {e}")
        return f"Error: the arguments for {name} are not valid JSON ({e}). Send the call again with a JSON object.", "invalid"
    missing = [k for k in specs[name]["function"]["parameters"].get("required", []) if k not in args]
    if missing:
        emit("invalid_tool_call", tool=name, error=f"missing {missing}")
        return f"Error: {name} needs the argument(s) {', '.join(missing)}.", "invalid"

    sig = name + json.dumps(args, sort_keys=True)
    if seen is not None and sig in seen:  # the exact same call again: don't re-run it (inc10 finding)
        emit("repeat_call", tool=name)
        return (f"You already made this exact call. Its result was: {seen[sig]}. "
                f"Use a different query or source, or stop if you have enough ({_progress(state, cfg)})."), "dup"
    result, outcome = await _execute(name, args, folder, state, tools, cfg, emit)
    if seen is not None and (outcome == "fail" or (outcome == "ok" and name == "searxng_web_search")):
        seen[sig] = result.splitlines()[0][:200] if outcome == "fail" else "see the earlier result above"
    return result, outcome


async def _execute(name: str, args: dict, folder: Path, state: dict, tools, cfg: Config, emit) -> tuple[str, str]:
    task = state["id"]
    try:
        if name == "searxng_web_search":
            query = str(args["query"])
            emit("search", query=query)
            results = await tools.search(query, int(args.get("num_results", 10) or 10), task=task)
            state["queries_done"].append(query)
            compact = [{"title": r["title"], "url": r["url"], "snippet": r["snippet"][:300]} for r in results[:10]]
            return json.dumps(compact, ensure_ascii=False) if compact else "No results. Try a different query.", "ok" if compact else "fail"
        url = str(args["url"])
        if hit := store.find_source(state, url):  # SRS-FR-004: never refetch a saved URL
            emit("duplicate", url=url, n=hit["n"])
            return (f"already saved as [{hit['n']}]. Do not read it again: pick a different URL, "
                    f"or stop if you have enough sources ({_progress(state, cfg)})."), "dup"
        emit("read", url=url)
        text = await tools.read_url(url, task=task)
        if text is None:
            emit("skipped", url=url, reason="robots")
            return "skipped: robots", "skip"
        if not text.strip():
            return "Error: the page was empty. Try a different source.", "fail"
        m = HEADING.search(text)
        title = MDLINK.sub(r"\1", m.group(1)).replace("¶", "").strip() if m else ""
        n = store.add_source(folder, state, url, title or url, text)
        emit("saved", url=url, n=n)
        return f"saved as [{n}] ({_progress(state, cfg)}): {text[:1500]}", "ok"
    except ToolError as e:
        emit("tool_error", tool=name, error=str(e))
        return f"Error: {e}. Retry with a different query or source.", "fail"


async def tool_loop(folder: Path, state: dict, msgs: list[dict], llm, tools, cfg: Config, emit, *,
                    thinking: bool, max_turns: int, max_new: int, step: str, min_total: int = 0) -> str | None:
    """Shared model ↔ tool loop for gather and follow-ups. Returns the final assistant text, or None if it stopped on a cap."""
    schemas = await tools.schemas()
    specs = {s["function"]["name"]: s for s in schemas}
    start = len(state["sources"])
    fails = dups = nudges = 0
    seen: dict[str, str] = {}
    candidates: list[str] = []  # URLs from search results, in order (inc13 finding: point the model at unread ones)

    def unread_hint() -> str:
        bad = {sig for sig, res in seen.items()}
        unread = [u for u in candidates if not store.find_source(state, u)
                  and "web_url_read" + json.dumps({"url": u}, sort_keys=True) not in bad][:5]
        return ("\nUnread search results you could read next:\n" + "\n".join(f"- {u}" for u in unread)) if unread else ""

    def nudge() -> bool:
        """Below min_total, push the model to keep gathering, at most MAX_NUDGES times (SRS-FR-008; inc10 finding)."""
        nonlocal nudges, dups
        if len(state["sources"]) >= min_total or nudges >= MAX_NUDGES:
            return False
        nudges, dups = nudges + 1, 0
        unrun = [q for q in state["plan"] if q not in state["queries_done"]]
        emit("nudge", count=len(state["sources"]))
        msgs.append({"role": "user", "content": (
            f"Only {len(state['sources'])} sources are saved; the target is {cfg.min_sources}-{cfg.max_sources}. "
            f"Keep gathering: read unread pages from your results, or run searches you have not run yet"
            + (f" (for example: {'; '.join(unrun[:3])})" if unrun else " with new angles on the question")
            + ". Do not re-read saved URLs." + unread_hint())})
        return True

    for _ in range(max_turns):
        _trim(msgs, schemas, cfg.context_budget)
        r = await llm.chat(msgs, tools=schemas, thinking=thinking, task=state["id"])
        if not r["tool_calls"]:
            if nudge():
                msgs.append({"role": "assistant", "content": r["content"] or ""})
                msgs[-1], msgs[-2] = msgs[-2], msgs[-1]  # assistant reply first, then the nudge
                continue
            return r["content"]
        msgs.append({"role": "assistant", "content": r["content"] or "", "tool_calls": [
            {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": c["arguments"]}}
            for c in r["tool_calls"]]})
        for c in r["tool_calls"]:
            result, outcome = await _run_call(c, specs, folder, state, tools, cfg, emit, seen)
            if c["name"] == "searxng_web_search" and outcome == "ok":
                try:
                    candidates.extend(r["url"] for r in json.loads(result) if r.get("url") not in candidates)
                except (json.JSONDecodeError, TypeError, AttributeError):
                    pass
            elif c["name"] == "web_url_read" and outcome in ("ok", "dup"):
                result += unread_hint()
            msgs.append({"role": "tool", "tool_call_id": c["id"], "content": result})
            if outcome != "invalid":
                store.save_state(folder, state)
            if outcome in ("fail", "invalid"):
                fails += 1
                if fails >= MAX_FAILS:
                    line = f"{step}: {MAX_FAILS} tool calls failed in a row; last error: {result.splitlines()[0].split(". Retry with")[0][:200]}"
                    state["failures"].append(line)
                    store.save_state(folder, state)
                    emit("failure", error=line)
                    fails = 0
            elif outcome == "ok":
                fails = 0
            dups = dups + 1 if outcome == "dup" else 0
            if dups >= MAX_FAILS:  # the model keeps re-reading saved pages: it is done or stuck (inc07 finding)
                emit("stuck", count=len(state["sources"]))
                if not nudge():
                    return None
            if len(state["sources"]) - start >= max_new:  # SRS-FR-008 cap
                emit("source_cap", count=len(state["sources"]))
                return None
    return None


async def _plan(folder: Path, state: dict, llm, emit) -> None:
    emit("phase", phase="plan")
    msgs = [{"role": "system", "content": fill("planner", question=state["question"])},
            {"role": "user", "content": state["question"]}]
    queries = None
    for _ in range(3):  # first try plus 2 re-asks
        r = await llm.chat(msgs, thinking=True, task=state["id"])
        if queries := _parse_queries(r["content"]):
            break
        msgs += [{"role": "assistant", "content": r["content"] or ""},
                 {"role": "user", "content": 'Reply with only the JSON object {"queries": ["...", "..."]}.'}]
    state["plan"] = queries or [state["question"]]
    state["phase"] = "gather"
    store.save_state(folder, state)
    emit("plan", queries=state["plan"])


async def _gather(folder: Path, state: dict, llm, tools, cfg: Config, emit, resuming: bool = False) -> None:
    emit("phase", phase="gather")
    remaining = cfg.max_sources - len(state["sources"])
    if remaining <= 0:
        return
    plan = "\n".join(f"- {q}" for q in state["plan"])
    msgs = [{"role": "system", "content": fill("executor", question=state["question"], plan=plan,
                                               min_sources=cfg.min_sources, max_sources=cfg.max_sources)},
            {"role": "user", "content": state["question"]}]
    if resuming:  # SRS-FR-010: continue from the checkpoint instead of starting over
        done = "\n".join(f"- {q}" for q in state["queries_done"]) or "- (none)"
        saved = "\n".join(f"[{s['n']}] {s['title']} — {s['url']}" for s in state["sources"]) or "(none)"
        msgs.append({"role": "user", "content": (
            f"This task was interrupted and is resuming. Searches already run:\n{done}\n\n"
            f"Sources already saved (do not read these again):\n{saved}\n\n"
            f"Continue gathering until {cfg.min_sources}-{cfg.max_sources} sources are saved ({_progress(state, cfg)}).")})
    await tool_loop(folder, state, msgs, llm, tools, cfg, emit, thinking=False, max_turns=MAX_GATHER_TURNS,
                    max_new=remaining, step="gather", min_total=cfg.min_sources)


async def _synthesize(folder: Path, state: dict, llm, cfg: Config, emit) -> None:
    emit("phase", phase="synthesize")
    chunks = rank.top_chunks(state["question"], store.read_sources(folder), cfg.context_budget - 6000)
    msgs = [{"role": "system", "content": fill("synthesizer", question=state["question"], chunks=_format_chunks(chunks))},
            {"role": "user", "content": "Write the report now."}]
    r = await llm.chat(msgs, thinking=True, task=state["id"])
    if not (r["content"] or "").strip():
        raise RuntimeError("synthesizer returned no text (output limit reached while thinking?)")
    body = clean_citations(r["content"], state, emit)
    if state["failures"]:
        body = body.rstrip() + "\n\n## Failures\n\n" + "\n".join(f"- {f}" for f in state["failures"])
    store.write_report(folder, body, state)
    state["status"], state["phase"] = "done", "done"
    store.save_state(folder, state)
    emit("done", sources=len(state["sources"]))


async def run_research(folder: Path, llm, tools, cfg: Config, on_event=None) -> None:
    state = store.load_state(folder)
    if state["phase"] == "done":
        return
    emit = _emitter(state, on_event)
    start_phase = state["phase"]
    if state["status"] != "running":
        state["status"] = "running"
        store.save_state(folder, state)
    if start_phase != "plan":
        emit("resume", phase=start_phase, sources=len(state["sources"]))
    try:
        if start_phase == "plan":
            await _plan(folder, state, llm, emit)
        if start_phase in ("plan", "gather"):
            await _gather(folder, state, llm, tools, cfg, emit, resuming=start_phase == "gather")
            state["phase"] = "synthesize"
            store.save_state(folder, state)
        await _synthesize(folder, state, llm, cfg, emit)
    except Exception as e:
        state["status"] = "failed"
        store.save_state(folder, state)
        log.exception("failed", extra={"task": state["id"]})
        if on_event:
            on_event({"event": "failed", "task": state["id"], "error": str(e)})
        raise


async def resume_all(root: Path, llm, tools, cfg: Config, on_event=None) -> list[str]:
    ids = []
    for folder in store.unfinished(root):  # one at a time
        await run_research(folder, llm, tools, cfg, on_event)
        ids.append(folder.name)
    return ids


MAX_FOLLOWUP_TURNS = 15


async def ask(folder: Path, question: str, llm, tools, cfg: Config, on_event=None) -> str:
    state = store.load_state(folder)
    emit = _emitter(state, on_event)
    emit("followup", question=question)
    report = folder / "report.md"
    summary = report.read_text()[:2000] if report.exists() else "(no report yet)"
    chunks = rank.top_chunks(question, store.read_sources(folder), cfg.context_budget - 8000)
    msgs = [{"role": "system", "content": fill("followup", report=summary, chunks=_format_chunks(chunks), question=question)},
            {"role": "user", "content": question}]
    answer = await tool_loop(folder, state, msgs, llm, tools, cfg, emit, thinking=True,
                             max_turns=MAX_FOLLOWUP_TURNS, max_new=cfg.max_sources, step="followup")
    if answer is None:  # stopped on a cap: ask for the answer without tools
        msgs.append({"role": "user", "content": "Stop gathering. Answer the question now from the saved sources."})
        answer = (await llm.chat(msgs, thinking=True, task=state["id"]))["content"]
    if not (answer or "").strip():
        raise RuntimeError("follow-up returned no text")
    answer = clean_citations(answer, state, emit)
    store.append_followup(folder, question, answer)  # SRS-FR-012
    emit("answer", sources=len(state["sources"]))
    return answer
