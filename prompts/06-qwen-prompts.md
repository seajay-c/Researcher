# INCREMENT 06: Qwen system prompts

- **Status:** Standard
- **Dependencies:** 02, 03
- **SRS IDs:** **SRS-FR-006**, **SRS-FR-007**, **SRS-FR-009**, **SRS-FR-017**, **SRS-NFR-008**

### Rules

- Write prompts only in `researcher/prompts/`. Write no Python except a loader.
- Do not include text that tells the model it cannot browse, and do not ask for disclaimers.

### Capability

Four system prompts that make Qwen use its tools, cite only saved sources and stay concise.

### May change

Create `researcher/prompts/{planner,executor,synthesizer,followup}.md`. Add `load_prompt(name) -> str` to `researcher/agent.py` (create the file with only this function, which reads `researcher/prompts/<name>.md`).

### Implementation

Every prompt states:
- It **has live web access** through `searxng_web_search` and `web_url_read`, and must use them for anything that changes over time. It never says it can't browse (**SRS-NFR-008**).
- It does not refuse, moralize, hedge or add disclaimers on ordinary research or scraping.
- When a tool fails, it retries with a different query or source. If it still fails, it reports the failure in one line (**SRS-FR-009**).
- Today's date is `{today}`. The agent fills this placeholder.

Per prompt:
- **planner.md** (thinking on): given `{question}`, return only the JSON `{"queries": ["…", …]}` with 3–6 diverse search queries. No prose.
- **executor.md** (thinking off): gather sources for `{question}` using `{plan}`. Call one tool per turn. Prefer primary or official sources and skip duplicates. Stop calling tools (reply with a short plain-text note) when `{min_sources}`–`{max_sources}` good pages are saved. Tool calls only, with no prose around them. Few-shot examples in Qwen's native format:
  ```
  <tool_call>
  {"name": "searxng_web_search", "arguments": {"query": "Qwen3 tool calling llama.cpp jinja", "num_results": 10}}
  </tool_call>
  ```
  ```
  <tool_call>
  {"name": "web_url_read", "arguments": {"url": "https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md"}}
  </tool_call>
  ```
  Include one `<tool_response>` example showing a failed read followed by a retry with a different URL.
- **synthesizer.md** (thinking on): given `{question}` and chunks labelled `[n]`, write a markdown report: a short answer first, then sections. Every factual sentence ends with `[n]` taken only from the given labels. A claim with no supporting chunk gets `[unverified]` (**SRS-FR-007**). Never invent a number or URL. Do not write a sources list; the code appends it. Show one short good example paragraph.
- **followup.md**: given the report summary, chunks labelled `[n]` and `{question}`, answer from the chunks if they cover it. Otherwise call the tools as the executor does, then answer. Same citation rules.

### Verification

- `load_prompt` returns each of the four files.
- `grep -riE "cannot browse|can't browse|as an ai|disclaimer" researcher/prompts/` matches only lines that tell the model to avoid these (**SRS-NFR-008**).
- Each prompt contains `{today}` and its own placeholders. The executor contains both few-shot `<tool_call>` blocks.

### Rules (repeat)

- Write prompts only. Never say the model can't browse, and never ask for disclaimers.
