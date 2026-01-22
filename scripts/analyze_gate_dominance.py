"""Gate-dominance diagnostics.

Goal:
- Quantify which decision gates keep the strategy flat (no position) per (year, regime).
- Report both dominance share and "streakiness" (max and p95 flat-streak length).

Important semantics:
- Must match backtest/optimizer semantics: inject `_global_index` per bar so `evaluate_pipeline()`
  treats `configs` as authoritative (no champion merge) and indexes precomputed arrays correctly.
- Must run in canonical mode (fast_window=1 + precompute_features=1) unless the caller explicitly
  marks mode as debug-only.

This script is read-only diagnostics: it does not modify strategy logic or backtest artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from core.config.authority import ConfigAuthority
from core.pipeline import GenesisPipeline
from core.strategy.evaluate import evaluate_pipeline
from core.utils.diffing.canonical import fingerprint_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _scrub_for_fingerprint(cfg: dict[str, Any]) -> dict[str, Any]:
    scrubbed = dict(cfg or {})
    scrubbed.pop("precomputed_features", None)
    scrubbed.pop("_global_index", None)
    meta = dict(scrubbed.get("meta") or {})
    meta.pop("champion_loaded_at", None)
    scrubbed["meta"] = meta
    return scrubbed


def compute_effective_config_fingerprint(cfg: dict[str, Any]) -> str:
    """Match BacktestEngine._config_fingerprint semantics."""

    return fingerprint_config(_scrub_for_fingerprint(cfg), precision=6)


def select_blocker_reason(reasons: list[str] | None) -> tuple[str, bool]:
    """Select a single representative blocker reason.

    Rule:
    - If there is a non-ZONE reason, use the *last* non-ZONE token (gate ordering matters).
    - Otherwise, fall back to the last token (often ZONE:* indicating proba-threshold fail).

    Returns:
        (blocker_reason, had_zone)
    """

    if not reasons:
        return "NO_REASON", False

    had_zone = any(str(r).startswith("ZONE:") for r in reasons)
    last_non_zone: str | None = None
    for r in reasons:
        rs = str(r)
        if not rs.startswith("ZONE:"):
            last_non_zone = rs

    if last_non_zone is not None:
        return last_non_zone, had_zone
    return str(reasons[-1]), had_zone


def _percentile(values: list[int], q: float) -> int:
    if not values:
        raise ValueError("values must not be empty")
    q = max(0.0, min(1.0, float(q)))
    vals = sorted(values)
    if q <= 0:
        return int(vals[0])
    if q >= 1:
        return int(vals[-1])
    idx = int(round((len(vals) - 1) * q))
    idx = max(0, min(len(vals) - 1, idx))
    return int(vals[idx])


@dataclass(frozen=True)
class FlatEvent:
    idx: int
    timestamp: str
    year: int
    regime: str
    blocker_reason: str
    had_zone: bool


def _load_best_trial_payload(run_dir: Path) -> dict[str, Any]:
    best_path = run_dir / "best_trial.json"
    if not best_path.exists():
        raise FileNotFoundError(f"Missing best_trial.json in {run_dir}")
    payload = json.loads(best_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("best_trial.json must be a JSON object")
    return payload


def export_best_trial_config(*, run_dir: Path, out_path: Path) -> dict[str, Any]:
    payload = _load_best_trial_payload(run_dir)

    merged_cfg = payload.get("merged_config")
    if not isinstance(merged_cfg, dict):
        cfg_from_params = payload.get("cfg")
        if isinstance(cfg_from_params, dict):
            merged_cfg = cfg_from_params
        else:
            raise ValueError("best_trial.json missing merged_config/cfg")

    fp = compute_effective_config_fingerprint(merged_cfg)

    export = {
        "source": "best_trial",
        "run_dir": str(run_dir),
        "trial_id": payload.get("trial_id"),
        "parameters": payload.get("parameters"),
        "runtime_version": payload.get("runtime_version"),
        "effective_config_fingerprint": fp,
        "merged_config": _scrub_for_fingerprint(merged_cfg),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(export, indent=2, ensure_ascii=False, sort_keys=True), "utf-8")
    return export


def _load_effective_config_from_file(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (effective_cfg, metadata)."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("config file must be a JSON object")

    if isinstance(payload.get("merged_config"), dict):
        eff = payload["merged_config"]
        meta = {
            "used_runtime_merge": False,
            "runtime_version": payload.get("runtime_version"),
            "source": "config_file_complete",
        }
        return dict(eff), meta

    override_cfg = payload.get("cfg")
    if override_cfg is None:
        override_cfg = payload.get("parameters")
    if not isinstance(override_cfg, dict):
        raise ValueError("config file must contain 'cfg' (or 'parameters')")

    authority = ConfigAuthority()
    runtime_obj, _, runtime_version = authority.get()
    runtime_cfg = runtime_obj.model_dump()

    merged = _deep_merge(runtime_cfg, override_cfg)
    eff_obj = authority.validate(merged)
    eff = eff_obj.model_dump()

    meta = {
        "used_runtime_merge": True,
        "runtime_version": runtime_version,
        "source": "config_file_merged_with_runtime",
    }
    return dict(eff), meta


def analyze_gate_dominance(
    *,
    config: dict[str, Any],
    source_label: str,
    symbol: str,
    timeframe: str,
    start: str | None,
    end: str | None,
    warmup_bars: int,
    out_dir: Path,
) -> dict[str, Any]:
    pipeline = GenesisPipeline()

    # Canonical mode unless explicitly requested otherwise by the caller.
    os.environ.setdefault("GENESIS_MODE_EXPLICIT", "0")

    seed_raw = os.environ.get("GENESIS_RANDOM_SEED", "42")
    try:
        seed = int(seed_raw)
    except ValueError:
        seed = 42

    pipeline.setup_environment(seed=seed)

    engine = pipeline.create_engine(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start,
        end_date=end,
        warmup_bars=warmup_bars,
    )
    if not engine.load_data():
        raise RuntimeError("Failed to load data")

    # Prepare config for replay.
    effective_cfg = dict(config)
    effective_cfg.setdefault("meta", {})

    # Mirror BacktestEngine.run() semantics for HTF exit engine selection.
    engine._init_htf_exit_engine(effective_cfg.get("htf_exit_config"))

    # Inject precomputed features (but keep them out of fingerprinting).
    if getattr(engine, "_precomputed_features", None):
        effective_cfg["precomputed_features"] = dict(engine._precomputed_features)

    cfg_fp = compute_effective_config_fingerprint(effective_cfg)

    policy = {"symbol": symbol, "timeframe": timeframe}

    events: list[FlatEvent] = []
    state: dict[str, Any] = {}

    num_bars = len(engine.candles_df) if engine.candles_df is not None else 0
    for i in range(num_bars):
        if i < engine.warmup_bars:
            continue

        # Only measure entry blocking on bars where we start flat.
        was_flat = not engine.position_tracker.has_position()

        candles_window = engine._build_candles_window(i)
        effective_cfg["_global_index"] = i

        result, meta = evaluate_pipeline(
            candles=candles_window,
            policy=policy,
            configs=effective_cfg,
            state=state,
        )

        decision_meta = meta.get("decision") or {}
        reasons = decision_meta.get("reasons") or []
        state_out = decision_meta.get("state_out") or {}

        # Best-effort regime extraction
        regime_val = result.get("regime", "BALANCED")
        if isinstance(regime_val, dict):
            regime = str(regime_val.get("name") or "BALANCED")
        else:
            regime = str(regime_val or "BALANCED")
        regime = regime.upper()

        # Entry action + sizing
        action = str(result.get("action", "NONE") or "NONE")
        size = float((decision_meta.get("size") or 0.0) or 0.0)

        # Exit check (matches BacktestEngine.run order: exit before entry)
        if engine.position_tracker.has_position():
            ts = pd.Timestamp(engine._np_arrays["timestamp"][i])
            close_price = float(engine._np_arrays["close"][i])
            open_price = float(engine._np_arrays["open"][i])
            high_price = float(engine._np_arrays["high"][i])
            low_price = float(engine._np_arrays["low"][i])
            volume_arr = engine._np_arrays.get("volume")
            volume_val = float(volume_arr[i]) if volume_arr is not None else 0.0
            bar_data = {
                "timestamp": ts,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume_val,
            }
            exit_reason = engine._check_htf_exit_conditions(
                current_price=close_price,
                timestamp=ts,
                bar_data=bar_data,
                result=result,
                meta=meta,
                configs=effective_cfg,
                bar_index=i,
            )
            if exit_reason:
                engine.position_tracker.close_position_with_reason(
                    price=close_price, timestamp=ts, reason=exit_reason
                )

        executed_entry = False
        if action != "NONE" and size > 0 and not engine.position_tracker.has_position():
            if hasattr(engine.position_tracker, "set_pending_reasons"):
                engine.position_tracker.set_pending_reasons(reasons or [])
            ts = pd.Timestamp(engine._np_arrays["timestamp"][i])
            close_price = float(engine._np_arrays["close"][i])
            exec_result = engine.position_tracker.execute_action(
                action=action,
                size=size,
                price=close_price,
                timestamp=ts,
                symbol=symbol,
                meta={"entry_regime": regime},
            )
            executed_entry = bool(exec_result.get("executed"))
            if not executed_entry and hasattr(engine.position_tracker, "clear_pending_reasons"):
                engine.position_tracker.clear_pending_reasons()
            if executed_entry:
                engine._initialize_position_exit_context(result, meta, close_price, ts)

        # State progression must match backtest behavior.
        state = dict(state_out)

        if was_flat and not executed_entry:
            ts = pd.Timestamp(engine._np_arrays["timestamp"][i])
            blocker, had_zone = select_blocker_reason([str(r) for r in reasons])
            events.append(
                FlatEvent(
                    idx=i,
                    timestamp=ts.isoformat(),
                    year=int(ts.year),
                    regime=regime,
                    blocker_reason=blocker,
                    had_zone=had_zone,
                )
            )

    # --- Aggregate dominance and streak stats ---
    totals_by_year_regime: dict[tuple[int, str], int] = {}
    counts_by_key: dict[tuple[int, str, str], int] = {}

    streaks_by_key: dict[tuple[int, str, str], list[int]] = {}
    current_key: tuple[int, str, str] | None = None
    current_len = 0

    for ev in events:
        yr_key = (ev.year, ev.regime)
        totals_by_year_regime[yr_key] = totals_by_year_regime.get(yr_key, 0) + 1

        key = (ev.year, ev.regime, ev.blocker_reason)
        counts_by_key[key] = counts_by_key.get(key, 0) + 1

        if current_key is None:
            current_key = key
            current_len = 1
        elif key == current_key:
            current_len += 1
        else:
            streaks_by_key.setdefault(current_key, []).append(current_len)
            current_key = key
            current_len = 1

    if current_key is not None:
        streaks_by_key.setdefault(current_key, []).append(current_len)

    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, Any]] = []
    for (year, regime, reason), n_flat in sorted(counts_by_key.items()):
        denom = totals_by_year_regime.get((year, regime), 0)
        share = (n_flat / denom) if denom else 0.0
        streaks = streaks_by_key.get((year, regime, reason), [])
        max_streak = max(streaks) if streaks else 0
        p95_streak = _percentile(streaks, 0.95) if streaks else 0
        summary_rows.append(
            {
                "year": year,
                "regime": regime,
                "blocker_reason": reason,
                "flat_bars": n_flat,
                "flat_bars_in_year_regime": denom,
                "share": round(float(share), 6),
                "max_streak": int(max_streak),
                "p95_streak": int(p95_streak),
                "effective_config_fingerprint": cfg_fp,
                "source_label": source_label,
            }
        )

    summary_path = out_dir / "gate_dominance_summary.csv"
    with open(summary_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = list(summary_rows[0].keys()) if summary_rows else []
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if summary_rows:
            w.writeheader()
            w.writerows(summary_rows)

    meta_path = out_dir / "gate_dominance_meta.json"
    meta_payload = {
        "source_label": source_label,
        "symbol": symbol,
        "timeframe": timeframe,
        "start": start,
        "end": end,
        "warmup_bars": warmup_bars,
        "events": len(events),
        "effective_config_fingerprint": cfg_fp,
    }
    meta_path.write_text(
        json.dumps(meta_payload, indent=2, ensure_ascii=False, sort_keys=True), "utf-8"
    )

    return {
        "meta": meta_payload,
        "summary_csv": str(summary_path),
        "events": len(events),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate dominance diagnostics")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_export = sub.add_parser("export-best", help="Export best_trial merged_config to stable file")
    p_export.add_argument("--run-dir", type=Path, required=True)
    p_export.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "diagnostics" / "best_trial_config.json",
    )

    p_an = sub.add_parser("analyze", help="Analyze gate dominance for a config")
    p_an.add_argument("--config-file", type=Path, required=True)
    p_an.add_argument("--symbol", type=str, default="tBTCUSD")
    p_an.add_argument("--timeframe", type=str, default="1h")
    p_an.add_argument("--start", type=str, default=None)
    p_an.add_argument("--end", type=str, default=None)
    p_an.add_argument("--warmup", type=int, default=150)
    p_an.add_argument(
        "--out-dir",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "diagnostics" / "gate_dominance",
    )

    args = parser.parse_args()

    if args.cmd == "export-best":
        export_best_trial_config(run_dir=args.run_dir, out_path=args.out)
        return 0

    if args.cmd == "analyze":
        eff_cfg, cfg_meta = _load_effective_config_from_file(args.config_file)
        source_label = f"{cfg_meta.get('source')}:{args.config_file.name}"
        analyze_gate_dominance(
            config=eff_cfg,
            source_label=source_label,
            symbol=args.symbol,
            timeframe=args.timeframe,
            start=args.start,
            end=args.end,
            warmup_bars=int(args.warmup),
            out_dir=args.out_dir,
        )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
