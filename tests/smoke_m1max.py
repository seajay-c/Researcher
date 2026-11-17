"""Live tool-call round trip against the m1max. Not collected by pytest (no test_ prefix)."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from researcher import config  # noqa: E402
from researcher.llm import LLM  # noqa: E402

TOOL = {"type": "function", "function": {
    "name": "get_time", "description": "Current time in a timezone",
    "parameters": {"type": "object", "properties": {"timezone": {"type": "string"}}, "required": ["timezone"]}}}


async def round_trip(llm: LLM, thinking: bool) -> None:
    msgs = [{"role": "user", "content": "What time is it in Tokyo? Use the tool."}]
    raw = await llm.client.chat.completions.create(
        model=llm.cfg.m1max_model, messages=msgs, tools=[TOOL],
        extra_body={"chat_template_kwargs": {"enable_thinking": thinking}})
    m = raw.choices[0].message
    reasoning = getattr(m, "reasoning_content", None) or (m.model_extra or {}).get("reasoning_content")
    think_seen = bool(reasoning) or "<think>" in (m.content or "")
    print(f"thinking={thinking}: think block seen={think_seen}, content={m.content!r:.120}")
    assert m.tool_calls, f"no structured tool_calls; content={m.content!r}"
    call = m.tool_calls[0]
    assert call.function.name == "get_time", call.function.name
    args = json.loads(call.function.arguments)
    print(f"  tool_call get_time {args}")
    msgs += [{"role": "assistant", "content": None, "tool_calls": [
                 {"id": call.id, "type": "function", "function": {"name": "get_time", "arguments": call.function.arguments}}]},
             {"role": "tool", "tool_call_id": call.id, "content": "2026-11-17 06:30 JST"}]
    final = await llm.chat(msgs, tools=[TOOL], thinking=thinking, task="smoke")
    print(f"  final answer: {final['content']!r:.200}")


async def main() -> None:
    cfg = config.load()
    llm = LLM(cfg)
    models = await llm.client.models.list()
    print("GET /models:", json.dumps(models.model_dump(), default=str)[:800])
    for thinking in (True, False):
        await round_trip(llm, thinking)
    print("SMOKE OK")


if __name__ == "__main__":
    asyncio.run(main())
