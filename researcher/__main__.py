import argparse
import asyncio
import json
import sys
from pathlib import Path

from . import agent, config, store
from .llm import LLM
from .log import get_logger
from .mcp_tools import Tools, ToolError


def _print_event(e: dict) -> None:
    print(json.dumps(e, ensure_ascii=False), flush=True)


async def _research(cfg, question: str) -> None:
    folder = store.new_task(cfg.research_dir, question)
    async with Tools(cfg) as tools:
        await agent.run_research(folder, LLM(cfg), tools, cfg, on_event=_print_event)
    print(folder)


async def _resume(cfg, folder: str | None) -> None:
    async with Tools(cfg) as tools:
        if folder:
            await agent.run_research(Path(folder), LLM(cfg), tools, cfg, on_event=_print_event)
            print(folder)
        else:
            for task_id in await agent.resume_all(cfg.research_dir, LLM(cfg), tools, cfg, on_event=_print_event):
                print(cfg.research_dir / task_id)


async def _ask(cfg, folder: str, question: str) -> None:
    async with Tools(cfg) as tools:
        print(await agent.ask(Path(folder), question, LLM(cfg), tools, cfg))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="researcher", description="Local research agent")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("research", help="start research on a question")
    r.add_argument("question")
    rs = sub.add_parser("resume", help="resume unfinished research")
    rs.add_argument("folder", nargs="?")
    a = sub.add_parser("ask", help="ask a follow-up about a research folder")
    a.add_argument("folder")
    a.add_argument("question")
    sub.add_parser("serve", help="run the web GUI")
    args = p.parse_args(argv)

    get_logger("cli")  # install JSON logging before any library logs
    try:
        cfg = config.load()
        if args.cmd == "research":
            asyncio.run(_research(cfg, args.question))
        elif args.cmd == "resume":
            asyncio.run(_resume(cfg, args.folder))
        elif args.cmd == "ask":
            asyncio.run(_ask(cfg, args.folder, args.question))
        else:
            import uvicorn

            from .web.app import create_app
            # log_config=None: uvicorn adds no plain-text handlers; its records go to the root JSON handler (SRS-NFR-006)
            uvicorn.run(create_app(cfg), host=cfg.gui_host, port=cfg.gui_port, log_config=None)  # SRS-NFR-007: no auth
    except (ValueError, ToolError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted; run `python -m researcher resume` to continue", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
