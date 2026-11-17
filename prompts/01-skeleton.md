# INCREMENT 01: Project skeleton, config and logging

- **Status:** Standard
- **Dependencies:** none
- **SRS IDs:** structure/stack, **SRS-NFR-005**, **SRS-NFR-006**

### Rules

- Create only the files listed below. Write no agent logic.
- Read secrets only from `.env`. Never commit `.env`.

### Capability

The package installs, reads its config from `.env`, and logs JSON lines.

### May change

Everything listed below. This increment creates them all.

### Implementation

- `pyproject.toml`: project `researcher`, Python `>=3.12`. Dependencies `openai`, `mcp`, `fastapi`, `uvicorn`, `jinja2`, `markdown-it-py`. Extra `dev` = `pytest`, `pytest-asyncio`. Set `asyncio_mode = "auto"` under `[tool.pytest.ini_options]`.
- `.gitignore`: `.env`, `.venv/`, `__pycache__/`, `*.egg-info/`.
- `.env.example`: every variable from the master context, each with a one-line comment. `M1MAX_URL=http://100.67.98.112:8080/v1`, `MCP_URL=http://12.0.0.225:3000/mcp`. Leave `M1MAX_API_KEY` empty.
- `researcher/__init__.py`: empty.
- `researcher/config.py` (`derived`):
  ```python
  @dataclass(frozen=True)
  class Config: m1max_url: str; m1max_api_key: str; m1max_model: str; mcp_url: str
      research_dir: Path; context_budget: int; min_sources: int; max_sources: int; gui_host: str; gui_port: int
  def load(env_file: Path = Path(".env")) -> Config
  ```
  Write a small `KEY=VALUE` parser that skips `#` lines and blank lines. Real environment variables override the file. Raise `ValueError` naming any missing required key (`M1MAX_URL`, `M1MAX_API_KEY`, `M1MAX_MODEL`, `MCP_URL`). Clamp `context_budget` to 32000–64000.
- `researcher/log.py` (`derived`): `get_logger(name) -> logging.Logger` writes one JSON object per line to stderr with `ts`, `level`, `event` (the message), `task` (from `extra`, default `null`), and any other `extra` fields.
- `researcher/__main__.py`: an `argparse` parser with subcommands `research`, `resume`, `ask`, `serve`. Each prints `not implemented` and exits 2.
- `research/.gitkeep`; `tests/conftest.py` (empty for now).

### Verification

- `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'` succeeds.
- `.venv/bin/python -m researcher --help` lists the four subcommands.
- A test in `tests/test_store.py` (create it now with this one test) checks that `config.load` on a temporary `.env` returns the values and raises `ValueError` when the key is missing. A log call produces a line that `json.loads` parses (**SRS-NFR-006**).
- `git grep -i api_key` shows only variable names (**SRS-NFR-005**).

### Rules (repeat)

- Create only the files listed. Write no agent logic. Keep secrets in `.env` only.
