#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys

from core.config.settings import get_settings
from core.utils.nonce_manager import get_nonce


def build_headers(endpoint: str, body: dict | None) -> dict[str, str]:
    s = get_settings()
    api_key = (s.BITFINEX_API_KEY or "").strip()
    api_secret = (s.BITFINEX_API_SECRET or "").strip()
    if not api_key or not api_secret:
        raise RuntimeError("BITFINEX API credentials saknas i settings")
    nonce = get_nonce(api_key)
    payload_str = json.dumps(body or {}, separators=(",", ":"))
    message = f"/api/v2/{endpoint}{nonce}{payload_str}"
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha384).hexdigest()
    return {
        "bfx-apikey": api_key,
        "bfx-nonce": nonce,
        "bfx-signature": signature,
        "Content-Type": "application/json",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Bitfinex v2 auth headers")
    parser.add_argument("endpoint", help="Endpoint utan /v2/, t.ex. auth/r/alerts")
    parser.add_argument(
        "--body",
        help="JSON body som sträng (default: {} )",
        default="{}",
    )
    parser.add_argument(
        "--reveal",
        action="store_true",
        help="Visa api-key/signature i klartext (VARNING: osäkert)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON",
    )

    args = parser.parse_args(argv)

    try:
        body = json.loads(args.body) if args.body else {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON body: {e}", file=sys.stderr)
        return 2

    headers = build_headers(args.endpoint, body)

    if args.reveal:
        out = headers
    else:
        out = {
            key: ("***" if key in {"bfx-apikey", "bfx-signature"} else value)
            for key, value in headers.items()
        }
        out["info"] = "Hemligheter maskeras som standard. Använd --reveal för att visa."

    print(json.dumps(out, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
