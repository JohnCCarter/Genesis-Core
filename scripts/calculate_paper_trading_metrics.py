#!/usr/bin/env python3
"""
Calculate Paper Trading Metrics

Calculates comprehensive metrics from paper trading results including:
- Profit Factor
- PF Robustness (utan top-3)
- Expectancy (expected value per trade)
- Median PnL per trade
- Concentration
- Max Drawdown

Generates weekly report markdown file.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import statistics
from datetime import datetime


def calculate_pf(trades):
    """Calculate profit factor from trades list."""
    if not trades:
        return 0.0

    total_wins = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    total_losses = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))

    if total_losses == 0:
        return float("inf") if total_wins > 0 else 0.0

    return total_wins / total_losses


def calculate_expectancy(trades):
    """Calculate expectancy (expected value per trade).

    Expectancy = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)
    """
    if not trades:
        return 0.0

    winning_trades = [t for t in trades if t["pnl"] > 0]
    losing_trades = [t for t in trades if t["pnl"] < 0]

    num_trades = len(trades)
    win_rate = len(winning_trades) / num_trades if num_trades > 0 else 0.0
    loss_rate = len(losing_trades) / num_trades if num_trades > 0 else 0.0

    avg_win = sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
    avg_loss = sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0.0

    expectancy = (win_rate * avg_win) + (loss_rate * avg_loss)  # avg_loss is negative
    return expectancy


def calculate_median_pnl(trades):
    """Calculate median PnL per trade."""
    if not trades:
        return 0.0

    pnls = [t["pnl"] for t in trades]
    return statistics.median(pnls)


def calculate_robustness(trades, total_pnl):
    """Calculate robustness metrics."""
    if not trades:
        return {
            "pf_without_top1": 0.0,
            "pf_without_top3": 0.0,
            "top1_concentration_pct": 0.0,
        }

    sorted_trades = sorted(trades, key=lambda t: t["pnl"], reverse=True)

    # PF utan top-1
    if len(sorted_trades) > 1:
        trades_without_top1 = sorted_trades[1:]
        pf_without_top1 = calculate_pf(trades_without_top1)
    else:
        pf_without_top1 = 0.0

    # PF utan top-3
    if len(sorted_trades) > 3:
        trades_without_top3 = sorted_trades[3:]
        pf_without_top3 = calculate_pf(trades_without_top3)
    else:
        pf_without_top3 = 0.0

    # Top-1 concentration
    top1_pnl = sorted_trades[0]["pnl"] if len(sorted_trades) >= 1 else 0
    top1_pct = 100.0 * top1_pnl / total_pnl if total_pnl != 0 else 0.0

    return {
        "pf_without_top1": pf_without_top1,
        "pf_without_top3": pf_without_top3,
        "top1_concentration_pct": top1_pct,
    }


def evaluate_criteria(metrics):
    """Evaluate metrics against pass/fail criteria."""
    criteria = {
        "pf": (metrics["pf"], 1.30, ">="),
        "pf_without_top3": (metrics["pf_without_top3"], 1.20, ">="),
        "expectancy": (metrics["expectancy"], 0.0, ">"),
        "median_pnl": (metrics["median_pnl"], 0.0, ">"),
        "top1_concentration_pct": (metrics["top1_concentration_pct"], 30.0, "<"),
        "max_drawdown": (metrics["max_drawdown_pct"], 2.0, "<="),
        "win_rate": (metrics["win_rate"], 55.0, ">"),
    }

    results = {}
    for name, (value, target, op) in criteria.items():
        if op == ">=":
            passed = value >= target
        elif op == ">":
            passed = value > target
        elif op == "<=":
            passed = value <= target
        elif op == "<":
            passed = value < target
        else:
            passed = False

        results[name] = {
            "value": value,
            "target": target,
            "operator": op,
            "passed": passed,
        }

    # Primary vs secondary goals
    primary_goals = ["pf", "pf_without_top3", "expectancy", "max_drawdown"]
    primary_passed = all(results[g]["passed"] for g in primary_goals)
    all_passed = all(r["passed"] for r in results.values())

    return results, primary_passed, all_passed


def generate_weekly_report(
    metrics, criteria_results, primary_passed, all_passed, week_num, period_start, period_end
):
    """Generate weekly report markdown."""

    def status_emoji(passed):
        return "✅" if passed else "❌"

    report = f"""# Paper Trading Weekly Report: {period_end}

**Week**: {week_num}/6
**Period**: {period_start} to {period_end}
**Champion**: v5a_sizing_exp1
**Symbol**: tBTCUSD (TEST symbol: tTESTBTC:TESTUSD)

---

## Metrics Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **PF** | {metrics['pf']:.2f} | >= 1.30 | {status_emoji(criteria_results['pf']['passed'])} |
| **PF utan top-3** | {metrics['pf_without_top3']:.2f} | >= 1.20 | {status_emoji(criteria_results['pf_without_top3']['passed'])} |
| **Expectancy** | ${metrics['expectancy']:.2f} | > $0 | {status_emoji(criteria_results['expectancy']['passed'])} |
| **Median PnL/trade** | ${metrics['median_pnl']:.2f} | > $0 | {status_emoji(criteria_results['median_pnl']['passed'])} |
| **Top-1 concentration** | {metrics['top1_concentration_pct']:.1f}% | < 30% | {status_emoji(criteria_results['top1_concentration_pct']['passed'])} |
| **MaxDD** | {metrics['max_drawdown_pct']:.2f}% | <= 2.0% | {status_emoji(criteria_results['max_drawdown']['passed'])} |
| **Trade count** | {metrics['num_trades']} | ~10-15/wk | {status_emoji(8 <= metrics['num_trades'] <= 20)} |
| **Win rate** | {metrics['win_rate']:.1f}% | > 55% | {status_emoji(criteria_results['win_rate']['passed'])} |

