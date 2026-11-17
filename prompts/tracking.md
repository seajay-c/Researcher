# Tracking

Status values: `not started`, `green`, `yellow`, `red`, `rolled back`. Put evidence (command and trimmed output) in the Notes section under the row's number.

| Increment | File | SRS IDs | Status | Metric | Green | Yellow | Red |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | `01-skeleton.md` | stack, NFR-005, NFR-006 | green | install + config test | pip install OK, `--help` lists 4 subcommands, config/log test passes | Installs, but a test is skipped | Install fails or a key is found in git |
| 02 | `02-llm-client.md` | NFR-002, NFR-003, FR-017, NFR-001 | green | smoke tool call | Structured `tool_calls` from the m1max, lock test has no overlap, budget test raises | Tool call works but the thinking toggle is ignored | Tool call comes back as text in `content`, or the m1max is unreachable |
| 03 | `03-mcp-tools.md` | FR-002, FR-005, NFR-001 | green | live search + read | Live search and read work, robots/rate/timeout tests pass | Unit tests pass, but MCP is not yet reachable from the LAN | Direct fetch used, or robots blocks every URL |
| 04 | `04-store.md` | FR-001, 003, 004, 006, 012, 013 | green | store tests | All store tests pass | — | Any store test fails, or a write lands outside `RESEARCH_DIR` |
| 05 | `05-ranker.md` | NFR-003 | green | budget test | Under budget and the relevant chunk is kept | Under budget but the relevant chunk is dropped | Over budget |
| 06 | `06-qwen-prompts.md` | FR-006, 007, 009, 017, NFR-008 | green | prompt checks | 4 prompts, placeholders and few-shot present, grep is clean | A placeholder is missing | A prompt says it can't browse or asks for disclaimers |
| 07 | `07-research-loop.md` | FR-002–004, 006–009, 017, NFR-004 | green | fake-run tests | Citations match files, retries and failure line, bad JSON not executed, no refetch | Report written but a citation is stripped as bad | `BudgetExceeded`, an invalid call is executed, or a citation has no file |
| 08 | `08-resume.md` | FR-010, FR-004 | not started | kill/resume test | Resume finishes with no refetch and no replanning | Finishes but replans | Duplicate sources or unreadable `state.json` |
| 09 | `09-followup.md` | FR-011, FR-012, NFR-004 | not started | follow-up tests | Covered question makes no fetch, uncovered one adds the next source, `followups.md` has 2 entries | Answers but adds a needless fetch | New source lands outside the folder, or numbering collides |
| 10 | `10-cli.md` | FR-001, 010, 011 | not started | live CLI run | Live research has ≥8 sources, resume works, ask answers | Fewer than 8 sources | Live run fails |
| 11 | `11-gui-read.md` | FR-013, 014, NFR-007, 009 | not started | web tests + LAN open | List, links and source page work, opens from the LAN, `/health` returns JSON | Works only from localhost | Path traversal works, or pages error |
| 12 | `12-gui-live.md` | FR-015, 016, 010, NFR-002 | not started | browser run | Live progress, follow-up saved, resume on restart, no LLM overlap | Progress shows only after a reload | Overlapping model calls, or a task is stuck `running` |
| 13 | `13-e2e-verify.md` | FR-006–008, NFR-001, 005, 006, 008 | not started | pcap + checks | Only the m1max and MCP in the pcap, all checks pass with evidence | A `should` row fails | An unexpected outbound host, or a `must` row fails |

## Notes


### 01
- `pip install -e '.[dev]'` OK. `python -m researcher --help` lists research, resume, ask, serve.
- `pytest -q` → `1 passed` (config load, missing-key ValueError, JSON log line).
- `git grep --untracked -i api_key` → only variable names (`.env.example` has `M1MAX_API_KEY=` empty).
- Added `asyncio_default_fixture_loop_scope` and package-data for prompts/templates to `pyproject.toml`.

### 02
- Server: M1Model gateway (uvicorn proxy, per-client keys) on :8080 in front of `mlx_vlm.server` (vllm-metal build) on 127.0.0.1:8000, `--max-num-seqs 4`.
- Model id: `mlx-community/Qwen3.8-27B-4bit` (loaded). Context size: not set on the engine (model default); app budget stays 48000.
- Key: client `researcher` in the gateway's `GATEWAY_KEYS`; vm1 copy at `~/.config/m1model/researcher.key`; recorded in gbrain `homestack/services` (m1max).
- `tests/smoke_m1max.py` → structured `tool_calls[0].name == "get_time"` with `{'timezone': 'Asia/Tokyo'}` for both modes, final answer returned, `SMOKE OK`.
- Thinking toggle works: thinking=True → reasoning returned (`think block seen=True`), thinking=False → none.
- `pytest -q` → 3 passed (lock: no overlapping intervals; 300K chars → `BudgetExceeded`).
- Derived signature change: `LLM.__init__(cfg, client=None)` so tests can inject a fake `AsyncOpenAI`.

