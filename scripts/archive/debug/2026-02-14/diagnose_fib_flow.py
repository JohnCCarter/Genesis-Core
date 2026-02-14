"""Diagnostikskript for att spara fibonacci-dataflodet genom pipelinen."""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from core.backtest.engine import BacktestEngine
from core.config.authority import ConfigAuthority

# Sätt DEBUG-loggning för att se [FIB-FLOW] meddelanden
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(name)s - %(message)s")


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base."""
    merged = dict(base)
    for key, value in (override or {}).items():
        # If both base and override have dicts, recurse
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        # If base has None or non-dict, override replaces it
        else:
            merged[key] = value
    return merged


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnostisera fib-dataflodet")
    parser.add_argument(
        "--config-path",
        type=Path,
        help="Valfri profil att ladda i stallet for championen (kan vara tmp-profil)",
    )
    parser.add_argument(
        "--runtime-only",
        action="store_true",
        help="Anvand endast runtime-konfigurationen utan att merge:a champion",
    )
    return parser.parse_args()


def _load_profile(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Profil saknas: {path}")

    with open(path) as f:
        data = json.load(f)

    cfg_wrapper = data.get("cfg", {})
    profile_cfg = cfg_wrapper.get("parameters") or cfg_wrapper.get("config", {})
    if not profile_cfg:
        profile_cfg = data.get("parameters", data)
    return profile_cfg


def main():
    """Kor diagnostik pa fib-dataflod."""

    args = _parse_args()

    print("\n" + "=" * 80)
    print("FIBONACCI DATAFLODES-DIAGNOSTIK")
    print("=" * 80 + "\n")

    champion_path = Path("config/strategy/champions/tBTCUSD_1h.json")
    profile_cfg: dict | None = None

    if args.runtime_only:
        print("[CONFIG] Runtime-only-lage: ingen champion eller extern profil anvands")
    else:
        config_path = args.config_path or champion_path
        try:
            profile_cfg = _load_profile(config_path)
        except FileNotFoundError as exc:
            print(f"[ERROR] {exc}")
            return 1

        print(f"[CONFIG] Profil laddad: {config_path}")
        print(f"   Profil cfg keys: {list(profile_cfg.keys())[:10]}")
        print(f"   HTF fib entry: {profile_cfg.get('htf_fib', {}).get('entry', {}).get('enabled')}")
        print(f"   LTF fib entry: {profile_cfg.get('ltf_fib', {}).get('entry', {}).get('enabled')}")
        print(f"   HTF block: {profile_cfg.get('multi_timeframe', {}).get('use_htf_block')}")
        print()

    authority = ConfigAuthority()
    baseline_cfg, _, _ = authority.get()
    baseline_cfg = baseline_cfg.model_dump_canonical()

    print(f"[DEBUG] Baseline htf_fib: {baseline_cfg.get('htf_fib')}")
    print(f"[DEBUG] Baseline ltf_fib: {baseline_cfg.get('ltf_fib')}")
    if profile_cfg:
        print(f"[DEBUG] Profil htf_fib before merge: {profile_cfg.get('htf_fib')}")
        print()
        merged_cfg = deep_merge(baseline_cfg, profile_cfg)
    else:
        merged_cfg = baseline_cfg

    # Debug: visa merged config
    print(f"[DEBUG] After merge - htf_fib: {merged_cfg.get('htf_fib')}")
    print(f"[DEBUG] After merge - ltf_fib: {merged_cfg.get('ltf_fib')}")
    print(f"[DEBUG] After merge - multi_timeframe: {merged_cfg.get('multi_timeframe')}")
    print()

    policy = {
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "initial_capital": 10000.0,
    }

    snapshot_id = "tBTCUSD_1h_2024-10-22_2025-10-01_v1"
    start_date = "2024-10-22"
    end_date = "2024-11-22"

    print("[BACKTEST] Kor diagnostik:")
    print(f"   Symbol: {policy['symbol']}, TF: {policy['timeframe']}")
    print(f"   Period: {start_date} - {end_date}")
    print(f"   Snapshot: {snapshot_id}")
    print()

    print("[RUNNING] Startar backtest (se [FIB-FLOW] loggar)...")
    print()

    engine = BacktestEngine(
        symbol=policy["symbol"],
        timeframe=policy["timeframe"],
        start_date=start_date,
        end_date=end_date,
        initial_capital=policy["initial_capital"],
    )

    if not engine.load_data():
        print("[ERROR] Kunde inte ladda data")
        return 1

    result = engine.run(policy=policy, configs=merged_cfg)

    print("\n" + "=" * 80)
    print("RESULTAT")
    print("=" * 80 + "\n")

    summary = result.get("summary", {})

    print(f"[RESULT] Trades: {summary.get('total_trades', 0)}")
    print(f"[RESULT] Return: {summary.get('total_return_pct', 0):.2f}%")
    print(f"[RESULT] PF: {summary.get('profit_factor', 0):.2f}")
    print(f"[RESULT] DD: {summary.get('max_drawdown_pct', 0):.2f}%")
    print()

    if summary.get("total_trades", 0) == 0:
        print("[WARNING] 0 trades!")
        print()
        print("Granska loggarna ovan for [FIB-FLOW] meddelanden")
    else:
        print("[SUCCESS] Trades genererades - fib-dataflod fungerar!")

    print()
    return 0 if summary.get("total_trades", 0) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
