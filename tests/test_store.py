import json
import logging

import pytest

from researcher import config
from researcher.log import JsonFormatter, get_logger


def test_config_and_log(tmp_path, monkeypatch, capsys):
    for k in ("M1MAX_URL", "M1MAX_API_KEY", "M1MAX_MODEL", "MCP_URL", "CONTEXT_BUDGET"):
        monkeypatch.delenv(k, raising=False)
    env = tmp_path / ".env"
    env.write_text("# c\n\nM1MAX_URL=http://m/v1\nM1MAX_API_KEY=k\nM1MAX_MODEL=q\nMCP_URL=http://x/mcp\nCONTEXT_BUDGET=999999\n")
    cfg = config.load(env)
    assert (cfg.m1max_url, cfg.m1max_api_key, cfg.mcp_url, cfg.gui_port) == ("http://m/v1", "k", "http://x/mcp", 8090)
    assert cfg.context_budget == 64000
    env.write_text("M1MAX_URL=http://m/v1\nM1MAX_MODEL=q\nMCP_URL=http://x/mcp\n")
    with pytest.raises(ValueError, match="M1MAX_API_KEY"):
        config.load(env)

    get_logger("t")  # installs the JSON handler
    rec = logging.makeLogRecord({"msg": "hello", "levelname": "INFO", "name": "researcher.t", "task": "t1", "n": 3})
    line = json.loads(JsonFormatter().format(rec))
    assert line["event"] == "hello" and line["task"] == "t1" and line["n"] == 3 and "ts" in line
