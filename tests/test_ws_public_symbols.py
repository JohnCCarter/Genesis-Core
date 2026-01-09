import asyncio
import json

import websockets

URI = "wss://api-pub.bitfinex.com/ws/2"
SYMBOLS = ["tBTCUSD", "tETHUSD", "tADAUSD", "tDOTUSD"]


async def main():
    async with websockets.connect(URI, ping_interval=20, ping_timeout=20) as ws:
        # prenumerera på flera tickers
        for sym in SYMBOLS:
            sub_msg = {"event": "subscribe", "channel": "ticker", "symbol": sym}
            await ws.send(json.dumps(sub_msg))

        # läs meddelanden asynkront
        async for raw in ws:
            msg = json.loads(raw)

            # filtrera bort heartbeats
            if isinstance(msg, list) and len(msg) >= 2 and msg[1] == "hb":
                continue

            print(msg)


if __name__ == "__main__":
    asyncio.run(main())
