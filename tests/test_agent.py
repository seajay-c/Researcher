import asyncio
import time
from types import SimpleNamespace as NS

import pytest

from researcher.llm import LLM, BudgetExceeded


class FakeCompletions:
    def __init__(self):
        self.intervals = []

    async def create(self, **kw):
        t0 = time.monotonic()
        await asyncio.sleep(0.05)
        self.intervals.append((t0, time.monotonic()))
        return NS(choices=[NS(message=NS(content="<think>x</think>hi", tool_calls=None))])


def fake_client():
    return NS(chat=NS(completions=FakeCompletions()))


async def test_lock_no_overlap(cfg):
    c = fake_client()
    llm = LLM(cfg, client=c)
    r = await asyncio.gather(*(llm.chat([{"role": "user", "content": "q"}], thinking=False) for _ in range(3)))
    assert r[0]["content"] == "hi"
    iv = sorted(c.chat.completions.intervals)
    assert all(a[1] <= b[0] for a, b in zip(iv, iv[1:]))


async def test_budget(cfg):
    llm = LLM(cfg, client=fake_client())
    with pytest.raises(BudgetExceeded):
        await llm.chat([{"role": "user", "content": "x" * 300_000}], thinking=False)


import re

from researcher.agent import load_prompt

PLACEHOLDERS = {"planner": ["{today}", "{question}"],
                "executor": ["{today}", "{question}", "{plan}", "{min_sources}", "{max_sources}"],
                "synthesizer": ["{today}", "{question}", "{chunks}"],
                "followup": ["{today}", "{report}", "{chunks}", "{question}"]}


def test_prompts():
    for name, ph in PLACEHOLDERS.items():
        text = load_prompt(name)
        assert all(p in text for p in ph), name
        for line in text.splitlines():  # SRS-NFR-008: banned phrases only inside "never/do not" instructions
            if re.search(r"cannot browse|can't browse|as an ai|disclaimer", line, re.I):
                assert re.search(r"never|do not", line, re.I), line
    ex = load_prompt("executor")
    assert ex.count("<tool_call>") >= 3 and "searxng_web_search" in ex and "function-calling.md" in ex and "<tool_response>" in ex


from pathlib import Path

from conftest import FakeLLM, FakeTools, call
from researcher import store
from researcher.agent import run_research

PAGES = {"https://a.com/1": "# Alpha\nSearXNG is a metasearch engine.", "https://b.org/2": "# Beta\nIt forks Searx."}


def cited_ok(folder: Path) -> bool:
    body = (folder / "report.md").read_text().split("## Sources")[0]
    files = {int(p.name[:2]) for p in (folder / "sources").glob("*.md")}
    return all(int(n) in files for n in re.findall(r"\[(\d+)\]", body))


async def test_scripted_run(cfg):
    folder = store.new_task(cfg.research_dir, "What is SearXNG?")
    llm = FakeLLM({"plan": ['{"queries": ["searxng", "searxng fork"]}'],
                   "gather": [[call("searxng_web_search", query="searxng")],
                              [call("web_url_read", url="https://a.com/1")],
                              [call("web_url_read", url="https://b.org/2")],
                              [call("web_url_read", url="https://a.com/1")],
                              "Done gathering."],
                   "synth": ["SearXNG is a metasearch engine [1]. It forks Searx [2]. Bogus [7]. Unknown claim [unverified]."]})
    tools = FakeTools(PAGES)
    events = []
    await run_research(folder, llm, tools, cfg, on_event=events.append)
    report = (folder / "report.md").read_text()
    assert cited_ok(folder) and "[7]" not in report and "[unverified]" in report  # SRS-FR-006, FR-007
    assert tools.reads == ["https://a.com/1", "https://b.org/2"]  # SRS-FR-004: repeat not refetched
    assert any("already saved as [1]" in m["content"] for m in llm.calls[-2][2] if m["role"] == "tool")
    s = store.load_state(folder)
    assert (s["status"], s["phase"], s["plan"], s["queries_done"]) == ("done", "done", ["searxng", "searxng fork"], ["searxng"])
    assert [(st, th) for st, th, _ in llm.calls if st != "gather"] == [("plan", True), ("synth", True)]  # SRS-FR-017
    assert all(th is False for st, th, _ in llm.calls if st == "gather")
    assert {"plan", "search", "saved", "bad_citation", "done"} <= {e["event"] for e in events}


