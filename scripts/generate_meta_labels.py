"""
Generate meta-labels for FVG-based trading.

Meta-labeling approach:
1. FVG filter generates trade opportunities (LONG/SHORT signals)
2. For each signal, look forward to see if trade was profitable
3. Label: 1 = ACCEPT (profitable), 0 = REJECT (unprofitable)

This allows ML model to act as a "second opinion" filter,
improving Profit Factor by rejecting bad FVG signals.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.indicators.atr import calculate_atr
from core.ml.labeling import generate_adaptive_triple_barrier_labels
from core.strategy.fvg_filter import generate_fvg_opportunities
from src.core.utils import get_candles_path


def generate_meta_labels(
    features_df: pd.DataFrame,
    candles_df: pd.DataFrame,
    profit_multiplier: float = 1.0,
    stop_multiplier: float = 0.8,
    max_holding: int = 36,
    min_fvg_size_atr: float = 0.5,
    max_distance_to_midline_atr: float = 2.0,
) -> pd.DataFrame:
    """
    Generate meta-labels for FVG signals.

    Args:
        features_df: Features with FVG metrics
        candles_df: OHLCV data
        profit_multiplier: ATR multiplier for profit target
        stop_multiplier: ATR multiplier for stop loss
        max_holding: Maximum bars to hold
        min_fvg_size_atr: Minimum FVG size for signal
        max_distance_to_midline_atr: Max distance for entry

    Returns:
        DataFrame with meta-labels: index, signal, label (0/1), metadata
    """
    print("[FILTER] Generating FVG opportunities...")

    # Step 1: Get FVG opportunities from primary filter
    opportunities = generate_fvg_opportunities(
        features_df,
        min_fvg_size_atr=min_fvg_size_atr,
        max_distance_to_midline_atr=max_distance_to_midline_atr,
    )

    print(f"[FILTER] Found {len(opportunities)} FVG signals")

    if len(opportunities) == 0:
        print("[WARNING] No FVG opportunities found! Check filter parameters.")
        return pd.DataFrame()

    # Step 2: Generate outcome labels using triple-barrier
    print("[LABELS] Generating triple-barrier outcomes...")

    closes = candles_df["close"].tolist()
    highs = candles_df["high"].tolist()
    lows = candles_df["low"].tolist()

    atr_values = calculate_atr(highs, lows, closes, period=14)

    all_labels = generate_adaptive_triple_barrier_labels(
        closes,
        atr_values,
        profit_multiplier=profit_multiplier,
        stop_multiplier=stop_multiplier,
        max_holding_bars=max_holding,
    )

    # Step 3: Create meta-labels for each opportunity
    print("[META] Creating accept/reject labels...")

    meta_data = []
    for opp in opportunities:
        idx = opp["index"]
        signal = opp["signal"]

        # Get outcome at this bar
        if idx < len(all_labels):
            outcome = all_labels[idx]

            # Meta-label logic:
            # For LONG: Accept if outcome was profitable (1), Reject if loss (0)
            # For SHORT: Accept if outcome was loss (0), Reject if profit (1)
            # None outcomes are filtered

            if outcome is None:
                continue  # Skip filtered trades

            if signal == "LONG":
                meta_label = int(outcome)  # 1 = profitable, 0 = loss
            elif signal == "SHORT":
                meta_label = int(not outcome)  # 1 = loss (good for short), 0 = profit (bad)
            else:
                continue

            meta_data.append(
                {
                    "index": idx,
                    "signal": signal,
                    "meta_label": meta_label,
                    "outcome": outcome,
                    **opp["metadata"],
                }
            )

    meta_df = pd.DataFrame(meta_data)

    print(f"[META] Generated {len(meta_df)} meta-labels")
    if len(meta_df) > 0:
        accept_rate = meta_df["meta_label"].mean()
        print(f"[META] Accept rate: {accept_rate:.1%}")
        print(f"[META] LONG signals: {(meta_df['signal'] == 'LONG').sum()}")
        print(f"[META] SHORT signals: {(meta_df['signal'] == 'SHORT').sum()}")

    return meta_df


def main():
    parser = argparse.ArgumentParser(description="Generate meta-labels for FVG trading")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe (e.g., 1h)")
    parser.add_argument(
        "--profit-multiplier", type=float, default=1.0, help="Profit target (ATR multiplier)"
    )
    parser.add_argument(
        "--stop-multiplier", type=float, default=0.8, help="Stop loss (ATR multiplier)"
    )
    parser.add_argument("--max-holding", type=int, default=36, help="Max holding period (bars)")
    parser.add_argument("--min-fvg-size", type=float, default=0.5, help="Min FVG size (ATR)")
    parser.add_argument(
        "--max-distance", type=float, default=2.0, help="Max distance to midline (ATR)"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Output file (default: data/meta_labels/)"
    )

    args = parser.parse_args()

    # Load features
    features_path = Path(f"data/features/{args.symbol}_{args.timeframe}_features.parquet")

    if not features_path.exists():
        print(f"[ERROR] Features not found: {features_path}")
        print("[HINT] Run: python scripts/precompute_features.py first")
        sys.exit(1)

    features_df = pd.read_parquet(features_path)

    try:
        candles_path = get_candles_path(args.symbol, args.timeframe)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1

    candles_df = pd.read_parquet(candles_path)

    # Generate meta-labels
    meta_df = generate_meta_labels(
        features_df,
        candles_df,
        profit_multiplier=args.profit_multiplier,
        stop_multiplier=args.stop_multiplier,
        max_holding=args.max_holding,
        min_fvg_size_atr=args.min_fvg_size,
        max_distance_to_midline_atr=args.max_distance,
    )

    if len(meta_df) == 0:
        print("[ERROR] No meta-labels generated!")
        sys.exit(1)

    # Save
    output_dir = Path("data/meta_labels")
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = output_dir / f"{args.symbol}_{args.timeframe}_meta_labels.parquet"

    meta_df.to_parquet(output_path, index=False)
    print(f"\n[SUCCESS] Meta-labels saved to {output_path}")
    print(f"[SUMMARY] {len(meta_df)} labeled opportunities ready for training")


if __name__ == "__main__":
    main()
