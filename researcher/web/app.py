import asyncio
import json
import re
import urllib.request
from collections import defaultdict, deque
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from markdown_it import MarkdownIt

from .. import agent, store
from ..config import Config
from ..llm import LLM
from ..log import get_logger
from ..mcp_tools import Tools

log = get_logger("web")
END_EVENTS = ("done", "failed")

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


class Bus:
    """In-process event bus: live subscribers per task id plus the last 200 events for replay."""

    def __init__(self):
        self.subs: dict[str, list[asyncio.Queue]] = defaultdict(list)
        self.history: dict[str, deque] = defaultdict(lambda: deque(maxlen=200))

    def publish(self, event: dict) -> None:
        tid = event.get("task")
        self.history[tid].append(event)
        for q in self.subs[tid]:
            q.put_nowait(event)

    def subscribe(self, tid: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.subs[tid].append(q)
        return q

    def unsubscribe(self, tid: str, q: asyncio.Queue) -> None:
        if q in self.subs[tid]:
            self.subs[tid].remove(q)


def create_app(cfg: Config, llm=None, tools=None) -> FastAPI:
    root = cfg.research_dir
    bus = Bus()
    jobs: set[asyncio.Task] = set()  # strong refs so background tasks are not garbage-collected
    ask_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
    shared: dict = {"llm": llm, "tools": tools}

    def spawn(coro, label: str) -> None:
        job = asyncio.create_task(coro)
        jobs.add(job)

        def finished(j: asyncio.Task):
            jobs.discard(j)
            if not j.cancelled() and j.exception():
                log.error("background_failed", extra={"job": label, "error": str(j.exception())})
        job.add_done_callback(finished)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # one LLM (one lock, SRS-NFR-002) and one MCP session shared by every task
        async with AsyncExitStack() as stack:
            if shared["tools"] is None:
                try:
                    shared["tools"] = await stack.enter_async_context(Tools(cfg))
                except Exception as e:  # MCP down: keep browsing and /health up, refuse new work
                    log.error("mcp_connect_failed", extra={"error": str(e)})
            shared["llm"] = shared["llm"] or LLM(cfg)
            if shared["tools"] is not None:
                spawn(agent.resume_all(root, shared["llm"], shared["tools"], cfg, on_event=bus.publish), "resume_all")  # SRS-FR-010
            yield
            for j in list(jobs):
                j.cancel()  # tasks stay "running" in state.json and resume on the next start

    def need_tools() -> None:
        if shared["tools"] is None:
            raise HTTPException(503, "MCP-Searxng is not connected; check /health and restart serve")

    app = FastAPI(title="Researcher", lifespan=lifespan)

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

    @app.post("/research")
    async def start(request: Request):
        question = (parse_qs((await request.body()).decode()).get("question") or [""])[0].strip()
        if not question:
            raise HTTPException(400, "question is required")
        need_tools()
        folder = store.new_task(root, question)  # SRS-FR-001
        bus.publish({"event": "queued", "task": folder.name})
        spawn(agent.run_research(folder, shared["llm"], shared["tools"], cfg, on_event=bus.publish), folder.name)
        return RedirectResponse(f"/r/{folder.name}", status_code=303)

    @app.get("/r/{task_id}/events")
    async def events(task_id: str):
        folder = folder_of(task_id)

        async def stream():
            q = bus.subscribe(task_id)
            try:
                for e in list(bus.history[task_id]):  # replay first
                    yield f"data: {json.dumps(e)}\n\n"
                    if e["event"] in END_EVENTS:
                        return
                if store.load_state(folder)["status"] != "running":
                    yield f"data: {json.dumps({'event': 'done', 'task': task_id})}\n\n"
                    return
                while True:
                    try:
                        e = await asyncio.wait_for(q.get(), 15)
                    except asyncio.TimeoutError:
                        yield ": keepalive\n\n"
                        continue
                    yield f"data: {json.dumps(e)}\n\n"
                    if e["event"] in END_EVENTS:
                        return
            finally:
                bus.unsubscribe(task_id, q)
        return StreamingResponse(stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})  # SRS-FR-016

    @app.post("/r/{task_id}/ask")
    async def ask(task_id: str, request: Request):
        folder = folder_of(task_id)
        try:
            question = str((await request.json()).get("question", "")).strip()
        except (json.JSONDecodeError, AttributeError):
            question = ""
        if not question:
            raise HTTPException(400, "question is required")
        need_tools()
        if store.load_state(folder)["status"] == "running":
            return JSONResponse({"error": "research is still running; ask when it is done"}, status_code=409)
        async with ask_locks[task_id]:  # one follow-up per folder at a time: they share state.json
            answer = await agent.ask(folder, question, shared["llm"], shared["tools"], cfg, on_event=bus.publish)
        valid = {s["n"] for s in store.load_state(folder)["sources"]}
        return {"question": question, "answer_html": render_md(answer, task_id, valid)}  # SRS-FR-015

    @app.get("/health")
    async def health():  # SRS-NFR-009; urllib only to the two allowed hosts (SRS-NFR-001)
        mcp = urlsplit(cfg.mcp_url)
        m1max, mcp_ok = await asyncio.gather(
            asyncio.to_thread(_probe, f"{cfg.m1max_url}/models", {"Authorization": f"Bearer {cfg.m1max_api_key}"}),
            asyncio.to_thread(_probe, f"{mcp.scheme}://{mcp.netloc}/health"))
        return {"m1max": m1max, "mcp": mcp_ok}

    return app

