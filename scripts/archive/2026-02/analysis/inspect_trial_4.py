import optuna

study_name = "optuna_phase3_fine_v7"
storage_url = "sqlite:///results/hparam_search/storage/optuna_phase3_fine_v7.db"

try:
    study = optuna.load_study(study_name=study_name, storage=storage_url)
    # Find trial with ID 4
    trial = next(t for t in study.trials if t.number == 4)

    print(f"Trial {trial.number} Analysis:")
    print(f"Value: {trial.value}")
    print(f"State: {trial.state}")
    print(f"User Attrs: {trial.user_attrs}")
    print(f"Params: {trial.params}")

except Exception as e:
    print(f"Error: {e}")
