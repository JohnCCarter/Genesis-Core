import json

import optuna

storage = "sqlite:///results/hparam_search/storage/optuna_phase3_fine_v7_long_v2_until_20251222_newstudy_20251219_1627.db"
study_name = "optuna_phase3_fine_v7_long_v2_until_20251222_newstudy_20251219_1627"

try:
    study = optuna.load_study(storage=storage, study_name=study_name)
    target_trial = next((t for t in study.trials if t.number == 208), None)

    if target_trial:
        print(json.dumps(target_trial.params, indent=2))
    else:
        print("Trial 208 not found")
except Exception as e:
    print(f"Error: {e}")
