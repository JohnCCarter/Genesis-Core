from __future__ import annotations

import json
import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    # scripts/<this file> -> parents[1] == repo root
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.optimizer.runner import _deep_merge


def test_deep_merge_side_effects() -> None:
    default_cache = {
        "thresholds": {"signal_adaptation": {"zones": {"low": {"entry": 0.33, "regime": 0.60}}}},
        "risk": {"risk_map": [[0.1, 0.01]]},
    }

    params1 = {
        "thresholds": {"signal_adaptation": {"zones": {"low": {"entry_conf_overall": 0.27}}}},
        "risk": {"risk_map": [[0.1, 0.02]]},
    }

    params2 = {
        "thresholds": {"signal_adaptation": {"zones": {"low": {"entry_conf_overall": 0.24}}}},
        "risk": {"risk_map": [[0.1, 0.03]]},
    }

    print("Original Cache:", json.dumps(default_cache))

    merged1 = _deep_merge(default_cache, params1)
    print("\nMerged 1:", json.dumps(merged1))
    print("Cache after 1:", json.dumps(default_cache))

    if default_cache["risk"]["risk_map"][0][1] != 0.01:
        print("FAIL: Cache modified by Trial 1 (risk_map)!")

    if "entry_conf_overall" in default_cache["thresholds"]["signal_adaptation"]["zones"]["low"]:
        print("FAIL: Cache modified by Trial 1 (nested key)!")

    merged2 = _deep_merge(default_cache, params2)
    print("\nMerged 2:", json.dumps(merged2))
    print("Cache after 2:", json.dumps(default_cache))

    if merged2["risk"]["risk_map"][0][1] == 0.02:
        print("FAIL: Merged 2 has Trial 1 values!")


if __name__ == "__main__":
    test_deep_merge_side_effects()
