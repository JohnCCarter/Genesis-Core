#!/usr/bin/env python3
"""
Bygger Bitfinex v2-autentiserings-headers.
CodeQL-säker: ingen clear-text-loggning av känsliga data.
"""

from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import sys

from core.config.settings import get_settings
from core.utils.nonce_manager import get_nonce


def make_message_path(endpoint: str) -> str:
    """Normalisera endpoint och bygg /api/v2/…-sökvägen."""
    ep = endpoint.strip().lstrip("/")
    ep = ep.removeprefix("v2/")
    return f"/api/v2/{ep}"


def build_headers(endpoint: str, payload_str: str) -> tuple[dict[str, str], str, str]:
    """
    Bygg headers för Bitfinex API v2.

    Returnerar: (headers, nonce, message_path)
      - headers: faktiska auth-headers att använda i request
      - nonce: används för ev. säker logg (icke-hemlig i detta sammanhang)
      - message_path: säkert att logga
    """
    s = get_settings()
    api_key = (s.BITFINEX_API_KEY or "").strip()
    api_secret = (s.BITFINEX_API_SECRET or "").strip()
    if not api_key or not api_secret:
        raise RuntimeError("BITFINEX_API_KEY/SECRET saknas i settings.")

    message_path = make_message_path(endpoint)
    nonce = str(get_nonce(api_key))
    message = f"{message_path}{nonce}{payload_str}"

    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha384).hexdigest()

    headers = {
        "bfx-apikey": api_key,
        "bfx-nonce": nonce,
        "bfx-signature": signature,
        "Content-Type": "application/json",
    }
    return headers, nonce, message_path


def log_safe_json(data: dict, pretty: bool = False) -> None:
    """
    Logga endast säkra, icke-känsliga uppgifter.
    Denna funktion får aldrig ta emot hemliga värden.
    """
    # CodeQL [py/clear-text-logging-sensitive-data]: Datan är sanerad (inga secrets).
    print(json.dumps(data, indent=2 if pretty else None))


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

    # 1) Ta fram payload_str på ett deterministiskt sätt (detta är vad som ska skickas).
    try:
        if args.raw_body is not None:
            # Om du vill exakt styra strängen — använd raw, men validera att det är JSON
            _ = json.loads(args.raw_body.strip() or "{}")
            payload_str = args.raw_body.strip() or "{}"
        else:
            body = json.loads(args.body) if args.body else {}
            payload_str = json.dumps(body, separators=(",", ":"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON body: {e}", file=sys.stderr)
        return 2

    # 2) Bygg headers (hemliga värden stannar i denna scope)
    headers, nonce, message_path = build_headers(args.endpoint, payload_str)

    # 3) Skapa en HELT separat, säker loggstruktur — INTE härledd från `headers`.
    #    (Viktigt: använd INTE dict-comprehension över headers; ta INTE värden ur headers)
    safe_log = {
        "info": "Auth headers built",
        "endpoint": args.endpoint,
        "message_path": message_path,
        "nonce": nonce,              # anses icke-känslig i denna kontext
        "content_type": "application/json",
        "apikey": "***",             # aldrig härledd från headers
        "signature": "***",          # aldrig härledd från headers
        # Logga gärna metadata som inte är hemlig:
        "payload_preview_len": len(payload_str),
        "payload_is_empty": (payload_str == "{}"),
    }

    # 4) Logga endast säkra data
    log_safe_json(safe_log, args.pretty)

    # 5) Skriv ut headers för vidare bruk om du vill (ex. till stdout som JSON)
    #    OBS: Dessa ska inte loggas i produktion; de returneras här för CLI-verktygsbruk
    #    och kan konsumeras av en annan process via stdout-redirection.
    #    För att undvika CodeQL-varning: returnera dem endast maskerat om du skriver ut.
    #    Om du MÅSTE skriva ut ofiltrerat till ett rör: skriv till fil/pipe utan att visa i konsol.
    # Här väljer vi att inte skriva ut headers ofiltrerat för att undvika falska positiva i CodeQL.
    # Vill du ändå exponera dem till ett annat steg: använd en fil med restriktioner.

    # CLI output contract:
    # ------------------------------------------------------------
    # För downstream consumers (t.ex. scripts som använder detta CLI):
    # Headers skrivs INTE ut till stdout av säkerhetsskäl.
    # Om du förlitar dig på CLI-utdata i ett script, var medveten om att headers
    # är maskerade/utelämnade från stdout och måste hämtas via fil eller pipe
    # med restriktioner om du behöver dem ofiltrerade.
    # ------------------------------------------------------------

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


