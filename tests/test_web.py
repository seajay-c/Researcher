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
    assert "No report yet" in r


def test_health(cfg, monkeypatch):
    seen = []
    def probe(url, headers=None):
        seen.append((url, headers))
        return "models" in url
    monkeypatch.setattr(webapp, "_probe", probe)
    r = TestClient(webapp.create_app(cfg)).get("/health")
    assert r.json() == {"m1max": True, "mcp": False}  # SRS-NFR-009
    assert sorted(u for u, _ in seen) == ["http://m/v1/models", "http://x/health"]
