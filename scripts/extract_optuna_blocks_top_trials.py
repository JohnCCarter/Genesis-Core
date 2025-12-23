"""Extract key config blocks from top Optuna trials.

Focuses on the blocks that most often dominate behavior:
- thresholds.signal_adaptation.zones.* (ATR-zoner)
- fib gates (htf_fib/ltf_fib tolerances)
- override logic (multi_timeframe ltf override)

The script reads trial result JSONs from a run directory, selects the top-N by *train* score,
loads the corresponding trial config JSONs, and writes a flat CSV for analysis.

Example:
    python scripts/extract_optuna_blocks_top_trials.py --run-id 20251222_164040 --top-n 50
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _get(d: dict, path: str, default=None):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract ATR zones + fib/override blocks from top trials"
    )
    parser.add_argument(
        "--run-id", required=True, help="Run id folder under results/hparam_search/"
    )
    parser.add_argument(
        "--top-n", type=int, default=20, help="How many top trials (by train score) to extract"
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    run_dir = project_root / "results" / "hparam_search" / args.run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run dir not found: {run_dir}")

    trial_files = [
        p for p in run_dir.glob("trial_*.json") if "_config" not in p.name and p.is_file()
    ]
    if not trial_files:
        raise FileNotFoundError(f"No trial_*.json files found in: {run_dir}")

    trials = []
    for p in trial_files:
        data = json.loads(p.read_text(encoding="utf-8"))
        train_score = _get(data, "score.score")
        config_path = data.get("config_path")
        trial_id = data.get("trial_id")
        if train_score is None or not config_path or trial_id is None:
            continue
        trials.append(
            {
                "trial_id": int(trial_id),
                "train_score": float(train_score),
                "config_path": config_path,
            }
        )

    trials.sort(key=lambda x: x["train_score"], reverse=True)
    trials = trials[: args.top_n]

    rows: list[dict] = []
    for t in trials:
        cfg_file = run_dir / t["config_path"]
        cfg_raw = json.loads(cfg_file.read_text(encoding="utf-8"))
        cfg = cfg_raw.get("merged_config") or cfg_raw.get("cfg") or cfg_raw.get("parameters") or {}

        row = {
            "trial_id": t["trial_id"],
            "train_score": t["train_score"],
            "entry_conf_overall": _get(cfg, "thresholds.entry_conf_overall"),
            "min_edge": _get(cfg, "thresholds.min_edge"),
            "zone_low_entry": _get(
                cfg, "thresholds.signal_adaptation.zones.low.entry_conf_overall"
            ),
            "zone_low_regime": _get(cfg, "thresholds.signal_adaptation.zones.low.regime_proba"),
            "zone_mid_entry": _get(
                cfg, "thresholds.signal_adaptation.zones.mid.entry_conf_overall"
            ),
            "zone_mid_regime": _get(cfg, "thresholds.signal_adaptation.zones.mid.regime_proba"),
            "zone_high_entry": _get(
                cfg, "thresholds.signal_adaptation.zones.high.entry_conf_overall"
            ),
            "zone_high_regime": _get(cfg, "thresholds.signal_adaptation.zones.high.regime_proba"),
            "allow_ltf_override": _get(cfg, "multi_timeframe.allow_ltf_override"),
            "ltf_override_threshold": _get(cfg, "multi_timeframe.ltf_override_threshold"),
            "ltf_override_percentile": _get(
                cfg, "multi_timeframe.ltf_override_adaptive.percentile"
            ),
            "htf_tol_atr": _get(cfg, "htf_fib.entry.tolerance_atr"),
            "ltf_tol_atr": _get(cfg, "ltf_fib.entry.tolerance_atr"),
            "htf_exit_fib_threshold_atr": _get(cfg, "htf_exit_config.fib_threshold_atr"),
            "htf_exit_trail_atr_multiplier": _get(cfg, "htf_exit_config.trail_atr_multiplier"),
            "htf_exit_enable_partials": _get(cfg, "htf_exit_config.enable_partials"),
            "htf_exit_enable_trailing": _get(cfg, "htf_exit_config.enable_trailing"),
            "risk_map": json.dumps(_get(cfg, "risk.risk_map"), separators=(",", ":")),
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    out_dir = project_root / "results" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"top_trial_blocks_{args.run_id}_top{args.top_n}.csv"
    df.to_csv(out_path, index=False)

    print(f"[OK] Wrote: {out_path}")
    if not df.empty:
        print("\n[Preview] Top 5 rows (train order):")
        print(df.head(5).to_string(index=False))

        print("\n[Ranges] (min..max) for key knobs in top set:")
        for col in [
            "zone_low_entry",
            "zone_mid_entry",
            "zone_high_entry",
            "htf_tol_atr",
            "ltf_tol_atr",
            "ltf_override_threshold",
            "ltf_override_percentile",
        ]:
            if col in df.columns:
                s = pd.to_numeric(df[col], errors="coerce")
                if s.notna().any():
                    print(f"  - {col}: {s.min():.4g} .. {s.max():.4g}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
