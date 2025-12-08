import json

from core.optimizer.runner import _deep_merge


def test_deep_merge_side_effects():
    # Simulate default config cache
    default_cache = {
        "thresholds": {"signal_adaptation": {"zones": {"low": {"entry": 0.33, "regime": 0.60}}}},
        "risk": {"risk_map": [[0.1, 0.01]]},
    }

    # Trial 1 params
    params1 = {
        "thresholds": {"signal_adaptation": {"zones": {"low": {"entry_conf_overall": 0.27}}}},
        "risk": {"risk_map": [[0.1, 0.02]]},
    }

    # Trial 2 params
    params2 = {
        "thresholds": {"signal_adaptation": {"zones": {"low": {"entry_conf_overall": 0.24}}}},
        "risk": {"risk_map": [[0.1, 0.03]]},
    }

    print("Original Cache:", json.dumps(default_cache))

    # Merge Trial 1
    merged1 = _deep_merge(default_cache, params1)
    print("\nMerged 1:", json.dumps(merged1))
    print("Cache after 1:", json.dumps(default_cache))

    # Check if cache was modified
    if default_cache["risk"]["risk_map"][0][1] != 0.01:
        print("FAIL: Cache modified by Trial 1 (risk_map)!")

    if "entry_conf_overall" in default_cache["thresholds"]["signal_adaptation"]["zones"]["low"]:
        print("FAIL: Cache modified by Trial 1 (nested key)!")

    # Merge Trial 2
    merged2 = _deep_merge(default_cache, params2)
    print("\nMerged 2:", json.dumps(merged2))
    print("Cache after 2:", json.dumps(default_cache))

    # Check if Merged 2 has Trial 1 values
    if merged2["risk"]["risk_map"][0][1] == 0.02:
        print("FAIL: Merged 2 has Trial 1 values!")


if __name__ == "__main__":
    test_deep_merge_side_effects()
