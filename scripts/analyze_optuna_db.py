import argparse
import sys
from pathlib import Path

import optuna
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Analyze Optuna SQLite Database")
    parser.add_argument(
        "db_path",
        type=str,
        help="Path to SQLite DB file (e.g., results/hparam_search/storage/optuna_phase3_fine_v4.db)",
    )
    parser.add_argument(
        "--study-name", type=str, help="Study name (optional, will try to guess or list all)"
    )
    parser.add_argument("--top", type=int, default=10, help="Number of top trials to show")
    args = parser.parse_args()

    # Handle relative paths
    db_path = Path(args.db_path).resolve()
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)

    db_url = f"sqlite:///{db_path}"

    try:
        # List studies if not provided
        if not args.study_name:
            summaries = optuna.study.get_all_study_summaries(storage=db_url)
            if not summaries:
                print(f"No studies found in {db_url}")
                return

            print(f"Found {len(summaries)} studies:")
            for s in summaries:
                print(f"  - {s.study_name} (Trials: {s.n_trials})")

            # Pick the one with most trials or the first one
            if summaries:
                study_summary = max(summaries, key=lambda s: s.n_trials)
                study_name = study_summary.study_name
                print(f"\nSelecting study: {study_name}")
            else:
                return
        else:
            study_name = args.study_name

        study = optuna.load_study(study_name=study_name, storage=db_url)

        print(f"\nStudy: {study_name}")
        print(f"Total Trials: {len(study.trials)}")

        completed_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]
        print(f"Completed Trials: {len(completed_trials)}")

        if len(completed_trials) == 0:
            print("No completed trials yet.")
            return

        # Best trial
        try:
            best_trial = study.best_trial
            print(f"\nBest Trial (ID: {best_trial.number}):")
            print(f"  Value: {best_trial.value}")
            print("  Params:")
            for k, v in best_trial.params.items():
                print(f"    {k}: {v}")
        except ValueError:
            print("\nNo successful trials yet.")

        # Top N trials
        print(f"\nTop {args.top} Trials:")
        df = study.trials_dataframe()
        if not df.empty and "value" in df.columns:
            # Filter completed
            df_completed = df[df["state"] == "COMPLETE"].copy()
            if not df_completed.empty:
                df_completed.sort_values("value", ascending=False, inplace=True)

                # Select relevant columns
                base_cols = ["number", "value", "duration"]
                param_cols = [c for c in df.columns if c.startswith("params_")]
                cols = base_cols + param_cols

                # Print with pandas options for better visibility
                pd.set_option("display.max_rows", args.top)
                pd.set_option("display.max_columns", None)
                pd.set_option("display.width", 1000)
                pd.set_option("display.max_colwidth", 50)

                print(df_completed[cols].head(args.top).to_string(index=False))
            else:
                print("No completed trials.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
