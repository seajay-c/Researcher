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
