import asyncio
import time
from types import SimpleNamespace as NS

import pytest

from researcher.llm import LLM, BudgetExceeded


class FakeCompletions:
    def __init__(self):
        self.intervals = []

    async def create(self, **kw):
        t0 = time.monotonic()
        await asyncio.sleep(0.05)
        self.intervals.append((t0, time.monotonic()))
        return NS(choices=[NS(message=NS(content="<think>x</think>hi", tool_calls=None))])


def fake_client():
    return NS(chat=NS(completions=FakeCompletions()))


async def test_lock_no_overlap(cfg):
    c = fake_client()
    llm = LLM(cfg, client=c)
    r = await asyncio.gather(*(llm.chat([{"role": "user", "content": "q"}], thinking=False) for _ in range(3)))
    assert r[0]["content"] == "hi"
    iv = sorted(c.chat.completions.intervals)
    assert all(a[1] <= b[0] for a, b in zip(iv, iv[1:]))


async def test_budget(cfg):
    llm = LLM(cfg, client=fake_client())
    with pytest.raises(BudgetExceeded):
        await llm.chat([{"role": "user", "content": "x" * 300_000}], thinking=False)


import re

from researcher.agent import load_prompt

PLACEHOLDERS = {"planner": ["{today}", "{question}"],
                "executor": ["{today}", "{question}", "{plan}", "{min_sources}", "{max_sources}"],
                "synthesizer": ["{today}", "{question}", "{chunks}"],
                "followup": ["{today}", "{report}", "{chunks}", "{question}"]}


def test_prompts():
    for name, ph in PLACEHOLDERS.items():
        text = load_prompt(name)
        assert all(p in text for p in ph), name
        for line in text.splitlines():  # SRS-NFR-008: banned phrases only inside "never/do not" instructions
            if re.search(r"cannot browse|can't browse|as an ai|disclaimer", line, re.I):
                assert re.search(r"never|do not", line, re.I), line
    ex = load_prompt("executor")
    assert ex.count("<tool_call>") >= 3 and "searxng_web_search" in ex and "function-calling.md" in ex and "<tool_response>" in ex
