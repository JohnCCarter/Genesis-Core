#!/usr/bin/env python3
"""Test att float-normalisering fungerar korrekt."""

import json


def normalize_float_value(value, step):
    """Normalisera float till exakt step-multipel."""
    if step is None or step == 0:
        return value
    step_float = float(step)
    # Beräkna antal decimaler från step
    step_str = str(step_float)
    if "." in step_str:
        decimals = len(step_str.split(".")[1])
    else:
        decimals = 0
    # Round till rätt antal decimaler
    return round(round(value / step_float) * step_float, decimals)


def _trial_key(params):
    """Simulera trial key-funktionen."""
    return json.dumps(params, sort_keys=True, separators=(",", ":"))


# Test precision-problem
test_cases = [
    (0.44999999999999996, 0.05, 0.45),
    (0.39999999999999997, 0.05, 0.4),
    (0.6000000000000001, 0.05, 0.6),
    (2.4000000000000004, 0.1, 2.4),
    (1.9000000000000001, 0.1, 1.9),
]

print("Testing float normalization:")
print("-" * 60)

all_ok = True
for raw_value, step, expected in test_cases:
    normalized = normalize_float_value(raw_value, step)
    params_before = {"value": raw_value}
    params_after = {"value": normalized}
    key_before = _trial_key(params_before)
    key_after = _trial_key(params_after)
    key_expected = _trial_key({"value": expected})

    match_expected = key_after == key_expected
    status = "[OK]" if match_expected else "[FAIL]"

    print(f"{status} {raw_value} -> {normalized} (step={step})")
    if not match_expected:
        print(f"    Expected: {expected}, Got: {normalized}")
        all_ok = False

print()
if all_ok:
    print("[OK] Normalisering fungerar korrekt - cache-nycklar blir konsekventa")
else:
    print("[FAIL] Normalisering har problem")
