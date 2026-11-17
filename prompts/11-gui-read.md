# INCREMENT 11: Web GUI viewer and health check

- **Status:** Standard
- **Dependencies:** 04, 10
- **SRS IDs:** **SRS-FR-013**, **SRS-FR-014**, **SRS-NFR-007**, **SRS-NFR-009**

### Rules

- No auth. Bind `cfg.gui_host:cfg.gui_port` (default `0.0.0.0:8090`).
- Serve files only from inside `RESEARCH_DIR`. Reject task ids that contain `/` or `..`.

### Capability

Browse research folders, read reports with clickable citations, read sources, and check health.

### May change

Create `researcher/web/app.py` and `researcher/web/templates/{base,index,report,source}.html`, and add `tests/test_web.py`. Make `serve` in `__main__.py` run uvicorn.

### Implementation

- `derived`: `def create_app(cfg: Config) -> FastAPI`.
- `GET /`: `store.list_tasks`, showing question, status and date, newest first (**SRS-FR-013**).
- `GET /r/{id}`: render `report.md` with markdown-it-py, then replace each `[n]` with `<a href="/r/{id}/s/{n}">[n]</a>` (**SRS-FR-014**). Show `followups.md` below it. If there is no report yet, show the status.
- `GET /r/{id}/s/{n}`: the rendered source, with a link to its original URL.
- `GET /health`: `{"m1max": bool, "mcp": bool}`. m1max is checked with `GET {M1MAX_URL}/models` with the key, and MCP with `GET` on the MCP base URL's `/health`. Use a 3 s timeout each (**SRS-NFR-009**). Use `urllib.request` from the standard library here: these are the two allowed hosts, so **SRS-NFR-001** holds.
- Templates: one small inline CSS block in `base.html` that reads well on a phone. No JS framework.

### Verification

- `tests/test_web.py` with FastAPI `TestClient` on a temp research dir: the list is ordered, `[2]` becomes a link to `/r/<id>/s/2`, and a source page renders. `/r/..%2F..` returns 404.
- `.venv/bin/python -m researcher serve`, then open `http://12.0.0.179:8090` from another LAN machine (**SRS-NFR-007**), and run `curl http://12.0.0.179:8090/health` (**SRS-NFR-009**).

### Rules (repeat)

- No auth. Bind to `GUI_HOST:GUI_PORT`. Serve files only from `RESEARCH_DIR`.