async def test_three_failures_line(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    bad = ["https://x.com/1", "https://y.com/2", "https://z.com/3"]
    llm = FakeLLM({"plan": ['{"queries": ["q"]}'],
                   "gather": [[call("web_url_read", url=u)] for u in bad] + ["stop"],
                   "synth": ["Nothing found [unverified]."]})
    await run_research(folder, llm, FakeTools(fail_urls=bad), cfg)
    report = (folder / "report.md").read_text()
    assert "## Failures" in report and "3 tool calls failed in a row" in report  # SRS-FR-009
    assert len(store.load_state(folder)["failures"]) == 1


async def test_bad_json_not_executed(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    llm = FakeLLM({"plan": ['{"queries": ["q"]}'],
                   "gather": [[{"name": "web_url_read", "arguments": '{"url": "https://a.com/1"'}],
                              [{"name": "rm_rf", "arguments": "{}"}],
                              "stop"],
                   "synth": ["x"]})
    tools = FakeTools(PAGES)
    await run_research(folder, llm, tools, cfg)
    assert tools.reads == [] and tools.searches == []  # SRS-NFR-004
    gather = [m for st, _, m in llm.calls if st == "gather"]
    assert "not valid JSON" in gather[1][-1]["content"] and "unknown tool 'rm_rf'" in gather[2][-1]["content"]


async def test_plan_fallback_and_source_cap(cfg):
    from dataclasses import replace
    cfg = replace(cfg, max_sources=2)
    folder = store.new_task(cfg.research_dir, "fallback question")
    urls = [f"https://s{i}.com/" for i in range(5)]
    llm = FakeLLM({"plan": ["not json", "still not", "nope"],
                   "gather": [[call("web_url_read", url=u)] for u in urls],
                   "synth": ["r [1][2]"]})
    tools = FakeTools()
    await run_research(folder, llm, tools, cfg)
    s = store.load_state(folder)
    assert s["plan"] == ["fallback question"] and len(s["sources"]) == 2 and len(tools.reads) == 2  # SRS-FR-008 cap


async def test_failure_sets_status(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    llm = FakeLLM({"plan": [RuntimeError("boom")]})
    with pytest.raises(RuntimeError):
        await run_research(folder, llm, FakeTools(), cfg)
    assert store.load_state(folder)["status"] == "failed"


async def test_trim_keeps_gather_under_budget(cfg):
    from dataclasses import replace
    from researcher.llm import estimate_tokens
    cfg = replace(cfg, context_budget=6000, max_sources=30)
    folder = store.new_task(cfg.research_dir, "q")
    urls = [f"https://s{i}.com/" for i in range(25)]
    pages = {u: "# P\n" + "word " * 2000 for u in urls}
    llm = FakeLLM({"plan": ['{"queries": ["q"]}'], "gather": [[call("web_url_read", url=u)] for u in urls] + ["stop"], "synth": ["r"]})
    await run_research(folder, llm, FakeTools(pages), cfg)
    from conftest import SCHEMAS
    sizes = [estimate_tokens(m, SCHEMAS) for st, _, m in llm.calls if st == "gather"]
    assert len(sizes) == 26 and max(sizes) <= cfg.context_budget  # SRS-NFR-003


async def test_duplicate_reads_stop_gather(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    llm = FakeLLM({"plan": ['{"queries": ["q"]}'],
                   "gather": [[call("web_url_read", url="https://a.com/1")]] * 10,
                   "synth": ["r [1]"]})
    tools = FakeTools(PAGES)
    await run_research(folder, llm, tools, cfg)
    gather_calls = [1 for st, _, _ in llm.calls if st == "gather"]
    assert tools.reads == ["https://a.com/1"] and len(gather_calls) == 4  # 1 save + 3 duplicates, then stop


async def test_max_tokens_inside_budget(cfg):
    c = fake_client()
    seen = {}
    orig = c.chat.completions.create
    async def create(**kw):
        seen.update(kw)
        return await orig(**kw)
    c.chat.completions.create = create
    await LLM(cfg, client=c).chat([{"role": "user", "content": "x" * 3000}], thinking=True)
    assert 0 < seen["max_tokens"] <= 8192 and seen["extra_body"]["chat_template_kwargs"]["enable_thinking"] is True


async def test_empty_synth_fails_not_empty_report(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    llm = FakeLLM({"plan": ['{"queries": ["q"]}'], "gather": ["stop"], "synth": [""]})
    with pytest.raises(RuntimeError, match="no text"):
        await run_research(folder, llm, FakeTools(), cfg)
    assert not (folder / "report.md").exists() and store.load_state(folder)["status"] == "failed"


from researcher.agent import resume_all


async def test_resume_after_crash_in_gather(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    urls = [f"https://s{i}.com/" for i in range(5)]
    tools = FakeTools()
    llm1 = FakeLLM({"plan": ['{"queries": ["q1", "q2"]}'],
                    "gather": [[call("web_url_read", url=u)] for u in urls[:3]] + [RuntimeError("killed"), RuntimeError("killed")]})
    with pytest.raises(RuntimeError):
        await run_research(folder, llm1, tools, cfg)
    s = store.load_state(folder)
    assert (s["phase"], len(s["sources"])) == ("gather", 3)
    llm2 = FakeLLM({"gather": [[call("web_url_read", url=urls[0])], [call("web_url_read", url=urls[3])], "enough"],
                    "synth": ["r [1][4]"]})
    await run_research(folder, llm2, tools, cfg)  # SRS-FR-010
    assert tools.reads == urls[:4]  # no second read of the first 3 (SRS-FR-004)
    assert "plan" not in [st for st, _, _ in llm2.calls]  # plan not regenerated
    seed = llm2.calls[0][2][-1]["content"]
    assert "resuming" in seed and "[3] Page https://s2.com/" in seed
    s = store.load_state(folder)
    assert (s["status"], s["plan"], [x["n"] for x in s["sources"]]) == ("done", ["q1", "q2"], [1, 2, 3, 4])
    assert (folder / "report.md").exists()


async def test_resume_synthesize_no_tools(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    s = store.load_state(folder)
    store.add_source(folder, s, "https://a.com/1", "A", "text")
    s["phase"] = "synthesize"; store.save_state(folder, s)
    tools = FakeTools()
    llm = FakeLLM({"synth": ["r [1]"]})
    await run_research(folder, llm, tools, cfg)
    assert tools.reads == [] and tools.searches == [] and [st for st, _, _ in llm.calls] == ["synth"]


async def test_resume_all_and_done_noop(cfg):
    a = store.new_task(cfg.research_dir, "a")
    b = store.new_task(cfg.research_dir, "b")
    sb = store.load_state(b); sb["status"] = sb["phase"] = "done"; store.save_state(b, sb)
    llm = FakeLLM({"plan": ['{"queries": ["q"]}'], "gather": ["stop"], "synth": ["r"]})
    assert await resume_all(cfg.research_dir, llm, FakeTools(), cfg) == [a.name]
    n = len(llm.calls)
    await run_research(b, llm, FakeTools(), cfg)
    assert len(llm.calls) == n


async def test_kill_leaves_task_running_for_resume(cfg):
    folder = store.new_task(cfg.research_dir, "q")
    llm = FakeLLM({"plan": ['{"queries": ["q"]}'], "gather": [[call("web_url_read", url="https://a.com/1")], asyncio.CancelledError(), asyncio.CancelledError()]})
    with pytest.raises(asyncio.CancelledError):
        await run_research(folder, llm, FakeTools(PAGES), cfg)
    assert store.load_state(folder)["status"] == "running" and store.unfinished(cfg.research_dir) == [folder]


from researcher.agent import ask


def _done_task(cfg):
    folder = store.new_task(cfg.research_dir, "What is SearXNG?")
    s = store.load_state(folder)
    store.add_source(folder, s, "https://a.com/1", "Alpha", "SearXNG is a metasearch engine.")
    store.add_source(folder, s, "https://b.org/2", "Beta", "It forks Searx.")
    store.write_report(folder, "SearXNG is a metasearch engine [1].", s)
    s["status"] = s["phase"] = "done"; store.save_state(folder, s)
    return folder


async def test_followup_covered_no_tools(cfg):
    folder = _done_task(cfg)
    tools = FakeTools()
    llm = FakeLLM({"followup": ["It is a fork of Searx [2]. Also [9]."]})
    ans = await ask(folder, "What did it fork?", llm, tools, cfg)
    assert ans == "It is a fork of Searx [2]. Also ." and tools.reads == tools.searches == []  # SRS-FR-011
    assert llm.calls[0][1] is True and "[1] SearXNG is a metasearch engine." in llm.calls[0][2][0]["content"]
    assert "## Q: What did it fork?" in (folder / "followups.md").read_text()  # SRS-FR-012


async def test_followup_uncovered_adds_next_source(cfg):
    folder = _done_task(cfg)
    tools = FakeTools({"https://c.net/maint": "# Maintainers\nThe SearXNG team maintains it."})
    llm = FakeLLM({"followup": [[call("searxng_web_search", query="searxng maintainers")],
                                [call("web_url_read", url="https://c.net/maint")],
                                "The SearXNG team maintains it [3]."]})
    ans = await ask(folder, "Who maintains it?", llm, tools, cfg)
    assert (folder / "sources/03-c.net.md").exists() and "[3]" in ans  # SRS-FR-011: next number, same folder
    assert [x["n"] for x in store.load_state(folder)["sources"]] == [1, 2, 3]


async def test_two_followups_two_entries(cfg):
    folder = _done_task(cfg)
    llm = FakeLLM({"followup": ["A [1]."]})
    await ask(folder, "one?", llm, FakeTools(), cfg)
    await ask(folder, "two?", llm, FakeTools(), cfg)
    assert (folder / "followups.md").read_text().count("## Q: ") == 2


async def test_followup_bad_json_not_executed(cfg):
    folder = _done_task(cfg)
    tools = FakeTools()
    llm = FakeLLM({"followup": [[{"name": "web_url_read", "arguments": "{bad"}], "Answer [1]."]})
    await ask(folder, "q?", llm, tools, cfg)
    assert tools.reads == [] and "not valid JSON" in llm.calls[1][2][-1]["content"]  # SRS-NFR-004
