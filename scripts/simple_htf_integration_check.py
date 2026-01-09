#!/usr/bin/env python3
"""
Simplified HTF integration check - verify features_asof passes HTF context correctly
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.htf_fibonacci import load_candles_data
from core.strategy.features_asof import extract_features_backtest


def check_htf_in_features():
    """Check if HTF context is actually being passed in extract_features()."""

    print("=== Checking HTF Context in extract_features() ===\n")

    # Load recent 1h data
    ltf_data = load_candles_data("tBTCUSD", "1h").tail(200)

    # Convert to dict format
    candles_dict = {
        "open": ltf_data["open"].tolist(),
        "high": ltf_data["high"].tolist(),
        "low": ltf_data["low"].tolist(),
        "close": ltf_data["close"].tolist(),
        "volume": ltf_data["volume"].tolist(),
    }

    # Extract features AS-OF last closed bar in dataset
    features, meta = extract_features_backtest(
        candles_dict,
        asof_bar=len(candles_dict["close"]) - 1,
        timeframe="1h",
        symbol="tBTCUSD",
    )

    # Check HTF context
    htf_context = meta.get("htf_fibonacci", {})

    print(f"HTF Context in meta: {htf_context.get('available', False)}")

    if htf_context.get("available"):
        levels = htf_context.get("levels", {})
        print(f"   Fib 0.382: {levels.get(0.382, 'N/A')}")
        print(f"   Fib 0.5: {levels.get(0.5, 'N/A')}")
        print(f"   Fib 0.618: {levels.get(0.618, 'N/A')}")
        print(f"   Swing High: {htf_context.get('swing_high', 'N/A')}")
        print(f"   Swing Low: {htf_context.get('swing_low', 'N/A')}")
        print(f"   Data age: {htf_context.get('data_age_hours', 'N/A'):.1f} hours")
        print("\n[SUCCESS] HTF context is available and should work in backtest!")
        return True
    else:
        reason = htf_context.get("reason", "UNKNOWN")
        error = htf_context.get("error", "N/A")
        print(f"   Reason: {reason}")
        print(f"   Error: {error}")
        print("\n[ISSUE] HTF context not available - this explains why no partial exits!")
        return False


if __name__ == "__main__":
    success = check_htf_in_features()
    sys.exit(0 if success else 1)
