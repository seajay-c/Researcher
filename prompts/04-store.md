# INCREMENT 04: Research folder store

- **Status:** Standard
- **Dependencies:** 01
- **SRS IDs:** **SRS-FR-001**, **SRS-FR-003**, **SRS-FR-004**, **SRS-FR-006** (reference list), **SRS-FR-012** (file), **SRS-FR-013** (listing data)

### Rules

- Write only inside `RESEARCH_DIR`.
- Write `state.json` atomically: write a temp file, then `os.replace`.

### Capability

Create, read and update research folders as the master context's `state.json` contract describes.

### May change

Create `researcher/store.py` and extend `tests/test_store.py`.

### Implementation

- `researcher/store.py` (`derived`):
  ```python
  def new_task(root: Path, question: str) -> Path      # research/<YYYY-MM-DD>-<slug>/, state status=running phase=plan
  def load_state(folder: Path) -> dict
  def save_state(folder: Path, state: dict) -> None   # sets "updated"
  def url_hash(url: str) -> str                        # sha256 hex of the URL
  def find_source(state: dict, url: str) -> dict | None
  def add_source(folder: Path, state: dict, url: str, title: str, markdown: str) -> int  # next n, writes file, saves state
  def read_sources(folder: Path) -> list[dict]        # [{n,url,title,text}] (text without header)
  def write_report(folder: Path, body_md: str, state: dict) -> None   # appends "## Sources" list: "[n] title — url"
  def append_followup(folder: Path, question: str, answer_md: str) -> None
  def list_tasks(root: Path) -> list[dict]           # [{id,question,status,created}] newest first
  def unfinished(root: Path) -> list[Path]           # status == "running"
  ```
- Slug: lowercase the question, replace each run of non-alphanumeric characters with `-`, and cut to 50 characters. If the folder name is taken, add `-2`, `-3` and so on.
- Source file names: `sources/{n:02d}-{netloc}.md`, with the YAML-style header from the master context.
- `followups.md` entries: `## Q: <question>` followed by the answer and a blank line.

### Verification

- Tests:
  - `new_task` creates the folder (**SRS-FR-001**).
  - `add_source` numbers sources 1, 2, 3 and writes the headers (**SRS-FR-003**).
  - `find_source` finds a URL that is already saved, which the agent uses to skip a refetch (**SRS-FR-004**).
  - `write_report` ends with a source list that matches `state["sources"]` (**SRS-FR-006**).
  - Two `append_followup` calls leave two entries (**SRS-FR-012**).
  - `list_tasks` returns tasks newest first (**SRS-FR-013**).
- `.venv/bin/pytest tests/test_store.py` passes.

### Rules (repeat)

- Write only inside `RESEARCH_DIR`. Write `state.json` atomically.
