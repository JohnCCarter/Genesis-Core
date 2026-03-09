#!/usr/bin/env python3
"""Test att Optuna returnerar float-värden korrekt med step."""

import optuna


def is_multiple_of(value, step, tolerance=1e-9):
    """Kontrollera om värde är multipel av step."""
    if step == 0:
        return True
    remainder = abs(value % step)
    return remainder < tolerance or abs(remainder - step) < tolerance


# Test med step-värden
study = optuna.create_study()
print("Testing Optuna float values with step:")
print("-" * 60)

errors = []

for i in range(10):
    trial = study.ask()

    # Test olika step-värden
    v1 = trial.suggest_float("entry_conf", low=0.35, high=0.55, step=0.05)
    v2 = trial.suggest_float("tolerance", low=0.3, high=0.7, step=0.05)
    v3 = trial.suggest_float("trail_mult", low=1.8, high=2.6, step=0.1)

    study.tell(trial, 1.0)  # Dummy score

    # Verifiera att värdena är multiplar av step
    ok1 = is_multiple_of(v1, 0.05)
    ok2 = is_multiple_of(v2, 0.05)
    ok3 = is_multiple_of(v3, 0.1)

    status1 = "[OK]" if ok1 else "[FAIL]"
    status2 = "[OK]" if ok2 else "[FAIL]"
    status3 = "[OK]" if ok3 else "[FAIL]"

    print(f"Trial {i+1}:")
    print(f"  entry_conf: {v1} {status1} (multipel av 0.05: {ok1})")
    print(f"  tolerance:  {v2} {status2} (multipel av 0.05: {ok2})")
    print(f"  trail_mult: {v3} {status3} (multipel av 0.1: {ok3})")
    print()

    if not ok1 or not ok2 or not ok3:
        errors.append((i + 1, v1, v2, v3, ok1, ok2, ok3))

if errors:
    print(f"[PROBLEM] {len(errors)} trials har värden som INTE är multiplar av step!")
    print("Detta kan orsaka problem med cache-nycklar och jämförelser.")
else:
    print("[OK] Alla värden är korrekta multiplar av step-värden")
