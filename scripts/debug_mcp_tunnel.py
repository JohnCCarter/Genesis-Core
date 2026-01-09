"""Debug helper for MCP remote server reachability.

This project does not maintain provider-specific tunnel examples. Use any reverse proxy / port
forwarding solution you prefer.

Usage:
    python scripts/debug_mcp_tunnel.py
    python scripts/debug_mcp_tunnel.py http://127.0.0.1:3333

The remote MCP server (`python -m mcp_server.remote_server`) exposes:
    - GET  /healthz
    - POST /mcp

This script only checks /healthz.
"""

from __future__ import annotations

import sys

import requests


def main() -> int:
    base_url = "http://127.0.0.1:3333"
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip("/")

    healthz = f"{base_url}/healthz"
    print(f"Checking {healthz} ...")

    try:
        resp = requests.get(healthz, timeout=10)
        print(f"Status: {resp.status_code}")
        print(resp.text.strip())
        return 0 if resp.ok else 2
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
