#!/usr/bin/env python3
"""Pre-run validator to estimate zero-trade risk from configuration.

Analyzes optimizer configuration and estimates the probability that
trials will generate zero trades based on parameter ranges.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


def estimate_pass_rate(param_spec: dict[str, Any]) -> tuple[float, str]:
    """Estimate pass rate for a parameter gate.
    
    Returns: (pass_rate, description)
    """
    param_type = param_spec.get("type", "fixed")
    
    if param_type == "fixed":
        value = param_spec.get("value")
        return _estimate_fixed_pass_rate(value)
    
    elif param_type == "grid":
        values = param_spec.get("values", [])
        # Average pass rate across grid values
        rates = [_estimate_fixed_pass_rate(v)[0] for v in values]
        avg_rate = sum(rates) / len(rates) if rates else 0.0
        return avg_rate, f"grid avg across {len(values)} values"
    
    elif param_type == "float":
        low = float(param_spec.get("low", 0))
        high = float(param_spec.get("high", 1))
        mid = (low + high) / 2
        return _estimate_fixed_pass_rate(mid)
    
    elif param_type == "int":
        low = int(param_spec.get("low", 0))
        high = int(param_spec.get("high", 1))
        mid = (low + high) // 2
        return _estimate_fixed_pass_rate(mid)
    
    return 0.5, "unknown"


def _estimate_fixed_pass_rate(value: Any) -> tuple[float, str]:
    """Estimate pass rate for a fixed value based on empirical data."""
    if not isinstance(value, (int, float)):
        return 0.5, "non-numeric"
    
    val = float(value)
    
    # Entry confidence threshold (most critical)
    # Based on empirical observation of signal distributions
    if val < 0.30:
        return 0.70, "very permissive"
    elif val < 0.40:
        return 0.40, "permissive"
    elif val < 0.50:
        return 0.20, "moderate"
    elif val < 0.60:
        return 0.08, "strict"
    elif val < 0.70:
        return 0.03, "very strict"
    else:
        return 0.01, "extremely strict"


def estimate_fib_pass_rate(tolerance: float) -> tuple[float, str]:
    """Estimate pass rate for Fibonacci tolerance parameter."""
    if tolerance < 0.2:
        return 0.02, "extremely tight"
    elif tolerance < 0.3:
        return 0.05, "very tight"
    elif tolerance < 0.4:
        return 0.10, "tight"
    elif tolerance < 0.5:
        return 0.20, "moderate"
    elif tolerance < 0.7:
        return 0.40, "permissive"
    else:
        return 0.60, "very permissive"


def analyze_config(config: dict[str, Any]) -> dict[str, Any]:
    """Analyze configuration for zero-trade risk."""
    parameters = config.get("parameters", {})
    
    # Extract key gating parameters
    thresholds = parameters.get("thresholds", {})
    htf_fib = parameters.get("htf_fib", {})
    ltf_fib = parameters.get("ltf_fib", {})
    multi_tf = parameters.get("multi_timeframe", {})
    
    # Analyze entry confidence
    entry_conf = thresholds.get("entry_conf_overall", {})
    entry_rate, entry_desc = estimate_pass_rate(entry_conf)
    
    # Analyze HTF fibonacci
    htf_enabled = True  # Assume enabled if in config
    htf_entry = htf_fib.get("entry", {}) if isinstance(htf_fib, dict) else {}
    htf_tolerance = htf_entry.get("tolerance_atr", {}) if isinstance(htf_entry, dict) else {}
    
    if isinstance(htf_tolerance, dict):
        htf_tol_val = (float(htf_tolerance.get("low", 0.3)) + float(htf_tolerance.get("high", 0.5))) / 2
    else:
        htf_tol_val = float(htf_tolerance) if htf_tolerance else 0.5
    
    htf_rate, htf_desc = estimate_fib_pass_rate(htf_tol_val)
    
    # Analyze LTF fibonacci
    ltf_entry = ltf_fib.get("entry", {}) if isinstance(ltf_fib, dict) else {}
    ltf_tolerance = ltf_entry.get("tolerance_atr", {}) if isinstance(ltf_entry, dict) else {}
    
    if isinstance(ltf_tolerance, dict):
        ltf_tol_val = (float(ltf_tolerance.get("low", 0.3)) + float(ltf_tolerance.get("high", 0.5))) / 2
    else:
        ltf_tol_val = float(ltf_tolerance) if ltf_tolerance else 0.5
    
    ltf_rate, ltf_desc = estimate_fib_pass_rate(ltf_tol_val)
    
    # Check for overrides
    has_override = False
    if isinstance(multi_tf, dict):
        allow_override = multi_tf.get("allow_ltf_override")
        if isinstance(allow_override, dict):
            # Grid of true/false
            has_override = True in allow_override.get("values", [])
        else:
            has_override = bool(allow_override)
    
    # Estimate other gates (conservative estimates)
    confidence_rate = 0.30  # Confidence gate
    edge_rate = 0.40  # Edge requirement
    hysteresis_rate = 0.50  # Hysteresis delay
    ev_rate = 0.80  # EV filter
    
    # Combined pass rate (multiplicative)
    combined_rate = (
        entry_rate * 
        htf_rate * 
        ltf_rate * 
        confidence_rate * 
        edge_rate * 
        hysteresis_rate * 
        ev_rate
    )
    
    # Adjust if override enabled (reduces HTF blocking impact)
    if has_override:
        # Override provides escape valve - estimate 30% of HTF blocks can override
        effective_htf_rate = htf_rate + (1 - htf_rate) * 0.30
        combined_rate_with_override = (
            entry_rate * 
            effective_htf_rate * 
            ltf_rate * 
            confidence_rate * 
            edge_rate * 
            hysteresis_rate * 
            ev_rate
        )
    else:
        combined_rate_with_override = combined_rate
    
    return {
        "gate_analysis": {
            "entry_confidence": {
                "pass_rate": entry_rate,
                "description": entry_desc,
                "config": entry_conf,
            },
            "htf_fibonacci": {
                "pass_rate": htf_rate,
                "description": htf_desc,
                "tolerance": htf_tol_val,
            },
            "ltf_fibonacci": {
                "pass_rate": ltf_rate,
                "description": ltf_desc,
                "tolerance": ltf_tol_val,
            },
            "confidence_gate": {
                "pass_rate": confidence_rate,
                "description": "estimated",
            },
            "edge_requirement": {
                "pass_rate": edge_rate,
                "description": "estimated",
            },
            "hysteresis": {
                "pass_rate": hysteresis_rate,
                "description": "estimated",
            },
        },
        "combined_pass_rate": combined_rate,
        "combined_with_override": combined_rate_with_override if has_override else None,
        "has_ltf_override": has_override,
        "estimated_trades_per_1000_bars": combined_rate_with_override * 1000 if has_override else combined_rate * 1000,
    }


def print_analysis(analysis: dict[str, Any]) -> None:
    """Pretty print configuration analysis."""
    print("\n" + "="*80)
    print("ZERO-TRADE RISK ANALYSIS")
    print("="*80)
    
    gates = analysis["gate_analysis"]
    
    print("\nINDIVIDUAL GATE PASS RATES:")
    print("-" * 80)
    
    for gate_name, gate_info in gates.items():
        rate = gate_info["pass_rate"]
        desc = gate_info["description"]
        
        # Color coding based on severity
        if rate < 0.10:
            symbol = "🔴 CRITICAL"
        elif rate < 0.30:
            symbol = "🟡 WARNING"
        else:
            symbol = "🟢 OK"
        
        print(f"{symbol} {gate_name:20s}: {rate:6.1%} ({desc})")
    
    print("\n" + "="*80)
    print("COMBINED ANALYSIS:")
    print("="*80)
    
    combined = analysis["combined_pass_rate"]
    estimated_trades = analysis["estimated_trades_per_1000_bars"]
    
    print(f"\nCombined pass rate: {combined:.4%}")
    print(f"Estimated trades per 1000 bars: {estimated_trades:.1f}")
    
    if analysis["has_ltf_override"]:
        combined_override = analysis["combined_with_override"]
        estimated_override = combined_override * 1000
        print(f"\nWith LTF override enabled:")
        print(f"  Adjusted pass rate: {combined_override:.4%}")
        print(f"  Estimated trades per 1000 bars: {estimated_override:.1f}")
    
    print("\n" + "="*80)
    print("RISK ASSESSMENT:")
    print("="*80)
    
    if estimated_trades < 1:
        print("\n🔴 CRITICAL: Very high zero-trade risk!")
        print("   This configuration will likely produce 0 trades.")
        print("\n   IMMEDIATE ACTIONS REQUIRED:")
        print("   1. Lower entry_conf_overall to 0.30-0.40")
        print("   2. Increase fibonacci tolerances to 0.5-0.8")
        print("   3. Enable LTF override with threshold 0.70-0.85")
        print("   4. Run smoke test (2-5 trials) before long runs")
    
    elif estimated_trades < 5:
        print("\n🟡 WARNING: Moderate zero-trade risk")
        print("   Configuration may produce very few trades.")
        print("\n   RECOMMENDED ACTIONS:")
        print("   1. Consider lowering entry thresholds")
        print("   2. Consider widening fibonacci tolerances")
        print("   3. Enable LTF override if not already enabled")
        print("   4. Monitor first 10-20 trials for zero-trade patterns")
    
    elif estimated_trades < 20:
        print("\n🟢 ACCEPTABLE: Low zero-trade risk")
        print("   Configuration should produce trades, but may be selective.")
        print("\n   RECOMMENDATIONS:")
        print("   - Monitor early trials to confirm trades are generated")
        print("   - May want to widen ranges slightly for more exploration")
    
    else:
        print("\n🟢 GOOD: Very low zero-trade risk")
        print("   Configuration should reliably produce trades.")
        print("\n   RECOMMENDATIONS:")
        print("   - Proceed with optimization")
        print("   - Consider smoke test for additional validation")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_zero_trade_risk.py <config.yaml>")
        print("\nExample:")
        print("  python validate_zero_trade_risk.py config/optimizer/tBTCUSD_1h_optuna.yaml")
        sys.exit(1)
    
    config_path = Path(sys.argv[1])
    
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    
    try:
        config_text = config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(config_text)
    except Exception as e:
        print(f"ERROR: Failed to parse config: {e}")
        sys.exit(1)
    
    analysis = analyze_config(config)
    print_analysis(analysis)


if __name__ == "__main__":
    main()
