"""Cost-stress sweep for champion strategies.

Runs champion tBTCUSD_1h and tBTCUSD_3h over a grid of
commission × slippage levels and reports where the edge disappears.

Grid
----
  commission : 0, 5, 10, 20 bps
  slippage   : 5, 10, 20, 40 bps

Output
------
  artifacts/diagnostics/cost_stress_sweep_<date>.md
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

os.environ.setdefault("GENESIS_FAST_WINDOW", "1")
os.environ.setdefault("GENESIS_PRECOMPUTE_FEATURES", "1")
os.environ.setdefault("SYMBOL_MODE", "realistic")
os.environ.setdefault("GENESIS_RANDOM_SEED", "42")

COMMISSION_BPS = [0, 5, 10, 20]
SLIPPAGE_BPS = [5, 10, 20, 40]
DEFAULT_CHAMPIONS = [
    ("tBTCUSD", "1h"),
    ("tBTCUSD", "3h"),
]

EDGE_DEAD_SHARPE = 1.0
EDGE_DEAD_PF = 1.1
MIN_TRADES_FOR_SHARPE = 5

# Bars per year for each timeframe (for Sharpe annualisation)
_BARS_PER_YEAR: dict[str, float] = {
    "1m": 525_600,
    "5m": 105_120,
    "15m": 35_040,
    "30m": 17_520,
    "1h": 8_760,
    "3h": 2_920,
    "6h": 1_460,
    "12h": 730,
    "1D": 365,
    "1W": 52,
    "14D": 26,
}

# Workaround for nanosecond-timestamp staleness bug in evaluate.py.
# pandas datetime64 values arrive as ns since epoch but the staleness check
# assumes ms → halves quality_gate → confidence ~0.25 → below risk_map minimum.
_STALE_BYPASS_CONFIG = {
    "quality": {
        "pipeline": {
            "stale_threshold_factor": 1e9,
        }
    }
}


def bps(n: int) -> float:
    return n / 10_000.0


def _sharpe_from_equity(equity_curve: list[dict], timeframe: str) -> float:
    """Compute annualised Sharpe from bar-level equity curve.

    Returns NaN when there are fewer than MIN_TRADES_FOR_SHARPE meaningful
    equity points (e.g. fewer than 5 traded bars).
    """
    import numpy as np

    if not equity_curve or len(equity_curve) < 2:
        return float("nan")

    values = [p.get("total_equity", 0.0) for p in equity_curve if p.get("total_equity", 0.0) > 0]
    if len(values) < MIN_TRADES_FOR_SHARPE:
        return float("nan")

    arr = np.array(values, dtype=float)
    rets = np.diff(arr) / arr[:-1]
    if rets.std() == 0:
        return float("nan")

    annual_factor = math.sqrt(_BARS_PER_YEAR.get(timeframe, 365))
    return float(rets.mean() / rets.std() * annual_factor)


def run_single(symbol: str, timeframe: str, commission_bps: int, slippage_bps: int) -> dict:
    from core.backtest.engine import BacktestEngine

    base: dict = {
        "symbol": symbol,
        "timeframe": timeframe,
        "commission_bps": commission_bps,
        "slippage_bps": slippage_bps,
        "total_cost_bps": commission_bps + slippage_bps,
    }

    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        commission_rate=bps(commission_bps),
        slippage_rate=bps(slippage_bps),
        fast_window=True,
        data_source_policy="frozen_first",
    )
    if not engine.load_data():
        return {**base, "error": "load_data_failed",
                "sharpe_ratio": float("nan"), "profit_factor": float("nan"),
                "win_rate": float("nan"), "max_drawdown": float("nan"),
                "total_trades": 0, "total_pnl": float("nan"), "total_return_pct": float("nan")}

    result = engine.run(configs=_STALE_BYPASS_CONFIG)
    if "error" in result:
        return {**base, "error": result["error"],
                "sharpe_ratio": float("nan"), "profit_factor": float("nan"),
                "win_rate": float("nan"), "max_drawdown": float("nan"),
                "total_trades": 0, "total_pnl": float("nan"), "total_return_pct": float("nan")}

    summary = result.get("summary", {})
    equity_curve = result.get("equity_curve", [])
    sharpe = _sharpe_from_equity(equity_curve, timeframe)

    return {
        **base,
        "error": None,
        "sharpe_ratio": sharpe,
        "profit_factor": float(summary.get("profit_factor", 0.0)),
        "win_rate": float(summary.get("win_rate", 0.0)),          # already 0-100
        "max_drawdown": float(summary.get("max_drawdown", 0.0)),  # already percentage
        "total_trades": int(summary.get("num_trades", 0)),
        "total_pnl": float(summary.get("total_return_usd", 0.0)),
        "total_return_pct": float(summary.get("total_return", 0.0)),
    }


def diagnose_staleness_bug(symbol: str, timeframe: str) -> dict:
    """Sample confidence with vs without the stale_threshold_factor bypass."""
    import numpy as np
    import pandas as pd
    from core.strategy.champion_loader import ChampionLoader
    from core.strategy.evaluate import evaluate_pipeline

    loader = ChampionLoader()
    champion = loader.load_cached(symbol, timeframe)
    if champion is None:
        return {"error": "no_champion"}
    configs_base = champion.config
    configs_fixed = {**configs_base, **_STALE_BYPASS_CONFIG}
    policy = {"symbol": symbol, "timeframe": timeframe}

    data_path = (
        REPO_ROOT / "data" / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet"
    )
    if not data_path.exists():
        return {"error": f"no_data: {data_path}"}

    df = pd.read_parquet(data_path)
    confs_bugged, confs_fixed = [], []
    state_bugged: dict = {}
    state_fixed: dict = {}
    for i in range(200, min(260, len(df)), 5):
        w = {k: df[k].values[max(0, i - 199): i + 1] for k in ["open", "high", "low", "close", "volume"]}
        w["timestamp"] = df["timestamp"].values[max(0, i - 199): i + 1].tolist()
        try:
            r1, m1 = evaluate_pipeline(candles=w, policy=policy, configs=configs_base, state=state_bugged)
            state_bugged = {**state_bugged, **m1.get("decision", {}).get("state_out", {})}
            c1 = r1.get("confidence", {})
            confs_bugged.append(c1.get("overall", 0) if isinstance(c1, dict) else 0)

            r2, m2 = evaluate_pipeline(candles=w, policy=policy, configs=configs_fixed, state=state_fixed)
            state_fixed = {**state_fixed, **m2.get("decision", {}).get("state_out", {})}
            c2 = r2.get("confidence", {})
            confs_fixed.append(c2.get("overall", 0) if isinstance(c2, dict) else 0)
        except Exception:
            pass

    arr_b = np.array(confs_bugged) if confs_bugged else np.array([0.0])
    arr_f = np.array(confs_fixed) if confs_fixed else np.array([0.0])
    return {
        "bugged_mean": float(arr_b.mean()),
        "bugged_max": float(arr_b.max()),
        "fixed_mean": float(arr_f.mean()),
        "fixed_max": float(arr_f.max()),
        "samples": len(arr_b),
    }


def fmt_val(v: float, decimals: int = 2) -> str:
    if v != v:  # NaN
        return "  ERR "
    return f"{v:+.{decimals}f}" if abs(v) < 1000 else f"{v:.0f}"


def fmt_metric_table(
    results: list[dict],
    symbol: str,
    timeframe: str,
    metric: str,
    dead_threshold: float | None = None,
    higher_is_better: bool = True,
) -> str:
    subset = {
        (r["commission_bps"], r["slippage_bps"]): r[metric]
        for r in results
        if r["symbol"] == symbol and r["timeframe"] == timeframe
    }
    col_header = "  comm\\slip"
    col_width = 9
    header = col_header + "".join(f"{f'{s} bps':>{col_width}}" for s in SLIPPAGE_BPS)
    sep = "-" * len(header)
    lines = [sep, header, sep]
    for c in COMMISSION_BPS:
        row = f"  {c:>3} bps "
        for s in SLIPPAGE_BPS:
            v = subset.get((c, s), float("nan"))
            cell = fmt_val(v)
            if dead_threshold is not None and v == v:
                dead = v < dead_threshold if higher_is_better else v > dead_threshold
                cell = f"[{cell}]" if dead else f" {cell} "
            else:
                cell = f" {cell} "
            row += f"{cell:>{col_width}}"
        lines.append(row)
    lines.append(sep)
    return "\n".join(lines)


def find_break_even(results: list[dict], symbol: str, timeframe: str) -> list[str]:
    subset = [
        r for r in results
        if r["symbol"] == symbol and r["timeframe"] == timeframe and not r.get("error")
    ]
    if not subset:
        return ["  No valid results for this champion."]

    max_trades = max(r["total_trades"] for r in subset)
    if max_trades < MIN_TRADES_FOR_SHARPE:
        return [
            f"  **VERDICT: Insufficient trades (max={max_trades}) — champion config is "
            f"misaligned with current model confidence distribution.**  \n"
            f"  Sharpe is statistically meaningless at N<{MIN_TRADES_FOR_SHARPE}.  \n"
            f"  PF alone indicates cost sensitivity but edge depth is unproven.  \n"
            f"  Root cause: `entry_conf_overall` threshold is too high for current ML model outputs."
        ]

    lines = []
    for c in COMMISSION_BPS:
        for s in SLIPPAGE_BPS:
            r = next((x for x in subset if x["commission_bps"] == c and x["slippage_bps"] == s), None)
            if r is None:
                continue
            sr = r["sharpe_ratio"]
            pf = r["profit_factor"]
            trades = r["total_trades"]
            sr_dead = (sr != sr) or (sr < EDGE_DEAD_SHARPE)   # NaN counts as dead
            pf_dead = pf < EDGE_DEAD_PF
            if sr_dead or pf_dead:
                reason = []
                if sr_dead:
                    reason.append(f"Sharpe={'N/A' if sr != sr else f'{sr:.3f}'}")
                if pf_dead:
                    reason.append(f"PF={pf:.3f}")
                reason.append(f"Trades={trades}")
                lines.append(
                    f"  Edge dies at commission={c} bps + slippage={s} bps "
                    f"(total={c + s} bps): {', '.join(reason)}"
                )
    if not lines:
        return ["  **Edge survives all tested cost levels.**"]
    return lines


def write_csv(results: list[dict], path: Path) -> None:
    fields = [
        "symbol", "timeframe", "commission_bps", "slippage_bps", "total_cost_bps",
        "sharpe_ratio", "profit_factor", "win_rate", "max_drawdown",
        "total_trades", "total_pnl", "total_return_pct", "error",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


def write_artifact(
    results: list[dict],
    champions: list[tuple[str, str]],
    output_dir: Path,
    diagnostics: dict | None = None,
) -> Path:
    today = date.today().isoformat()
    md_path = output_dir / f"cost_stress_sweep_{today}.md"
    csv_path = output_dir / f"cost_stress_sweep_{today}.csv"

    write_csv(results, csv_path)

    sections: list[str] = []
    sections.append(f"# Cost-Stress Sweep — {today}\n")
    sections.append(
        "Grid: commission ∈ {0, 5, 10, 20} bps × slippage ∈ {5, 10, 20, 40} bps.  \n"
        f"Edge-death thresholds: Sharpe < {EDGE_DEAD_SHARPE}, PF < {EDGE_DEAD_PF}.  \n"
        "Values in `[brackets]` are below threshold.\n"
    )

    if diagnostics:
        sections.append("\n## Pre-flight: Staleness-timestamp bug\n")
        sections.append(
            "The `evaluate_pipeline` staleness check assumes ms timestamps but receives "
            "nanosecond pandas values → `data_quality=0.5` on every bar → confidence halved → "
            "risk_map minimum (0.53) unreachable → **0 trades without bypass**.  \n\n"
            "This sweep injects `stale_threshold_factor=1e9` to bypass the penalty.  "
            "Confidence impact:\n"
        )
        rows = []
        for champ_key, diag in diagnostics.items():
            if "error" not in diag:
                rows.append(
                    f"| {champ_key} "
                    f"| {diag['bugged_mean']:.3f} "
                    f"| {diag['bugged_max']:.3f} "
                    f"| {diag['fixed_mean']:.3f} "
                    f"| {diag['fixed_max']:.3f} "
                    f"| {diag.get('samples', '?')} |"
                )
            else:
                rows.append(f"| {champ_key} | ERROR: {diag['error']} | — | — | — | — |")
        if rows:
            sections.append("| Champion | Bugged mean | Bugged max | Fixed mean | Fixed max | Samples |")
            sections.append("|----------|------------|-----------|-----------|----------|---------|")
            sections.extend(rows)
        sections.append("")

    sections.append("\n## Key findings\n")
    for symbol, tf in champions:
        label = f"{symbol}_{tf}"
        subset = [r for r in results if r["symbol"] == symbol and r["timeframe"] == tf]
        if not subset:
            continue
        baseline = next((r for r in subset if r["commission_bps"] == 0 and r["slippage_bps"] == 5), None)
        if baseline and not baseline.get("error"):
            trades = baseline["total_trades"]
            sr = baseline["sharpe_ratio"]
            pf = baseline["profit_factor"]
            sr_str = f"{sr:.3f}" if sr == sr else "N/A (too few trades)"
            sections.append(
                f"- **{label}** baseline (0+5 bps): Trades={trades}, "
                f"Sharpe={sr_str}, PF={pf:.3f}, "
                f"WR={baseline['win_rate']:.1f}%, MaxDD={baseline['max_drawdown']:.2f}%"
            )
    sections.append("")

    for symbol, tf in champions:
        label = f"{symbol}_{tf}"
        sections.append(f"\n## {label}\n")

        baseline = next(
            (r for r in results
             if r["symbol"] == symbol and r["timeframe"] == tf
             and r["commission_bps"] == 0 and r["slippage_bps"] == 5),
            None,
        )
        if baseline and not baseline.get("error"):
            sr = baseline["sharpe_ratio"]
            sr_str = f"{sr:.3f}" if sr == sr else "N/A"
            sections.append(
                f"**Baseline (0+5 bps)**: Sharpe={sr_str}, "
                f"PF={baseline['profit_factor']:.3f}, "
                f"WR={baseline['win_rate']:.1f}%, "
                f"MaxDD={baseline['max_drawdown']:.2f}%, "
                f"Trades={baseline['total_trades']}\n"
            )

        sections.append("\n### Sharpe Ratio\n```")
        sections.append(
            fmt_metric_table(results, symbol, tf, "sharpe_ratio",
                             dead_threshold=EDGE_DEAD_SHARPE, higher_is_better=True)
        )
        sections.append("```\n")

        sections.append("\n### Profit Factor\n```")
        sections.append(
            fmt_metric_table(results, symbol, tf, "profit_factor",
                             dead_threshold=EDGE_DEAD_PF, higher_is_better=True)
        )
        sections.append("```\n")

        sections.append("\n### Win Rate (%)\n```")
        sections.append(fmt_metric_table(results, symbol, tf, "win_rate"))
        sections.append("```\n")

        sections.append("\n### Max Drawdown (%)\n```")
        sections.append(
            fmt_metric_table(results, symbol, tf, "max_drawdown",
                             dead_threshold=10.0, higher_is_better=False)
        )
        sections.append("```\n")

        sections.append("\n### Trade count\n```")
        sections.append(fmt_metric_table(results, symbol, tf, "total_trades"))
        sections.append("```\n")

        sections.append("\n### Break-even analysis\n")
        sections.extend(find_break_even(results, symbol, tf))
        sections.append("")

    sections.append(f"\n---\nFull data: `{csv_path.name}`\n")

    md_path.write_text("\n".join(sections), encoding="utf-8")
    return md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Cost-stress sweep over champion configs")
    parser.add_argument(
        "--champions",
        nargs="+",
        default=["tBTCUSD_1h", "tBTCUSD_3h"],
        help="Champions to sweep (e.g. tBTCUSD_1h tBTCUSD_3h)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "artifacts" / "diagnostics"),
        help="Directory for output artifacts",
    )
    parser.add_argument(
        "--skip-diagnostics",
        action="store_true",
        help="Skip the pre-flight staleness diagnostics (faster)",
    )
    args = parser.parse_args()

    champions: list[tuple[str, str]] = []
    for c in args.champions:
        parts = c.rsplit("_", 1)
        if len(parts) != 2:
            print(f"[WARN] Cannot parse champion '{c}' — expected format symbol_timeframe")
            continue
        champions.append((parts[0], parts[1]))

    if not champions:
        champions = list(DEFAULT_CHAMPIONS)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    grid = [
        (symbol, tf, c, s)
        for symbol, tf in champions
        for c in COMMISSION_BPS
        for s in SLIPPAGE_BPS
    ]

    diagnostics: dict = {}
    if not args.skip_diagnostics:
        print("\nRunning pre-flight confidence diagnostics...")
        for symbol, tf in champions:
            key = f"{symbol}_{tf}"
            print(f"  {key}...", end=" ", flush=True)
            diag = diagnose_staleness_bug(symbol, tf)
            diagnostics[key] = diag
            if "error" not in diag:
                print(
                    f"bugged conf: {diag['bugged_mean']:.3f}/{diag['bugged_max']:.3f} "
                    f"→ fixed: {diag['fixed_mean']:.3f}/{diag['fixed_max']:.3f} "
                    f"({diag.get('samples', '?')} samples)"
                )
            else:
                print(f"ERROR: {diag['error']}")

    total = len(grid)
    print(f"\nCost-stress sweep: {total} runs across {len(champions)} champion(s)\n")
    print(f"{'Run':>4}  {'Champion':<16}  {'comm':>5}  {'slip':>5}  {'Sharpe':>8}  {'PF':>6}  {'Trades':>7}  {'Time':>6}")
    print("-" * 72)

    results: list[dict] = []
    for idx, (symbol, tf, c_bps, s_bps) in enumerate(grid, 1):
        t0 = time.monotonic()
        row = run_single(symbol, tf, c_bps, s_bps)
        elapsed = time.monotonic() - t0
        results.append(row)

        if row.get("error"):
            print(
                f"{idx:>4}  {symbol}_{tf:<10}  {c_bps:>4}b  {s_bps:>4}b  "
                f"{'ERROR':>8}  {'':>6}  {'':>7}  ({elapsed:.1f}s)"
            )
        else:
            sr = row["sharpe_ratio"]
            pf = row["profit_factor"]
            trades = row["total_trades"]
            sr_str = f"{sr:+.3f}" if sr == sr else "   N/A"
            sr_flag = " *" if (sr != sr or sr < EDGE_DEAD_SHARPE) else "  "
            pf_flag = " *" if pf < EDGE_DEAD_PF else "  "
            print(
                f"{idx:>4}  {symbol}_{tf:<10}  {c_bps:>4}b  {s_bps:>4}b  "
                f"{sr_str:>8}{sr_flag}  {pf:>5.3f}{pf_flag}  {trades:>6}  ({elapsed:.1f}s)"
            )

    print("-" * 72)
    print(f"\n* = below edge threshold (Sharpe<{EDGE_DEAD_SHARPE} or PF<{EDGE_DEAD_PF})\n")

    artifact = write_artifact(results, champions, output_dir, diagnostics=diagnostics or None)
    print(f"[ARTIFACT] {artifact}")


if __name__ == "__main__":
    main()
