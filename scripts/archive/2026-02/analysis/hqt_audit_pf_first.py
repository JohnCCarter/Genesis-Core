#!/usr/bin/env python3
"""
HQT Audit (PF-first) for v4a baseline full 2024.

Read-only analysis of extended validation results.

Deliverables:
1. PF helår + PF per kvartal (Q1-Q4)
2. PnL concentration: top-1 och top-5 trades som % av total PnL
3. PF robustness: PF efter att bästa trade tas bort, samt efter att bästa 3 trades tas bort
4. Bonus: fees/trade och fees burden

HQT-pass (PF-first):
- helår PF ≥ 1.5
- minst 3/4 kvartal PF ≥ 1.3
- inget kvartal < 1.0
- PF kollapsar inte under ~1.2 när top trades tas bort
"""

import json
from pathlib import Path


def calculate_pf(trades):
    """Calculate profit factor from trades list."""
    if not trades:
        return 0.0

    total_wins = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    total_losses = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))

    if total_losses == 0:
        return float("inf") if total_wins > 0 else 0.0

    return total_wins / total_losses


def hqt_audit(results_path: Path):
    """Run HQT audit on extended validation results."""

    # Load results
    with open(results_path) as f:
        results = json.load(f)

    print(f"{'='*90}")
    print("HQT AUDIT (PF-FIRST) - v4a baseline full 2024")
    print(f"{'='*90}")
    print()

    # (1) PF helår + per kvartal
    print("(1) Profit Factor Overview")
    print("-" * 90)

    quarters = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]
    pf_quarters = []

    for quarter in quarters:
        if quarter in results:
            pf = results[quarter]["summary"]["profit_factor"]
            num_trades = results[quarter]["summary"]["num_trades"]
            pf_quarters.append(pf)
            print(f"  {quarter}: PF = {pf:.2f} ({num_trades} trades)")
        else:
            print(f"  {quarter}: No data")

    print()

    if "Full 2024" in results:
        full_pf = results["Full 2024"]["summary"]["profit_factor"]
        full_trades = results["Full 2024"]["summary"]["num_trades"]
        print(f"  Full 2024: PF = {full_pf:.2f} ({full_trades} trades)")
    else:
        print("  Full 2024: No data")
        return

    print()

    # (2) PnL Concentration
    print("(2) PnL Concentration")
    print("-" * 90)

    trades = results["Full 2024"]["trades"]

    # Sort trades by pnl descending
    sorted_trades = sorted(trades, key=lambda t: t["pnl"], reverse=True)

    total_pnl = sum(t["pnl"] for t in trades)

    if len(sorted_trades) >= 1:
        top1_pnl = sorted_trades[0]["pnl"]
        top1_pct = 100.0 * top1_pnl / total_pnl if total_pnl != 0 else 0.0
        print(f"  Top-1 trade: ${top1_pnl:.2f} ({top1_pct:.1f}% of total PnL)")
        print(f"    Entry: {sorted_trades[0]['entry_time']}, Exit: {sorted_trades[0]['exit_time']}")
        print(f"    Side: {sorted_trades[0]['side']}, PnL%: {sorted_trades[0]['pnl_pct']:.2f}%")

    print()

    if len(sorted_trades) >= 5:
        top5_pnl = sum(t["pnl"] for t in sorted_trades[:5])
        top5_pct = 100.0 * top5_pnl / total_pnl if total_pnl != 0 else 0.0
        print(f"  Top-5 trades: ${top5_pnl:.2f} ({top5_pct:.1f}% of total PnL)")
        print("  Top-5 breakdown:")
        for i, trade in enumerate(sorted_trades[:5], 1):
            pct = 100.0 * trade["pnl"] / total_pnl if total_pnl != 0 else 0.0
            print(
                f"    #{i}: ${trade['pnl']:.2f} ({pct:.1f}%) - {trade['entry_time']} to {trade['exit_time']}"
            )

    print()

    # (3) PF Robustness
    print("(3) PF Robustness (Remove Top Trades)")
    print("-" * 90)

    # PF without top-1
    if len(sorted_trades) > 1:
        trades_without_top1 = sorted_trades[1:]
        pf_without_top1 = calculate_pf(trades_without_top1)
        print(f"  PF without top-1 trade: {pf_without_top1:.2f} (was {full_pf:.2f})")
        pf_drop_top1 = full_pf - pf_without_top1
        pf_drop_pct_top1 = 100.0 * pf_drop_top1 / full_pf if full_pf != 0 else 0.0
        print(f"    Drop: {pf_drop_top1:.2f} ({pf_drop_pct_top1:.1f}%)")
    else:
        print("  Not enough trades to remove top-1")

    print()

    # PF without top-3
    if len(sorted_trades) > 3:
        trades_without_top3 = sorted_trades[3:]
        pf_without_top3 = calculate_pf(trades_without_top3)
        print(f"  PF without top-3 trades: {pf_without_top3:.2f} (was {full_pf:.2f})")
        pf_drop_top3 = full_pf - pf_without_top3
        pf_drop_pct_top3 = 100.0 * pf_drop_top3 / full_pf if full_pf != 0 else 0.0
        print(f"    Drop: {pf_drop_top3:.2f} ({pf_drop_pct_top3:.1f}%)")
    else:
        print("  Not enough trades to remove top-3")

    print()

    # (4) Bonus: Fees
    print("(4) Bonus: Fees Analysis")
    print("-" * 90)

    total_commission = results["Full 2024"]["summary"]["total_commission"]
    total_slippage = results["Full 2024"]["summary"].get("total_slippage", 0.0)
    total_fees = total_commission + total_slippage

    fees_per_trade = total_fees / full_trades if full_trades > 0 else 0.0

    # Fees burden: fees as % of gross profit
    gross_profit = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    fees_burden_pct = 100.0 * total_fees / gross_profit if gross_profit > 0 else 0.0

    print(f"  Total commission: ${total_commission:.2f}")
    print(f"  Total slippage: ${total_slippage:.2f}")
    print(f"  Total fees: ${total_fees:.2f}")
    print(f"  Fees per trade: ${fees_per_trade:.2f}")
    print(f"  Fees burden: {fees_burden_pct:.1f}% of gross profit")

    print()

    # HQT-pass criteria
    print(f"{'='*90}")
    print("HQT-PASS CRITERIA (PF-first)")
    print(f"{'='*90}")
    print()

    checks = []

    # Helår PF >= 1.5
    check1 = full_pf >= 1.5
    checks.append(check1)
    status1 = "PASS" if check1 else "FAIL"
    print(f"  [1] Helar PF >= 1.5: {full_pf:.2f} - {status1}")

    # Minst 3/4 kvartal PF >= 1.3
    quarters_above_1_3 = sum(1 for pf in pf_quarters if pf >= 1.3)
    check2 = quarters_above_1_3 >= 3
    checks.append(check2)
    status2 = "PASS" if check2 else "FAIL"
    print(f"  [2] Minst 3/4 kvartal PF >= 1.3: {quarters_above_1_3}/4 - {status2}")

    # Inget kvartal < 1.0
    min_quarter_pf = min(pf_quarters) if pf_quarters else 0.0
    check3 = min_quarter_pf >= 1.0
    checks.append(check3)
    status3 = "PASS" if check3 else "FAIL"
    print(f"  [3] Inget kvartal < 1.0: min = {min_quarter_pf:.2f} - {status3}")

    # PF kollapsar inte under ~1.2 när top trades tas bort
    if len(sorted_trades) > 3:
        check4 = pf_without_top3 >= 1.2
        checks.append(check4)
        status4 = "PASS" if check4 else "FAIL"
        print(f"  [4] PF utan top-3 >= 1.2: {pf_without_top3:.2f} - {status4}")
    else:
        print("  [4] PF utan top-3 >= 1.2: N/A (not enough trades)")
        checks.append(False)

    print()

    # Overall verdict
    all_pass = all(checks)
    verdict = "HQT-PASS" if all_pass else "HQT-FAIL"
    symbol = "[PASS]" if all_pass else "[FAIL]"

    print(f"  Overall: {verdict} {symbol}")
    print()

    print(f"{'='*90}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="HQT Audit (PF-first)")
    parser.add_argument(
        "--results",
        default="results/extended_validation/v4a_ml_regime_relaxed_full2024_20260203_092718.json",
        help="Path to extended validation results",
    )

    args = parser.parse_args()

    results_path = Path(args.results)

    if not results_path.exists():
        print(f"ERROR: Results file not found: {results_path}")
        return

    hqt_audit(results_path)


if __name__ == "__main__":
    main()
