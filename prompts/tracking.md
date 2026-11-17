# Tracking

Status values: `not started`, `green`, `yellow`, `red`, `rolled back`. Put evidence (command and trimmed output) in the Notes section under the row's number.

| Increment | File | SRS IDs | Status | Metric | Green | Yellow | Red |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | `01-skeleton.md` | stack, NFR-005, NFR-006 | green | install + config test | pip install OK, `--help` lists 4 subcommands, config/log test passes | Installs, but a test is skipped | Install fails or a key is found in git |
| 02 | `02-llm-client.md` | NFR-002, NFR-003, FR-017, NFR-001 | green | smoke tool call | Structured `tool_calls` from the m1max, lock test has no overlap, budget test raises | Tool call works but the thinking toggle is ignored | Tool call comes back as text in `content`, or the m1max is unreachable |
| 03 | `03-mcp-tools.md` | FR-002, FR-005, NFR-001 | not started | live search + read | Live search and read work, robots/rate/timeout tests pass | Unit tests pass, but MCP is not yet reachable from the LAN | Direct fetch used, or robots blocks every URL |
| 04 | `04-store.md` | FR-001, 003, 004, 006, 012, 013 | not started | store tests | All store tests pass | — | Any store test fails, or a write lands outside `RESEARCH_DIR` |
| 05 | `05-ranker.md` | NFR-003 | not started | budget test | Under budget and the relevant chunk is kept | Under budget but the relevant chunk is dropped | Over budget |
| 06 | `06-qwen-prompts.md` | FR-006, 007, 009, 017, NFR-008 | not started | prompt checks | 4 prompts, placeholders and few-shot present, grep is clean | A placeholder is missing | A prompt says it can't browse or asks for disclaimers |
| 07 | `07-research-loop.md` | FR-002–004, 006–009, 017, NFR-004 | not started | fake-run tests | Citations match files, retries and failure line, bad JSON not executed, no refetch | Report written but a citation is stripped as bad | `BudgetExceeded`, an invalid call is executed, or a citation has no file |
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
