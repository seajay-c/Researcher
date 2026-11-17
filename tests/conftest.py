from pathlib import Path

import pytest

from researcher.config import Config


@pytest.fixture
def cfg(tmp_path):
    return Config("http://m/v1", "k", "qwen", "http://x/mcp", tmp_path / "research", 48000, 8, 15, "127.0.0.1", 8090)
