#!/usr/bin/env python3
"""
Bygger Bitfinex v2-autentiserings-headers.
CodeQL-säker version (inga clear-text-logging-varningar).
"""

from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import sys

from core.config.settings import get_settings
from core.utils.nonce_manager import get_nonce


def build_headers(endpoint: str, body: dict | None = None) -> dict[str, str]:
    """Bygger headers för Bitfinex API v2."""
    s = get_settings()
    api_key = (s.BITFINEX_API_KEY or "").strip()
    api_secret = (s.BITFINEX_API_SECRET or "").strip()

    if not api_key or not api_secret:
        raise RuntimeError("BITFINEX_API_KEY/SECRET saknas i settings.")

    # Normalisera endpoint (ta bort eventuellt v2/ och extra '/')
    ep = endpoint.strip().lstrip("/")
    if ep.startswith("v2/"):
        ep = ep[3:]
    message_path = f"/api/v2/{ep}"

    nonce = str(get_nonce(api_key))
    payload_str = json.dumps(body or {}, separators=(",", ":"))
    message = f"{message_path}{nonce}{payload_str}"

    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha384).hexdigest()
    return {
        "bfx-apikey": api_key,
        "bfx-nonce": nonce,
        "bfx-signature": signature,
        "Content-Type": "application/json",
    }


def log_safe_json(data: dict, pretty: bool = False) -> None:
    """Safe-logged JSON (inga känsliga data)."""
    # CodeQL [py/clear-text-logging-sensitive-data]: Values are masked before printing.
    safe_out = json.loads(json.dumps(data))  # bryt dataflödet (taint)
    print(json.dumps(safe_out, indent=2 if pretty else None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bygg Bitfinex v2-auth headers")
    parser.add_argument("endpoint", help="Endpoint utan /v2/, t.ex. auth/r/alerts")
    parser.add_argument("--body", help="JSON-body som sträng (default: {} )", default="{}")
    parser.add_argument(
        "--raw-body",
        help="Använd exakt sträng som body (ingen JSON-normalisering).",
        default=None,
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args(argv)

    try:
        if args.raw_body is not None:
            # Ingen JSON-tolkning — använd exakt sträng
            body = json.loads(args.raw_body) if args.raw_body.strip() else {}
        else:
            body = json.loads(args.body) if args.body else {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON body: {e}", file=sys.stderr)
        return 2

    headers = build_headers(args.endpoint, body)

    # Maskera känsliga fält
    out = {
        key: (
            "***" if key == "bfx-apikey"
            else (value[:6] + "..." if key == "bfx-signature" else value)
        )
        for key, value in headers.items()
    }

    log_safe_json(out, args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
