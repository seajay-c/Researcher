import json
import logging

import pytest

from researcher import config
from researcher.log import JsonFormatter, get_logger


def test_config_and_log(tmp_path, monkeypatch, capsys):
    for k in ("M1MAX_URL", "M1MAX_API_KEY", "M1MAX_MODEL", "MCP_URL", "CONTEXT_BUDGET"):
        monkeypatch.delenv(k, raising=False)
    env = tmp_path / ".env"
    env.write_text("# c\n\nM1MAX_URL=http://m/v1\nM1MAX_API_KEY=k\nM1MAX_MODEL=q\nMCP_URL=http://x/mcp\nCONTEXT_BUDGET=999999\n")
    cfg = config.load(env)
    assert (cfg.m1max_url, cfg.m1max_api_key, cfg.mcp_url, cfg.gui_port) == ("http://m/v1", "k", "http://x/mcp", 8090)
    assert cfg.context_budget == 64000
    env.write_text("M1MAX_URL=http://m/v1\nM1MAX_MODEL=q\nMCP_URL=http://x/mcp\n")
    with pytest.raises(ValueError, match="M1MAX_API_KEY"):
        config.load(env)

    get_logger("t")  # installs the JSON handler
    rec = logging.makeLogRecord({"msg": "hello", "levelname": "INFO", "name": "researcher.t", "task": "t1", "n": 3})
    line = json.loads(JsonFormatter().format(rec))
    assert line["event"] == "hello" and line["task"] == "t1" and line["n"] == 3 and "ts" in line


from researcher import store


def test_new_task(tmp_path):
    f = store.new_task(tmp_path, "What is SearXNG?")
    assert f.name.endswith("-what-is-searxng") and (f / "sources").is_dir()
    s = store.load_state(f)
    assert (s["status"], s["phase"], s["id"]) == ("running", "plan", f.name)
    assert store.new_task(tmp_path, "What is SearXNG?").name == f.name + "-2"


def test_add_find_sources(tmp_path):
    f = store.new_task(tmp_path, "q")
    s = store.load_state(f)
    ns = [store.add_source(f, s, f"https://ex{i}.com/p", f"T{i}", f"# T{i}\nbody {i}") for i in (1, 2, 3)]
    assert ns == [1, 2, 3]
    head = (f / "sources/02-ex2.com.md").read_text().split("---")[1]
    assert "n: 2" in head and "url: https://ex2.com/p" in head and "title: T2" in head and "fetched_at: " in head
    assert store.find_source(s, "https://ex2.com/p")["n"] == 2 and store.find_source(s, "https://nope") is None
    assert store.add_source(f, s, "https://ex2.com/p", "dup", "x") == 2 and len(s["sources"]) == 3
    assert store.load_state(f)["sources"] == s["sources"]
    assert store.read_sources(f)[0]["text"] == "# T1\nbody 1"


def test_write_report(tmp_path):
    f = store.new_task(tmp_path, "q")
    s = store.load_state(f)
    for i in (1, 2):
        store.add_source(f, s, f"https://ex{i}.com/", f"T{i}", "x")
    store.write_report(f, "Answer [1] and [2].", s)
    tail = (f / "report.md").read_text().split("## Sources")[1]
    assert [l for l in tail.splitlines() if l] == ["[1] T1 — https://ex1.com/", "[2] T2 — https://ex2.com/"]


def test_followups(tmp_path):
    f = store.new_task(tmp_path, "q")
    store.append_followup(f, "one?", "A [1]")
    store.append_followup(f, "two?", "B")
    assert (f / "followups.md").read_text().count("## Q: ") == 2


def test_list_and_unfinished(tmp_path):
    a = store.new_task(tmp_path, "first")
    b = store.new_task(tmp_path, "second")
    sb = store.load_state(b); sb["status"] = "done"; store.save_state(b, sb)
    assert [t["id"] for t in store.list_tasks(tmp_path)] == [b.name, a.name]
    assert store.unfinished(tmp_path) == [a]


def test_save_state_kill_keeps_old(tmp_path, monkeypatch):
    f = store.new_task(tmp_path, "q")
    s = store.load_state(f)
    s["plan"] = ["x"]
    def boom(*a):
        raise KeyboardInterrupt
    monkeypatch.setattr(store.os, "replace", boom)
    try:
        store.save_state(f, s)
    except KeyboardInterrupt:
        pass
    assert store.load_state(f)["plan"] == []
