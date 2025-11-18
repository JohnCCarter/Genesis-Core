#!/usr/bin/env python3
"""Debug script to see what config is actually used."""

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

# Load champion
champion_loader = ChampionLoader()
champion_cfg = champion_loader.load_cached("tBTCUSD", "1h")

# Load tmp_v4_test
tmp_path = ROOT_DIR / "config" / "tmp" / "tmp_v4_test.json"
tmp_data = json.loads(tmp_path.read_text(encoding="utf-8"))
tmp_cfg = tmp_data.get("cfg", {})

# Simulate merge in BacktestEngine.run()
merged_engine = {**champion_cfg.config, **tmp_cfg}

# Simulate merge in evaluate_pipeline()
champion_cfg_dict = dict(champion_cfg.config or {})
if tmp_cfg:
    merged_pipeline = champion_cfg_dict
    merged_pipeline.update(tmp_cfg)
else:
    merged_pipeline = champion_cfg_dict

print("=" * 70)
print("CHAMPION CONFIG")
print("=" * 70)
print(json.dumps(champion_cfg.config, indent=2, default=str))

print("\n" + "=" * 70)
print("TMP_V4_TEST CONFIG")
print("=" * 70)
print(json.dumps(tmp_cfg, indent=2, default=str))

print("\n" + "=" * 70)
print("MERGED (BacktestEngine.run() style)")
print("=" * 70)
print(json.dumps(merged_engine, indent=2, default=str))

print("\n" + "=" * 70)
print("KEY DIFFERENCES")
print("=" * 70)

# Check for differences
champion_keys = set(champion_cfg.config.keys())
tmp_keys = set(tmp_cfg.keys())
only_in_champion = champion_keys - tmp_keys
only_in_tmp = tmp_keys - champion_keys
common_keys = champion_keys & tmp_keys

print(f"\nKeys only in champion: {sorted(only_in_champion)}")
print(f"Keys only in tmp_v4_test: {sorted(only_in_tmp)}")
print("\nCommon keys (checking for differences):")

for key in sorted(common_keys):
    champ_val = champion_cfg.config.get(key)
    tmp_val = tmp_cfg.get(key)
    if champ_val != tmp_val:
        print(f"\n  {key}:")
        print(f"    Champion: {champ_val}")
        print(f"    Tmp:      {tmp_val}")
