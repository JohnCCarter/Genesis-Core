"""
Analyze feature importance from trained ML models.

Usage:
    python scripts/analyze_feature_importance.py --model results/models/tBTCUSD_1h_v3_adaptive_6m.json
    python scripts/analyze_feature_importance.py --model results/models/tBTCUSD_1h_v3_adaptive_6m.json --top-n 7
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_model(model_path: Path) -> dict:
    """Load Genesis-Core model JSON."""
    with open(model_path) as f:
        return json.load(f)


def extract_feature_importance(model: dict, model_type: str = "buy") -> pd.DataFrame:
    """
    Extract feature importance from logistic regression coefficients.

    For logistic regression, the absolute value of coefficients indicates
    feature importance (how much they affect the decision boundary).

    Args:
        model: Genesis-Core model dict
        model_type: "buy" or "sell"

    Returns:
        DataFrame with features and their importance scores
    """
    # Genesis-Core model format: {buy: {w: [...], b: ...}, sell: {w: [...], b: ...}, schema: [...]}
    coefficients = model[model_type]["w"]
    feature_names = model["schema"]

    # Absolute value of coefficients = importance
    importance = [abs(coef) for coef in coefficients]

    df = pd.DataFrame(
        {
            "feature": feature_names,
            "coefficient": coefficients,
            "importance": importance,
        }
    )

    # Sort by importance (descending)
    df = df.sort_values("importance", ascending=False).reset_index(drop=True)

    return df


def plot_feature_importance(
    buy_importance: pd.DataFrame,
    sell_importance: pd.DataFrame,
    output_path: Path,
    top_n: int = None,
):
    """
    Create visualization of feature importance.

    Args:
        buy_importance: Buy model feature importance
        sell_importance: Sell model feature importance
        output_path: Path to save plot
        top_n: Show only top N features (None = all)
    """
    if top_n:
        buy_importance = buy_importance.head(top_n)
        sell_importance = sell_importance.head(top_n)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Buy model
    colors_buy = ["green" if c > 0 else "red" for c in buy_importance["coefficient"]]
    ax1.barh(buy_importance["feature"], buy_importance["importance"], color=colors_buy, alpha=0.7)
    ax1.set_xlabel("Importance (|coefficient|)")
    ax1.set_title(f"Buy Model Feature Importance{' (Top ' + str(top_n) + ')' if top_n else ''}")
    ax1.invert_yaxis()
    ax1.grid(axis="x", alpha=0.3)

    # Sell model
    colors_sell = ["green" if c > 0 else "red" for c in sell_importance["coefficient"]]
    ax2.barh(
        sell_importance["feature"], sell_importance["importance"], color=colors_sell, alpha=0.7
    )
    ax2.set_xlabel("Importance (|coefficient|)")
    ax2.set_title(f"Sell Model Feature Importance{' (Top ' + str(top_n) + ')' if top_n else ''}")
    ax2.invert_yaxis()
    ax2.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"[PLOT] Saved to {output_path}")


def generate_report(
    buy_importance: pd.DataFrame,
    sell_importance: pd.DataFrame,
    model_path: Path,
    output_path: Path,
    top_n: int = None,
):
    """Generate text report with recommendations."""

    # Calculate average importance across both models
    combined = pd.merge(
        buy_importance[["feature", "importance"]].rename(columns={"importance": "buy_importance"}),
        sell_importance[["feature", "importance"]].rename(
            columns={"importance": "sell_importance"}
        ),
        on="feature",
    )
    combined["avg_importance"] = (combined["buy_importance"] + combined["sell_importance"]) / 2
    combined = combined.sort_values("avg_importance", ascending=False).reset_index(drop=True)

    report = []
    report.append("=" * 80)
    report.append("FEATURE IMPORTANCE ANALYSIS")
    report.append("=" * 80)
    report.append(f"Model: {model_path.name}")
    report.append(f"Total features: {len(combined)}")
    report.append("")

    # Combined importance
    report.append("## Combined Importance (Average of Buy & Sell)")
    report.append("")
    for idx, row in combined.iterrows():
        rank = idx + 1
        report.append(
            f"{rank:2d}. {row['feature']:20s} | "
            f"Avg: {row['avg_importance']:.4f} | "
            f"Buy: {row['buy_importance']:.4f} | "
            f"Sell: {row['sell_importance']:.4f}"
        )
    report.append("")

    # Recommendations
    report.append("=" * 80)
    report.append("RECOMMENDATIONS")
    report.append("=" * 80)
    report.append("")

    # Top features
    if top_n:
        top_features = combined.head(top_n)["feature"].tolist()
        report.append(f"### Top {top_n} Features (Keep):")
        for i, feat in enumerate(top_features, 1):
            report.append(f"  {i}. {feat}")
        report.append("")

        # Low importance features
        bottom_features = combined.tail(len(combined) - top_n)["feature"].tolist()
        if bottom_features:
            report.append("### Low Importance Features (Consider removing):")
            for i, feat in enumerate(bottom_features, 1):
                report.append(f"  {i}. {feat}")
            report.append("")

    # Statistical summary
    report.append("### Statistical Summary:")
    report.append(f"  Mean importance: {combined['avg_importance'].mean():.4f}")
    report.append(f"  Median importance: {combined['avg_importance'].median():.4f}")
    report.append(f"  Std deviation: {combined['avg_importance'].std():.4f}")
    report.append(f"  Min importance: {combined['avg_importance'].min():.4f}")
    report.append(f"  Max importance: {combined['avg_importance'].max():.4f}")
    report.append("")

    # Feature groups
    report.append("### Feature Groups:")
    report.append("")

    # Original features
    original = combined[combined["feature"].isin(["ema_delta_pct", "rsi"])]
    if not original.empty:
        report.append("  **Original Features (2):**")
        for _, row in original.iterrows():
            report.append(f"    - {row['feature']:20s} (importance: {row['avg_importance']:.4f})")
        report.append("")

    # Volatility features
    volatility = combined[combined["feature"].isin(["atr_pct", "bb_width", "bb_position"])]
    if not volatility.empty:
        report.append("  **Volatility Features (3):**")
        for _, row in volatility.iterrows():
            report.append(f"    - {row['feature']:20s} (importance: {row['avg_importance']:.4f})")
        report.append("")

    # Trend features
    trend = combined[combined["feature"].isin(["adx", "ema_slope", "price_vs_ema"])]
    if not trend.empty:
        report.append("  **Trend Features (3):**")
        for _, row in trend.iterrows():
            report.append(f"    - {row['feature']:20s} (importance: {row['avg_importance']:.4f})")
        report.append("")

    # Volume features
    volume = combined[combined["feature"].isin(["vol_change", "vol_trend", "obv_normalized"])]
    if not volume.empty:
        report.append("  **Volume Features (3):**")
        for _, row in volume.iterrows():
            report.append(f"    - {row['feature']:20s} (importance: {row['avg_importance']:.4f})")
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

    return combined


def main():
    parser = argparse.ArgumentParser(description="Analyze feature importance from trained models")
    parser.add_argument("--model", type=str, required=True, help="Path to model JSON file")
    parser.add_argument(
        "--top-n", type=int, default=None, help="Show only top N features (default: all)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="results/feature_importance", help="Output directory"
    )

    args = parser.parse_args()

    # Load model
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        sys.exit(1)

    print(f"[LOAD] Loading model: {model_path}")
    model = load_model(model_path)

    # Extract feature importance
    print("[ANALYZE] Extracting feature importance...")
    buy_importance = extract_feature_importance(model, "buy")
    sell_importance = extract_feature_importance(model, "sell")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate outputs
    model_name = model_path.stem

    # Plot
    plot_path = output_dir / f"{model_name}_feature_importance.png"
    plot_feature_importance(buy_importance, sell_importance, plot_path, args.top_n)

    # Report
    report_path = output_dir / f"{model_name}_feature_importance.txt"
    combined = generate_report(buy_importance, sell_importance, model_path, report_path, args.top_n)

    # CSV
    csv_path = output_dir / f"{model_name}_feature_importance.csv"
    combined.to_csv(csv_path, index=False)
    print(f"[CSV] Saved to {csv_path}")

    print("\n[SUCCESS] Feature importance analysis complete!")


if __name__ == "__main__":
    main()
