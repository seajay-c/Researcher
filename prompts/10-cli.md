# INCREMENT 10: CLI commands

- **Status:** Standard
- **Dependencies:** 08, 09
- **SRS IDs:** **SRS-FR-001**, **SRS-FR-010**, **SRS-FR-011**

### Rules

- The CLI only parses arguments and calls functions from `agent`, `store` and `config`. It holds no logic.

### Capability

The `research`, `resume` and `ask` subcommands work from the terminal. `serve` is still a stub.

### May change

`researcher/__main__.py`.

### Implementation

- `research "<question>"`: `store.new_task`, then `run_research` inside `async with Tools(cfg)`. Print each event as one line and print the folder path at the end.
- `resume [folder]`: with a folder, call `run_research` on it. Without one, call `resume_all`.
- `ask <folder> "<question>"`: print the answer.
- Use the `cfg.research_dir` root. Exit non-zero with a one-line message on `ValueError` from config or on `ToolError`.

### Verification

- `.venv/bin/python -m researcher research "What is SearXNG?"` creates `research/<date>-what-is-searxng/` with `report.md` and 8 or more `sources/` files (**SRS-FR-001**, **SRS-FR-008**).
- Press Ctrl-C during gather, then run `.venv/bin/python -m researcher resume`: it finishes and the log shows no refetch (**SRS-FR-010**).
- `.venv/bin/python -m researcher ask research/<that folder> "Who maintains it?"` prints a cited answer (**SRS-FR-011**).

### Rules (repeat)

- The CLI holds no logic.
