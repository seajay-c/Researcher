import re

from .llm import estimate_tokens

_TERM = re.compile(r"[a-z0-9]{3,}")


def chunks(sources: list[dict], max_chars: int = 1500) -> list[dict]:
    out = []
    for s in sources:
        buf = ""
        for para in (p.strip() for p in re.split(r"\n\s*\n", s["text"])):
            if not para:
                continue
            pieces = [para[i:i + max_chars] for i in range(0, len(para), max_chars)]  # oversized paragraphs get cut
            for piece in pieces:
                if buf and len(buf) + 2 + len(piece) > max_chars:
                    out.append({"n": s["n"], "text": buf})
                    buf = ""
                buf = f"{buf}\n\n{piece}" if buf else piece
        if buf:
            out.append({"n": s["n"], "text": buf})
    return out


def top_chunks(question: str, sources: list[dict], budget_tokens: int) -> list[dict]:
    # shortcut: term overlap, upgrade to BM25/embeddings if answers miss obvious passages
    terms = set(_TERM.findall(question.lower()))
    def score(c):
        return len(terms & set(_TERM.findall(c["text"].lower()))) / (1 + len(c["text"]) / 1000)
    picked: list[dict] = []
    for c in sorted(chunks(sources), key=score, reverse=True):
        if estimate_tokens(picked + [c]) > budget_tokens:
            break
        picked.append(c)
    return sorted(picked, key=lambda c: c["n"])
