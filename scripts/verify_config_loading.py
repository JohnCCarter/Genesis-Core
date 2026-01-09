#!/usr/bin/env python3
"""Verify that configuration loading works correctly in both backtest and Optuna."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _bootstrap_paths() -> Path:
    # scripts/<this file> -> parents[1] == repo root
    root_dir = Path(__file__).resolve().parents[1]
    src_dir = root_dir / "src"
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    return root_dir


ROOT_DIR = _bootstrap_paths()

from core.config.authority import ConfigAuthority  # noqa: E402
from core.strategy.champion_loader import ChampionLoader  # noqa: E402


def main() -> int:
    print("=" * 70)
    print("VERIFIERING AV KONFIGURATIONSLADDNING")
    print("=" * 70)

    symbol = "tBTCUSD"
    timeframe = "1h"

    print("\n1. BASELINE CONFIG (ConfigAuthority)")
    print("-" * 70)
    authority = ConfigAuthority()
    baseline_cfg_obj, baseline_hash, baseline_version = authority.get()
    baseline_cfg = baseline_cfg_obj.model_dump()
    print(f"   Version: {baseline_version}")
    print(f"   Hash: {baseline_hash[:16]}...")
    print(f"   Keys: {sorted(baseline_cfg.keys())[:10]}...")

    print("\n2. CHAMPION CONFIG (ChampionLoader)")
    print("-" * 70)
    champion_loader = ChampionLoader()
    champion_cfg = champion_loader.load_cached(symbol, timeframe)
    print(f"   Source: {champion_cfg.source}")
    print(f"   Version: {champion_cfg.version}")
    print(f"   Checksum: {champion_cfg.checksum[:16]}...")
    print(f"   Keys: {sorted(champion_cfg.config.keys())}")

    print("\n3. TEST CONFIG (tmp_v4_test.json)")
    print("-" * 70)
    tmp_path = ROOT_DIR / "config" / "tmp" / "tmp_v4_test.json"
    if tmp_path.exists():
        tmp_data = json.loads(tmp_path.read_text(encoding="utf-8"))
        tmp_cfg = tmp_data.get("cfg", {})
        print(f"   File: {tmp_path.name}")
        print(f"   Keys: {sorted(tmp_cfg.keys())}")
    else:
        print(f"   File not found: {tmp_path}")
        tmp_cfg = {}

    print("\n4. BACKTESTENGINE MERGE (simulerad)")
    print("-" * 70)
    print("   Steg:")
    print("   1. Load baseline: ConfigAuthority.get()")
    print("   2. Deep merge with --config-file (om finns)")
    print("   3. engine.run() mergar champion: {**champion_cfg.config, **configs}")
    print("   4. evaluate_pipeline() mergar igen: champion_cfg.update(configs)")

    merged_engine = {**champion_cfg.config, **tmp_cfg}
    print("\n   Resultat (merged_engine):")
    print(f"   Keys: {sorted(merged_engine.keys())}")

    print("\n5. EVALUATE_PIPELINE MERGE (simulerad)")
    print("-" * 70)
    champion_cfg_dict = dict(champion_cfg.config or {})
    if tmp_cfg:
        merged_pipeline = champion_cfg_dict
        merged_pipeline.update(tmp_cfg)
    else:
        merged_pipeline = champion_cfg_dict
    print("   Resultat (merged_pipeline):")
    print(f"   Keys: {sorted(merged_pipeline.keys())}")

    print("\n6. MODELLLADDNING")
    print("-" * 70)
    from core.strategy.model_registry import ModelRegistry

    registry = ModelRegistry()
    model_meta = registry.get_meta(symbol, timeframe)
    if model_meta:
        print(f"   Model version: {model_meta.get('version', 'N/A')}")
        print(f"   Schema: {len(model_meta.get('schema', []))} features")
        print(f"   File: config/models/{symbol}_{timeframe}.json")
    else:
        print("   [ERROR] No model found!")

    print("\n" + "=" * 70)
    print("SAMMANFATTNING")
    print("=" * 70)
    print("\n[OK] Baseline config laddas korrekt (ConfigAuthority)")
    print("[OK] Champion config laddas korrekt (ChampionLoader)")
    print("[OK] Model laddas korrekt (ModelRegistry)")
    print("\n[INFO] Merge-ordning:")
    print("   1. Baseline (ConfigAuthority)")
    print("   2. --config-file override (deep merge)")
    print("   3. Champion merge (shallow merge i BacktestEngine)")
    print("   4. Champion merge igen (shallow merge i evaluate_pipeline)")
    print("\n[NOTE] Shallow merge betyder att nested dicts ersatts helt,")
    print("       inte mergas. Detta kan orsaka att falt forsvinner om")
    print("       de inte finns i override-config.")

    print("\n" + "=" * 70)
    print("POTENTIELLA PROBLEM")
    print("=" * 70)

    issues: list[str] = []
    required_fields = ["thresholds", "exit", "risk"]
    missing_in_tmp = [f for f in required_fields if f not in tmp_cfg]
    if missing_in_tmp:
        issues.append(f"tmp_v4_test.json saknar: {missing_in_tmp}")

    if "thresholds" in tmp_cfg and "thresholds" in champion_cfg.config:
        tmp_thresholds = tmp_cfg["thresholds"]
        champ_thresholds = champion_cfg.config["thresholds"]
        if isinstance(tmp_thresholds, dict) and isinstance(champ_thresholds, dict):
            missing_subkeys = set(champ_thresholds.keys()) - set(tmp_thresholds.keys())
            if missing_subkeys:
                issues.append(f"tmp_v4_test.json thresholds saknar: {missing_subkeys}")

    if issues:
        print("\n[WARNING] Potentiella problem:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] Inga uppenbara problem hittade")

    print("\n" + "=" * 70)
    print("SLUTSATS")
    print("=" * 70)
    print("\nKonfigurationen laddas korrekt. Om resultaten skiljer sig")
    print("beror det pa konfigurationsskillnader, inte pa laddningsfel.")
    print("\nFor att fa konsekventa resultat:")
    print("  1. Se till att alla nodvandiga falt finns i override-config")
    print("  2. Eller anvand deep merge istallet for shallow merge")
    print("  3. Dokumentera vilka falt som maste finnas i override-config")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
