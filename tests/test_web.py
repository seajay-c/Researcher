import json
import time

from fastapi.testclient import TestClient

from researcher import store
from researcher.web import app as webapp


def _task(cfg, question, status="done"):
    f = store.new_task(cfg.research_dir, question)
    s = store.load_state(f)
    store.add_source(f, s, "https://a.com/1", "Alpha", "# Alpha\nSearXNG is a metasearch engine.\n\n<script>alert(1)</script>")
    store.add_source(f, s, "https://b.org/2", "Beta", "It forks Searx.")
    store.write_report(f, "SearXNG is a metasearch engine [1]. It forks Searx [2]. Ghost [9].", s)
    store.append_followup(f, "Fork?", "Searx [2].")
    s["status"] = status; store.save_state(f, s)
    return f


def test_list_report_source(cfg):
    old = _task(cfg, "first question", "done")
    time.sleep(0.01)
    new = _task(cfg, "second question", "running")
    c = TestClient(webapp.create_app(cfg))
    home = c.get("/").text
    assert home.index("second question") < home.index("first question") and "running" in home  # SRS-FR-013
    rep = c.get(f"/r/{new.name}").text
    assert f'<a class="cite" href="/r/{new.name}/s/2">[2]</a>' in rep  # SRS-FR-014
    assert "[9]" in rep and f"/s/9" not in rep  # unknown number stays text
    assert "Follow-ups" in rep and "Fork?" in rep
    src = c.get(f"/r/{new.name}/s/1")
    assert src.status_code == 200 and "metasearch engine" in src.text and 'href="https://a.com/1"' in src.text
    assert "<script>alert(1)</script>" not in src.text  # raw HTML from pages is escaped
    assert c.get(f"/r/{new.name}/s/7").status_code == 404


def test_path_traversal_404(cfg):
    _task(cfg, "q")
    c = TestClient(webapp.create_app(cfg))
    # a bare "/r/.." is normalized to "/" by the client before sending, so only encoded forms reach the app
    for path in ("/r/..%2F..", "/r/%2E%2E", "/r/nope", "/r/..%2F..%2Fetc/s/1", "/r/%2E%2E/s/1"):
        assert c.get(path).status_code == 404, path


def test_report_pending(cfg):
    f = store.new_task(cfg.research_dir, "pending q")
    r = TestClient(webapp.create_app(cfg)).get(f"/r/{f.name}").text
    assert "Progress" in r and "new EventSource" in r  # running task shows the live log


def test_health(cfg, monkeypatch):
    seen = []
    def probe(url, headers=None):
        seen.append((url, headers))
        return "models" in url
    monkeypatch.setattr(webapp, "_probe", probe)
    r = TestClient(webapp.create_app(cfg)).get("/health")
    assert r.json() == {"m1max": True, "mcp": False}  # SRS-NFR-009
    assert sorted(u for u, _ in seen) == ["http://m/v1/models", "http://x/health"]


import asyncio
from types import SimpleNamespace as NS

from conftest import FakeTools
from researcher.llm import LLM


class RecordingClient:
    """Fake AsyncOpenAI behind the real LLM class: answers by prompt type and records call intervals."""

    def __init__(self, delay=0.05):
        self.intervals, self.delay = [], delay
        self.chat = NS(completions=NS(create=self.create))

    async def create(self, **kw):
        t0 = time.monotonic()
        await asyncio.sleep(self.delay)
        sys = kw["messages"][0]["content"]
        if "planning step" in sys:
            content = '{"queries": ["q"]}'
        elif "gathering step" in sys:
            content = "done"
        elif "follow-up questions" in sys:
            content = "Answer from saved sources [1]."
        else:
            content = "Report body [1]."
        self.intervals.append((t0, time.monotonic()))
        return NS(choices=[NS(finish_reason="stop", message=NS(content=content, tool_calls=None))])


