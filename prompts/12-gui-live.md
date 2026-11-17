# INCREMENT 12: GUI start research, live progress, follow-up chat, resume on start

- **Status:** CRITICAL
- **Dependencies:** 11
- **SRS IDs:** **SRS-FR-015**, **SRS-FR-016**, **SRS-FR-010**, **SRS-NFR-002**

### Rules

- Share one `LLM` and one `Tools` session across all background tasks, so the global lock serializes model calls (**SRS-NFR-002**).
- Do not add a job queue service or a database.

### Capability

Start research from the browser and watch its progress live, ask follow-ups on a report page, and have unfinished tasks resume when the server starts.

### May change

`researcher/web/app.py`, `templates/index.html`, `templates/report.html` and `tests/test_web.py`.

### Implementation

- App lifespan: open `Tools(cfg)` and create `LLM(cfg)` once. Start `resume_all` as a background `asyncio` task (**SRS-FR-010**).
- `POST /research` (form field `question`): `store.new_task`, then `asyncio.create_task(run_research(..., on_event=bus.publish(id)))`, then redirect to `/r/{id}`.
- `derived` in-process bus: `dict[id, list[asyncio.Queue]]` plus the last 200 events per id, kept in memory.
- `GET /r/{id}/events`: SSE stream of the events, replaying the stored ones first. `report.html` uses `EventSource` while the status is `running`, appends each event as a line, and reloads when a `done` event arrives (**SRS-FR-016**).
- `POST /r/{id}/ask` (JSON `{"question"}`): `await agent.ask(...)` and return `{"answer_html"}`. `report.html` has a textarea and button, and appends the question and answer under the earlier follow-ups (**SRS-FR-015**).

### Verification

- In a browser, start research. The progress lines appear while it runs, and the report renders at the end (**SRS-FR-016**).
- Ask a follow-up on that page. The answer appears, and `followups.md` has it after a reload (**SRS-FR-015**).
- Kill the server during gather and restart `serve`. The task finishes without refetching (**SRS-FR-010**).
- Test: start two research tasks at once with a fake LLM that records call intervals. The intervals don't overlap (**SRS-NFR-002**).

### Risk

Background tasks, SSE and one shared MCP session running together. This can cause concurrent use of the MCP session, events lost on reconnect, or tasks dying silently.

### Failure indicators

- The SSE stream stays empty while the log shows progress.
- A second task makes the first one fail with an MCP session error.
- After a restart, the task stays `running` forever.

### Isolation test

Run `run_research` in the app with a fake LLM and fake Tools, and only the bus with SSE. Then add the real Tools. If concurrent MCP calls fail, put an `asyncio.Lock` around `Tools.call` and record that in tracking.

### Rollback

Revert `app.py` and the templates to the state after increment 11. The read-only GUI and the CLI still work.

### Rules (repeat)

- Use one shared `LLM` and one `Tools` session. No queue service and no database.
