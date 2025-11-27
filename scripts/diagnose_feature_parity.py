import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, "src")

from core.backtest.engine import BacktestEngine
from core.strategy.evaluate import evaluate_pipeline

DEFAULT_CONFIG = Path("config/strategy/champions/tBTCUSD_1h.json")
FEATURE_KEYS = ("atr_14", "atr_50", "ema", "ema_slope50_z")
BACKTEST_KW = {
    "symbol": "tBTCUSD",
    "timeframe": "1h",
    "start_date": "2024-01-01",
    "end_date": "2024-02-15",
}
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_config(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("config") or data.get("cfg") or data if isinstance(data, dict) else {}


def _extract_atr_period(cfg: dict) -> int:
    if not isinstance(cfg, dict):
        return 14
    if "atr_period" in cfg:
        try:
            return int(cfg["atr_period"])
        except (TypeError, ValueError):
            return 14
    indicators = cfg.get("indicators") or {}
    atr_cfg = indicators.get("atr") if isinstance(indicators, dict) else None
    if isinstance(atr_cfg, dict) and "period" in atr_cfg:
        try:
            return int(atr_cfg["period"])
        except (TypeError, ValueError):
            return 14
    return 14


def _summarize(
    bar_idx: int,
    timestamp,
    result: dict,
    meta: dict,
    *,
    candles_window: dict[str, Any],
    warmup_bars: int,
    atr_period: int,
    close_tail: int,
) -> dict:
    feats = result.get("features") or {}
    subset = {
        k: (float(feats.get(k)) if feats.get(k) is not None else None)
        for k in FEATURE_KEYS
        if k in feats
    }
    decision = meta.get("decision") or {}
    size = decision.get("size")
    state_out = decision.get("state_out") or {}
    features_meta = meta.get("features") or {}
    htf = features_meta.get("htf_fibonacci") or {}
    ltf = features_meta.get("ltf_fibonacci") or {}
    raw_closes = candles_window.get("close") if isinstance(candles_window, dict) else None
    if raw_closes is None:
        closes = []
    else:
        closes = list(raw_closes)
    close_len = len(closes)
    tail = []
    if close_len:
        tail_slice = closes[-close_tail:]
        tail = [float(val) for val in tail_slice]
    inferred_last_close = tail[-1] if tail else None
    state_debug = {
        "state_last_close": state_out.get("last_close"),
        "state_current_atr": state_out.get("current_atr"),
        "inferred_last_close": inferred_last_close,
    }
    return {
        "bar": bar_idx,
        "timestamp": str(timestamp),
        "action": result.get("action"),
        "size": float(size) if size is not None else None,
        "features": subset,
        "meta_flags": {
            "htf_available": bool(htf.get("available")),
            "ltf_available": bool(ltf.get("available")),
            "htf_level": htf.get("current_level"),
            "ltf_level": ltf.get("current_level"),
        },
        "fib_summary": state_out.get("fib_gate_summary"),
        "htf_entry": state_out.get("htf_fib_entry_debug"),
        "ltf_entry": state_out.get("ltf_fib_entry_debug"),
        "atr_debug": {
            "value": subset.get("atr_14"),
            "period": atr_period,
            "percentiles": features_meta.get("atr_percentiles"),
            "warmup_bars": warmup_bars,
            "window_len": close_len,
            "close_tail": tail,
        },
        "state_debug": state_debug,
    }


def _capture_snapshots(
    *,
    use_precompute: bool,
    cfg: dict,
    bars: int,
    start_bar: int | None,
    warmup: int,
    fast_window: bool,
    invalidate_cache: bool,
    close_tail: int,
) -> list[dict]:
    os.environ["GENESIS_FAST_WINDOW"] = "1" if fast_window else "0"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1" if use_precompute else "0"
    engine = BacktestEngine(**BACKTEST_KW, warmup_bars=warmup, fast_window=fast_window)
    if use_precompute:
        engine.precompute_features = True
    if not engine.load_data():
        raise RuntimeError("Unable to load candles")
    if use_precompute and invalidate_cache:
        cache_dir = PROJECT_ROOT / "cache" / "precomputed"
        cache_key = f"{engine.symbol}_{engine.timeframe}_{len(engine.candles_df)}.npz"
        cache_path = cache_dir / cache_key
        if cache_path.exists():
            cache_path.unlink()
    base_cfg = dict(cfg or {})
    if use_precompute and getattr(engine, "_precomputed_features", None):
        base_cfg["precomputed_features"] = dict(engine._precomputed_features)
    start = max(start_bar if start_bar is not None else engine.warmup_bars, engine.warmup_bars)
    end = min(start + bars, len(engine.candles_df))
    policy = {"symbol": engine.symbol, "timeframe": engine.timeframe}
    state: dict = {}
    snapshots: list[dict] = []
    atr_period = _extract_atr_period(cfg)
    for bar_idx in range(start, end):
        local_cfg = dict(base_cfg)
        local_cfg["_global_index"] = bar_idx
        candles_window = engine._build_candles_window(bar_idx)
        result, meta = evaluate_pipeline(
            candles=candles_window,
            policy=policy,
            configs=local_cfg,
            state=state,
        )
        state = (meta.get("decision") or {}).get("state_out") or {}
        snapshots.append(
            _summarize(
                bar_idx,
                engine.candles_df["timestamp"].iloc[bar_idx],
                result,
                meta,
                candles_window=candles_window,
                warmup_bars=warmup,
                atr_period=atr_period,
                close_tail=close_tail,
            )
        )
    return snapshots


def _compare(streaming: list[dict], precompute: list[dict]) -> list[dict]:
    reference = {item["bar"]: item for item in precompute}
    diffs: list[dict] = []
    keys = (
        "action",
        "size",
        "features",
        "meta_flags",
        "fib_summary",
        "htf_entry",
        "ltf_entry",
        "atr_debug",
    )
    for sample in streaming:
        other = reference.get(sample["bar"])
        if not other:
            continue
        delta = {
            k: {"stream": sample.get(k), "precompute": other.get(k)}
            for k in keys
            if sample.get(k) != other.get(k)
        }
        if delta:
            diffs.append(
                {"bar": sample["bar"], "timestamp": sample["timestamp"], "differences": delta}
            )
    return diffs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diagnos av feature-paritet mellan streaming- och precompute-lägen"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--bars", type=int, default=32)
    parser.add_argument("--start-bar", type=int, default=None)
    parser.add_argument("--warmup", type=int, default=150)
    parser.add_argument("--close-tail", type=int, default=5, help="Antal senaste closes att logga")
    parser.add_argument(
        "--fast-window",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Aktivera/avaktivera fast-window optimeringen",
    )
    parser.add_argument(
        "--invalidate-cache",
        action="store_true",
        help="Ta bort motsvarande .npz före precompute-körningen",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("results/diagnostics/feature_parity_latest.json")
    )
    args = parser.parse_args()
    cfg = _load_config(args.config)
    streaming = _capture_snapshots(
        use_precompute=False,
        cfg=cfg,
        bars=args.bars,
        start_bar=args.start_bar,
        warmup=args.warmup,
        fast_window=args.fast_window,
        invalidate_cache=False,
        close_tail=args.close_tail,
    )
    precompute = _capture_snapshots(
        use_precompute=True,
        cfg=cfg,
        bars=args.bars,
        start_bar=args.start_bar,
        warmup=args.warmup,
        fast_window=args.fast_window,
        invalidate_cache=args.invalidate_cache,
        close_tail=args.close_tail,
    )
    differences = _compare(streaming, precompute)
    payload = {
        "config": str(args.config),
        "bars": args.bars,
        "start_bar": args.start_bar,
        "warmup": args.warmup,
        "streaming": streaming,
        "precompute": precompute,
        "differences": differences,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Captured {len(streaming)} bars (streaming) and {len(precompute)} bars (precompute)")
    print(f"Differences found: {len(differences)}")
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
