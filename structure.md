# Structure

## Directory tree

```
pyproject.toml
.env.example
.gitignore                 # .env, .venv, __pycache__
researcher/
  __init__.py
  __main__.py              # argparse: research | resume | ask | serve
  config.py                # reads .env: M1MAX_URL, M1MAX_API_KEY, M1MAX_MODEL, MCP_URL, RESEARCH_DIR, CONTEXT_BUDGET, MAX_SOURCES, GUI_HOST, GUI_PORT
  log.py                   # JSON-lines logging
  llm.py
  mcp_tools.py
  rank.py
  store.py
  agent.py
  prompts/
    planner.md
    executor.md
    synthesizer.md
    followup.md
  web/
    app.py
    templates/
      base.html
      index.html
      report.html
      source.html
tests/
  conftest.py              # fake model, fake MCP session
  test_store.py
  test_rank.py
  test_mcp_tools.py
  test_agent.py
  test_web.py
  smoke_m1max.py           # live tool-call round trip (not run by default)
research/
  .gitkeep
  <YYYY-MM-DD>-<slug>/     # created at runtime
    state.json
    report.md
    followups.md
    sources/NN-<domain>.md
```

## Ownership

| Path | Architecture part | What it holds |
| --- | --- | --- |
| `researcher/__main__.py` | CLI | Subcommands |
| `researcher/config.py`, `log.py` | CLI | Env config, JSON logging used by all parts |
| `researcher/agent.py` | Agent | Research and follow-up loops, tool-call validation, retries, checkpoints |
| `researcher/prompts/` | Agent | Qwen system prompts with few-shot tool calls |
| `researcher/llm.py` | LLM client | m1max client, lock, thinking flag, budget |
| `researcher/mcp_tools.py` | MCP tools | MCP session, robots check, per-domain rate limit, timeouts |
| `researcher/rank.py` | Ranker | Chunk + rank to fit the budget |
| `researcher/store.py` | Store | Folder layout, state.json, URL-hash dedupe, source numbering |
| `researcher/web/` | Web GUI | FastAPI app, templates, SSE progress, `/health` |
| `tests/` | all | Unit tests with fakes, plus the live m1max smoke test |
| `research/` | Store | Research output (committed) |

## Build and run

1. `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'`
2. `cp .env.example .env` (fill in `M1MAX_API_KEY`), then `.venv/bin/python -m researcher serve` and open `http://12.0.0.179:8090`
3. `.venv/bin/pytest`, then `.venv/bin/python tests/smoke_m1max.py`

## If the build fails

1. `/health` shows m1max down: run `curl -H "Authorization: Bearer $M1MAX_API_KEY" $M1MAX_URL/v1/models` from vm1 over the tailnet. A 401 means a bad key. No response means the server or Tailscale is down.
2. MCP fails to connect: run `curl http://12.0.0.225:3000/health`. If the connection is refused, the container is bound to 127.0.0.1 again and needs `MCP_HTTP_HOST=0.0.0.0`. If `/mcp` returns 404, check the transport path in the container logs.
3. The model returns tool calls as plain text instead of `tool_calls`: the server's chat template or tool parser is wrong (for llama.cpp, use `--jinja` with the Qwen template). Fix the server, not the prompt.
