"""Optimizer CLI helpers (Phase-7)."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results" / "hparam_search"
BACKTEST_RESULTS_DIR = ROOT / "results" / "backtests"

# Cache for trial summaries to avoid repeated file I/O
_SUMMARY_CACHE: dict[str, dict[str, Any]] = {}


@dataclass(frozen=True)
class _SingleParamResult:
    param: str
    best_bin: str
    best_median: float
    best_count: int
    lift_vs_baseline: float


@dataclass(frozen=True)
class _PairParamResult:
    param_a: str
    param_b: str
    best_bin_a: str
    best_bin_b: str
    best_median: float
    best_count: int
    synergy_vs_best_single: float


def _coerce_trial_fields(trial: dict[str, Any]) -> dict[str, Any]:
    for key, caster in (("duration_seconds", float), ("attempts", int)):
        value = trial.get(key)
        if value is None:
            continue
        try:
            trial[key] = caster(value)
        except (TypeError, ValueError):
            trial.pop(key, None)
    return trial


def _format_trial_summary(idx: int, entry: dict[str, Any]) -> str:
    metrics = entry.get("metrics") or {}
    parts = [
        f"{idx}. {entry.get('trial_id')}",
        f"score={entry.get('score')}",
        f"sharpe={metrics.get('sharpe_ratio')}",
        f"trades={metrics.get('num_trades')}",
    ]
    duration = entry.get("duration_seconds")
    attempts = entry.get("attempts")
    if duration is not None:
        parts.append(f"duration={duration:.1f}s")
    if attempts is not None:
        parts.append(f"attempts={attempts}")
    return "  " + " ".join(parts)


def summarize_run(run_id: str, use_cache: bool = True) -> dict[str, Any]:
    """Summarize an optimizer run with performance optimizations.

    Performance improvements:
    - Lazy loading of trial data
    - Early filtering to reduce memory usage
    - Single-pass validation and sorting
    - Optional caching to avoid repeated file reads

    Args:
        run_id: The run identifier
        use_cache: If True, use cached summary if available (default: True)
    """
    # Check cache first
    cache_key = f"{run_id}"
    if use_cache and cache_key in _SUMMARY_CACHE:
        # Validate cache is still fresh by checking run directory mtime
        run_dir = (RESULTS_DIR / run_id).resolve()
        if run_dir.exists():
            cached = _SUMMARY_CACHE[cache_key]
            cached_mtime = cached.get("_cache_mtime")
            current_mtime = os.path.getmtime(run_dir)
            if cached_mtime and cached_mtime >= current_mtime:
                return cached

    run_dir = (RESULTS_DIR / run_id).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    meta_path = run_dir / "run_meta.json"
    meta: dict[str, Any] = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {meta_path}") from exc

    # Only include real trial result payloads (exclude trial_*_config.json, etc.)
    trial_pattern = re.compile(r"^trial_\d+\.json$")
    trial_paths = sorted(
        (p for p in run_dir.iterdir() if p.is_file() and trial_pattern.match(p.name)),
        key=lambda p: p.name,
    )
    trials: list[dict[str, Any]] = []
    valid_trials: list[dict[str, Any]] = []

    score_versions_known: set[str] = set()
    score_versions_missing = 0

    # Performance: Single pass through trials with early filtering
    skipped_count = 0
    failed_count = 0

    for path in trial_paths:
        try:
            content = path.read_text(encoding="utf-8")
            raw = json.loads(content)
        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(raw, dict):
            continue

        trial = dict(raw)
        trial["trial_file"] = path.name
        trial = _coerce_trial_fields(trial)
        trials.append(trial)

        # Early counting
        if trial.get("skipped"):
            skipped_count += 1
            continue
        if trial.get("error"):
            failed_count += 1
            continue

        # Performance: Validate and extract in one pass
        score_block = trial.get("score") or {}
        constraints_block = trial.get("constraints") or {}
        hard_failures = list(score_block.get("hard_failures") or [])
        constraints_ok = bool(constraints_block.get("ok"))

        if hard_failures or not constraints_ok:
            continue

        try:
            score_value = float(score_block.get("score"))
        except (TypeError, ValueError):
            continue

        score_version = None
        if isinstance(score_block, dict):
            raw_sv = score_block.get("score_version")
            if isinstance(raw_sv, str) and raw_sv.strip():
                score_version = raw_sv.strip()
        if score_version is None:
            score_versions_missing += 1
        else:
            score_versions_known.add(score_version)

        metrics = dict(score_block.get("metrics") or {})
        valid_trials.append(
            {
                "trial_id": trial.get("trial_id"),
                "trial_file": trial.get("trial_file"),
                "results_path": trial.get("results_path"),
                "score": score_value,
                "metrics": metrics,
                "score_version": score_version,
                "parameters": trial.get("parameters") or {},
                "duration_seconds": trial.get("duration_seconds"),
                "attempts": trial.get("attempts"),
                "raw": trial,
            }
        )

    # Performance: Sort once at the end
    valid_trials.sort(key=lambda item: item["score"], reverse=True)

    total = len(trials)
    completed = total - skipped_count

    result = {
        "meta": meta,
        "run_dir": str(run_dir),
        "counts": {
            "total": total,
            "skipped": skipped_count,
            "failed": failed_count,
            "completed": completed,
            "valid": len(valid_trials),
        },
        "best_trial": valid_trials[0] if valid_trials else None,
        "valid_trials": valid_trials,
        "trials": trials,
        "score_versions": {
            "known": sorted(score_versions_known),
            "missing": score_versions_missing,
        },
        "_cache_mtime": os.path.getmtime(run_dir) if run_dir.exists() else 0,
    }

    # Cache result for future calls
    if use_cache:
        _SUMMARY_CACHE[cache_key] = result

    return result


def _flatten_scalar_params(params: dict[str, Any], *, prefix: str = "") -> dict[str, Any]:
    """Flatten nested dicts into dot keys, keeping only scalar values.

    We intentionally skip lists/tuples to avoid exploding the feature space (e.g. risk maps).
    """

    flat: dict[str, Any] = {}
    for key, value in (params or {}).items():
        if prefix:
            full_key = f"{prefix}.{key}"
        else:
            full_key = str(key)

        if value is None:
            continue
        if isinstance(value, dict):
            flat.update(_flatten_scalar_params(value, prefix=full_key))
            continue
        if isinstance(value, str | bool | int | float):
            flat[full_key] = value
            continue

        # Skip non-scalars (lists, tuples, objects)
        continue

    return flat


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("median() requires at least one value")
    return float(statistics.median(values))


def _make_numeric_bins(values: list[float], *, bins: int) -> list[float]:
    """Return monotonic cutpoints for quantile-like binning.

    Cutpoints are chosen as value lookups in the sorted sample to avoid heavy dependencies.
    The returned list has length (bins-1). Values are used with <= comparisons.
    """

    if bins < 2:
        return []
    if len(values) < 2:
        return []

    sorted_vals = sorted(values)
    n = len(sorted_vals)
    edges: list[float] = []
    for i in range(1, bins):
        # Choose a representative quantile boundary.
        idx = int((n * i) / bins)
        idx = max(0, min(idx, n - 1))
        edges.append(float(sorted_vals[idx]))

    # Ensure strictly increasing edges (dedupe). If everything collapses, binning becomes categorical.
    deduped: list[float] = []
    for e in edges:
        if not deduped or e > deduped[-1]:
            deduped.append(e)
    if len(deduped) >= bins:
        deduped = deduped[: bins - 1]
    return deduped


def _value_to_bin_label(value: Any, *, numeric_edges: list[float] | None) -> str:
    if numeric_edges is None:
        return str(value)

    # numeric
    v = float(value)
    for idx, edge in enumerate(numeric_edges):
        if v <= edge:
            return f"bin_{idx}"  # low -> high
    return f"bin_{len(numeric_edges)}"


def _describe_bin(label: str, *, numeric_edges: list[float] | None) -> str:
    """Human readable description for a bin label."""

    if numeric_edges is None:
        return label

    if not label.startswith("bin_"):
        return label

    try:
        idx = int(label.split("_", 1)[1])
    except (ValueError, IndexError):
        return label

    if idx <= 0:
        return f"(-inf, {numeric_edges[0]:.6g}]"
    if idx >= len(numeric_edges):
        return f"({numeric_edges[-1]:.6g}, +inf)"
    lo = numeric_edges[idx - 1]
    hi = numeric_edges[idx]
    return f"({lo:.6g}, {hi:.6g}]"


def _compute_group_medians(rows: list[tuple[str, float]]) -> dict[str, tuple[float, int]]:
    grouped: dict[str, list[float]] = {}
    for key, score in rows:
        grouped.setdefault(key, []).append(float(score))
    return {k: (_median(v), len(v)) for k, v in grouped.items()}


def _analyze_param_synergy(
    valid_trials: list[dict[str, Any]],
    *,
    top_params: int = 12,
    bins: int = 4,
    min_count: int = 3,
    top_pairs: int = 25,
) -> tuple[list[_SingleParamResult], list[_PairParamResult], dict[str, list[float] | None]]:
    """Compute simple pairwise interaction statistics over scalar parameters.

    The intent is operational: identify parameter combinations that consistently produce higher
    scores, not to build a perfect causal model.
    """

    if not valid_trials:
        return [], [], {}

    # Build per-trial flattened params and baseline scores.
    flat_trials: list[dict[str, Any]] = []
    scores: list[float] = []
    for t in valid_trials:
        score = t.get("score")
        if score is None:
            continue
        params = t.get("parameters") or {}
        flat = _flatten_scalar_params(params)
        flat["__score__"] = float(score)
        flat_trials.append(flat)
        scores.append(float(score))

    if not scores:
        return [], [], {}

    baseline = _median(scores)

    # Build a per-param binning scheme.
    param_values: dict[str, list[Any]] = {}
    for flat in flat_trials:
        for k, v in flat.items():
            if k == "__score__":
                continue
            param_values.setdefault(k, []).append(v)

    numeric_edges: dict[str, list[float] | None] = {}
    for k, vals in param_values.items():
        unique = set(vals)
        if len(unique) <= 1:
            numeric_edges[k] = None
            continue

        if all(isinstance(v, int | float) and not isinstance(v, bool) for v in vals):
            if len(unique) <= bins:
                numeric_edges[k] = None
            else:
                edges = _make_numeric_bins([float(v) for v in vals], bins=bins)
                numeric_edges[k] = edges if edges else None
        else:
            numeric_edges[k] = None

    # Single-param lifts.
    singles: list[_SingleParamResult] = []
    for k in sorted(param_values.keys()):
        rows: list[tuple[str, float]] = []
        for flat in flat_trials:
            if k not in flat:
                continue
            b = _value_to_bin_label(flat[k], numeric_edges=numeric_edges[k])
            rows.append((b, float(flat["__score__"])))
        if not rows:
            continue
        grouped = _compute_group_medians(rows)
        # Require enough samples per bin.
        grouped = {b: (m, c) for b, (m, c) in grouped.items() if c >= min_count}
        if not grouped:
            continue
        best_bin, (best_median, best_count) = max(grouped.items(), key=lambda item: item[1][0])
        singles.append(
            _SingleParamResult(
                param=k,
                best_bin=best_bin,
                best_median=float(best_median),
                best_count=int(best_count),
                lift_vs_baseline=float(best_median - baseline),
            )
        )

    singles.sort(key=lambda r: r.lift_vs_baseline, reverse=True)
    top_single = singles[: max(1, int(top_params))]
    single_best_by_param = {r.param: r for r in top_single}

    # Pairwise synergy among the most promising parameters.
    pairs: list[_PairParamResult] = []
    for a, b in combinations([r.param for r in top_single], 2):
        rows: list[tuple[str, float]] = []
        for flat in flat_trials:
            if a not in flat or b not in flat:
                continue
            ba = _value_to_bin_label(flat[a], numeric_edges=numeric_edges[a])
            bb = _value_to_bin_label(flat[b], numeric_edges=numeric_edges[b])
            rows.append((f"{ba}|{bb}", float(flat["__score__"])))
        if not rows:
            continue
        grouped = _compute_group_medians(rows)
        grouped = {k: (m, c) for k, (m, c) in grouped.items() if c >= min_count}
        if not grouped:
            continue
        best_key, (best_median, best_count) = max(grouped.items(), key=lambda item: item[1][0])
        best_a, best_b = best_key.split("|", 1)
        best_single = max(
            float(single_best_by_param[a].best_median),
            float(single_best_by_param[b].best_median),
        )
        pairs.append(
            _PairParamResult(
                param_a=a,
                param_b=b,
                best_bin_a=best_a,
                best_bin_b=best_b,
                best_median=float(best_median),
                best_count=int(best_count),
                synergy_vs_best_single=float(best_median - best_single),
            )
        )

    pairs.sort(key=lambda r: (r.synergy_vs_best_single, r.best_median), reverse=True)
    return singles, pairs[: max(1, int(top_pairs))], numeric_edges


def _write_csv(path: Path, *, header: list[str], rows: list[list[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def _print_summary(data: dict[str, Any], *, top_n: int) -> None:
    meta = data.get("meta") or {}
    counts = data.get("counts") or {}
    valid_trials = data.get("valid_trials") or []
    all_trials = data.get("trials") or []
    total_duration = sum(float(trial.get("duration_seconds") or 0.0) for trial in all_trials)
    completed_trials = [
        trial for trial in all_trials if not trial.get("skipped") and trial.get("duration_seconds")
    ]
    avg_duration = total_duration / len(completed_trials) if completed_trials else 0.0

    print("== Optimizer Summary ==")
    print(f"Run dir: {data.get('run_dir')}")
    if meta:
        print("Meta:")
        for key in ("run_id", "symbol", "timeframe", "snapshot_id", "git_commit"):
            if key in meta:
                print(f"  {key}: {meta[key]}")
    print("Counts:")
    print(
        f"  total={counts.get('total', 0)} completed={counts.get('completed', 0)} "
        f"skipped={counts.get('skipped', 0)} failed={counts.get('failed', 0)} "
        f"valid={counts.get('valid', 0)}"
    )
    if total_duration:
        print(f"  total_duration={total_duration:.1f}s avg_duration={avg_duration:.1f}s")

    if not valid_trials:
        print("No trial satisfied the constraints.")
        return

    score_versions = data.get("score_versions") or {}
    known = score_versions.get("known") or []
    missing = int(score_versions.get("missing") or 0)
    if known or missing:
        print(f"Score versions (valid trials): known={known} missing={missing}")
        if len(known) > 1:
            print("[WARN] [Comparable] Mixed score_version within run (äpplen och päron risk)")
        elif missing and known:
            print("[WARN] [Comparable] Some trials missing score_version (legacy/unknown)")

    best = valid_trials[0]
    print("Best trial:")
    print(f"  id: {best.get('trial_id')}")
    print(f"  file: {best.get('trial_file')}")
    print(f"  score: {best.get('score')}")
    if best.get("score_version") is not None:
        print(f"  score_version: {best.get('score_version')}")
    metrics = best.get("metrics") or {}
    if metrics:
        print(f"  num_trades: {metrics.get('num_trades')}")
        print(f"  sharpe_ratio: {metrics.get('sharpe_ratio')}")
        print(f"  total_return: {metrics.get('total_return')}")
        print(f"  profit_factor: {metrics.get('profit_factor')}")

    # Best-effort comparability info from the saved backtest artifact (mode/fees/fingerprint).
    results_path = best.get("results_path")
    if isinstance(results_path, str) and results_path.strip():
        try:
            p = Path(results_path)
            if not p.is_absolute():
                if "/" in results_path or "\\" in results_path:
                    p = (ROOT / p).resolve()
                else:
                    p = (BACKTEST_RESULTS_DIR / p).resolve()
            if p.exists():
                payload = json.loads(p.read_text(encoding="utf-8"))
                info = payload.get("backtest_info") if isinstance(payload, dict) else None
                if isinstance(info, dict):
                    em = (
                        info.get("execution_mode")
                        if isinstance(info.get("execution_mode"), dict)
                        else {}
                    )
                    fp = info.get("effective_config_fingerprint")
                    print(
                        "Comparable(best): "
                        f"fw={em.get('fast_window')!r} pc={em.get('env_precompute_features')!r} "
                        f"commission={info.get('commission_rate')!r} slippage={info.get('slippage_rate')!r} "
                        f"warmup={info.get('warmup_bars')!r} fp={fp!r}"
                    )
        except Exception:
            # Never break summarize on missing/legacy artifacts.
            pass

    if top_n > 1:
        print(f"Top {min(top_n, len(valid_trials))} trials (score desc):")
        for idx, entry in enumerate(valid_trials[:top_n], start=1):
            print(_format_trial_summary(idx, entry))
        if top_n < len(valid_trials):
            print(f"  ... {len(valid_trials) - top_n} more")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optimizer CLI")
    subparsers = parser.add_subparsers(dest="command")

    summarize_parser = subparsers.add_parser("summarize", help="Summarise a run")
    summarize_parser.add_argument("run_id", type=str, help="Run id (directory name)")
    summarize_parser.add_argument(
        "--top",
        type=int,
        default=1,
        help="Number of top trials to list (default: 1)",
    )

    synergy_parser = subparsers.add_parser("synergy", help="Analyze parameter interactions")
    synergy_parser.add_argument("run_id", type=str, help="Run id (directory name)")
    synergy_parser.add_argument(
        "--top-params",
        type=int,
        default=12,
        help="Number of parameters to consider for pair analysis (default: 12)",
    )
    synergy_parser.add_argument(
        "--top-pairs",
        type=int,
        default=25,
        help="Number of top pairs to report (default: 25)",
    )
    synergy_parser.add_argument(
        "--bins",
        type=int,
        default=4,
        help="Numeric bins (approx quantiles) (default: 4)",
    )
    synergy_parser.add_argument(
        "--min-count",
        type=int,
        default=3,
        help="Minimum observations per bin/combination (default: 3)",
    )

    args = parser.parse_args(argv)
    if args.command == "summarize":
        data = summarize_run(args.run_id)
        top_n = max(1, int(args.top))
        _print_summary(data, top_n=top_n)
        return 0

    if args.command == "synergy":
        data = summarize_run(args.run_id)
        valid_trials = data.get("valid_trials") or []
        singles, pairs, numeric_edges = _analyze_param_synergy(
            valid_trials,
            top_params=int(args.top_params),
            bins=int(args.bins),
            min_count=int(args.min_count),
            top_pairs=int(args.top_pairs),
        )

        run_dir = Path(data.get("run_dir") or RESULTS_DIR / args.run_id)
        singles_path = run_dir / "param_synergy_singles.csv"
        pairs_path = run_dir / "param_synergy_pairs.csv"

        _write_csv(
            singles_path,
            header=[
                "param",
                "best_bin",
                "best_bin_desc",
                "best_median",
                "best_count",
                "lift_vs_baseline",
            ],
            rows=[
                [
                    s.param,
                    s.best_bin,
                    _describe_bin(s.best_bin, numeric_edges=numeric_edges.get(s.param)),
                    s.best_median,
                    s.best_count,
                    s.lift_vs_baseline,
                ]
                for s in singles
            ],
        )
        _write_csv(
            pairs_path,
            header=[
                "param_a",
                "param_b",
                "best_bin_a",
                "best_bin_a_desc",
                "best_bin_b",
                "best_bin_b_desc",
                "best_median",
                "best_count",
                "synergy_vs_best_single",
            ],
            rows=[
                [
                    p.param_a,
                    p.param_b,
                    p.best_bin_a,
                    _describe_bin(p.best_bin_a, numeric_edges=numeric_edges.get(p.param_a)),
                    p.best_bin_b,
                    _describe_bin(p.best_bin_b, numeric_edges=numeric_edges.get(p.param_b)),
                    p.best_median,
                    p.best_count,
                    p.synergy_vs_best_single,
                ]
                for p in pairs
            ],
        )

        print("== Parameter Synergy ==")
        print(f"Run dir: {run_dir}")
        print(f"Valid trials: {len(valid_trials)}")
        print(f"Wrote: {singles_path.name}, {pairs_path.name}")
        if singles:
            print("\nTop single-parameter lifts (best bin median vs baseline):")
            for s in singles[: min(10, len(singles))]:
                desc = _describe_bin(s.best_bin, numeric_edges=numeric_edges.get(s.param))
                print(
                    f"  {s.param} -> {s.best_bin} ({desc}) "
                    f"median={s.best_median:.6f} n={s.best_count} "
                    f"lift={s.lift_vs_baseline:+.6f}"
                )
        if pairs:
            print("\nTop parameter pairs (synergy vs best single):")
            for p in pairs[: min(15, len(pairs))]:
                desc_a = _describe_bin(p.best_bin_a, numeric_edges=numeric_edges.get(p.param_a))
                desc_b = _describe_bin(p.best_bin_b, numeric_edges=numeric_edges.get(p.param_b))
                print(
                    f"  {p.param_a}={p.best_bin_a} ({desc_a}) + "
                    f"{p.param_b}={p.best_bin_b} ({desc_b}) "
                    f"median={p.best_median:.6f} n={p.best_count} "
                    f"synergy={p.synergy_vs_best_single:+.6f}"
                )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
