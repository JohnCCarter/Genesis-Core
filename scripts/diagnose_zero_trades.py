#!/usr/bin/env python3
"""Deep diagnostic tool to understand why Optuna trials produce zero trades.

This script traces the ENTIRE decision chain from data loading through
backtest execution to understand each gate that blocks trade generation.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def analyze_trial_log(log_path: Path) -> dict[str, Any]:
    """Analyze a trial's backtest log to extract decision gate statistics."""
    if not log_path.exists():
        return {"error": "Log file not found"}

    try:
        log_text = log_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": f"Failed to read log: {e}"}

    # Extract decision reasons from log
    reason_counts = Counter()
    lines = log_text.split("\n")

    for line in lines:
        # Look for decision reasons in log output
        if "reasons" in line.lower() or "blocked" in line.lower():
            # Extract reason if present
            if "HTF_FIB" in line:
                reason_counts["HTF_FIB_BLOCK"] += 1
            elif "LTF_FIB" in line:
                reason_counts["LTF_FIB_BLOCK"] += 1
            elif "CONF_TOO_LOW" in line:
                reason_counts["CONF_TOO_LOW"] += 1
            elif "EV_NEG" in line:
                reason_counts["EV_NEG"] += 1
            elif "COOLDOWN" in line:
                reason_counts["COOLDOWN"] += 1

    return {
        "log_path": str(log_path),
        "log_size": len(log_text),
        "reason_counts": dict(reason_counts),
    }


def analyze_trial_config(config_path: Path) -> dict[str, Any]:
    """Analyze trial configuration to identify overly strict gates."""
    if not config_path.exists():
        return {"error": "Config file not found"}

    try:
        config_text = config_path.read_text(encoding="utf-8")
        config_data = json.loads(config_text)
    except Exception as e:
        return {"error": f"Failed to parse config: {e}"}

    cfg = config_data.get("cfg", {})

    # Extract key thresholds that affect trade generation
    thresholds = cfg.get("thresholds", {})
    htf_fib = (cfg.get("htf_fib") or {}).get("entry", {})
    ltf_fib = (cfg.get("ltf_fib") or {}).get("entry", {})
    multi_tf = cfg.get("multi_timeframe", {})

    analysis = {
        "entry_conf_overall": thresholds.get("entry_conf_overall"),
        "regime_proba": thresholds.get("regime_proba", {}),
        "min_edge": thresholds.get("min_edge"),
        "htf_fib_enabled": htf_fib.get("enabled"),
        "htf_fib_tolerance_atr": htf_fib.get("tolerance_atr"),
        "htf_fib_missing_policy": htf_fib.get("missing_policy"),
        "ltf_fib_enabled": ltf_fib.get("enabled"),
        "ltf_fib_tolerance_atr": ltf_fib.get("tolerance_atr"),
        "ltf_fib_missing_policy": ltf_fib.get("missing_policy"),
        "use_htf_block": multi_tf.get("use_htf_block"),
        "allow_ltf_override": multi_tf.get("allow_ltf_override"),
        "ltf_override_threshold": multi_tf.get("ltf_override_threshold"),
    }

    # Identify potential issues
    issues = []

    # Check entry confidence threshold
    entry_conf = analysis.get("entry_conf_overall")
    if entry_conf and entry_conf > 0.50:
        issues.append(f"HIGH_ENTRY_CONF: {entry_conf:.2f} (>0.50 is very strict)")

    # Check HTF fibonacci gates
    if analysis.get("htf_fib_enabled"):
        htf_tol = analysis.get("htf_fib_tolerance_atr")
        if htf_tol and htf_tol < 0.3:
            issues.append(f"TIGHT_HTF_FIB_TOLERANCE: {htf_tol:.2f} (< 0.3 is very strict)")

    # Check LTF fibonacci gates
    if analysis.get("ltf_fib_enabled"):
        ltf_tol = analysis.get("ltf_fib_tolerance_atr")
        if ltf_tol and ltf_tol < 0.3:
            issues.append(f"TIGHT_LTF_FIB_TOLERANCE: {ltf_tol:.2f} (< 0.3 is very strict)")

    # Check multi-timeframe blocking
    if analysis.get("use_htf_block") and not analysis.get("allow_ltf_override"):
        issues.append("HTF_BLOCK_ENABLED_NO_OVERRIDE: HTF can block without LTF override option")

    analysis["potential_issues"] = issues

    return analysis


