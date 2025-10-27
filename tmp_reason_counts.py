import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from core.config.authority import ConfigAuthority
from core.strategy.evaluate import evaluate_pipeline


def deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(config_path: Path) -> dict:
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    base_cfg = cfg_obj.model_dump()
    override_payload = json.loads(config_path.read_text(encoding="utf-8"))
    override_cfg = override_payload.get("cfg", {})
    return deep_merge(base_cfg, override_cfg)


def load_candles(symbol: str, timeframe: str, start: str, end: str) -> pd.DataFrame:
    data_path = Path("data/curated/v1/candles") / f"{symbol}_{timeframe}.parquet"
    df = pd.read_parquet(data_path)
    mask = (df["timestamp"] >= start) & (df["timestamp"] <= end)
    return df.loc[mask].reset_index(drop=True)


def candles_window(df: pd.DataFrame, idx: int, window: int = 200) -> dict:
    start = max(0, idx - window + 1)
    window_df = df.iloc[start : idx + 1]
    return {
        "open": window_df["open"].tolist(),
        "high": window_df["high"].tolist(),
        "low": window_df["low"].tolist(),
        "close": window_df["close"].tolist(),
        "volume": window_df["volume"].tolist(),
        "timestamp": window_df["timestamp"].tolist(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate decision reasons over sample bars")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("results/hparam_search/run_20251026_194233/trial_001_config.json"),
        help="Path till JSON-konfig (med 'cfg'-nyckel) som ska mergen med runtime",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    print("Risk config:", cfg.get("risk"))

    symbol = cfg.get("meta", {}).get("symbol", "tBTCUSD")
    timeframe = cfg.get("meta", {}).get("timeframe", "1h")
    start = "2024-10-22"
    end = "2025-10-01"
    df = load_candles(symbol, timeframe, start, end)

    warmup = int(cfg.get("warmup_bars", 50))
    policy = {"symbol": symbol, "timeframe": timeframe}

    counts = Counter()
    ev_values = []
    htf_samples = []
    htf_debug = []
    action_counts = Counter()
    entry_samples = []
    state: dict = {}

    max_samples = 200
    end_index = min(len(df), warmup + max_samples)

    for idx in range(warmup, end_index):
        candles = candles_window(df, idx)
        result, meta = evaluate_pipeline(candles, policy=policy, configs=cfg, state=state)
        decision_meta = meta.get("decision", {})
        reasons = decision_meta.get("reasons") or []
        counts.update(reasons)
        state = decision_meta.get("state_out", state)

        action = result.get("action")
        action_counts.update([action])
        confidence_vals = result.get("confidence", {}) or {}
        probas = result.get("probas", {}) or {}

        ev_debug = decision_meta.get("ev_debug")
        if isinstance(ev_debug, dict):
            ev_values.append(ev_debug)

        htf_ctx = meta.get("features", {}).get("htf_fibonacci")
        if htf_ctx and len(htf_samples) < 5:
            htf_samples.append(htf_ctx)

        htf_entry_debug = state.get("htf_fib_entry_debug")
        if htf_entry_debug and len(htf_debug) < 5:
            htf_debug.append(htf_entry_debug)

        if (
            "ENTRY_LONG" in reasons or "ENTRY_SHORT" in reasons or action in {"LONG", "SHORT"}
        ) and len(entry_samples) < 5:
            entry_samples.append(
                {
                    "idx": idx,
                    "action": action,
                    "size": decision_meta.get("size"),
                    "reasons": reasons,
                    "confidence": confidence_vals,
                    "probas": probas,
                    "zone_debug": state.get("zone_debug"),
                    "ltf_fib_debug": state.get("ltf_fib_entry_debug"),
                    "htf_fib_debug": state.get("htf_fib_entry_debug"),
                }
            )

    print("Top decision reasons:")
    for reason, count in counts.most_common(15):
        print(f"  {reason}: {count}")

    if ev_values:
        max_abs_ev = max(
            (abs(item.get("ev_long", 0.0)) + abs(item.get("ev_short", 0.0))) for item in ev_values
        )
        print(f"EV samples collected: {len(ev_values)} (max abs sum: {max_abs_ev:.4f})")

    print("Action counts:")
    for action, count in action_counts.most_common():
        print(f"  {action}: {count}")

    if htf_samples:
        print("Sample HTF fib contexts:")
        for sample in htf_samples:
            print(sample)
    else:
        print("No HTF fib context samples captured.")

    if htf_debug:
        print("Sample HTF fib entry debug:")
        for debug_entry in htf_debug:
            print(debug_entry)

    if entry_samples:
        print("Sample entries / candidates:")
        for sample in entry_samples:
            print(sample)


if __name__ == "__main__":
    main()
