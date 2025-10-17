import asyncio

from core.io.bitfinex.ws_public import one_message_ticker


async def main():
    res = await one_message_ticker()
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
