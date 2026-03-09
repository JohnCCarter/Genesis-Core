import glob
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid")

# Configuration
RUN_ID = "run_20251215_092751"
PROJECT_ROOT = Path("c:/Users/fa06662/HCP/Skrivbord/Genesis-Core")
RESULTS_DIR = PROJECT_ROOT / "results" / "hparam_search" / RUN_ID
OUTPUT_DIR = PROJECT_ROOT / "docs" / "analysis"

print(f"Analyzing run: {RUN_ID}")
print(f"Directory: {RESULTS_DIR}")

# Load Data
data = []
json_files = glob.glob(str(RESULTS_DIR / "*.json"))

for f in json_files:
    if "optimization_results" in f or "summary" in f:
        continue

    try:
        with open(f) as file:
            content = json.load(file)

            # Extract flat metrics
            metrics = content.get("metrics", {})
            row = {
                "trial_id": content.get("trial_id"),
                "total_trades": metrics.get("total_trades", 0),
                "total_return": metrics.get("total_return", 0.0),
                "profit_factor": metrics.get("profit_factor", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
                "win_rate": metrics.get("win_rate", 0.0),
            }

            # Extract parameters (flattening nested structure)
            params = content.get("parameters", {})

            # Entry Confidence
            zones = params.get("signal_adaptation", {}).get("zones", {})
            row["entry_conf_low"] = zones.get("low", {}).get("entry")
            row["entry_conf_mid"] = zones.get("mid", {}).get("entry")
            row["entry_conf_high"] = zones.get("high", {}).get("entry")

            # Min Edge
            row["min_edge"] = params.get("thresholds", {}).get("min_edge")

            # Risk
            row["risk_p1"] = params.get("risk", {}).get("risk_map", {}).get("p1")

            data.append(row)
    except Exception as e:
        print(f"Error loading {f}: {e}")

df = pd.DataFrame(data)
print(f"Loaded {len(df)} trials")

if not df.empty:
    # Filter for trials with trades
    df_trades = df[df["total_trades"] > 0].copy()
    print(f"Trials with trades: {len(df_trades)}")

    if not df_trades.empty:
        print("\nSummary Statistics:")
        print(df_trades.describe())

        # Visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Profit Factor vs Total Trades
        sns.scatterplot(
            data=df_trades, x="total_trades", y="profit_factor", hue="total_return", ax=axes[0, 0]
        )
        axes[0, 0].set_title("Profit Factor vs Total Trades")
        axes[0, 0].axhline(1.0, color="red", linestyle="--")

        # Return vs Entry Confidence (Low)
        sns.scatterplot(
            data=df_trades, x="entry_conf_low", y="total_return", hue="profit_factor", ax=axes[0, 1]
        )
        axes[0, 1].set_title("Return vs Entry Conf (Low)")

        # Return vs Min Edge
        sns.scatterplot(
            data=df_trades, x="min_edge", y="total_return", hue="profit_factor", ax=axes[1, 0]
        )
        axes[1, 0].set_title("Return vs Min Edge")

        # Win Rate vs Profit Factor
        sns.scatterplot(
            data=df_trades, x="win_rate", y="profit_factor", hue="total_return", ax=axes[1, 1]
        )
        axes[1, 1].set_title("Win Rate vs Profit Factor")

        plt.tight_layout()
        output_path = OUTPUT_DIR / "optimization_analysis.png"
        plt.savefig(output_path)
        print(f"\nPlot saved to {output_path}")
    else:
        print("No trials with trades found.")
else:
    print("No data loaded.")
