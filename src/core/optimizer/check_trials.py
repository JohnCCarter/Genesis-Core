import os

import optuna

storage = os.getenv("OPTUNA_DB", "sqlite:///optuna_search.db")
study = optuna.load_study(study_name="tBTCUSD_1h_phase7b", storage=storage)

print(f"Trials finished: {sum(t.state.is_finished() for t in study.trials)} / {len(study.trials)}")
if study.trials:
    t = study.best_trial
    print(f"Best value: {t.value:.6f}, params: {t.params}")
