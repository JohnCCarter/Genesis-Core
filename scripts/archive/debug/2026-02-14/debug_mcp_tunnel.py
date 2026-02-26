"""Debug helper for MCP remote server reachability.

This project does not maintain provider-specific tunnel examples. Use any reverse proxy / port
forwarding solution you prefer.

Usage:
    python scripts/debug_mcp_tunnel.py
    python scripts/debug_mcp_tunnel.py http://127.0.0.1:3333
    python scripts/debug_mcp_tunnel.py https://<your-host>

The remote MCP server (`python -m mcp_server.remote_server`) exposes:
    - GET  /healthz
    - POST /mcp

This script checks:
    1) /healthz reachability
    2) POST /mcp tools/list
    3) POST /mcp tools/call (ping)
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


def _normalize_base_url(raw: str) -> str:
    base = raw.rstrip("/")
    if base.endswith("/mcp"):
        base = base[: -len("/mcp")]
    return base


def _http_get_text(url: str, *, timeout_s: float) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        status = int(getattr(resp, "status", 0) or 0)
        body = resp.read().decode("utf-8", errors="replace")
        return status, body


def _http_post_json(url: str, payload: dict, *, timeout_s: float) -> tuple[int, str]:
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        data=data,
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        status = int(getattr(resp, "status", 0) or 0)
        body = resp.read().decode("utf-8", errors="replace")
        return status, body


def main() -> int:
    base_url = "http://127.0.0.1:3333"
    if len(sys.argv) > 1:
        base_url = _normalize_base_url(sys.argv[1])

    base_url = _normalize_base_url(base_url)

    healthz = f"{base_url}/healthz"
    print(f"Checking {healthz} ...")

    try:
        status, text = _http_get_text(healthz, timeout_s=10)
        print(f"Status: {status}")
        print(text.strip())
        if status < 200 or status >= 300:
            return 2
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Error: {exc}")
        return 1

    mcp_url = f"{base_url}/mcp"
    print(f"\nProbing MCP endpoint {mcp_url} (tools/list) ...")
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        status, raw = _http_post_json(mcp_url, payload, timeout_s=10)
        print(f"Status: {status}")
        if status < 200 or status >= 300:
            print(raw.strip())
            return 3

        obj = json.loads(raw)
        tools = (obj.get("result") or {}).get("tools") or []
        names = [t.get("name") for t in tools if isinstance(t, dict) and t.get("name")]
        print("Tools: " + ", ".join(names))
    except Exception as exc:
        print(f"Error: {exc}")
        return 3

    print(f"\nProbing MCP endpoint {mcp_url} (tools/call ping) ...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "ping", "arguments": {}},
        }
        status, raw = _http_post_json(mcp_url, payload, timeout_s=10)
        print(f"Status: {status}")
        if status < 200 or status >= 300:
            print(raw.strip())
            return 4

        obj = json.loads(raw)
        result = (obj.get("result") or {}).get("content") or []
        # Server returns text content containing JSON.
        if result and isinstance(result, list) and isinstance(result[0], dict):
            print(result[0].get("text", "").strip())
        else:
            print(raw.strip())
    except Exception as exc:
        print(f"Error: {exc}")
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