### 03
- `curl http://12.0.0.225:3000/health` → 200. MCP-Searxng 2.10.1 lists 4 tools; `schemas()` exposes only `searxng_web_search`, `web_url_read`.
- Live: `search("qwen 3")` → 10 results (first `https://huggingface.co/collections/Qwen/qwen3`); `read_url("https://example.com")` → markdown.
- Live robots: `read_url("https://github.com/search/advanced")` → `None` with log `skipped: robots`; `https://github.com/ggml-org/llama.cpp` → 42801 chars, fetched 2.97 s after the robots fetch to the same host.
- Live robots text arrives wrapped in ```` ```text ```` fences; `_strip_fences` removes them (unit test parses the fenced text correctly). A missing robots.txt comes back as an MCP error → allowed.
- `pytest -q` → 9 passed (robots disallow + log, 2 s gap with patched clock, 0.1 s timeout → `ToolError`, schema filter, search shape).
- Derived deviations: mcp 2.3.0 renamed `streamablehttp_client` → `streamable_http_client` (yields 2 streams) and uses snake_case (`input_schema`, `is_error`). Log field is `tool_args`, not `args` (`args` is reserved on `LogRecord`). Added a per-host `asyncio.Lock` so the 2 s gap holds across concurrent tasks (needed for inc12). `search` takes an optional `task` kwarg for logging.
- Known limit (shortcut comment in code): stdlib `RobotFileParser` ignores `*`/`$` wildcards, so wildcard-only rules (e.g. GitHub `Disallow: /search$`) are not enforced.
- Seen once at session close: mcp library logs `Error parsing SSE message ... BrokenResourceError` during teardown after a large response; results were already returned. Not a failure; watch for it in inc12.

### 04
- `pytest tests/test_store.py -q` → 7 passed (all 15 in the suite): new_task folder + `-2` suffix (FR-001), sources numbered 1,2,3 with `n/url/title/fetched_at` headers (FR-003), `find_source` hit and `add_source` dedupe (FR-004), report ends with `[n] title — url` list matching `state["sources"]` (FR-006), two follow-up entries (FR-012), `list_tasks` newest first and `unfinished` (FR-013).
- Atomic write check (also the inc08 isolation test): `os.replace` raising mid-save leaves the previous `state.json` readable.
- Writes stay inside `RESEARCH_DIR`: folder names come from `slugify` (only `[a-z0-9-]`), source names from a sanitized netloc.
- Added helper `slugify` (public) and `add_source` returns the existing number on a duplicate URL.

### 05
- `pytest tests/test_rank.py -q` → 2 passed: 20 sources × 50K chars, budget 8000 → estimated tokens ≤ 8000, the chunk holding the question terms is kept, output sorted by `n`.
- Standard library only. Paragraphs longer than `max_chars` are cut into `max_chars` pieces so no chunk exceeds it.

### 06
- `load_prompt` returns all 4 files (planner 1039, executor 2063, synthesizer 1436, followup 1303 chars).
- Placeholders present: planner `{today} {question}`; executor `{today} {question} {plan} {min_sources} {max_sources}`; synthesizer `{today} {question} {chunks}`; followup `{today} {report} {chunks} {question}`.
- Executor has both few-shot `<tool_call>` blocks plus a `<tool_response>` failure → retry example.
- `grep -rinE "cannot browse|can't browse|as an ai|disclaimer" researcher/prompts/` → 5 lines, each a "Never say…/Do not… add disclaimers" instruction. `test_prompts` enforces this.
- The prompts hold literal JSON braces, so the agent fills placeholders with `str.replace`, not `str.format`.

### 07
- `pytest -q` → 27 passed. Fake-run tests: every `[n]` in the report has a `sources/NN-*.md` file and a bad `[7]` is stripped (FR-006); `[unverified]` passes through (FR-007); a repeated URL is read once and the model gets `already saved as [1]` (FR-004); 3 failing reads → `## Failures` line (FR-009); bad JSON and an unknown tool (`rm_rf`) are not executed and the next message carries the error (NFR-004); thinking True for plan/synth, False for gather (FR-017); plan fallback to `[question]` after 3 bad replies; `max_sources` cap (FR-008); trimming keeps 26 gather requests ≤ a 6000-token budget (NFR-003); exception → `status=failed`.
- Isolation run 1 (real Qwen, fake Tools): plan JSON parsed (6 queries), structured tool calls every turn, 7 sources. Two failures found:
  1. Report body empty: synth returned `finish_reason=length` after 2048 tokens of reasoning (server default `max_tokens`). Fix in `llm.py` (bug fix): `max_tokens=min(8192, budget - est)` so input + output stay in budget; log `finish`; `est >= budget` raises.
  2. Gather looped: ~30 re-reads of saved URLs until the 40-turn cap. Fix in `agent.py`: duplicate reads get a "do not read it again" result, every `saved as` result shows progress against the target, and 3 duplicate reads in a row stop gather (`stuck` event).
- Isolation run 2: loop fix confirmed (6 saved, 3 duplicates, `stuck`, 13 model calls vs 42). Synth did not finish inside 25 min: the m1max was shared with other clients (engine ~3 tok/s per request) and the OpenAI SDK's default 600 s timeout + 2 retries silently re-sent the request (engine log showed two copies decoding). Fix in `llm.py` (bug fix): `timeout=1800` (gateway `REQUEST_TIMEOUT_S`), `max_retries=0`. Empty synth text now raises → `status=failed` instead of writing an empty report.
- Not yet confirmed live: a full synth on the real model. Covered by inc10's live run.
- Derived: `tool_loop(...)` is the shared model↔tool helper (inc09 reuses it). `fill(name, **values)` fills placeholders with `str.replace`.
