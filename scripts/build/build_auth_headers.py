#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sys

from core.config.settings import get_settings
from core.utils.nonce_manager import get_nonce

REVEAL_ACK_ENV = "GENESIS_ALLOW_SECRET_OUTPUT"
REVEAL_ACK_VALUE = "1"
SAFE_REDACTION = "***"
GENERATED_VALUE_PLACEHOLDER = "<generated>"
SENSITIVE_HEADER_KEYS = {"bfx-apikey", "bfx-signature"}
SENSITIVE_KEY_FRAGMENTS = {
    "apikey",
    "api_key",
    "secret",
    "signature",
    "token",
    "password",
    "passwd",
    "pwd",
    "authorization",
    "auth",
    "cookie",
}
_SENSITIVE_KEY_PATTERNS = [
    re.compile(rf"(?<![a-z0-9]){re.escape(fragment)}(?![a-z0-9])")
    for fragment in SENSITIVE_KEY_FRAGMENTS
]


def _normalize_key_for_sensitive_matching(key: object) -> str:
    key_str = str(key)
    key_with_boundaries = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key_str)
    return key_with_boundaries.lower()


def _mask_sensitive_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Mask known sensitive header values so that no secrets are printed.
    """
    return {
        key: ("***" if key.lower() in SENSITIVE_HEADER_KEYS else value)
        for key, value in headers.items()
    }


def _build_safe_cli_preview(reveal_requested: bool) -> dict[str, str]:
    preview = {
        "bfx-apikey": SAFE_REDACTION,
        "bfx-nonce": GENERATED_VALUE_PLACEHOLDER,
        "bfx-signature": SAFE_REDACTION,
        "Content-Type": "application/json",
    }
    if reveal_requested:
        preview["info"] = (
            "Reveal acknowledgement accepted, but CLI output stays redacted. "
            "Import build_headers() for in-process use instead of logging secrets."
        )
    else:
        preview["info"] = (
            "Sensitive header values are never printed. "
            "Import build_headers() for in-process use instead of logging secrets."
        )
    return preview


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


def _sanitize_for_logging(value: object) -> object:
    """
    Recursively sanitize structures before logging to prevent secret leakage.
    """
    if isinstance(value, dict):
        sanitized: dict[object, object] = {}
        for key, item in value.items():
            key_str = _normalize_key_for_sensitive_matching(key)
            if any(pattern.search(key_str) for pattern in _SENSITIVE_KEY_PATTERNS):
                sanitized[key] = "***"
            else:
                sanitized[key] = _sanitize_for_logging(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_for_logging(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize_for_logging(item) for item in value)
    return value


def print_data(data: dict, pretty: bool = False) -> None:
    """
    Write only sanitized data to stdout.
    """
    sanitized = _sanitize_for_logging(data)
    print(json.dumps(sanitized, indent=2 if pretty else None))


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

    _ = build_headers(args.endpoint, body)

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

    out = _build_safe_cli_preview(reveal_requested=args.reveal)

    print_data(out, args.pretty)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
