import os
from dataclasses import dataclass
from pathlib import Path

REQUIRED = ("M1MAX_URL", "M1MAX_API_KEY", "M1MAX_MODEL", "MCP_URL")


@dataclass(frozen=True)
class Config:
    m1max_url: str
    m1max_api_key: str
    m1max_model: str
    mcp_url: str
    research_dir: Path
    context_budget: int
    min_sources: int
    max_sources: int
    gui_host: str
    gui_port: int


def _parse(env_file: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not env_file.exists():
        return out
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load(env_file: Path = Path(".env")) -> Config:
    env = _parse(env_file) | {k: v for k, v in os.environ.items() if v}
    missing = [k for k in REQUIRED if not env.get(k)]
    if missing:
        raise ValueError(f"missing required config: {', '.join(missing)}")
    return Config(
        m1max_url=env["M1MAX_URL"].rstrip("/"),
        m1max_api_key=env["M1MAX_API_KEY"],
        m1max_model=env["M1MAX_MODEL"],
        mcp_url=env["MCP_URL"],
        research_dir=Path(env.get("RESEARCH_DIR", "./research")),
        context_budget=min(64000, max(32000, int(env.get("CONTEXT_BUDGET", 48000)))),
        min_sources=int(env.get("MIN_SOURCES", 8)),
        max_sources=int(env.get("MAX_SOURCES", 15)),
        gui_host=env.get("GUI_HOST", "0.0.0.0"),
        gui_port=int(env.get("GUI_PORT", 8090)),
    )
