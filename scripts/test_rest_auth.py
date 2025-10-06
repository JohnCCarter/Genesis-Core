import asyncio

from core.config.settings import get_settings
from core.io.bitfinex.rest_auth import post_auth


async def main():
    s = get_settings()
    if not ((s.BITFINEX_API_KEY or "").strip() and (s.BITFINEX_API_SECRET or "").strip()):
        print({"skip": "missing api keys"})
        return
    # Minimal privat endpoint: auth/r/alerts (exempel; kräver rättigheter)
    try:
        r = await post_auth("auth/r/wallets", {})
        print({"status": r.status_code})
    except Exception as e:
        print({"error": str(e)})


if __name__ == "__main__":
    asyncio.run(main())
