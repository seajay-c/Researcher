import random

from researcher.llm import estimate_tokens
from researcher.rank import chunks, top_chunks


def test_budget_and_relevance():
    rnd = random.Random(0)
    words = ["lorem", "ipsum", "dolor", "amet", "consectetur", "adipiscing", "elit", "sed", "tempor"]
    filler = lambda n: "\n\n".join(" ".join(rnd.choice(words) for _ in range(60)) for _ in range(n))
    sources = [{"n": i, "text": filler(130)[:50_000]} for i in range(1, 21)]
    needle = "The SearXNG maintainer team released version nine of the metasearch engine."
    sources[13]["text"] = sources[13]["text"][:25_000] + "\n\n" + needle + "\n\n" + sources[13]["text"][25_000:]
    picked = top_chunks("Who maintains the SearXNG metasearch engine?", sources, 8000)
    assert estimate_tokens(picked) <= 8000
    assert any(needle in c["text"] for c in picked)
    assert [c["n"] for c in picked] == sorted(c["n"] for c in picked)


def test_chunks_merge_and_cut():
    cs = chunks([{"n": 1, "text": "a\n\nb\n\n" + "x" * 4000}], max_chars=1500)
    assert cs[0]["text"].startswith("a\n\nb") and all(len(c["text"]) <= 1500 for c in cs)