def analyze_backtest_result(result_path: Path) -> dict[str, Any]:
    """Analyze backtest result JSON to understand why no trades occurred."""
    if not result_path.exists():
        return {"error": "Result file not found"}

    try:
        result_text = result_path.read_text(encoding="utf-8")
        result_data = json.loads(result_text)
    except Exception as e:
        return {"error": f"Failed to parse result: {e}"}

    summary = result_data.get("summary", {})
    trades = result_data.get("trades", [])

    num_trades = len(trades)

    if num_trades == 0:
        # Analyze why no trades - need to look at bars processed
        bars_processed = summary.get("bars_processed", 0)
        warmup_bars = result_data.get("metadata", {}).get("warmup_bars", 0)
        total_bars = bars_processed + warmup_bars

        analysis = {
            "num_trades": 0,
            "bars_processed": bars_processed,
            "warmup_bars": warmup_bars,
            "total_bars": total_bars,
            "issue": "ZERO_TRADES",
        }

        # If very few bars processed, might be data issue
        if bars_processed < 100:
            analysis["likely_cause"] = "INSUFFICIENT_DATA"
        else:
            analysis["likely_cause"] = "GATES_TOO_STRICT"

        return analysis

    return {
        "num_trades": num_trades,
        "trades": trades[:3],  # Sample first 3 trades
    }


