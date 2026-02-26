"""Join extracted Optuna "block" knobs with corrected holdout sweep metrics.

This is a lightweight post-processing helper for robustness runs.

Inputs are CSVs produced by:
  - scripts/extract_optuna_blocks_top_trials.py
  - scripts/sweep_optuna_holdout_top_trials.py

It writes a joined CSV and prints a small table + a best-vs-worst comparison
for the key knobs.

Notes:
- We intentionally keep this script stdlib-only (no pandas) for portability.
- holdout_return_pct / holdout_dd_pct are expected to be in percent units.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _read_csv_by_trial_id(path: Path) -> dict[int, dict[str, str]]:
    rows: dict[int, dict[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            trial_raw = (row.get("trial_id") or "").strip()
            if not trial_raw:
                continue
            trial_id = int(float(trial_raw))
            rows[trial_id] = row
    return rows


def _safe_float(value: str | None) -> float:
    if value is None:
        return 0.0
    s = str(value).strip()
    if s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--top-n", type=int, default=20)
    ap.add_argument(
        "--blocks-csv",
        type=Path,
        default=None,
        help="Override blocks CSV path (otherwise inferred from run-id/top-n).",
    )
    ap.add_argument(
        "--holdout-csv",
        type=Path,
        default=None,
        help="Override holdout sweep CSV path (otherwise inferred from run-id/top-n).",
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=None,
        help="Output joined CSV path (otherwise inferred from run-id/top-n).",
    )
    ap.add_argument("--best-k", type=int, default=5)

    args = ap.parse_args()

    run_id = args.run_id
    top_n = int(args.top_n)

    blocks_csv = args.blocks_csv or Path(
        f"results/diagnostics/top_trial_blocks_{run_id}_top{top_n}.csv"
    )
    holdout_csv = args.holdout_csv or Path(
        f"results/diagnostics/holdout_sweep_{run_id}_top{top_n}/holdout_sweep_summary.csv"
    )
    out_csv = args.out_csv or Path(
        f"results/diagnostics/holdout_blocks_join_{run_id}_top{top_n}.csv"
    )

    if not blocks_csv.exists():
        raise FileNotFoundError(f"Blocks CSV not found: {blocks_csv}")
    if not holdout_csv.exists():
        raise FileNotFoundError(f"Holdout CSV not found: {holdout_csv}")

    blocks_by_id = _read_csv_by_trial_id(blocks_csv)
    holdout_by_id = _read_csv_by_trial_id(holdout_csv)

    joined: list[dict[str, str]] = []

    # Inner join on trial_id
    for trial_id, b in blocks_by_id.items():
        h = holdout_by_id.get(trial_id)
        if h is None:
            continue
        merged = dict(b)
        for k, v in h.items():
            if k == "trial_id":
                continue
            merged[k] = v
        joined.append(merged)

    if not joined:
        raise RuntimeError("No rows after join; check trial_id compatibility between CSVs.")

    out_csv.parent.mkdir(parents=True, exist_ok=True)

    # Preserve a stable column order: blocks first, then holdout columns.
    blocks_header = list(next(iter(blocks_by_id.values())).keys())
    holdout_header = [k for k in next(iter(holdout_by_id.values())).keys() if k not in {"trial_id"}]
    fieldnames = blocks_header + [k for k in holdout_header if k not in blocks_header]

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in joined:
            writer.writerow(row)

    print(f"[OK] wrote {out_csv}")

    # Sort by holdout_return_pct desc, PF desc.
    joined_sorted = sorted(
        joined,
        key=lambda r: (
            _safe_float(r.get("holdout_return_pct")),
            _safe_float(r.get("holdout_pf")),
        ),
        reverse=True,
    )

    show_cols = [
        "trial_id",
        "train_score",
        "holdout_return_pct",
        "holdout_pf",
        "holdout_dd_pct",
        "holdout_trades",
        "zone_low_entry",
        "zone_mid_entry",
        "zone_high_entry",
        "htf_tol_atr",
        "ltf_tol_atr",
        "ltf_override_threshold",
        "ltf_override_percentile",
    ]

    print("\nTop 8 (least bad holdout_return_pct first):")
    for row in joined_sorted[:8]:
        print(
            "  "
            + ", ".join(
                f"{c}={row.get(c, '')}" for c in show_cols if row.get(c, "") not in (None, "")
            )
        )

    best_k = max(1, min(int(args.best_k), len(joined_sorted)))
    worst_k = best_k
    best = joined_sorted[:best_k]
    worst = list(reversed(joined_sorted[-worst_k:]))

    knobs = [
        "zone_low_entry",
        "zone_low_regime",
        "zone_mid_entry",
        "zone_mid_regime",
        "zone_high_entry",
        "zone_high_regime",
        "htf_tol_atr",
        "ltf_tol_atr",
        "ltf_override_threshold",
        "ltf_override_percentile",
    ]

    print(f"\nBest-vs-worst (mean over top {best_k} vs bottom {worst_k}):")
    for k in knobs:
        best_mean = _mean([_safe_float(r.get(k)) for r in best])
        worst_mean = _mean([_safe_float(r.get(k)) for r in worst])
        delta = best_mean - worst_mean
        print(f"  {k}: best_mean={best_mean:.4f}  worst_mean={worst_mean:.4f}  delta={delta:+.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
