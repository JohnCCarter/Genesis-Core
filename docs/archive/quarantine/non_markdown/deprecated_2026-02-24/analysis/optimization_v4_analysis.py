import optuna

# Configuration
STORAGE_URL = "sqlite:///results/hparam_search/storage/optuna_high_quality_v2.db"
STUDY_NAME = "optuna_high_quality_v2"

print(f"Loading study '{STUDY_NAME}' from {STORAGE_URL}...")

# Load Study
try:
    study = optuna.load_study(study_name=STUDY_NAME, storage=STORAGE_URL)
    print(f"Loaded study '{STUDY_NAME}' with {len(study.trials)} trials.")
except Exception as e:
    print(f"Error loading study: {e}")
    exit(1)

# Manual extraction of completed trials
completed_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
completed_trials.sort(key=lambda t: t.value if t.value is not None else float("-inf"), reverse=True)

print(f"Number of completed trials: {len(completed_trials)}")

if len(completed_trials) > 0:
    print("\nTop 10 Trials:")
    print(
        f"{'Trial':<6} | {'Score':<10} | {'Entry Conf':<12} | {'Min Edge':<10} | {'Duration (s)':<12}"
    )
    print("-" * 60)

    for t in completed_trials[:10]:
        entry_conf = t.params.get("thresholds.entry_conf_overall", "N/A")
        min_edge = t.params.get("thresholds.min_edge", "N/A")
        duration = t.duration.total_seconds() if t.duration else 0

        # Format floats
        score_str = f"{t.value:.4f}" if t.value is not None else "None"
        entry_str = f"{entry_conf:.4f}" if isinstance(entry_conf, float) else str(entry_conf)
        edge_str = f"{min_edge:.4f}" if isinstance(min_edge, float) else str(min_edge)

        print(
            f"{t.number:<6} | {score_str:<10} | {entry_str:<12} | {edge_str:<10} | {duration:<12.1f}"
        )

    print("\nBest Trial Params:")
    best_trial = completed_trials[0]
    for key, value in best_trial.params.items():
        print(f"  {key}: {value}")
else:
    print("No completed trials found yet.")
