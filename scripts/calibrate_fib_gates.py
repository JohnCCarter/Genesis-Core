"""Analysera fibonacci-nivåer och toleranser för att kalibrera gates."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.config.authority import ConfigAuthority


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base."""
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def test_config(config_name: str, test_cfg: dict, baseline_cfg: dict, champion_cfg: dict):
    """Testa en konfiguration och visa resultat."""
    print(f"\n{'='*80}")
    print(f"TEST: {config_name}")
    print(f"{'='*80}")

    # Deep merge: baseline -> champion -> test
    merged = deep_merge(baseline_cfg, champion_cfg)
    merged = deep_merge(merged, test_cfg)

    # Visa HTF/LTF config
    htf_cfg = merged.get("htf_fib", {}).get("entry", {})
    ltf_cfg = merged.get("ltf_fib", {}).get("entry", {})
    print(f"HTF enabled: {htf_cfg.get('enabled')}, tolerance: {htf_cfg.get('tolerance_atr')}")
    print(f"LTF enabled: {ltf_cfg.get('enabled')}, tolerance: {ltf_cfg.get('tolerance_atr')}")
    print(f"Use HTF block: {merged.get('multi_timeframe', {}).get('use_htf_block')}")

    policy = {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "initial_capital": 10000.0,
    }

    engine = BacktestEngine(
        symbol=policy["symbol"],
        timeframe=policy["timeframe"],
        start_date="2024-10-22",
        end_date="2024-11-22",
        initial_capital=policy["initial_capital"],
    )

    if not engine.load_data():
        print("[ERROR] Could not load data")
        return

    result = engine.run(policy=policy, configs=merged)
    summary = result.get("summary", {})

    trades = summary.get("total_trades", 0)
    ret = summary.get("total_return_pct", 0)
    pf = summary.get("profit_factor", 0)

    print(f"\nRESULTAT: {trades} trades, Return: {ret:.2f}%, PF: {pf:.2f}")

    return trades, ret, pf


def main():
    """Kalibrera fib-gates genom att testa olika konfigurationer."""

    print("=" * 80)
    print("FIBONACCI GATE KALIBRERING")
    print("=" * 80)

    # Ladda baseline och champion
    authority = ConfigAuthority()
    baseline_cfg, _, _ = authority.get()
    baseline_cfg = baseline_cfg.model_dump_canonical()

    champion_path = Path("config/strategy/champions/tBTCUSD_1h.json")
    with open(champion_path) as f:
        champion_data = json.load(f)

    cfg_wrapper = champion_data.get("cfg", {})
    champion_cfg = cfg_wrapper.get("parameters") or cfg_wrapper.get("config", {})

    print("\nBaseline champion:")
    test_config("Champion baseline", {}, baseline_cfg, champion_cfg)

    # Test 1: Inaktivera HTF block
    print("\n" + "-" * 80)
    test_config(
        "HTF block disabled",
        {"multi_timeframe": {"use_htf_block": False}},
        baseline_cfg,
        champion_cfg,
    )

    # Test 2: Dubbla toleranser
    print("\n" + "-" * 80)
    test_config(
        "2x tolerance (0.5 -> 1.0)",
        {
            "htf_fib": {"entry": {"tolerance_atr": 1.0}},
            "ltf_fib": {"entry": {"tolerance_atr": 1.0}},
        },
        baseline_cfg,
        champion_cfg,
    )

    # Test 3: Missing policy = pass
    print("\n" + "-" * 80)
    test_config(
        "Missing policy: pass",
        {
            "htf_fib": {"entry": {"missing_policy": "pass"}},
            "ltf_fib": {"entry": {"missing_policy": "pass"}},
        },
        baseline_cfg,
        champion_cfg,
    )

    # Test 4: Inaktivera både HTF och LTF
    print("\n" + "-" * 80)
    test_config(
        "All fib gates disabled",
        {"htf_fib": {"entry": {"enabled": False}}, "ltf_fib": {"entry": {"enabled": False}}},
        baseline_cfg,
        champion_cfg,
    )

    # Test 5: Endast LTF disabled
    print("\n" + "-" * 80)
    test_config(
        "Only LTF disabled", {"ltf_fib": {"entry": {"enabled": False}}}, baseline_cfg, champion_cfg
    )

    print("\n" + "=" * 80)
    print("KALIBRERING KLAR")
    print("=" * 80)
    print("\nAnalysera resultaten ovan for att se vilken konfiguration som ger trades.")


if __name__ == "__main__":
    main()
