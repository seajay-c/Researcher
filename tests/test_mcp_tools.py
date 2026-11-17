import asyncio
import json
import logging
from types import SimpleNamespace as NS

import pytest

from researcher import mcp_tools
from researcher.mcp_tools import Tools, ToolError, _strip_fences

ROBOTS = "```text\nUser-agent: *\nDisallow: /private/\n```"


class FakeSession:
    def __init__(self, hang=False):
        self.calls, self.hang = [], hang

    async def list_tools(self):
        mk = lambda n: NS(name=n, description=n, input_schema={"type": "object"})
        return NS(tools=[mk("searxng_web_search"), mk("web_url_read"), mk("searxng_instance_info")])

    async def call_tool(self, name, args):
        self.calls.append((name, args, mcp_tools._now()))
        if self.hang:
            await asyncio.sleep(10)
        if name == "searxng_web_search":
            return NS(is_error=False, content=[NS(text=json.dumps({"results": [{"title": "T", "url": "https://a.com/x", "content": "s"}]}))])
        if args["url"].endswith("/robots.txt"):
            return NS(is_error=False, content=[NS(text=ROBOTS)])
        return NS(is_error=False, content=[NS(text="# Page\nbody")])


@pytest.fixture
def clock(monkeypatch):
    t = {"now": 1000.0}
    async def sleep(s):
        t["now"] += s
    monkeypatch.setattr(mcp_tools, "_now", lambda: t["now"])
    monkeypatch.setattr(mcp_tools, "_sleep", sleep)
    return t


def test_strip_fences_parses():
    from urllib.robotparser import RobotFileParser
    rp = RobotFileParser(); rp.parse(_strip_fences(ROBOTS).splitlines())
    assert rp.can_fetch("*", "https://a.com/ok") and not rp.can_fetch("*", "https://a.com/private/x")


async def test_schemas_filtered(cfg):
    names = [s["function"]["name"] for s in await Tools(cfg, FakeSession()).schemas()]
    assert names == ["searxng_web_search", "web_url_read"]


async def test_robots_disallow(cfg, clock, caplog):
    caplog.set_level(logging.INFO, logger="researcher")
    t = Tools(cfg, FakeSession())
    assert await t.read_url("https://a.com/private/x") is None
    assert "skipped: robots" in [r.getMessage() for r in caplog.records]
    assert await t.read_url("https://a.com/ok") == "# Page\nbody"


async def test_rate_limit(cfg, clock):
    s = FakeSession()
    t = Tools(cfg, s)
    await t.read_url("https://a.com/1")
    await t.read_url("https://a.com/2")
    times = [c[2] for c in s.calls if c[0] == "web_url_read"]  # robots, /1, /2
    assert len(times) == 3 and all(b - a >= 2.0 for a, b in zip(times, times[1:]))


async def test_timeout(cfg, monkeypatch):
    monkeypatch.setattr(mcp_tools, "TIMEOUT", 0.1)
    with pytest.raises(ToolError, match="timed out"):
        await Tools(cfg, FakeSession(hang=True)).search("q")


async def test_search_shape(cfg):
    assert await Tools(cfg, FakeSession()).search("q") == [{"title": "T", "url": "https://a.com/x", "snippet": "s"}]
