from __future__ import annotations

import json
from typing import Any

from core.io.bitfinex.exchange_client import get_exchange_client


async def get_wallets() -> Any:
    """Hämta plånböcker via privata REST v2 (auth/r/wallets).

    Returnerar JSON-avkodad respons (lista/dict) eller text.
    """
    ec = get_exchange_client()
    resp = await ec.signed_request(method="POST", endpoint="auth/r/wallets", body={})
    try:
        return resp.json()  # type: ignore[attr-defined]
    except Exception:
        try:
            return json.loads(resp.text)
        except Exception:
            return resp.text


async def get_positions() -> Any:
    """Hämta positioner via privata REST v2 (auth/r/positions).

    Returnerar JSON-avkodad respons (lista/dict) eller text.
    """
    ec = get_exchange_client()
    resp = await ec.signed_request(method="POST", endpoint="auth/r/positions", body={})
    try:
        return resp.json()  # type: ignore[attr-defined]
    except Exception:
        try:
            return json.loads(resp.text)
        except Exception:
            return resp.text
