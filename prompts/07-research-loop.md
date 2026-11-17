# INCREMENT 07: Research loop (plan, gather, synthesize)

- **Status:** CRITICAL
- **Dependencies:** 02, 03, 04, 05, 06
- **SRS IDs:** **SRS-FR-002**, **SRS-FR-003**, **SRS-FR-004**, **SRS-FR-006**, **SRS-FR-007**, **SRS-FR-008**, **SRS-FR-009**, **SRS-FR-017**, **SRS-NFR-004**

### Rules

- The Agent talks to the network only through `LLM` and `Tools`.
- Never execute a tool call with invalid JSON or an unknown name. Return the error to the model as the tool result (**SRS-NFR-004**).

### Capability

`run_research` turns a new task folder into a finished cited `report.md`.

### May change

Extend `researcher/agent.py`, `tests/conftest.py` (add a scripted fake LLM and fake Tools) and `tests/test_agent.py`. Leave `llm.py`, `mcp_tools.py`, `store.py` and `rank.py` unchanged, except for bug fixes recorded in tracking.

### Implementation

- `derived`: `async def run_research(folder: Path, llm: LLM, tools: Tools, cfg: Config, on_event=None) -> None`. `on_event(dict)` is optional and gets every progress event; also log each event with `task=state["id"]`.
- **plan** (`thinking=True`): planner prompt → parse `{"queries": [...]}`. If parsing fails, re-ask up to 2 times, then fall back to `[question]`. Save `state["plan"]`, set `phase="gather"`, save the state.
- **gather** (`thinking=False`): executor messages plus `tools.schemas()`. Loop at most 40 model turns:
  - No `tool_calls` → stop.
  - For each call, validate the JSON arguments and the name against the schemas.
  - `searxng_web_search`: run it, append the query to `state["queries_done"]`, and return compact results (title, url, snippet, at most 10).
  - `web_url_read`: if `store.find_source` hits, return `"already saved as [n]"` without fetching (**SRS-FR-004**). Otherwise call `tools.read_url`. If it returns `None`, the tool result is "skipped: robots". If it returns text, take the title from the first markdown heading (or the URL), call `store.add_source`, and return `"saved as [n]: "` plus the first 1500 characters.
  - On `ToolError`, return the error text to the model so it can retry. After 3 consecutive failures in this phase, append a one-line failure to `state["failures"]` and reset the counter (**SRS-FR-009**).
  - Stop when the number of sources reaches `cfg.max_sources` (**SRS-FR-008**).
  - Save the state after every executed tool call.
  - Before every model call, if `llm.estimate_tokens` is over 80% of the budget, replace older tool results with `"[trimmed]"`.
- **synthesize** (`thinking=True`): `rank.top_chunks(question, store.read_sources(folder), cfg.context_budget - 6000)` → synthesizer. Remove any `[n]` that is not a saved source number, log `bad_citation`, and append a `Failures` section listing `state["failures"]` if there are any. Then `store.write_report`, set `status="done"` and `phase="done"`, and save.
- If an unexpected exception occurs, set `status="failed"`, log it, and re-raise.

### Verification

- With a fake LLM and fake Tools:
  - A scripted run produces `report.md`. Every `[n]` matches a source file, checked by `re.findall(r"\[(\d+)\]")` against `sources/` (**SRS-FR-006**).
  - With 3 failing reads, the report has a failure line (**SRS-FR-009**).
  - A bad-JSON tool call is not executed and the next message to the model contains the error (**SRS-NFR-004**).
  - A repeated URL is fetched only once (**SRS-FR-004**).
  - Fake sources that don't cover the question make the synthesizer stub produce `[unverified]`. This only proves the code passes the tag through; check prompt behavior in increment 13.
- `.venv/bin/pytest` passes.

### Risk

The first time all parts work together. The context grows during gather. Qwen may stop too early or loop.

### Failure indicators

- `BudgetExceeded` during gather.
- Fewer than `min_sources` sources while there are still unread search results.
- The same query repeated more than twice.
- A citation number with no file.

### Isolation test

Run `run_research` with the fake LLM and fake Tools only. Then run it with the real `Tools` and the fake LLM, and then with the real `LLM` and fake `Tools`, to find the side that fails.

### Rollback

Revert `agent.py` to the state after increment 06 (only `load_prompt`). Then rerun the increment 05 and 06 checks.

### Rules (repeat)

- Use the network only through `LLM` and `Tools`. Never execute invalid tool calls.
