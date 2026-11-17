import argparse
import sys


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
    p.parse_args(argv)
    print("not implemented")
    return 2


if __name__ == "__main__":
    sys.exit(main())
