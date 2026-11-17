# INCREMENT 02: m1max LLM client and live tool-call round trip

- **Status:** CRITICAL
- **Dependencies:** 01
- **SRS IDs:** **SRS-NFR-002**, **SRS-NFR-003**, **SRS-FR-017**, **SRS-NFR-001**

### Rules

- Call only `M1MAX_URL`. Do not use OmniRoute or any other endpoint.
- If tool calling does not come back as structured `tool_calls`, stop and fix the m1max server config (for llama.cpp, `--jinja` with the Qwen chat template). Do not parse tool calls out of `content`.

### Capability

An async client that sends one request at a time to Qwen on the m1max, with a thinking switch and a context-budget guard. It is proven by a live tool call.

### May change

Create `researcher/llm.py` and `tests/smoke_m1max.py`. Add tests to `tests/test_agent.py` (create the file). Do not change `config.py` except to add a field that this increment needs, and record any such addition in tracking.

### Implementation

- `researcher/llm.py` (`derived`):
  ```python
  _LOCK = asyncio.Lock()  # process-wide; SRS-NFR-002
  def estimate_tokens(messages: list[dict], tools: list[dict] | None = None) -> int
  class BudgetExceeded(Exception): ...
  class LLM:
      def __init__(self, cfg: Config)            # openai.AsyncOpenAI(base_url=cfg.m1max_url, api_key=cfg.m1max_api_key)
      async def chat(self, messages, *, tools=None, thinking: bool, task: str | None = None) -> dict
          # returns {"content": str|None, "tool_calls": [{"id","name","arguments": str}]}
  ```
- `estimate_tokens`: `len(json.dumps(...)) // 3`. Add the comment `# shortcut: char estimate, upgrade to the server's /tokenize if budget errors appear`. `chat` raises `BudgetExceeded` before sending if the estimate is over `cfg.context_budget` (**SRS-NFR-003**).
- Thinking (**SRS-FR-017**): send `extra_body={"chat_template_kwargs": {"enable_thinking": thinking}}`. Strip any `<think>…</think>` block from the returned `content`.
- Hold `_LOCK` around the HTTP call. Log `llm_request` (with `thinking`, `est_tokens`, `task`) and `llm_response` (with `ms`, `n_tool_calls`).
- `tests/smoke_m1max.py`: a standalone script. Load `.env`, print `GET /models`, then send one tool to Qwen, `get_time(timezone: str)`, with the prompt "What time is it in Tokyo? Use the tool." Assert that the response has `tool_calls[0].name == "get_time"` and that its arguments parse as JSON. Send a fake tool result back and print the final answer. Run it twice, with `thinking=True` and `thinking=False`, and print whether a `<think>` block appeared each time.
- Record in `prompts/tracking.md` notes: the server type (llama.cpp, MLX, LM Studio or Ollama, from the `/models` response or headers), the model id, the context size, and whether the thinking toggle took effect.

### Verification

- `.venv/bin/python tests/smoke_m1max.py` shows a structured tool call and a final answer.
- Unit test (fake `AsyncOpenAI`): fire two `chat` calls with `asyncio.gather` and record start and end times. The intervals never overlap (**SRS-NFR-002**).
- Unit test: a 300K-character message raises `BudgetExceeded` (**SRS-NFR-003**).

### Risk

Qwen tool calling on Apple Silicon servers is often broken by a missing or wrong chat template. The thinking flag may be ignored.

### Failure indicators

- The tool call appears as text inside `content` (`<tool_call>…` or raw JSON) and `tool_calls` is empty.
- The response is 401 or 404, or the connection times out.
- Thinking output appears even when thinking is off.

### Isolation test

Send the smoke test's request as raw `curl` with a minimal `tools` array, without using this package. If `curl` also fails, the problem is on the server side: fix the server flags or template. If only the package fails, fix `llm.py`.

### Rollback

Delete `researcher/llm.py` and `tests/smoke_m1max.py` to return to the state after increment 01. Set the row to `rolled back` and report the server finding to the owner.

### Rules (repeat)

- Call only the m1max. Fix the server, not the parsing, when tool calls are broken.
