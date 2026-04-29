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
SENSITIVE_HEADER_KEYS = {"bfx-apikey", "bfx-signature"}


def _mask_sensitive_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Mask known sensitive header values so that no secrets are printed.
    """
    return {
        key: ("***" if key.lower() in SENSITIVE_HEADER_KEYS else value)
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
    Write only sanitized data to stdout.
    """
    # CodeQL [py/clear-text-logging-sensitive-data]: The data is sanitized (no secrets).
    print(json.dumps(data, indent=2 if pretty else None))  # nosec B101 - Safe logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Bitfinex v2 auth headers")
    parser.add_argument("endpoint", help="Endpoint without /v2/, e.g. auth/r/alerts")
    parser.add_argument(
        "--body",
        help="JSON body as string (default: {})",
        default="{}",
    )
    parser.add_argument(
        "--reveal",
        action="store_true",
        help=(
            "Requires explicit acknowledgement via environment variable "
            f"{REVEAL_ACK_ENV}={REVEAL_ACK_VALUE}. Clear text is not shown."
        ),
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON",
    )

    args = parser.parse_args(argv)

    try:
        body = json.loads(args.body)
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
    if args.reveal:
        out["info"] = "Reveal acknowledgement accepted, but secrets remain masked for safe logging."
    else:
        out["info"] = (
            "Secrets are masked by default. --reveal requires explicit acknowledgement and still does not show clear text."
        )

    print_data(out, args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
