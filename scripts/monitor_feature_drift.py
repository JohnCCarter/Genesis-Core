"""Feature drift monitoring using PSI and K-S tests."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from scipy.stats import ks_2samp

from core.utils.data_loader import load_features


def calculate_psi(expected, actual, bins=10):
    """Calculate Population Stability Index."""
    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]

    if len(expected) == 0 or len(actual) == 0:
        return float("inf")

    expected_percents, bin_edges = np.histogram(expected, bins=bins)
    expected_percents = expected_percents / len(expected)

    actual_percents, _ = np.histogram(actual, bins=bin_edges)
    actual_percents = actual_percents / len(actual)

    epsilon = 1e-6
    expected_percents = np.maximum(expected_percents, epsilon)
    actual_percents = np.maximum(actual_percents, epsilon)

    psi = np.sum(
        (actual_percents - expected_percents) * np.log(actual_percents / expected_percents)
    )

    return float(psi)


def ks_drift_test(training_dist, production_dist, alpha=0.05):
    """Kolmogorov-Smirnov test for distribution drift."""
    training_dist = training_dist[~np.isnan(training_dist)]
    production_dist = production_dist[~np.isnan(production_dist)]

    if len(training_dist) == 0 or len(production_dist) == 0:
        return {"statistic": float("inf"), "p_value": 0.0, "drifted": True}

    statistic, p_value = ks_2samp(training_dist, production_dist)

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "drifted": bool(p_value < alpha),
        "interpretation": "DRIFT" if p_value < alpha else "NO_DRIFT",
    }


def monitor_all_features(training_features, production_features, psi_bins=10, ks_alpha=0.05):
    """Monitor drift for all features."""
    feature_cols = [c for c in training_features.columns if c != "timestamp"]

    psi_results = {}
    ks_results = {}

    for feature_name in feature_cols:
        psi = calculate_psi(
            training_features[feature_name].values,
            production_features[feature_name].values,
            bins=psi_bins,
        )

        psi_status = "OK" if psi < 0.1 else ("WARNING" if psi < 0.25 else "CRITICAL")
        psi_results[feature_name] = {"psi": psi, "status": psi_status}

        ks_result = ks_drift_test(
            training_features[feature_name].values,
            production_features[feature_name].values,
            alpha=ks_alpha,
        )

        ks_results[feature_name] = ks_result

    return {"psi": psi_results, "ks_test": ks_results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--training-start", type=int, required=True)
    parser.add_argument("--training-end", type=int, required=True)
    parser.add_argument("--production-start", type=int, required=True)
    parser.add_argument("--production-end", type=int, required=True)
    parser.add_argument("--output", default="results/drift_monitoring")

    args = parser.parse_args()

    features_df = load_features(args.symbol, args.timeframe)

    training_features = features_df.iloc[args.training_start : args.training_end]
    production_features = features_df.iloc[args.production_start : args.production_end]

    drift_results = monitor_all_features(training_features, production_features)

    critical = [f for f, r in drift_results["psi"].items() if r["status"] == "CRITICAL"]

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{args.symbol}_{args.timeframe}_drift_monitoring.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "symbol": args.symbol,
                "psi_results": drift_results["psi"],
                "ks_results": drift_results["ks_test"],
                "critical_features": critical,
            },
            f,
            indent=2,
        )

    print(f"Saved: {output_path}")
    sys.exit(0 if not critical else 1)


if __name__ == "__main__":
    main()
