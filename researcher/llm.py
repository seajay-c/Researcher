import asyncio
import json
import re
import time

import openai

from .config import Config
from .log import get_logger

_LOCK = asyncio.Lock()  # process-wide; SRS-NFR-002
_THINK = re.compile(r"<think>.*?</think>\s*", re.S)
REQUEST_TIMEOUT = 1800.0  # matches the gateway's REQUEST_TIMEOUT_S
MAX_OUTPUT = 8192  # server default is 2048, which thinking alone can use up (inc07 finding)
log = get_logger("llm")


class BudgetExceeded(Exception):
    pass


def estimate_tokens(messages: list[dict], tools: list[dict] | None = None) -> int:
    # shortcut: char estimate, upgrade to the server's /tokenize if budget errors appear
    return len(json.dumps(messages, ensure_ascii=False) + json.dumps(tools or [], ensure_ascii=False)) // 3


class LLM:
    def __init__(self, cfg: Config, client=None):
        self.cfg = cfg
        self.client = client or openai.AsyncOpenAI(
            base_url=cfg.m1max_url, api_key=cfg.m1max_api_key,
            # no silent SDK retries: a retried long generation runs twice on the shared m1max (inc07 finding)
            timeout=REQUEST_TIMEOUT, max_retries=0)

    async def chat(self, messages, *, tools=None, thinking: bool, task: str | None = None) -> dict:
        est = estimate_tokens(messages, tools)
        if est >= self.cfg.context_budget:  # no room left for output
            raise BudgetExceeded(f"estimated {est} tokens > budget {self.cfg.context_budget}")
        kw = {"tools": tools} if tools else {}
        async with _LOCK:
            log.info("llm_request", extra={"task": task, "thinking": thinking, "est_tokens": est})
            t0 = time.monotonic()
            resp = await self.client.chat.completions.create(
                model=self.cfg.m1max_model,
                messages=messages,
                max_tokens=min(MAX_OUTPUT, self.cfg.context_budget - est),  # input + output stay inside the budget
                extra_body={"chat_template_kwargs": {"enable_thinking": thinking}},
                **kw,
            )
        choice = resp.choices[0]
        msg = choice.message
        calls = [{"id": c.id, "name": c.function.name, "arguments": c.function.arguments or ""}
                 for c in (msg.tool_calls or [])]
        content = _THINK.sub("", msg.content).strip() if msg.content else msg.content
        log.info("llm_response", extra={"task": task, "ms": int((time.monotonic() - t0) * 1000), "n_tool_calls": len(calls),
                                         "finish": getattr(choice, "finish_reason", None)})
        return {"content": content, "tool_calls": calls}
