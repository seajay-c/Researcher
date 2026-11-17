# INCREMENT 09: Follow-up questions

- **Status:** Standard
- **Dependencies:** 07
- **SRS IDs:** **SRS-FR-011**, **SRS-FR-012**, **SRS-NFR-004**

### Rules

- New sources found while answering a follow-up go into the same folder under the next numbers.
- Reuse the gather tool-call handling from increment 07. Do not write a second copy.

### Capability

Answer a question about an existing research folder, citing saved sources, and search for more only when they don't cover it.

### May change

`researcher/agent.py` (you may extract the gather tool handling into a shared helper) and `tests/test_agent.py`.

### Implementation

- `derived`: `async def ask(folder: Path, question: str, llm, tools, cfg, on_event=None) -> str`.
- Messages: the followup prompt, the first 2000 characters of `report.md`, and `rank.top_chunks(question, read_sources, budget - 8000)`. Pass `tools.schemas()` and `thinking=True`.
- Run the same tool loop as gather, capped at 15 turns and at `cfg.max_sources` new sources. The final assistant `content` is the answer.
- Remove `[n]` citations that don't match a source number. Then `store.append_followup(folder, question, answer)` and return the answer.

### Verification

- Fake LLM that answers right away: no `Tools` calls, and `followups.md` has the entry (**SRS-FR-011**, **SRS-FR-012**).
- Fake LLM that calls search and read: a new `sources/NN-*.md` is created with the next number and cited in the answer (**SRS-FR-011**).
- Two follow-ups leave two entries in `followups.md`.

### Rules (repeat)

- Save new sources in the same folder under the next numbers. Reuse the gather tool handling.
