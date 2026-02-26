import optuna

storage = "sqlite:///results/hparam_search/storage/optuna_phase3_fine_v7_long_v2_until_20251222_newstudy_20251219_1627.db"
study_name = "optuna_phase3_fine_v7_long_v2_until_20251222_newstudy_20251219_1627"

try:
    study = optuna.load_study(study_name=study_name, storage=storage)
    df = study.trials_dataframe()

    # Filter completed
    df = df[df.state == "COMPLETE"]

    # Sort by value (descending)
    df = df.sort_values("value", ascending=False)

    print("Top 10 Trials:")
    # Select a few interesting columns to display
    cols = [
        "number",
        "value",
        "params_thresholds.entry_conf_overall",
        "params_exit.exit_conf_threshold",
    ]
    # Handle cases where columns might be missing or named differently (using a safer approach if needed, but these should exist)
    available_cols = [c for c in cols if c in df.columns]

    print(df[available_cols].head(10).to_string(index=False))

except Exception as e:
    print(f"Error: {e}")
