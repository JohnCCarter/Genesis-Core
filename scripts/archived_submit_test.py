from __future__ import annotations

import asyncio

import httpx

SYMBOLS = [
    "tTESTBTC:TESTUSD",
    "tTESTETH:TESTUSD",
    "tTESTSOL:TESTUSD",
]


async def main() -> None:
    base_url = "http://127.0.0.1:8000"
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as client:
        # Auth sanity (kan vara False men vi fortsätter ändå)
        try:
            r = await client.get("/auth/check")
            print("AUTH:", r.status_code, r.text[:200])
        except Exception as e:
            print("AUTH error:", e)

        # Skicka tre MARKET-ordrar
        for sym in SYMBOLS:
            payload = {"symbol": sym, "side": "LONG", "size": 0.001, "type": "MARKET"}
            try:
                r = await client.post("/paper/submit", json=payload)
                print(sym, r.status_code, r.text[:400])
            except Exception as e:
                print(sym, "error:", e)


if __name__ == "__main__":
    asyncio.run(main())
