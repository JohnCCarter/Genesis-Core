#!/usr/bin/env python3
"""Trace champion loading to understand the merge flow."""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.config.authority import ConfigAuthority  # noqa: E402
from core.strategy.champion_loader import ChampionLoader  # noqa: E402


def trace_champion_loading():
    """Trace how champion is loaded and merged."""

    print("=" * 70)
    print("CHAMPION LOADING TRACE")
    print("=" * 70)

    # 1. Load champion directly
    loader = ChampionLoader()
    champion = loader.load_cached("tBTCUSD", "1h")

    print("\n1. Champion loaded:")
    print(f"   Source: {champion.source}")
    print(f"   Version: {champion.version}")
    print(f"   Config keys: {list(champion.config.keys())}")

    # Check signal_adaptation in champion
    champ_signal = champion.config.get("thresholds", {}).get("signal_adaptation", {})
    if champ_signal:
        zones = champ_signal.get("zones", {})
        print("\n   Champion signal_adaptation zones:")
        for zone_name, zone_data in zones.items():
            entry_conf = zone_data.get("entry_conf_overall", "N/A")
            regime_proba = zone_data.get("regime_proba", {})
            print(f"     {zone_name}: entry_conf={entry_conf}, regime_proba={regime_proba}")

    # 2. Load baseline config
    authority = ConfigAuthority()
    cfg_obj, _, _ = authority.get()
    baseline = cfg_obj.model_dump()

    print(f"\n2. Baseline config keys: {list(baseline.keys())}")
    baseline_signal = baseline.get("thresholds", {}).get("signal_adaptation", {})
    if baseline_signal:
        zones = baseline_signal.get("zones", {})
        print("   Baseline signal_adaptation zones:")
        for zone_name, zone_data in zones.items():
            entry_conf = zone_data.get("entry_conf_overall", "N/A")
            regime_proba = zone_data.get("regime_proba", {})
            print(f"     {zone_name}: entry_conf={entry_conf}, regime_proba={regime_proba}")

    # 3. Load tmp_v4_test.json
    tmp_path = ROOT_DIR / "config" / "tmp" / "tmp_v4_test.json"
    if tmp_path.exists():
        tmp_payload = json.loads(tmp_path.read_text(encoding="utf-8"))
        tmp_cfg = tmp_payload.get("cfg", {})

        print(f"\n3. tmp_v4_test.json config keys: {list(tmp_cfg.keys())}")
        tmp_signal = tmp_cfg.get("thresholds", {}).get("signal_adaptation", {})
        if tmp_signal:
            zones = tmp_signal.get("zones", {})
            print("   tmp_v4_test signal_adaptation zones:")
            for zone_name, zone_data in zones.items():
                entry_conf = zone_data.get("entry_conf_overall", "N/A")
                regime_proba = zone_data.get("regime_proba", {})
                print(f"     {zone_name}: entry_conf={entry_conf}, regime_proba={regime_proba}")

    # 4. Simulate engine.py merge
    print("\n4. Simulating engine.py merge:")
    print("   configs = {**champion_cfg.config, **configs}")
    engine_merged = {**champion.config, **baseline}
    engine_signal = engine_merged.get("thresholds", {}).get("signal_adaptation", {})
    if engine_signal:
        zones = engine_signal.get("zones", {})
        print("   After engine.py merge (champion first, then baseline):")
        for zone_name, zone_data in zones.items():
            entry_conf = zone_data.get("entry_conf_overall", "N/A")
            regime_proba = zone_data.get("regime_proba", {})
            print(f"     {zone_name}: entry_conf={entry_conf}, regime_proba={regime_proba}")

    # 5. Simulate with tmp_v4_test override
    if tmp_path.exists():
        print("\n5. Simulating engine.py merge with tmp_v4_test override:")
        print("   configs = {**champion_cfg.config, **tmp_cfg}")
        engine_merged_tmp = {**champion.config, **tmp_cfg}
        engine_signal_tmp = engine_merged_tmp.get("thresholds", {}).get("signal_adaptation", {})
        if engine_signal_tmp:
            zones = engine_signal_tmp.get("zones", {})
            print("   After engine.py merge (champion first, then tmp_v4_test):")
            for zone_name, zone_data in zones.items():
                entry_conf = zone_data.get("entry_conf_overall", "N/A")
                regime_proba = zone_data.get("regime_proba", {})
                print(f"     {zone_name}: entry_conf={entry_conf}, regime_proba={regime_proba}")

    # 6. Simulate evaluate_pipeline merge (SHALLOW!)
    print("\n6. Simulating evaluate_pipeline merge (SHALLOW!):")
    print("   merged_cfg = champion_cfg")
    print("   merged_cfg.update(configs)  # ← SHALLOW MERGE!")

    # This is what happens in evaluate_pipeline
    eval_merged = dict(champion.config)
    eval_merged.update(engine_merged_tmp if tmp_path.exists() else engine_merged)

    eval_signal = eval_merged.get("thresholds", {}).get("signal_adaptation", {})
    if eval_signal:
        zones = eval_signal.get("zones", {})
        print("   After evaluate_pipeline merge (champion.update(configs) - SHALLOW):")
        for zone_name, zone_data in zones.items():
            entry_conf = zone_data.get("entry_conf_overall", "N/A")
            regime_proba = zone_data.get("regime_proba", {})
            print(f"     {zone_name}: entry_conf={entry_conf}, regime_proba={regime_proba}")

    print("\n" + "=" * 70)
    print("ANALYSIS:")
    print("=" * 70)
    print("1. engine.py merges: {**champion.config, **configs}")
    print("   → Champion läggs till FÖRST, sedan override:ar configs")
    print("2. evaluate_pipeline merges: champion_cfg.update(configs)")
    print("   → SHALLOW MERGE! Nested dicts override:as helt!")
    print("3. Om configs har 'thresholds' key, så override:as hela thresholds-dict")
    print("   → signal_adaptation från champion kan försvinna om configs har thresholds!")


if __name__ == "__main__":
    trace_champion_loading()
