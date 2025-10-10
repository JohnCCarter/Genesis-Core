#!/usr/bin/env python3
"""
Fetch historical candle data from Bitfinex and save to Parquet.

Usage:
    python scripts/fetch_historical.py --symbol tBTCUSD --timeframe 1m --months 1
    python scripts/fetch_historical.py --symbol tETHUSD --timeframe 1h --months 6
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import pandas as pd
from tqdm import tqdm

# Bitfinex API configuration
BASE_URL = "https://api-pub.bitfinex.com/v2"
MAX_CANDLES_PER_REQUEST = 10000

# Rate limiting (verified from Bitfinex docs)
# Source: https://docs.bitfinex.com/reference/rest-public-candles
REQUESTS_PER_MINUTE = 30
SAFE_REQUESTS_PER_MINUTE = 27  # 90% safety margin
DELAY_BETWEEN_REQUESTS = 60 / SAFE_REQUESTS_PER_MINUTE  # ~2.22 seconds

# Supported timeframes (verified from Bitfinex API v2)
# Note: 4h is NOT supported by Bitfinex! Use 3h or 6h instead.
SUPPORTED_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "3h", "6h", "12h", "1D", "1W", "14D", "1M"]


def calculate_candle_count(timeframe: str, days: int) -> int:
    """Calculate expected number of candles for given timeframe and days."""
    minutes_per_candle = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "3h": 180,
        "6h": 360,
        "12h": 720,
        "1D": 1440,
        "1W": 10080,
        "14D": 20160,
        "1M": 43200,  # Approximate (30 days)
    }
    if timeframe not in minutes_per_candle:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    total_minutes = days * 24 * 60
    return total_minutes // minutes_per_candle[timeframe]


def fetch_candles_page(
    symbol: str,
    timeframe: str,
    start_ms: int,
    end_ms: int,
    limit: int = MAX_CANDLES_PER_REQUEST,
) -> list:
    """
    Fetch one page of candles from Bitfinex.

    Returns:
        List of candles: [[MTS, OPEN, CLOSE, HIGH, LOW, VOLUME], ...]
    """
    endpoint = f"{BASE_URL}/candles/trade:{timeframe}:{symbol}/hist"
    params = {"start": start_ms, "end": end_ms, "limit": limit, "sort": 1}  # oldest first

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # Check for error response
            if isinstance(data, dict) and "error" in data:
                error_msg = data.get("error")
                if error_msg == "ERR_RATE_LIMIT":
                    print("\n[RATE LIMIT] Hit rate limit, sleeping 60s...")
                    time.sleep(60)
                    return fetch_candles_page(symbol, timeframe, start_ms, end_ms, limit)
                raise ValueError(f"API Error: {error_msg}")

            return data if isinstance(data, list) else []

    except httpx.HTTPStatusError as e:
        print(f"\n[HTTP ERROR] {e.response.status_code}: {e.response.text}")
        if e.response.status_code == 429:  # Rate limit
            print("[RATE LIMIT] Sleeping 60s...")
            time.sleep(60)
            return fetch_candles_page(symbol, timeframe, start_ms, end_ms, limit)
        raise
    except Exception as e:
        print(f"\n[ERROR] Failed to fetch candles: {e}")
        raise


def fetch_historical_data(symbol: str, timeframe: str, months: int = 1) -> pd.DataFrame:
    """
    Fetch historical candle data for specified period.

    Args:
        symbol: Trading pair (e.g., 'tBTCUSD')
        timeframe: Candle timeframe (e.g., '1m', '1h', '1D')
        months: Number of months of history to fetch

    Returns:
        DataFrame with columns: [timestamp, open, close, high, low, volume]
    """
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe '{timeframe}'. " f"Supported: {', '.join(SUPPORTED_TIMEFRAMES)}"
        )

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)

    print(f"\n{'='*60}")
    print("Fetching Historical Data")
    print(f"{'='*60}")
    print(f"Symbol:    {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Period:    {start_date.date()} to {end_date.date()} ({months} months)")

    # Calculate expected candles and requests
    days = (end_date - start_date).days
    expected_candles = calculate_candle_count(timeframe, days)
    expected_requests = (expected_candles // MAX_CANDLES_PER_REQUEST) + 1

    print(f"Expected:  ~{expected_candles:,} candles in ~{expected_requests} requests")
    print(f"Rate:      {SAFE_REQUESTS_PER_MINUTE} req/min (~{DELAY_BETWEEN_REQUESTS:.1f}s delay)")
    print(f"ETA:       ~{(expected_requests * DELAY_BETWEEN_REQUESTS):.0f} seconds")
    print(f"{'='*60}\n")

    all_candles = []
    current_start_ms = start_ms
    request_count = 0

    # Progress bar
    pbar = tqdm(
        total=expected_candles,
        desc=f"{symbol} {timeframe}",
        unit="candles",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
    )

    while current_start_ms < end_ms:
        # Fetch page
        candles = fetch_candles_page(
            symbol, timeframe, current_start_ms, end_ms, MAX_CANDLES_PER_REQUEST
        )

        if not candles:
            break

        all_candles.extend(candles)
        pbar.update(len(candles))
        request_count += 1

        # Update start time for next request
        last_candle_time = candles[-1][0]
        current_start_ms = last_candle_time + 1

        # Check if we got less than max (reached end)
        if len(candles) < MAX_CANDLES_PER_REQUEST:
            break

        # Rate limiting
        time.sleep(DELAY_BETWEEN_REQUESTS)

    pbar.close()

    print(f"\n[OK] Fetched {len(all_candles):,} candles in {request_count} requests")

    # Convert to DataFrame
    df = pd.DataFrame(
        all_candles,
        columns=["timestamp", "open", "close", "high", "low", "volume"],
    )

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    return df


def save_to_parquet(
    df: pd.DataFrame, symbol: str, timeframe: str, use_two_layer: bool = True
) -> tuple[Path, Path | None]:
    """
    Save DataFrame to Parquet file.

    If use_two_layer=True (default), saves to both:
      - Raw Lake: data/raw/bitfinex/candles/{symbol}_{timeframe}_{date}.parquet
      - Curated: data/curated/v1/candles/{symbol}_{timeframe}.parquet

    Args:
        df: DataFrame with candle data
        symbol: Trading pair
        timeframe: Candle timeframe
        use_two_layer: Use two-layer architecture (default: True)

    Returns:
        (curated_path, raw_path) or (legacy_path, None)
    """
    from datetime import datetime

    if use_two_layer:
        # Two-layer architecture
        base_dir = Path(__file__).parent.parent / "data"

        # 1. Raw Lake (immutable, timestamped)
        fetch_date = datetime.now().strftime("%Y-%m-%d")
        raw_dir = base_dir / "raw" / "bitfinex" / "candles"
        raw_dir.mkdir(parents=True, exist_ok=True)

        raw_filename = f"{symbol}_{timeframe}_{fetch_date}.parquet"
        raw_path = raw_dir / raw_filename
        df.to_parquet(raw_path, index=False, compression="snappy")
        print(f"[RAW] {raw_path} ({len(df):,} rows)")

        # 2. Curated (validated, versioned)
        curated_dir = base_dir / "curated" / "v1" / "candles"
        curated_dir.mkdir(parents=True, exist_ok=True)

        curated_filename = f"{symbol}_{timeframe}.parquet"
        curated_path = curated_dir / curated_filename
        df.to_parquet(curated_path, index=False, compression="snappy")
        print(f"[CURATED] {curated_path} ({len(df):,} rows)")

        return curated_path, raw_path
    else:
        # Legacy flat structure
        data_dir = Path(__file__).parent.parent / "data" / "candles"
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{symbol}_{timeframe}.parquet"
        filepath = data_dir / filename
        df.to_parquet(filepath, index=False, compression="snappy")
        print(f"[SAVED] {filepath} ({len(df):,} rows)")

        return filepath, None


def save_metadata(
    symbol: str,
    timeframe: str,
    df: pd.DataFrame,
    months: int,
    raw_path: Path | None = None,
    use_two_layer: bool = True,
) -> None:
    """Save metadata about fetched data."""
    if use_two_layer:
        # Save to curated metadata directory
        metadata_dir = Path(__file__).parent.parent / "data" / "metadata" / "curated"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "dataset_version": "v1",
            "symbol": symbol,
            "timeframe": timeframe,
            "source": "bitfinex_public_api",
            "fetched_at": datetime.now().isoformat(),
            "start_date": df["timestamp"].min().isoformat(),
            "end_date": df["timestamp"].max().isoformat(),
            "total_candles": len(df),
            "months_requested": months,
            "raw_file": raw_path.name if raw_path else None,
            "quality_score": 1.0,  # Basic validation - can be improved
            "adjustments": [],
        }

        filename = f"{symbol}_{timeframe}_v1.json"
    else:
        # Legacy flat structure
        metadata_dir = Path(__file__).parent.parent / "data" / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "symbol": symbol,
            "timeframe": timeframe,
            "fetched_at": datetime.now().isoformat(),
            "start_date": df["timestamp"].min().isoformat(),
            "end_date": df["timestamp"].max().isoformat(),
            "total_candles": len(df),
            "months_requested": months,
            "source": "bitfinex_public_api",
        }

        filename = f"{symbol}_{timeframe}_meta.json"

    filepath = metadata_dir / filename

    with open(filepath, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[METADATA] {filepath}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Fetch historical candle data from Bitfinex")
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading pair (e.g., tBTCUSD, tETHUSD)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        required=True,
        choices=SUPPORTED_TIMEFRAMES,
        help=f"Candle timeframe: {', '.join(SUPPORTED_TIMEFRAMES)}",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=1,
        help="Number of months of history to fetch (default: 1)",
    )

    args = parser.parse_args()

    try:
        # Fetch data
        df = fetch_historical_data(args.symbol, args.timeframe, args.months)

        # Save to parquet (two-layer structure by default)
        curated_path, raw_path = save_to_parquet(
            df, args.symbol, args.timeframe, use_two_layer=True
        )

        # Save metadata
        save_metadata(
            args.symbol, args.timeframe, df, args.months, raw_path=raw_path, use_two_layer=True
        )

        print(f"\n{'='*60}")
        print("[SUCCESS] Historical data fetched and saved!")
        print("Two-layer structure:")
        print(f"  Raw Lake (immutable): {raw_path}")
        print(f"  Curated (validated):  {curated_path}")
        print(f"{'='*60}\n")

        return 0

    except KeyboardInterrupt:
        print("\n[CANCELLED] Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[FAILED] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
