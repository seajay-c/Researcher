import asyncio
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

from .. import store
from ..config import Config

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
_MD = MarkdownIt("commonmark", {"html": False}).enable("table")  # html off: scraped pages must not inject markup
_CITE = re.compile(r"\[(\d+)\]")


def render_md(text: str, task_id: str | None = None, valid: set[int] | None = None) -> str:
    html = _MD.render(text)
    if task_id is None:
        return html
    def link(m):
        n = int(m.group(1))
        return f'<a class="cite" href="/r/{task_id}/s/{n}">[{n}]</a>' if valid is None or n in valid else m.group(0)
    return _CITE.sub(link, html)  # SRS-FR-014


def _probe(url: str, headers: dict | None = None) -> bool:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=3) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def create_app(cfg: Config) -> FastAPI:
    app = FastAPI(title="Researcher")
    root = cfg.research_dir

    def folder_of(task_id: str) -> Path:
        if not task_id or "/" in task_id or "\\" in task_id or ".." in task_id:
            raise HTTPException(404)
        folder = (root / task_id).resolve()
        if folder.parent != root.resolve() or not (folder / "state.json").is_file():
            raise HTTPException(404)
        return folder

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return TEMPLATES.TemplateResponse(request, "index.html", {"tasks": store.list_tasks(root)})  # SRS-FR-013

    @app.get("/r/{task_id}", response_class=HTMLResponse)
    def report(request: Request, task_id: str):
        folder = folder_of(task_id)
        state = store.load_state(folder)
        valid = {s["n"] for s in state["sources"]}
        rep, fu = folder / "report.md", folder / "followups.md"
        return TEMPLATES.TemplateResponse(request, "report.html", {
            "state": state,
            "report_html": render_md(rep.read_text(), task_id, valid) if rep.exists() else None,
            "followups_html": render_md(fu.read_text(), task_id, valid) if fu.exists() else "",
        })

    @app.get("/r/{task_id}/s/{n}", response_class=HTMLResponse)
    def source(request: Request, task_id: str, n: int):
        folder = folder_of(task_id)
        state = store.load_state(folder)
        src = next((s for s in store.read_sources(folder) if s["n"] == n), None)
        if src is None:
            raise HTTPException(404)
        return TEMPLATES.TemplateResponse(request, "source.html", {"state": state, "src": src, "html": render_md(src["text"])})

    @app.get("/health")
    async def health():  # SRS-NFR-009; urllib only to the two allowed hosts (SRS-NFR-001)
        mcp = urlsplit(cfg.mcp_url)
        m1max, mcp_ok = await asyncio.gather(
            asyncio.to_thread(_probe, f"{cfg.m1max_url}/models", {"Authorization": f"Bearer {cfg.m1max_api_key}"}),
            asyncio.to_thread(_probe, f"{mcp.scheme}://{mcp.netloc}/health"))
        return {"m1max": m1max, "mcp": mcp_ok}

    return app
