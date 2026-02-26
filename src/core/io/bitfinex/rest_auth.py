from __future__ import annotations

from typing import Any

import httpx

from core.config.settings import get_settings
from core.io.bitfinex.exchange_client import get_exchange_client
from core.symbols.symbols import SymbolMapper, SymbolMode


def _sign_v2(endpoint: str, body: dict[str, Any] | None) -> dict[str, str]:
    """Bygg Bitfinex v2 auth headers.

    SSOT: delegeras till ExchangeClient för att undvika dubbelimplementering av
    nonce/signering/serialisering.
    """

    ec = get_exchange_client()
    # OBS: ExchangeClient._build_headers är intern men är SSOT för signering.
    return ec._build_headers(endpoint, body)


async def post_auth(endpoint: str, body: dict[str, Any] | None = None) -> httpx.Response:
    s = get_settings()
    mapper = SymbolMapper(
        SymbolMode.REALISTIC
        if str(s.SYMBOL_MODE).lower() not in ("synthetic", "realistic")
        else SymbolMode(str(s.SYMBOL_MODE).lower())
    )
    b = dict(body or {})
    sym = b.get("symbol")
    if isinstance(sym, str):
        su = sym.upper()
        if su.startswith("TTEST") or ":TEST" in su:
            b["symbol"] = mapper.force(sym)
        else:
            b["symbol"] = mapper.resolve(sym)

    ec = get_exchange_client()
    # Bevara beteendet (timeout=10) men använd central klient + retry/nonce-hantering.
    return await ec.signed_request(method="POST", endpoint=endpoint, body=b, timeout=10)
