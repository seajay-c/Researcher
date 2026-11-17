# Prompt 0: Master context (Researcher)

Load this file at the start of every session. `srs.md`, `architecture.md` and `structure.md` hold the authoritative text. If this file and they disagree, they win: stop and report the conflict.

### Main rules

- Build only what `srs.md` lists. Do not build anything on its **Out of scope** list (PlutusBot, scheduler, sandbox, approval gates, headless browser, Docker, GUI auth, external APIs).
- Put files only on paths in the `structure.md` tree.
- Connect out only to `M1MAX_URL` and `MCP_URL` (**SRS-NFR-001**).
- Do not hard-code secrets. Read them from `.env` only (**SRS-NFR-005**).
- Commit after each increment turns green: `incNN: <capability> (<SRS IDs>)`.

### Domain background

Researcher is a small research agent that runs only on the homelab. The owner asks a question. Qwen 3.8 27B on the m1max plans the work, searches through MCP-Searxng (`searxng_web_search`), reads pages through MCP-Searxng (`web_url_read`, which returns markdown), and writes a markdown report with `[n]` citations. Each research task is one folder `research/<YYYY-MM-DD>-<slug>/` holding `state.json`, `report.md`, `followups.md` and `sources/NN-<domain>.md`. A FastAPI GUI on vm1 (`0.0.0.0:8090`) shows the folders, starts research and answers follow-up questions about a report. There is one user, the owner, on the LAN or tailnet.

Assumptions to verify, not trust:
- The m1max at `100.67.98.112:8080/v1` (tailnet) has its own key and is OpenAI-compatible. Tool calling and the thinking toggle are unproven (increment 02).
- MCP-Searxng is reachable at `http://12.0.0.225:3000/mcp` (streamable HTTP) only after `MCP_HTTP_HOST=0.0.0.0` is set on the container (increment 03).
- `web_url_read` is a plain HTTP fetch and does not run JavaScript.

### Architecture

Parts. Do not add any others:
- **CLI**: `research | resume | ask | serve`.
- **Agent**: runs the plan → gather → synthesize loop and the follow-up loop. Validates tool calls, retries failed ones and saves a checkpoint after each step.
- **LLM client**: OpenAI SDK pointed at the m1max. One global `asyncio.Lock` so only one request runs at a time. Sets thinking on or off per call and enforces the token budget.
- **MCP tools**: one MCP session. Wraps search and read_url, and handles robots.txt (fetched through `web_url_read`), the 2 s wait per domain and the 30 s timeout.
- **Ranker**: splits sources into paragraph chunks and keeps the chunks with the most term overlap that fit the budget.
- **Store**: folder layout, atomic writes of `state.json`, URL-hash dedupe and source numbering.
- **Web GUI**: FastAPI with Jinja pages. List page, report page with citation links, source page, follow-up chat, start form with an SSE progress log, and `/health`.

Decisions:
1. Search and scraping go through MCP-Searxng. There is no scraper container.
2. `state.json` in each folder is the only task store. There is no database.
3. The agent calls the m1max directly behind one lock, without OmniRoute.

Hard constraints: no external search, scrape or LLM APIs. No tools that write, delete or send outside `research/`. Tool definitions for search and scraping come from MCP `tools/list`. If tool calling is broken, fix the server; never parse tool calls out of the model's prose.

### Requirements (copied from `srs.md`)

