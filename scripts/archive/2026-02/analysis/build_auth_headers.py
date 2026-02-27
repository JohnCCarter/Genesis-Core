#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys

from core.config.settings import get_settings
from core.utils.nonce_manager import get_nonce


REVEAL_ACK_ENV = "GENESIS_ALLOW_SECRET_OUTPUT"
REVEAL_ACK_VALUE = "1"


def _mask_sensitive_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        key: ("***" if key in {"bfx-apikey", "bfx-signature"} else value)
        for key, value in headers.items()
    }


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


def print_data(data: dict, pretty: bool = False) -> None:
    """
    Skriv endast sanerad data till stdout.
    """
    # CodeQL [py/clear-text-logging-sensitive-data]: Datan är sanerad (inga secrets).
    print(json.dumps(data, indent=2 if pretty else None))  # nosec B101 - Säker loggning


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
        help=(
            "Kräver explicit ack via miljövariabel "
            f"{REVEAL_ACK_ENV}={REVEAL_ACK_VALUE}. Klartext visas inte."
        ),
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
        if os.getenv(REVEAL_ACK_ENV, "").strip() != REVEAL_ACK_VALUE:
            print(
                (
                    f"--reveal blocked: set {REVEAL_ACK_ENV}={REVEAL_ACK_VALUE} "
                    "to acknowledge unsafe mode."
                ),
                file=sys.stderr,
            )
            return 3

        out = _mask_sensitive_headers(headers)
        out["info"] = "Reveal ack accepterad, men hemligheter maskeras av säkerhetsskäl."
    else:
        out = _mask_sensitive_headers(headers)
        out["info"] = (
            "Hemligheter maskeras som standard. --reveal kräver explicit ack och visar inte klartext."
        )

    print_data(out, args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
