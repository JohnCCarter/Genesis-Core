import asyncio
from core.io.bitfinex.ws_auth import auth_ping
from core.config.settings import get_settings


async def main():
    s = get_settings()
    if not ((s.BITFINEX_API_KEY or "").strip() and (s.BITFINEX_API_SECRET or "").strip()):
        print({"skip": "missing api keys"})
        return
    res = await auth_ping()
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
