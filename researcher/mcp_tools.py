import asyncio
import json
import time
from collections import defaultdict
from contextlib import AsyncExitStack
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .config import Config
from .log import get_logger

EXPOSED = ("searxng_web_search", "web_url_read")
TIMEOUT = 30.0  # seconds per MCP call; SRS-FR-005
DOMAIN_GAP = 2.0  # seconds between fetches to one host; SRS-FR-005
_now = time.monotonic  # module-level so tests can patch the clock
_sleep = asyncio.sleep
log = get_logger("mcp")


class ToolError(Exception):
    pass


def _strip_fences(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not l.strip().startswith("```"))


class Tools:
    def __init__(self, cfg: Config, session=None):
        self.cfg = cfg
        self.session = session
        self._stack: AsyncExitStack | None = None
        self._schemas: list[dict] | None = None
        self._robots: dict[str, RobotFileParser | None] = {}
        self._last: dict[str, float] = {}
        self._host_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def __aenter__(self):
        if self.session is None:
            self._stack = AsyncExitStack()
            read, write = await self._stack.enter_async_context(streamable_http_client(self.cfg.mcp_url))
            self.session = await self._stack.enter_async_context(ClientSession(read, write))
            await self.session.initialize()
        return self

    async def __aexit__(self, *exc):
        if self._stack:
            await self._stack.aclose()
            self._stack, self.session = None, None

    async def _call(self, name: str, args: dict, task=None) -> str:
        t0 = _now()
        ok = False
        try:
            res = await asyncio.wait_for(self.session.call_tool(name, args), TIMEOUT)
            text = "\n".join(getattr(c, "text", "") for c in res.content)
            if res.is_error:
                raise ToolError(f"{name} error: {text.strip().splitlines()[0] if text.strip() else 'unknown'}")
            ok = True
            return text
        except asyncio.TimeoutError:
            raise ToolError(f"{name} timed out after {TIMEOUT:g}s") from None
        except ToolError:
            raise
        except Exception as e:  # transport and protocol errors
            raise ToolError(f"{name} failed: {type(e).__name__}: {e}".splitlines()[0]) from e
        finally:
            log.info("mcp_call", extra={"task": task, "tool": name, "tool_args": args, "ms": int((_now() - t0) * 1000), "ok": ok})

    async def schemas(self) -> list[dict]:
        if self._schemas is None:
            listed = await self.session.list_tools()
            self._schemas = [{"type": "function", "function": {
                "name": t.name, "description": t.description or "", "parameters": t.input_schema}}
                for t in listed.tools if t.name in EXPOSED]
        return self._schemas

    async def search(self, query: str, num_results: int = 10, task=None) -> list[dict]:
        text = await self._call("searxng_web_search",
                                {"query": query, "num_results": num_results, "response_format": "json"}, task)
        try:
            results = json.loads(text).get("results", [])
        except (json.JSONDecodeError, AttributeError):
            raise ToolError("searxng_web_search returned non-JSON output") from None
        return [{"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
                for r in results[:num_results] if r.get("url")]

    async def _fetch(self, url: str, task=None) -> str:
        host = urlsplit(url).netloc
        async with self._host_locks[host]:  # serializes fetches per host so the gap holds across tasks
            wait = self._last.get(host, -1e9) + DOMAIN_GAP - _now()
            if wait > 0:
                await _sleep(wait)
            try:
                return await self._call("web_url_read", {"url": url}, task)
            finally:
                self._last[host] = _now()

    async def _allowed(self, url: str, task=None) -> bool:
        p = urlsplit(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self._robots:
            try:
                rp = RobotFileParser()
                rp.parse(_strip_fences(await self._fetch(base + "/robots.txt", task)).splitlines())
                self._robots[base] = rp
            except ToolError:
                self._robots[base] = None  # unreadable robots.txt → allow
        rp = self._robots[base]
        # shortcut: stdlib parser ignores * and $ wildcards (prefix rules only), upgrade to a wildcard-aware matcher if a site's wildcard rules matter
        return rp is None or rp.can_fetch("*", url)

    async def read_url(self, url: str, task: str | None = None) -> str | None:
        if not await self._allowed(url, task):
            log.info("skipped: robots", extra={"task": task, "url": url})
            return None
        return await self._fetch(url, task)

    async def call(self, name: str, args: dict, task=None) -> str:
        if name == "searxng_web_search":
            return json.dumps(await self.search(args["query"], int(args.get("num_results", 10)), task))
        if name == "web_url_read":
            text = await self.read_url(args["url"], task)
            return "skipped: robots" if text is None else text
        raise ToolError(f"unknown tool {name}")
