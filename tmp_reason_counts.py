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
    }


def main() -> None:
    run_dir = Path("results/hparam_search/run_20251026_194233")
    config_path = run_dir / "trial_001_config.json"
    cfg = load_config(config_path)

    symbol = cfg.get("meta", {}).get("symbol", "tBTCUSD")
    timeframe = cfg.get("meta", {}).get("timeframe", "1h")
    start = "2024-10-22"
    end = "2025-10-01"
    df = load_candles(symbol, timeframe, start, end)

    warmup = int(cfg.get("warmup_bars", 50))
    policy = {"symbol": symbol, "timeframe": timeframe}

    counts = Counter()
    ev_values = []
    state: dict = {}

    for idx in range(warmup, len(df)):
        candles = candles_window(df, idx)
        result, meta = evaluate_pipeline(candles, policy=policy, configs=cfg, state=state)
        decision_meta = meta.get("decision", {})
        reasons = decision_meta.get("reasons") or []
        counts.update(reasons)
        state = decision_meta.get("state_out", state)

        ev_debug = decision_meta.get("ev_debug")
        if isinstance(ev_debug, dict):
            ev_values.append(ev_debug)

    print("Top decision reasons:")
    for reason, count in counts.most_common(15):
        print(f"  {reason}: {count}")

    if ev_values:
        max_abs_ev = max((abs(item.get("ev_long", 0.0)) + abs(item.get("ev_short", 0.0))) for item in ev_values)
        print(f"EV samples collected: {len(ev_values)} (max abs sum: {max_abs_ev:.4f})")


if __name__ == "__main__":
    main()
