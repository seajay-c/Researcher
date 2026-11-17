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
    root = logging.getLogger("researcher")
    if not root.handlers:
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(JsonFormatter())
        root.addHandler(h)
        root.setLevel(logging.INFO)
        root.propagate = False
    return root.getChild(name) if name != "researcher" else root
