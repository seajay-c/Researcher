import hashlib
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def slugify(question: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")[:50].strip("-") or "research"


def new_task(root: Path, question: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    base = f"{date.today().isoformat()}-{slugify(question)}"
    folder, i = root / base, 2
    while folder.exists():
        folder, i = root / f"{base}-{i}", i + 1
    (folder / "sources").mkdir(parents=True)
    now = _now()
    save_state(folder, {"id": folder.name, "question": question, "status": "running", "phase": "plan",
                        "created": now, "updated": now, "plan": [], "queries_done": [], "failures": [], "sources": []})
    return folder


def load_state(folder: Path) -> dict:
    return json.loads((folder / "state.json").read_text())


def save_state(folder: Path, state: dict) -> None:
    state["updated"] = _now()
    tmp = folder / "state.json.tmp"
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    os.replace(tmp, folder / "state.json")  # atomic: a kill leaves the old or the new file, never half


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def find_source(state: dict, url: str) -> dict | None:
    h = url_hash(url)
    return next((s for s in state["sources"] if s["url_hash"] == h), None)


def add_source(folder: Path, state: dict, url: str, title: str, markdown: str) -> int:
    if existing := find_source(state, url):
        return existing["n"]
    n = max((s["n"] for s in state["sources"]), default=0) + 1
    netloc = re.sub(r"[^A-Za-z0-9.-]", "_", urlsplit(url).netloc) or "source"
    rel = f"sources/{n:02d}-{netloc}.md"
    fetched = _now()
    title = " ".join(title.split())
    (folder / "sources").mkdir(exist_ok=True)
    (folder / rel).write_text(f"---\nn: {n}\nurl: {url}\ntitle: {title}\nfetched_at: {fetched}\n---\n\n{markdown}")
    state["sources"].append({"n": n, "url": url, "url_hash": url_hash(url), "title": title, "fetched_at": fetched, "file": rel})
    save_state(folder, state)
    return n


def read_sources(folder: Path) -> list[dict]:
    out = []
    for s in load_state(folder)["sources"]:
        text = (folder / s["file"]).read_text()
        out.append({"n": s["n"], "url": s["url"], "title": s["title"], "text": text.split("\n---\n", 1)[-1].lstrip("\n")})
    return out


def write_report(folder: Path, body_md: str, state: dict) -> None:
    refs = "\n\n".join(f"[{s['n']}] {s['title']} — {s['url']}" for s in sorted(state["sources"], key=lambda s: s["n"]))
    (folder / "report.md").write_text(f"{body_md.rstrip()}\n\n## Sources\n\n{refs}\n")


def append_followup(folder: Path, question: str, answer_md: str) -> None:
    with (folder / "followups.md").open("a") as f:
        f.write(f"## Q: {question}\n\n{answer_md.strip()}\n\n")


def list_tasks(root: Path) -> list[dict]:
    tasks = []
    for p in root.glob("*/state.json") if root.exists() else []:
        try:
            s = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        tasks.append({"id": s["id"], "question": s["question"], "status": s["status"], "created": s["created"]})
    return sorted(tasks, key=lambda t: t["created"], reverse=True)


def unfinished(root: Path) -> list[Path]:
    return [root / t["id"] for t in reversed(list_tasks(root)) if t["status"] == "running"]
