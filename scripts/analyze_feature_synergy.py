"""
Analyze feature correlation, redundancy, and synergistic effects.

Usage:
    python scripts/analyze_feature_synergy.py --symbol tBTCUSD --timeframe 1h
    python scripts/analyze_feature_synergy.py --symbol tBTCUSD --timeframe 1h --model results/models/tBTCUSD_1h_v3_adaptive_6m.json
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


def load_features_and_labels(symbol: str, timeframe: str) -> tuple[pd.DataFrame, list]:
    """Load preprocessed features and generate labels for analysis."""
    features_path = Path("data/features") / f"{symbol}_{timeframe}_features.parquet"
    candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"

    if not features_path.exists():
        raise FileNotFoundError(f"Features not found: {features_path}")
    if not candles_path.exists():
        raise FileNotFoundError(f"Candles not found: {candles_path}")

    from core.utils.data_loader import load_features

    features_df = load_features(symbol, timeframe)
    candles_df = pd.read_parquet(candles_path)

    # Simple forward-looking labels for analysis
    close_prices = candles_df["close"].tolist()
    labels = []
    for i in range(len(close_prices) - 10):
        future_price = close_prices[i + 10]
        current_price = close_prices[i]
        if current_price > 0:
            pct_change = 100 * (future_price - current_price) / current_price
            labels.append(1 if pct_change > 0.2 else 0)
        else:
            labels.append(None)

    # Align
    labels = labels + [None] * 10
    return features_df, labels


def analyze_correlation(features_df: pd.DataFrame, output_dir: Path, symbol: str, timeframe: str):
    """Analyze feature correlation matrix."""
    # Remove timestamp column
    feature_cols = [col for col in features_df.columns if col != "timestamp"]
    X = features_df[feature_cols]

    # Calculate correlation matrix
    corr_matrix = X.corr()

    # Plot heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
    )
    plt.title(f"Feature Correlation Matrix - {symbol} {timeframe}")
    plt.tight_layout()

    plot_path = output_dir / f"{symbol}_{timeframe}_correlation_matrix.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"[PLOT] Correlation matrix saved to {plot_path}")
    plt.close()

    # Find highly correlated pairs (redundant features)
    redundant_pairs = []
    for i in range(len(corr_matrix)):
        for j in range(i + 1, len(corr_matrix)):
            corr_val = abs(corr_matrix.iloc[i, j])
            if corr_val > 0.7:  # High correlation threshold
                redundant_pairs.append(
                    {
                        "feature1": corr_matrix.index[i],
                        "feature2": corr_matrix.columns[j],
                        "correlation": corr_matrix.iloc[i, j],
                    }
                )

    return corr_matrix, redundant_pairs


def analyze_individual_performance(
    features_df: pd.DataFrame, labels: list, output_dir: Path
) -> pd.DataFrame:
    """Test each feature individually to measure standalone predictive power."""
    import numpy as np

    feature_cols = [col for col in features_df.columns if col != "timestamp"]

    # Remove None labels and align
    valid_indices = [
        i for i, label in enumerate(labels) if label is not None and i < len(features_df)
    ]
    valid_labels = [labels[i] for i in valid_indices]
    valid_features = features_df.iloc[valid_indices]

    # Remove NaN values
    X = valid_features[feature_cols].values
    y = np.array(valid_labels)

    nan_mask = np.isnan(X).any(axis=1)
    X = X[~nan_mask]
    y = y[~nan_mask]

    results = []

    for i, feat_name in enumerate(feature_cols):
        # Train simple model with only this feature
        X_single = X[:, i].reshape(-1, 1)

        # Skip if all same value or all NaN
        if len(set(X_single.flatten())) < 2:
            results.append({"feature": feat_name, "auc": 0.5, "status": "constant"})
            continue

        try:
            model = LogisticRegression(max_iter=1000, random_state=42)
            model.fit(X_single, y)
            y_pred_proba = model.predict_proba(X_single)[:, 1]
            auc = roc_auc_score(y, y_pred_proba)
            results.append({"feature": feat_name, "auc": auc, "status": "ok"})
        except Exception as e:
            results.append({"feature": feat_name, "auc": 0.5, "status": f"error: {e}"})

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("auc", ascending=False).reset_index(drop=True)

    return results_df


def analyze_feature_pairs(
    features_df: pd.DataFrame, labels: list, top_features: list, output_dir: Path
) -> pd.DataFrame:
    """Test feature pairs to find synergistic combinations."""
    from itertools import combinations

    import numpy as np

    feature_cols = [col for col in features_df.columns if col != "timestamp"]

    # Remove None labels and align
    valid_indices = [
        i for i, label in enumerate(labels) if label is not None and i < len(features_df)
    ]
    valid_labels = [labels[i] for i in valid_indices]
    valid_features = features_df.iloc[valid_indices]

    # Remove NaN values
    X = valid_features[feature_cols].values
    y = np.array(valid_labels)

    nan_mask = np.isnan(X).any(axis=1)
    X = X[~nan_mask]
    y = y[~nan_mask]

    # Test pairs of top features only (to reduce computation)
    top_indices = [feature_cols.index(f) for f in top_features if f in feature_cols]

    pair_results = []

    print(f"[ANALYZE] Testing {len(list(combinations(top_indices, 2)))} feature pairs...")

    for idx1, idx2 in combinations(top_indices, 2):
        feat1 = feature_cols[idx1]
        feat2 = feature_cols[idx2]

        X_pair = X[:, [idx1, idx2]]

        try:
            model = LogisticRegression(max_iter=1000, random_state=42)
            model.fit(X_pair, y)
            y_pred_proba = model.predict_proba(X_pair)[:, 1]
            auc = roc_auc_score(y, y_pred_proba)

            pair_results.append({"feature1": feat1, "feature2": feat2, "auc": auc})
        except Exception:
            pair_results.append({"feature1": feat1, "feature2": feat2, "auc": 0.5})

    pairs_df = pd.DataFrame(pair_results)
    pairs_df = pairs_df.sort_values("auc", ascending=False).reset_index(drop=True)

    return pairs_df


def generate_synergy_report(
    corr_matrix: pd.DataFrame,
    redundant_pairs: list,
    individual_performance: pd.DataFrame,
    pair_performance: pd.DataFrame,
    output_path: Path,
    model_path: Path = None,
):
    """Generate comprehensive synergy analysis report."""
    report = []
    report.append("=" * 80)
    report.append("FEATURE SYNERGY & CORRELATION ANALYSIS")
    report.append("=" * 80)
    if model_path:
        report.append(f"Model: {model_path.name}")
    report.append(f"Total features: {len(corr_matrix)}")
    report.append("")

    # Individual performance
    report.append("## Individual Feature Performance (AUC when used alone)")
    report.append("")
    for idx, row in individual_performance.iterrows():
        rank = idx + 1
        report.append(f"{rank:2d}. {row['feature']:20s} | AUC: {row['auc']:.4f}")
    report.append("")

    # Redundant pairs (high correlation)
    report.append("=" * 80)
    report.append("REDUNDANT FEATURES (High Correlation > 0.7)")
    report.append("=" * 80)
    report.append("")

    if redundant_pairs:
        for pair in redundant_pairs:
            report.append(
                f"  - {pair['feature1']:20s} <-> {pair['feature2']:20s} | "
                f"Correlation: {pair['correlation']:+.3f}"
            )
        report.append("")
        report.append(
            "**Recommendation:** Consider removing one from each pair to reduce redundancy."
        )
    else:
        report.append("  No highly correlated feature pairs found (all < 0.7)")
    report.append("")

    # Best synergistic pairs
    report.append("=" * 80)
    report.append("SYNERGISTIC FEATURE PAIRS (Top 10 combinations)")
    report.append("=" * 80)
    report.append("")

    for idx, row in pair_performance.head(10).iterrows():
        rank = idx + 1
        report.append(
            f"{rank:2d}. {row['feature1']:20s} + {row['feature2']:20s} | AUC: {row['auc']:.4f}"
        )
    report.append("")

    # Compare individual vs pair performance
    report.append("=" * 80)
    report.append("SYNERGY ANALYSIS (Pair AUC vs Individual AUC)")
    report.append("=" * 80)
    report.append("")

    for _idx, row in pair_performance.head(10).iterrows():
        feat1_auc = individual_performance[individual_performance["feature"] == row["feature1"]][
            "auc"
        ].values[0]
        feat2_auc = individual_performance[individual_performance["feature"] == row["feature2"]][
            "auc"
        ].values[0]
        max_individual = max(feat1_auc, feat2_auc)
        synergy = row["auc"] - max_individual

        report.append(
            f"  {row['feature1']:15s} + {row['feature2']:15s} | "
            f"Pair: {row['auc']:.4f} | "
            f"Best solo: {max_individual:.4f} | "
            f"Synergy: {synergy:+.4f}"
        )
    report.append("")

    # Recommendations
    report.append("=" * 80)
    report.append("RECOMMENDATIONS")
    report.append("=" * 80)
    report.append("")

    report.append("### 1. Remove Redundant Features:")
    if redundant_pairs:
        for pair in redundant_pairs:
            # Choose which to remove based on individual performance
            feat1_auc = individual_performance[
                individual_performance["feature"] == pair["feature1"]
            ]["auc"].values[0]
            feat2_auc = individual_performance[
                individual_performance["feature"] == pair["feature2"]
            ]["auc"].values[0]

            if feat1_auc > feat2_auc:
                report.append(f"  - Remove {pair['feature2']} (keep {pair['feature1']})")
            else:
                report.append(f"  - Remove {pair['feature1']} (keep {pair['feature2']})")
    else:
        report.append("  - No redundant features found!")
    report.append("")

    report.append("### 2. Prioritize Synergistic Pairs:")
    report.append("  - Build features around top synergistic combinations")
    top_3_pairs = pair_performance.head(3)
    for _idx, row in top_3_pairs.iterrows():
        report.append(f"  - Keep {row['feature1']} + {row['feature2']} (AUC: {row['auc']:.4f})")
    report.append("")

    report.append("### 3. Weak Standalone Features:")
    weak_features = individual_performance[individual_performance["auc"] < 0.52]
    if not weak_features.empty:
        report.append("  - Consider removing features with AUC < 0.52 (barely better than random):")
        for _, row in weak_features.iterrows():
            report.append(f"    - {row['feature']} (AUC: {row['auc']:.4f})")
    else:
        report.append("  - All features have reasonable standalone performance!")
    report.append("")

    report.append("=" * 80)
    report.append("")

    # Save report
    report_text = "\n".join(report)
    with open(output_path, "w") as f:
        f.write(report_text)

    print(f"[REPORT] Saved to {output_path}")

    # Print to console
    print("\n" + report_text)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze feature correlation and synergistic effects"
    )
    parser.add_argument("--symbol", type=str, required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe (e.g., 1h)")
    parser.add_argument(
        "--model", type=str, default=None, help="Optional: Path to model JSON for context"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/feature_synergy",
        help="Output directory",
    )
    parser.add_argument(
        "--top-n", type=int, default=7, help="Number of top features to analyze pairs for"
    )

    args = parser.parse_args()

    # Load model if provided
    if args.model:
        model_path = Path(args.model)
        if model_path.exists():
            print(f"[LOAD] Loading model: {model_path}")
            with open(model_path) as f:
                json.load(f)
        else:
            print(f"[WARN] Model not found: {model_path}")

    # Load features and labels
    print(f"[LOAD] Loading features for {args.symbol} {args.timeframe}")
    features_df, labels = load_features_and_labels(args.symbol, args.timeframe)

    feature_cols = [col for col in features_df.columns if col != "timestamp"]
    print(f"[DATA] Loaded {len(features_df)} samples with {len(feature_cols)} features")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Correlation analysis
    print("[ANALYZE] Computing feature correlation matrix...")
    corr_matrix, redundant_pairs = analyze_correlation(
        features_df, output_dir, args.symbol, args.timeframe
    )

    # 2. Individual performance
    print("[ANALYZE] Testing individual feature performance...")
    individual_performance = analyze_individual_performance(features_df, labels, output_dir)

    # 3. Get top features for pair analysis
    top_features = individual_performance.head(args.top_n)["feature"].tolist()
    print(f"[ANALYZE] Top {args.top_n} features for pair analysis: {top_features}")

    # 4. Pair analysis
    pair_performance = analyze_feature_pairs(features_df, labels, top_features, output_dir)

    # 5. Generate report
    report_path = output_dir / f"{args.symbol}_{args.timeframe}_synergy_analysis.txt"
    model_path = Path(args.model) if args.model else None
    generate_synergy_report(
        corr_matrix,
        redundant_pairs,
        individual_performance,
        pair_performance,
        report_path,
        model_path,
    )

    # Save CSVs
    csv_corr = output_dir / f"{args.symbol}_{args.timeframe}_correlation.csv"
    corr_matrix.to_csv(csv_corr)
    print(f"[CSV] Correlation matrix saved to {csv_corr}")

    csv_individual = output_dir / f"{args.symbol}_{args.timeframe}_individual_performance.csv"
    individual_performance.to_csv(csv_individual, index=False)
    print(f"[CSV] Individual performance saved to {csv_individual}")

    csv_pairs = output_dir / f"{args.symbol}_{args.timeframe}_pair_performance.csv"
    pair_performance.to_csv(csv_pairs, index=False)
    print(f"[CSV] Pair performance saved to {csv_pairs}")

    print("\n[SUCCESS] Feature synergy analysis complete!")


if __name__ == "__main__":
    main()
