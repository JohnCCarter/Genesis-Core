import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.server import public_candles


async def mock_public_request(*args, **kwargs):
    await asyncio.sleep(0.1)  # Simulate 100ms network latency
    mock_resp = AsyncMock()
    mock_resp.json.return_value = [
        [1000, 1.0, 2.0, 3.0, 0.5, 100.0],  # MTS, OPEN, CLOSE, HIGH, LOW, VOL
        [2000, 2.0, 3.0, 4.0, 1.5, 200.0],
    ]
    return mock_resp


async def run_verification():
    print("=== Verifying Async Public Candles ===\n")

    # Mock the ExchangeClient.public_request
    with patch(
        "core.io.bitfinex.exchange_client.ExchangeClient.public_request",
        side_effect=mock_public_request,
    ):

        # 1. Test Single Call Latency (Cold Cache)
        print("1. Testing Cold Cache Latency...")
        t0 = time.perf_counter()
        await public_candles(symbol="tBTCUSD", timeframe="1m", limit=10)
        t1 = time.perf_counter()
        dur_cold = (t1 - t0) * 1000
        print(f"   Duration: {dur_cold:.2f} ms (expected ~100ms)")

        # 2. Test Cache Hit Latency (Warm Cache)
        print("\n2. Testing Warm Cache Latency...")
        t0 = time.perf_counter()
        await public_candles(symbol="tBTCUSD", timeframe="1m", limit=10)
        t1 = time.perf_counter()
        dur_warm = (t1 - t0) * 1000
        print(f"   Duration: {dur_warm:.2f} ms (expected ~0ms)")

        if dur_warm > 10:
            print("   [FAIL] Cache does not seem to be working!")
        else:
            print("   [PASS] Cache is working.")

        # 3. Test Concurrency (Simulating multiple users)
        # Clearing cache to test concurrency on fetch?
        # Actually server.py global cache persists. Let's use a new symbol to bypass cache.
        print("\n3. Testing Concurrency (5 concurrent requests, unique symbols)...")
        tasks = []
        for i in range(5):
            tasks.append(public_candles(symbol=f"tTEST{i}", timeframe="1m", limit=10))

        t0 = time.perf_counter()
        await asyncio.gather(*tasks)
        t1 = time.perf_counter()
        dur_concurrent = (t1 - t0) * 1000
        print(f"   Total Duration for 5 requests: {dur_concurrent:.2f} ms")

        # If it was serial, it would be 5 * 100ms = 500ms.
        # If async, it should be close to 100ms (plus overhead).
        if dur_concurrent < 200:
            print("   [PASS] Concurrency is working (parallel execution).")
        else:
            print("   [FAIL] Concurrency check failed (likely serial execution).")


if __name__ == "__main__":
    asyncio.run(run_verification())
