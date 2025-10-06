import asyncio

from core.io.bitfinex.rest_public import get_platform_status


async def main():
    st = await get_platform_status()
    print({"platform_status": st})


if __name__ == "__main__":
    asyncio.run(main())