| ID | Statement | Priority | Verification |
| --- | --- | --- | --- |
| SRS-FR-001 | Starting research with a question (CLI or GUI) creates a new folder `research/<YYYY-MM-DD>-<slug>/`. | must | Run one question and see the folder appear. |
| SRS-FR-002 | The agent finds candidate pages only through the MCP tool `searxng_web_search`. | must | The run log shows search calls going to MCP-Searxng. |
| SRS-FR-003 | Each page the agent uses is fetched with `web_url_read` and saved as `sources/NN-<domain>.md`, with a header giving its URL, title, fetch time and source number. | must | Open the source files and check the headers match the URLs fetched. |
| SRS-FR-004 | A URL already saved in the folder is not fetched again. | must | Re-run or resume and see no second fetch for the same URL in the log. |
| SRS-FR-005 | Before fetching a page, the agent reads that site's `robots.txt` through `web_url_read` and skips pages it disallows. It waits at least 2 s between fetches to the same domain, and each fetch times out after 30 s. | must | Test against a disallowed URL and see a "skipped: robots" log entry. Log timestamps show the per-domain gap. |
| SRS-FR-006 | `report.md` cites sources inline as `[n]`, where n is a saved source's number, and ends with a numbered list of those sources and their URLs. | must | Every `[n]` in the report has a matching `sources/NN-*.md` file, checked by a script. |
| SRS-FR-007 | A claim that no saved source supports is marked `[unverified]` in the report. | must | Prompt test: give a question the fake sources can't answer and see `[unverified]` in the output. |
| SRS-FR-008 | Default research saves 8–15 sources. The maximum can be changed in config. | must | Count the source files after a default run. |
| SRS-FR-009 | When a tool call fails, the agent retries with a different query or source, at most 3 times per step. After that it records the failure in one line in the report and continues. | must | Fake MCP failures in a test and see the retries and the failure line. |
| SRS-FR-010 | The agent saves task state to `state.json` in the folder after every step. Running resume, or restarting the GUI server, continues unfinished tasks from their last saved step. | must | Kill the process mid-run, restart it, and see it finish without redoing completed steps. |
| SRS-FR-011 | A follow-up question about a report is answered first from that folder's saved sources. If those don't cover it, the agent searches and scrapes more, saves the new pages under the next source numbers in the same folder, and cites them. | must | Ask a covered question and see no new fetches. Ask an uncovered one and see new numbered source files. |
| SRS-FR-012 | Each follow-up question and its cited answer are appended to `followups.md` in the folder. | must | Check the file after two follow-ups. |
| SRS-FR-013 | The GUI lists research folders newest first, with each folder's question and status. | must | Open the GUI and see the list. |
| SRS-FR-014 | The GUI renders `report.md`, and each `[n]` citation links to the rendered source file. | must | Click a citation and see the source page open. |
| SRS-FR-015 | The GUI has a follow-up chat on each report that shows earlier follow-ups and sends new ones (SRS-FR-011). | must | Ask a follow-up in the browser and see the answer appear and be saved. |
| SRS-FR-016 | The GUI can start new research and shows a progress log that updates while it runs. | must | Start research from the GUI and watch the steps appear. |
| SRS-FR-017 | Model calls run with thinking on for planning and synthesis, and off for picking URLs and extracting text. | should | The request log shows the thinking flag for each call type. |
| SRS-NFR-001 | The program opens network connections only to the m1max endpoint and MCP-Searxng. All page and robots fetches happen inside MCP-Searxng. | must | `ss -tnp` or tcpdump on vm1 during a run shows only those two hosts. |
| SRS-NFR-002 | At most one model request is in flight at a time, across research and follow-ups. | must | A test fires two tasks at once and sees model calls never overlap. |
| SRS-NFR-003 | No single model request goes over the configured context budget (default 48K tokens, allowed range 32–64K). Source text is chunked and ranked to fit. | must | Unit test with oversized sources: the prompt stays under budget. |
| SRS-NFR-004 | Tool calls with invalid JSON or unknown tools are not executed. The model is asked again with the error. | must | Unit test with a fake model that sends bad JSON. |
| SRS-NFR-005 | Secrets (the m1max key) come only from `.env`, which git ignores. `.env.example` lists every variable. | must | `git grep` finds no key. The app starts with only `.env` set. |
| SRS-NFR-006 | Logs are JSON lines, one event per line, with a task ID. | must | Read the log and check each line is valid JSON. |
| SRS-NFR-007 | The GUI listens on vm1's LAN and tailnet addresses without auth. | must | Open it from another LAN machine. |
| SRS-NFR-008 | The agent never says it can't browse, and adds no refusals or disclaimers to ordinary research. | should | Read three test transcripts and find none of these phrases. |
| SRS-NFR-009 | A health endpoint reports whether the m1max and MCP-Searxng answer. | should | `curl /health` returns JSON with both statuses. |

### Stack and dependencies

Python 3.12, venv + pip, `pyproject.toml`. Dependencies: `openai`, `mcp`, `fastapi`, `uvicorn`, `jinja2`, `markdown-it-py`. Dev dependencies: `pytest`, `pytest-asyncio`. Use the standard library for everything else: `urllib.robotparser`, JSON `logging`, `hashlib`, `argparse`, and a small `.env` parser. Do not add any other dependency.

### Directory tree

```
pyproject.toml  .env.example  .gitignore
researcher/{__init__,__main__,config,log,llm,mcp_tools,rank,store,agent}.py
researcher/prompts/{planner,executor,synthesizer,followup}.md
researcher/web/app.py  researcher/web/templates/{base,index,report,source}.html
tests/{conftest,test_store,test_rank,test_mcp_tools,test_agent,test_web}.py  tests/smoke_m1max.py
research/.gitkeep   research/<YYYY-MM-DD>-<slug>/{state.json,report.md,followups.md,sources/NN-<domain>.md}
```

### Shared contracts (all `derived`)

`state.json`:
```json
{"id": "2026-11-16-slug", "question": "...", "status": "running|done|failed",
 "phase": "plan|gather|synthesize|done", "created": "ISO", "updated": "ISO",
 "plan": ["query", "..."], "queries_done": ["..."], "failures": ["one line", "..."],
 "sources": [{"n": 1, "url": "...", "url_hash": "sha256", "title": "...", "fetched_at": "ISO", "file": "sources/01-example.com.md"}]}
```

Source file header:
```
---
n: 1
url: https://...
title: ...
fetched_at: 2026-11-16T21:00:00Z
---
```

Config variables (`.env`): `M1MAX_URL`, `M1MAX_API_KEY`, `M1MAX_MODEL`, `MCP_URL`, `RESEARCH_DIR=./research`, `CONTEXT_BUDGET=48000`, `MIN_SOURCES=8`, `MAX_SOURCES=15`, `GUI_HOST=0.0.0.0`, `GUI_PORT=8090`.

### Success metrics

- Every `must` row's verification holds.
- `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'` succeeds.
- `.venv/bin/pytest` passes.
- `.venv/bin/python tests/smoke_m1max.py` shows a real tool call round trip.
- `.venv/bin/python -m researcher serve` serves `http://12.0.0.179:8090`.

### Main rules (repeat)

- Build only what is in scope. Use only paths from the tree. Connect only to the m1max and MCP-Searxng. Keep secrets in `.env` only.
- Commit each increment once it is green.
