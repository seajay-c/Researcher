# INCREMENT 05: Chunk and rank sources to the budget

- **Status:** Standard
- **Dependencies:** 02, 04
- **SRS IDs:** **SRS-NFR-003**

### Rules

- Use only the standard library. No embeddings, no extra dependency.

### Capability

Pick the source text most relevant to a question that fits a token budget.

### May change

Create `researcher/rank.py` and `tests/test_rank.py`.

### Implementation

- `researcher/rank.py` (`derived`):
  ```python
  def chunks(sources: list[dict], max_chars: int = 1500) -> list[dict]       # [{n, text}], split on blank lines, merge small paragraphs
  def top_chunks(question: str, sources: list[dict], budget_tokens: int) -> list[dict]
  ```
- Score: the count of distinct lowercase question terms (3 or more characters) that appear in the chunk, divided by `1 + len(text)/1000`. Take chunks in score order until `llm.estimate_tokens` of their texts reaches the budget, then return them sorted by `n`. Add the comment `# shortcut: term overlap, upgrade to BM25/embeddings if answers miss obvious passages`.

### Verification

- Test: 20 fake sources of 50K characters each, with a budget of 8000. The total estimated tokens of the returned chunks are 8000 or fewer, and the chunk that contains the question terms is included (**SRS-NFR-003**).

### Rules (repeat)

- Use only the standard library.
