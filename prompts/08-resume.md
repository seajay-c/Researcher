# INCREMENT 08: Checkpoint and resume

- **Status:** CRITICAL
- **Dependencies:** 07
- **SRS IDs:** **SRS-FR-010**, **SRS-FR-004**

### Rules

- `state.json` is the only record of progress. Do not add a database or a second state file.

### Capability

`run_research` called on a folder with `status == "running"` continues from `state["phase"]` without repeating completed work.

### May change

`researcher/agent.py` and `tests/test_agent.py`.

### Implementation

- At the start of `run_research`, read `phase`:
  - `plan`: plan as usual.
  - `gather`: skip planning. Seed the executor with a user message that lists `queries_done` and the saved sources (`[n] title — url`), and tells it to continue gathering until it reaches the source target.
  - `synthesize`: go straight to synthesis.
  - `done`: return immediately.
- Set `phase="synthesize"` and save before calling the synthesizer.
- `derived`: `async def resume_all(root: Path, llm, tools, cfg, on_event=None) -> list[str]` calls `run_research` for each folder in `store.unfinished(root)`, one at a time, and returns their ids.

### Verification

- Test: run a fake gather that raises after 3 saved sources, then call `run_research` again. No second `read_url` happens for those 3 URLs, the plan is not regenerated, and the report is written (**SRS-FR-010**).
- Test: `phase="synthesize"` makes no tool calls.

### Risk

A partial write or a missing checkpoint duplicates sources or loses the plan when the process is killed.

### Failure indicators

- Source numbers have gaps or duplicates.
- The plan regenerates after a restart.
- `state.json` is unreadable after a kill.

### Isolation test

Call `store.save_state` with a kill in the middle: simulate it by raising between writing the temp file and `os.replace`. `load_state` must still return the previous state.

### Rollback

Revert `agent.py` to the state after increment 07. Resume becomes unavailable, and fresh runs still work.

### Rules (repeat)

- `state.json` is the only record of progress.