---

## Overall Assessment

**Primary Goals** (Must Pass): {"✅ PASS" if primary_passed else "❌ FAIL"}
**Secondary Goals**: {"✅ PASS" if all_passed else "⚠️ PARTIAL"}

### Primary Goals Status
- PF >= 1.30: {status_emoji(criteria_results['pf']['passed'])}
- PF utan top-3 >= 1.20: {status_emoji(criteria_results['pf_without_top3']['passed'])}
- Expectancy > $0: {status_emoji(criteria_results['expectancy']['passed'])}
- MaxDD <= 2.0%: {status_emoji(criteria_results['max_drawdown']['passed'])}

---

## Trade Details

- **Total trades**: {metrics['num_trades']}
- **Winning trades**: {metrics['winning_trades']} ({metrics['win_rate']:.1f}%)
- **Losing trades**: {metrics['losing_trades']} ({100 - metrics['win_rate']:.1f}%)
- **Avg win**: ${metrics['avg_win']:.2f}
- **Avg loss**: ${metrics['avg_loss']:.2f}
- **Largest win**: ${metrics['largest_win']:.2f}
- **Largest loss**: ${metrics['largest_loss']:.2f}

---

## Robustness Analysis

- **PF utan top-1**: {metrics['pf_without_top1']:.2f} (was {metrics['pf']:.2f})
- **PF utan top-3**: {metrics['pf_without_top3']:.2f} (was {metrics['pf']:.2f})
- **Top-1 concentration**: {metrics['top1_concentration_pct']:.1f}% of total PnL

---

## Notes

- Champion config: FROZEN (enforced by CI)
- Research branch: feature/composable-research
- Any anomalies or issues: [ADD NOTES HERE]
- Market conditions: [ADD NOTES HERE]
- Execution quality: [ADD NOTES HERE]

---

## Action Items

- [ ] Continue monitoring
- [ ] Investigate any anomalies
- [ ] Update freeze period if needed (emergency only)
"""

    return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Calculate paper trading metrics")
    parser.add_argument("results_file", help="Path to paper trading results JSON")
    parser.add_argument("--week", type=int, default=1, help="Week number (1-6)")
    parser.add_argument("--period-start", help="Period start date (YYYY-MM-DD)")
    parser.add_argument("--period-end", help="Period end date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output markdown file path")

    args = parser.parse_args()

    # Load results
    print(f"Loading results: {args.results_file}")
    with open(args.results_file) as f:
        results = json.load(f)

    # Extract trades and summary
    if "trades" in results:
        trades = results["trades"]
        summary = results.get("summary", {})
    else:
        # Assume multi-period results, use "Full 2024" or first key
        period_key = list(results.keys())[0]
        trades = results[period_key]["trades"]
        summary = results[period_key]["summary"]

    # Calculate metrics
    print("Calculating metrics...")
    total_pnl = sum(t["pnl"] for t in trades)
    pf = calculate_pf(trades)
    expectancy = calculate_expectancy(trades)
    median_pnl = calculate_median_pnl(trades)
    robustness = calculate_robustness(trades, total_pnl)

    winning_trades = [t for t in trades if t["pnl"] > 0]
    losing_trades = [t for t in trades if t["pnl"] < 0]

    metrics = {
        "num_trades": len(trades),
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "win_rate": 100.0 * len(winning_trades) / len(trades) if trades else 0.0,
        "pf": pf,
        "pf_without_top1": robustness["pf_without_top1"],
        "pf_without_top3": robustness["pf_without_top3"],
        "expectancy": expectancy,
        "median_pnl": median_pnl,
        "avg_win": (
            sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
        ),
        "avg_loss": (
            sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
        ),
        "largest_win": max((t["pnl"] for t in winning_trades), default=0.0),
        "largest_loss": min((t["pnl"] for t in losing_trades), default=0.0),
        "top1_concentration_pct": robustness["top1_concentration_pct"],
        "max_drawdown_pct": summary.get("max_drawdown", 0.0),
        "total_pnl": total_pnl,
    }

    # Evaluate criteria
    print("Evaluating criteria...")
    criteria_results, primary_passed, all_passed = evaluate_criteria(metrics)

    # Print summary
    print("\n" + "=" * 80)
    print("PAPER TRADING METRICS SUMMARY")
    print("=" * 80)
    print(f"Trades: {metrics['num_trades']}")
    print(f"PF: {metrics['pf']:.2f}")
    print(f"PF utan top-3: {metrics['pf_without_top3']:.2f}")
    print(f"Expectancy: ${metrics['expectancy']:.2f}/trade")
    print(f"Median PnL: ${metrics['median_pnl']:.2f}/trade")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    print(f"MaxDD: {metrics['max_drawdown_pct']:.2f}%")
    print(f"Top-1 Concentration: {metrics['top1_concentration_pct']:.1f}%")
    print("=" * 80)
    print(f"Primary Goals: {'✅ PASS' if primary_passed else '❌ FAIL'}")
    print(f"All Goals: {'✅ PASS' if all_passed else '⚠️ PARTIAL'}")
    print("=" * 80)

    # Generate weekly report
    if args.output:
        period_start = args.period_start or "YYYY-MM-DD"
        period_end = args.period_end or datetime.now().strftime("%Y-%m-%d")

        print(f"\nGenerating weekly report: {args.output}")
        report = generate_weekly_report(
            metrics,
            criteria_results,
            primary_passed,
            all_passed,
            args.week,
            period_start,
            period_end,
        )

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)

        print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
