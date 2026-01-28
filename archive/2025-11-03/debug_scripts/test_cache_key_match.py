#!/usr/bin/env python3
"""Test att cache-nycklar matchar efter normalisering."""

import json


def normalize_float_value(value, step):
    """Normalisera float till exakt step-multipel."""
    if step is None or step == 0:
        return value
    step_float = float(step)
    step_str = str(step_float)
    if "." in step_str:
        decimals = len(step_str.split(".")[1])
    else:
        decimals = 0
    return round(round(value / step_float) * step_float, decimals)


def _trial_key(params):
    """Simulera trial key-funktionen."""
    return json.dumps(params, sort_keys=True, separators=(",", ":"))


# Test att normaliserade värden ger samma cache-nyckel som exakta värden
test_cases = [
    (0.44999999999999996, 0.45, 0.05),
    (0.39999999999999997, 0.4, 0.05),
    (0.6000000000000001, 0.6, 0.05),
    (2.4000000000000004, 2.4, 0.1),
    (1.9000000000000001, 1.9, 0.1),
]

print("Testing cache key matching after normalization:")
print("-" * 60)

all_match = True
for raw_value, expected_exact, step in test_cases:
    normalized = normalize_float_value(raw_value, step)

    params_raw = {"thresholds": {"entry_conf": raw_value}}
    params_normalized = {"thresholds": {"entry_conf": normalized}}
    params_exact = {"thresholds": {"entry_conf": expected_exact}}

    key_raw = _trial_key(params_raw)
    key_normalized = _trial_key(params_normalized)
    key_exact = _trial_key(params_exact)

    matches = key_normalized == key_exact
    status = "[OK]" if matches else "[FAIL]"

    print(f"{status} {raw_value} -> {normalized} (step={step})")
    print(f"    Normalized key matches exact: {matches}")
    if not matches:
        print(f"    Raw key:      {key_raw[:50]}...")
        print(f"    Normalized:   {key_normalized[:50]}...")
        print(f"    Exact:        {key_exact[:50]}...")
        all_match = False
    print()

if all_match:
    print("[OK] Alla cache-nycklar matchar efter normalisering!")
else:
    print("[FAIL] Vissa cache-nycklar matchar inte")
