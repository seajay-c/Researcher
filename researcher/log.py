import json
import logging
import sys
from datetime import datetime, timezone

_STD = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        out = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
            "task": getattr(record, "task", None),
            "logger": record.name,
        }
        out |= {k: v for k, v in vars(record).items() if k not in _STD and k != "task"}
        if record.exc_info:
            out["exc"] = self.formatException(record.exc_info)
        return json.dumps(out, default=str)


def get_logger(name: str) -> logging.Logger:
    # The JSON handler sits on the root logger so uvicorn, mcp and httpx records are JSON lines too (SRS-NFR-006).
    root = logging.getLogger()
    if not any(isinstance(h.formatter, JsonFormatter) for h in root.handlers):
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(JsonFormatter())
        root.addHandler(h)
        root.setLevel(logging.INFO)
        for noisy in ("httpx", "httpx2", "httpcore", "openai", "mcp"):
            logging.getLogger(noisy).setLevel(logging.WARNING)
    return logging.getLogger("researcher").getChild(name) if name != "researcher" else logging.getLogger("researcher")