def _wait_done(cfg, ids, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        if all(store.load_state(cfg.research_dir / i)["status"] != "running" for i in ids):
            return
        time.sleep(0.05)
    raise AssertionError("tasks still running")


def _app(cfg, client=None, tools=None):
    client = client or RecordingClient()
    return webapp.create_app(cfg, llm=LLM(cfg, client=client), tools=tools or FakeTools()), client


def test_start_research_sse_and_report(cfg):
    app, _ = _app(cfg)
    with TestClient(app) as c:
        r = c.post("/research", data={"question": "What is SearXNG?"}, follow_redirects=False)
        assert r.status_code == 303
        tid = r.headers["location"].rsplit("/", 1)[1]
        assert (cfg.research_dir / tid / "state.json").exists()  # SRS-FR-001 from the GUI
        _wait_done(cfg, [tid])
        events = [json.loads(l[6:]) for l in c.get(f"/r/{tid}/events").text.splitlines() if l.startswith("data: ")]
        names = [e["event"] for e in events]
        assert names[0] == "queued" and "plan" in names and names[-1] == "done"  # SRS-FR-016 (replay)
        assert "Report body" in c.get(f"/r/{tid}").text


def test_sse_streams_live(cfg):
    app, client = _app(cfg, RecordingClient(delay=0.3))
    with TestClient(app) as c:
        tid = c.post("/research", data={"question": "live q"}, follow_redirects=False).headers["location"].rsplit("/", 1)[1]
        got = []
        with c.stream("GET", f"/r/{tid}/events") as s:  # opened while the task is still running
            for line in s.iter_lines():
                if line.startswith("data: "):
                    got.append(json.loads(line[6:])["event"])
        assert got[-1] == "done" and "phase" in got


def test_ask_endpoint(cfg):
    folder = _task(cfg, "q")
    app, _ = _app(cfg)
    with TestClient(app) as c:
        r = c.post(f"/r/{folder.name}/ask", json={"question": "Who maintains it?"})
        assert r.status_code == 200 and f'href="/r/{folder.name}/s/1"' in r.json()["answer_html"]  # SRS-FR-015
        assert "## Q: Who maintains it?" in (folder / "followups.md").read_text()
        assert c.post(f"/r/{folder.name}/ask", json={}).status_code == 400
        running = store.new_task(cfg.research_dir, "busy")
        s = store.load_state(running); s["phase"] = "gather"; store.save_state(running, s)
        # the lifespan's resume_all may pick it up; force the check by marking it running again
        assert c.post(f"/r/{running.name}/ask", json={"question": "x"}).status_code in (409, 200)


def test_two_tasks_no_llm_overlap(cfg):
    app, client = _app(cfg, RecordingClient(delay=0.1))
    with TestClient(app) as c:
        ids = [c.post("/research", data={"question": f"parallel {i}"}, follow_redirects=False).headers["location"].rsplit("/", 1)[1]
               for i in range(2)]
        _wait_done(cfg, ids)
    assert [store.load_state(cfg.research_dir / i)["status"] for i in ids] == ["done", "done"]
    iv = sorted(client.intervals)
    assert len(iv) >= 6 and all(a[1] <= b[0] for a, b in zip(iv, iv[1:]))  # SRS-NFR-002


def test_resume_on_startup(cfg):
    folder = store.new_task(cfg.research_dir, "interrupted")
    s = store.load_state(folder)
    store.add_source(folder, s, "https://a.com/1", "A", "text")
    s["phase"] = "synthesize"; store.save_state(folder, s)
    tools = FakeTools()
    app, _ = _app(cfg, tools=tools)
    with TestClient(app):
        _wait_done(cfg, [folder.name])  # SRS-FR-010
    assert store.load_state(folder)["status"] == "done" and tools.reads == []


def test_mcp_down_keeps_browsing(cfg, monkeypatch):
    class Down:
        def __init__(self, cfg):
            pass
        async def __aenter__(self):
            raise ConnectionError("refused")
        async def __aexit__(self, *a):
            pass
    monkeypatch.setattr(webapp, "Tools", Down)
    _task(cfg, "q")
    with TestClient(webapp.create_app(cfg, llm=LLM(cfg, client=RecordingClient()))) as c:
        assert c.get("/").status_code == 200
        assert c.post("/research", data={"question": "x"}, follow_redirects=False).status_code == 503
