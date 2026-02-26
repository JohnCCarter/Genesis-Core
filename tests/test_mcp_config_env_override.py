from __future__ import annotations

import json
from pathlib import Path

from mcp_server.config import load_config


def test_load_config_respects_env_override(monkeypatch, tmp_path: Path) -> None:
    cfg_path = tmp_path / "mcp_settings.env.json"
    cfg_path.write_text(
        json.dumps(
            {
                "server_name": "env-override",
                "security": {"allowed_paths": ["docs"]},
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("GENESIS_MCP_CONFIG_PATH", str(cfg_path))
    cfg = load_config()
    assert cfg.server_name == "env-override"
    assert cfg.security.allowed_paths == ["docs"]


# End of file