def diagnose_zero_trade_trial(run_dir: Path, trial_id: str) -> dict[str, Any]:
    """Comprehensive diagnosis of a single zero-trade trial."""
    trial_file = run_dir / f"{trial_id}.json"
    trial_log = run_dir / f"{trial_id}.log"
    trial_config = run_dir / f"{trial_id}_config.json"

    if not trial_file.exists():
        return {"error": f"Trial file not found: {trial_file}"}

    # Load trial data
    try:
        trial_data = json.loads(trial_file.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to parse trial: {e}"}

    # Get results path
    results_path = trial_data.get("results_path")
    if results_path:
        results_full_path = Path(__file__).parent.parent / "results" / "backtests" / results_path
    else:
        results_full_path = None

    diagnosis = {
        "trial_id": trial_id,
        "parameters": trial_data.get("parameters", {}),
        "score": trial_data.get("score", {}),
        "config_analysis": {},
        "log_analysis": {},
        "result_analysis": {},
    }

    # Analyze config
    if trial_config.exists():
        diagnosis["config_analysis"] = analyze_trial_config(trial_config)

    # Analyze log
    if trial_log.exists():
        diagnosis["log_analysis"] = analyze_trial_log(trial_log)

    # Analyze result
    if results_full_path and results_full_path.exists():
        diagnosis["result_analysis"] = analyze_backtest_result(results_full_path)

    # Synthesize findings
    findings = []

    # Check for data issues
    result_analysis = diagnosis.get("result_analysis", {})
    if result_analysis.get("likely_cause") == "INSUFFICIENT_DATA":
        findings.append(
            "CRITICAL: Insufficient data processed. Check data availability and date ranges."
        )

    # Check for config issues
    config_issues = diagnosis.get("config_analysis", {}).get("potential_issues", [])
    for issue in config_issues:
        findings.append(f"CONFIG: {issue}")

    # Check for blocking gates
    bars = result_analysis.get("bars_processed", 0)
    if bars > 100 and result_analysis.get("num_trades") == 0:
        findings.append(
            f"GATES_BLOCKING: Processed {bars} bars but generated 0 trades. Gates are too strict."
        )

    diagnosis["findings"] = findings

    return diagnosis


def print_diagnosis(diagnosis: dict[str, Any]) -> None:
    """Pretty print diagnosis results."""
    print("\n" + "=" * 80)
    print(f"ZERO-TRADE DIAGNOSIS: {diagnosis.get('trial_id', 'UNKNOWN')}")
    print("=" * 80)

    if "error" in diagnosis:
        print(f"\nERROR: {diagnosis['error']}")
        return

    # Parameters
    print("\nTRIAL PARAMETERS:")
    params = diagnosis.get("parameters", {})
    for key, value in params.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k2, v2 in value.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"  {key}: {value}")

    # Config analysis
    config_analysis = diagnosis.get("config_analysis", {})
    if config_analysis and "error" not in config_analysis:
        print("\nCONFIGURATION ANALYSIS:")
        print(f"  Entry Confidence: {config_analysis.get('entry_conf_overall')}")
        print(
            f"  HTF Fib Enabled: {config_analysis.get('htf_fib_enabled')} "
            f"(tolerance: {config_analysis.get('htf_fib_tolerance_atr')})"
        )
        print(
            f"  LTF Fib Enabled: {config_analysis.get('ltf_fib_enabled')} "
            f"(tolerance: {config_analysis.get('ltf_fib_tolerance_atr')})"
        )
        print(
            f"  HTF Block: {config_analysis.get('use_htf_block')} "
            f"(override: {config_analysis.get('allow_ltf_override')})"
        )

        issues = config_analysis.get("potential_issues", [])
        if issues:
            print("\n  Potential Issues:")
            for issue in issues:
                print(f"    ⚠️  {issue}")

    # Result analysis
    result_analysis = diagnosis.get("result_analysis", {})
    if result_analysis and "error" not in result_analysis:
        print("\nBACKTEST RESULTS:")
        print(f"  Trades: {result_analysis.get('num_trades', 0)}")
        print(f"  Bars Processed: {result_analysis.get('bars_processed', 0)}")
        print(f"  Warmup Bars: {result_analysis.get('warmup_bars', 0)}")

    # Findings
    findings = diagnosis.get("findings", [])
    if findings:
        print("\n" + "=" * 80)
        print("KEY FINDINGS:")
        print("=" * 80)
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. {finding}")

    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)

    has_config_issues = bool(config_analysis.get("potential_issues"))
    has_data_issues = result_analysis.get("likely_cause") == "INSUFFICIENT_DATA"

    if has_data_issues:
        print("\n1. DATA ISSUES:")
        print("   - Verify data files exist in data/curated/v1/candles/")
        print("   - Check date range covers the trial period")
        print("   - Ensure warmup_bars is appropriate for available data")

    if has_config_issues:
        print("\n2. CONFIGURATION FIXES:")

        if any("HIGH_ENTRY_CONF" in issue for issue in config_analysis.get("potential_issues", [])):
            print("   - Lower entry_conf_overall to 0.30-0.40 range")
            print("   - Adjust regime_proba thresholds if using regime-specific settings")

        if any("TIGHT_HTF" in issue for issue in config_analysis.get("potential_issues", [])):
            print("   - Increase htf_fib.entry.tolerance_atr to 0.4-0.8 range")
            print(
                "   - OR set htf_fib.entry.missing_policy to 'pass' to allow trading when HTF data unavailable"
            )

        if any("TIGHT_LTF" in issue for issue in config_analysis.get("potential_issues", [])):
            print("   - Increase ltf_fib.entry.tolerance_atr to 0.4-0.8 range")

        if any("HTF_BLOCK" in issue for issue in config_analysis.get("potential_issues", [])):
            print("   - Enable multi_timeframe.allow_ltf_override = true")
            print("   - Set multi_timeframe.ltf_override_threshold = 0.70-0.85")

    print("\n3. VALIDATION STEPS:")
    print("   - Run a smoke test with relaxed thresholds:")
    print("     entry_conf_overall: 0.25")
    print("     htf_fib.entry.tolerance_atr: 0.6")
    print("     ltf_fib.entry.tolerance_atr: 0.6")
    print("   - If trades appear, gradually tighten one parameter at a time")
    print("   - Monitor which gate blocks trades most frequently")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python diagnose_zero_trades.py <run_dir> <trial_id>")
        print("\nExample:")
        print("  python diagnose_zero_trades.py run_20251103_110227 trial_001")
        print(
            "  python diagnose_zero_trades.py results/hparam_search/run_20251103_110227 trial_001"
        )
        sys.exit(1)

    run_path = sys.argv[1]
    trial_id = sys.argv[2]

    run_dir = Path(run_path)

    # If just the run_id is given, prepend the results path
    if not run_dir.exists():
        run_dir = Path(__file__).parent.parent / "results" / "hparam_search" / run_path

    if not run_dir.exists():
        print(f"ERROR: Run directory not found: {run_dir}")
        sys.exit(1)

    diagnosis = diagnose_zero_trade_trial(run_dir, trial_id)
    print_diagnosis(diagnosis)


if __name__ == "__main__":
    main()
