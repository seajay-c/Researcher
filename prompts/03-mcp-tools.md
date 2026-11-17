# INCREMENT 03: MCP-Searxng tools with robots.txt, rate limit and timeout

- **Status:** CRITICAL
- **Dependencies:** 01
- **SRS IDs:** **SRS-FR-002**, **SRS-FR-005**, **SRS-NFR-001**

### Rules

- Every fetch, including `robots.txt`, goes through MCP `web_url_read`. Do not use `httpx`, `urllib.request` or any other direct fetch.
- Expose to the model only `searxng_web_search` and `web_url_read`. Take their schemas from `tools/list`.

### Capability

A single MCP session to MCP-Searxng that can search and read URLs. Reads respect robots.txt, wait 2 s between fetches to the same domain, and time out after 30 s.

### May change

Create `researcher/mcp_tools.py` and `tests/test_mcp_tools.py`. Leave earlier files unchanged.

### Implementation

- `researcher/mcp_tools.py` (`derived`):
  ```python
  class ToolError(Exception): ...
  class Tools:
      def __init__(self, cfg: Config, session=None)   # session injectable for tests
      async def __aenter__(self) / __aexit__(...)     # mcp.client.streamable_http.streamablehttp_client(cfg.mcp_url) + ClientSession.initialize()
      async def schemas(self) -> list[dict]           # OpenAI tool format, filtered to the two names
      async def search(self, query: str, num_results: int = 10) -> list[dict]   # [{title,url,snippet}]; response_format="json"
      async def read_url(self, url: str, task: str | None = None) -> str | None # None = robots disallow
      async def call(self, name: str, args: dict, task=None) -> str             # dispatch for model tool calls
  ```
- Robots: for `scheme://host`, call `web_url_read` on `/robots.txt` once per host and cache the result. Strip code fences and feed the lines to `urllib.robotparser.RobotFileParser.parse`. If that read fails, allow the URL. Check `can_fetch("*", url)`. When disallowed, log `skipped: robots` with the `url` and return `None`.
- Rate limit: keep a `dict[host, last_fetch_monotonic]` and sleep until 2 s have passed since the last fetch to that host. Count the robots fetch too.
- Timeout: wrap each MCP call in `asyncio.wait_for(…, 30)`. On a timeout, an MCP `isError` result, or an exception, raise `ToolError` with a one-line message.
- Log `mcp_call` with `tool`, `args`, `ms` and `ok` for every call (**SRS-FR-002** evidence).

### Verification

- Unit tests with a fake session:
  - A disallowed path returns `None` and logs `skipped: robots`.
  - Two reads to the same host are at least 2 s apart. Patch the clock or sleep to check this.
  - A hanging call raises `ToolError` after the timeout. Patch the timeout to 0.1 s in the test.
- Live check from vm1 (only after the Unraid fix is in): `curl http://12.0.0.225:3000/health` returns 200. A short script that opens `Tools` and runs `search("qwen 3")` and `read_url("https://example.com")` returns results.

### Risk

The MCP server may be unreachable because it is bound to 127.0.0.1. The streamable HTTP path may differ. The robots text may come back wrapped in markdown and parse wrong.

### Failure indicators

- Connection refused, or a 404 on `/mcp`.
- `can_fetch` returns `False` for every URL, which means the fences were parsed as rules.
- The live search returns an empty list while SearXNG `/search?format=json` returns results.

### Isolation test

Run the live script alone, with no agent and no LLM. Then feed `RobotFileParser` a known robots text and check `can_fetch` for allowed and disallowed paths.

### Rollback

Delete `researcher/mcp_tools.py` and its test to return to the state after increment 02. If the problem is reachability, report it to the owner. It is a container setting on plutus, not code.

### Rules (repeat)

- All fetches go through `web_url_read`. Only the two MCP tools are exposed to the model.
