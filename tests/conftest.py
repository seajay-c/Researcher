from pathlib import Path

import pytest

from researcher.config import Config


@pytest.fixture
def cfg(tmp_path):
    return Config("http://m/v1", "k", "qwen", "http://x/mcp", tmp_path / "research", 48000, 8, 15, "127.0.0.1", 8090)


import copy
import json

from researcher.mcp_tools import ToolError

SCHEMAS = [{"type": "function", "function": {"name": n, "description": n, "parameters": {
    "type": "object", "properties": {p: {"type": "string"}}, "required": [p]}}}
    for n, p in (("searxng_web_search", "query"), ("web_url_read", "url"))]


def call(name, **args):
    return {"name": name, "arguments": json.dumps(args)}


class FakeLLM:
    """Scripted model. `script` maps a step ("plan", "gather", "synth", "followup") to a list of replies.
    A reply is a str (content) or a list of tool calls (dicts with name/arguments)."""

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []  # (step, thinking, messages copy)

    @staticmethod
    def step_of(messages):
        sys = messages[0]["content"]
        for key, marker in (("plan", "planning step"), ("gather", "gathering step"),
                            ("synth", "writing step"), ("followup", "follow-up questions")):
            if marker in sys:
                return key
        raise AssertionError("unknown prompt")

    async def chat(self, messages, *, tools=None, thinking, task=None):
        step = self.step_of(messages)
        self.calls.append((step, thinking, copy.deepcopy(messages)))
        queue = self.script.get(step) or ["done"]
        reply = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(reply, BaseException):
            raise reply
        if isinstance(reply, list):
            return {"content": None, "tool_calls": [dict(id=f"c{len(self.calls)}_{i}", **c) for i, c in enumerate(reply)]}
        return {"content": reply, "tool_calls": []}


class FakeTools:
    def __init__(self, pages=None, fail_urls=(), robots_block=()):
        self.pages = pages or {}
        self.fail_urls, self.robots_block = set(fail_urls), set(robots_block)
        self.searches, self.reads = [], []

    async def schemas(self):
        return SCHEMAS

    async def search(self, query, num_results=10, task=None):
        self.searches.append(query)
        return [{"title": f"R {u}", "url": u, "snippet": "s"} for u in self.pages][:num_results]

    async def read_url(self, url, task=None):
        self.reads.append(url)
        if url in self.robots_block:
            return None
        if url in self.fail_urls:
            raise ToolError(f"web_url_read error: Website Error (404) for {url}")
        return self.pages.get(url, f"# Page {url}\nSome text about {url}.")


@pytest.fixture(autouse=True)
def fresh_llm_lock(monkeypatch):
    # asyncio.Lock binds to the first loop that contends for it; tests run several loops (pytest-asyncio, TestClient),
    # production runs one. Give each test its own lock.
    import asyncio
    from researcher import llm
    monkeypatch.setattr(llm, "_LOCK", asyncio.Lock())
