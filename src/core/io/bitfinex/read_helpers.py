from __future__ import annotations

import json
from typing import Any

from core.io.bitfinex.exchange_client import get_exchange_client


def _decode_response(resp: Any) -> Any:
    try:
        return resp.json()  # type: ignore[attr-defined]
    except Exception:
        try:
            return json.loads(resp.text)
        except Exception:
            return resp.text


async def _signed_post_json(endpoint: str) -> Any:
    ec = get_exchange_client()
    resp = await ec.signed_request(method="POST", endpoint=endpoint, body={})
    return _decode_response(resp)


async def get_wallets() -> Any:
    """Hämta plånböcker via privata REST v2 (auth/r/wallets).

    Returnerar JSON-avkodad respons (lista/dict) eller text.
    """
    return await _signed_post_json("auth/r/wallets")


async def get_positions() -> Any:
    """Hämta positioner via privata REST v2 (auth/r/positions).

    Returnerar JSON-avkodad respons (lista/dict) eller text.
    """
    return await _signed_post_json("auth/r/positions")


async def get_orders() -> Any:
    """Hämta öppna ordrar via privata REST v2 (auth/r/orders).

    Returnerar JSON-avkodad respons (lista/dict) eller text.
    """
    return await _signed_post_json("auth/r/orders")
