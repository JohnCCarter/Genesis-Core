#!/usr/bin/env python3
"""Identify exact configuration differences that cause trade count changes."""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.strategy.champion_loader import ChampionLoader  # noqa: E402


def deep_diff(base, override, path="", differences=None):
    """Find all differences between two dicts."""
    if differences is None:
        differences = []

    if not isinstance(base, dict) or not isinstance(override, dict):
        if base != override:
            differences.append({"path": path, "base": base, "override": override})
        return differences

    all_keys = set(base.keys()) | set(override.keys())

    for key in all_keys:
        new_path = f"{path}.{key}" if path else key

        if key not in base:
            differences.append(
                {"path": new_path, "base": None, "override": override[key], "action": "ADDED"}
            )
        elif key not in override:
            differences.append(
                {"path": new_path, "base": base[key], "override": None, "action": "REMOVED"}
            )
        else:
            deep_diff(base[key], override[key], new_path, differences)

    return differences


def main():
    print("=" * 70)
    print("KONFIGURATIONSJÄMFÖRELSE")
    print("=" * 70)

    # Load champion
    champion_loader = ChampionLoader()
    champion_cfg = champion_loader.load_cached("tBTCUSD", "1h")

    # Load tmp_v4_test
    tmp_path = ROOT_DIR / "config" / "tmp" / "tmp_v4_test.json"
    tmp_data = json.loads(tmp_path.read_text(encoding="utf-8"))
    tmp_cfg = tmp_data.get("cfg", {})

    # Simulate merge (as BacktestEngine does)
    merged = {**champion_cfg.config, **tmp_cfg}

    print("\n1. CHAMPION CONFIG (baseline)")
    print(f"   Keys: {sorted(champion_cfg.config.keys())}")

    print("\n2. TMP_V4_TEST CONFIG (override)")
    print(f"   Keys: {sorted(tmp_cfg.keys())}")

    print("\n3. MERGED CONFIG (final)")
    print(f"   Keys: {sorted(merged.keys())}")

    # Find differences
    print("\n" + "=" * 70)
    print("SKILLNADER SOM PÅVERKAR TRADES")
    print("=" * 70)

    differences = deep_diff(champion_cfg.config, merged)

    # Filter to important differences
    important_paths = [
        "exit",
        "htf_exit_config",
        "warmup_bars",
        "ltf_fib",
        "htf_fib",
        "thresholds.entry_conf_overall",
        "thresholds.signal_adaptation",
        "thresholds.regime_proba",
    ]

    important_diffs = [
        d for d in differences if any(d["path"].startswith(p) for p in important_paths)
    ]

    if important_diffs:
        print("\n[KRITISKA SKILLNADER]:")
        for diff in important_diffs:
            print(f"\n  {diff['path']}:")
            if diff.get("action") == "ADDED":
                print(f"    + LAGTS TILL: {json.dumps(diff['override'], indent=6)}")
            elif diff.get("action") == "REMOVED":
                print(f"    - TAGITS BORT: {json.dumps(diff['base'], indent=6)}")
            else:
                print(f"    Champion: {json.dumps(diff['base'], indent=6)}")
                print(f"    Merged:   {json.dumps(diff['override'], indent=6)}")
    else:
        print("\n[INGA KRITISKA SKILLNADER]")

    # Show what's ONLY in champion (gets merged in)
    print("\n" + "=" * 70)
    print("FÄLT SOM FINNS I CHAMPION MEN INTE I TMP_V4_TEST")
    print("(Dessa mergas in och kan påverka resultat)")
    print("=" * 70)

    champion_only = set(champion_cfg.config.keys()) - set(tmp_cfg.keys())
    if champion_only:
        for key in sorted(champion_only):
            value = champion_cfg.config[key]
            print(f"\n  {key}:")
            print(f"    {json.dumps(value, indent=4)}")
    else:
        print("\n  Inga extra fält i champion")

    # Show exit config specifically
    print("\n" + "=" * 70)
    print("EXIT CONFIG JÄMFÖRELSE")
    print("=" * 70)

    champion_exit = champion_cfg.config.get("exit", {})
    tmp_exit = tmp_cfg.get("exit", {})
    merged_exit = merged.get("exit", {})

    print("\n  Champion exit:")
    print(f"    {json.dumps(champion_exit, indent=4)}")
    print("\n  Tmp_v4_test exit:")
    print(f"    {json.dumps(tmp_exit, indent=4)}")
    print("\n  Merged exit (används):")
    print(f"    {json.dumps(merged_exit, indent=4)}")

    # Show htf_exit_config
    print("\n" + "=" * 70)
    print("HTF_EXIT_CONFIG (från champion, saknas i tmp_v4_test)")
    print("=" * 70)

    htf_exit = champion_cfg.config.get("htf_exit_config", {})
    if htf_exit:
        print(f"\n  {json.dumps(htf_exit, indent=2)}")
        print("\n  [WARNING] Detta mergas in fran champion och kan paverka exit-logiken!")

    print("\n" + "=" * 70)
    print("REKOMMENDATION")
    print("=" * 70)
    print("\nFör att få samma resultat som tidigare (141 trades):")
    print("1. Lägg till htf_exit_config i tmp_v4_test.json med samma värden")
    print("2. ELLER: Uppdatera champion-filen så den matchar tmp_v4_test")
    print("3. ELLER: Använd deep merge istället för shallow merge")

    return 0


if __name__ == "__main__":
    sys.exit(main())
