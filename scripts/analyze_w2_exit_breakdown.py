"""Analyze W2 exit reasons for champion vs quality-v2 candidate.

This script avoids heavy dependencies (pandas) and reads the saved trades CSVs.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def _to_float(x: str | None) -> float:
    try:
        return float(x) if x is not None and x != "" else 0.0
    except Exception:
        return 0.0


def _pick(cols: set[str], *cands: str) -> str | None:
    for c in cands:
        if c in cols:
            return c
    return None


def analyze_trades_csv(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {"rows": 0, "path": str(path)}

    norm_rows: list[dict[str, str]] = []
    for r in rows:
        norm_rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in r.items()})

    cols = set(norm_rows[0].keys())
    reason_col = _pick(cols, "exit_reason", "reason", "close_reason")
    pnl_col = _pick(cols, "pnl", "pnl_usd", "profit")
    comm_col = _pick(cols, "commission", "fees", "fee")

    if reason_col is None:
        raise RuntimeError(f"Missing exit reason column in {path}. Columns: {sorted(cols)}")

    counts: Counter[str] = Counter()
    net_by_reason: defaultdict[str, float] = defaultdict(float)
    wins = 0.0
    losses = 0.0

    enriched: list[dict[str, object]] = []

    for r in norm_rows:
        reason = r.get(reason_col) or "UNKNOWN"
        pnl = _to_float(r.get(pnl_col)) if pnl_col else 0.0
        comm = _to_float(r.get(comm_col)) if comm_col else 0.0
        net = pnl - comm

        counts[reason] += 1
        net_by_reason[reason] += net

        if net > 0:
            wins += net
        elif net < 0:
            losses += -net

        enriched.append(
            {
                "entry_time": r.get("entry_time") or r.get("entry_timestamp") or "",
                "exit_time": r.get("exit_time") or r.get("exit_timestamp") or "",
                "side": r.get("side") or r.get("action") or "",
                "exit_reason": reason,
                "net_pnl": net,
            }
        )

    pf_net = wins / losses if losses > 0 else float("inf")

    net_sorted = sorted(net_by_reason.items(), key=lambda kv: kv[1])
    losers = sorted(enriched, key=lambda x: float(x["net_pnl"]))[:10]
    winners = sorted(enriched, key=lambda x: float(x["net_pnl"]), reverse=True)[:10]

    return {
        "path": str(path),
        "rows": len(norm_rows),
        "used_cols": {"reason": reason_col, "pnl": pnl_col, "commission": comm_col},
        "pf_net": pf_net,
        "wins": wins,
        "losses": losses,
        "exit_reason_counts": dict(counts),
        "net_by_exit_reason": list(net_sorted),
        "top_losers": losers,
        "top_winners": winners,
    }


def _print_summary(name: str, res: dict) -> None:
    print(f"=== {name} ===")
    print(f"file: {res['path']}")
    print(
        "rows=",
        res.get("rows"),
        "pf_net=",
        round(float(res.get("pf_net", 0.0)), 4),
        "wins=",
        round(float(res.get("wins", 0.0)), 2),
        "losses=",
        round(float(res.get("losses", 0.0)), 2),
    )
    print("used_cols=", res.get("used_cols"))
    print("exit_reason_counts=", res.get("exit_reason_counts"))

    print("net_by_exit_reason=")
    net_map = {k: round(v, 2) for k, v in (res.get("net_by_exit_reason") or [])}
    print(net_map)

    print("top_losers=")
    for t in res.get("top_losers") or []:
        print(
            " ",
            t.get("entry_time"),
            "->",
            t.get("exit_time"),
            t.get("side"),
            t.get("exit_reason"),
            round(float(t.get("net_pnl", 0.0)), 2),
        )

    print("top_winners=")
    for t in res.get("top_winners") or []:
        print(
            " ",
            t.get("entry_time"),
            "->",
            t.get("exit_time"),
            t.get("side"),
            t.get("exit_reason"),
            round(float(t.get("net_pnl", 0.0)), 2),
        )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze trades CSV(s) and print net PF + exit reason breakdown. "
            "If no args are provided, falls back to the last-known W2 CSV defaults."
        )
    )
    parser.add_argument(
        "csv",
        nargs="*",
        help="One or more trades CSV paths (e.g. results/trades/...csv).",
    )
    parser.add_argument(
        "--label",
        nargs="*",
        default=None,
        help="Optional labels for each CSV (same count as csv args).",
    )
    args = parser.parse_args()

    if args.csv:
        paths = [Path(p) for p in args.csv]
        labels = list(args.label) if args.label else []
        if labels and len(labels) != len(paths):
            raise SystemExit(
                f"--label count ({len(labels)}) must match csv count ({len(paths)}), or be omitted"
            )

        for i, p in enumerate(paths):
            res = analyze_trades_csv(p)
            name = labels[i] if labels else p.name
            _print_summary(name, res)
        return

    # Backward-compatible default: previously hardcoded W2 comparison.
    champ_csv = Path("results/trades/tBTCUSD_1h_trades_20251225_183248.csv")
    cand_csv = Path("results/trades/tBTCUSD_1h_trades_20251225_183324.csv")

    _print_summary("W2 Champion", analyze_trades_csv(champ_csv))
    _print_summary("W2 Candidate (quality v2)", analyze_trades_csv(cand_csv))


if __name__ == "__main__":
    main()
