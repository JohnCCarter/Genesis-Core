"""
False Discovery Rate (FDR) correction for multiple testing.

When testing many features (e.g., 50 candidates), some will appear
significant by pure chance! FDR correction adjusts p-values to account
for multiple comparisons.

Methods:
- Benjamini-Hochberg: Less conservative, controls FDR
- Bonferroni: Very conservative, controls FWER (Family-Wise Error Rate)

Usage:
    python scripts/fdr_correction.py \
      --results results/ic_metrics/tBTCUSD_1h_feature_ic.json \
      --method benjamini-hochberg \
      --alpha 0.05
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def benjamini_hochberg(p_values, alpha=0.05):
    """
    Benjamini-Hochberg FDR correction.

    Controls False Discovery Rate - the expected proportion of
    false positives among all rejected hypotheses.

    Args:
        p_values: Array of p-values
        alpha: Target FDR level (default 0.05)

    Returns:
        Array of booleans (True = reject null hypothesis)
        Array of adjusted p-values
    """
    n = len(p_values)

    # Sort p-values
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # B-H critical values: (i/n) * alpha
    bh_critical = np.arange(1, n + 1) / n * alpha

    # Find largest i where p_i <= (i/n)*alpha
    rejections = sorted_p <= bh_critical

    if rejections.any():
        max_rejection_idx = np.where(rejections)[0][-1]
    else:
        max_rejection_idx = -1

    # Reject all hypotheses up to max_rejection_idx
    reject = np.zeros(n, dtype=bool)
    if max_rejection_idx >= 0:
        reject[sorted_indices[: max_rejection_idx + 1]] = True

    # Adjusted p-values (step-up)
    adjusted_p = np.minimum.accumulate(sorted_p[::-1] * n / np.arange(n, 0, -1))[::-1]
    adjusted_p = np.minimum(adjusted_p, 1.0)

    # Unsort
    unsorted_adjusted_p = np.zeros(n)
    unsorted_adjusted_p[sorted_indices] = adjusted_p

    return reject, unsorted_adjusted_p


def bonferroni(p_values, alpha=0.05):
    """
    Bonferroni correction (conservative).

    Controls Family-Wise Error Rate (FWER) - probability of
    making at least one Type I error.

    Args:
        p_values: Array of p-values
        alpha: Significance level (default 0.05)

    Returns:
        Array of booleans (True = reject null hypothesis)
        Array of adjusted p-values
    """
    n = len(p_values)

    # Adjusted p-values: p * n
    adjusted_p = np.minimum(p_values * n, 1.0)

    # Reject if adjusted p < alpha
    reject = adjusted_p < alpha

    return reject, adjusted_p


def holm_bonferroni(p_values, alpha=0.05):
    """
    Holm-Bonferroni correction (less conservative than Bonferroni).

    Sequential rejection method.

    Args:
        p_values: Array of p-values
        alpha: Significance level (default 0.05)

    Returns:
        Array of booleans (True = reject null hypothesis)
        Array of adjusted p-values
    """
    n = len(p_values)

    # Sort p-values
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # Holm critical values: alpha / (n - i + 1)
    holm_critical = alpha / (n - np.arange(n))

    # Reject while p_i <= alpha / (n - i + 1)
    rejections = sorted_p <= holm_critical

    if rejections.any():
        max_rejection_idx = np.where(~rejections)[0][0] - 1 if not rejections.all() else n - 1
    else:
        max_rejection_idx = -1

    # Reject all up to first non-rejection
    reject = np.zeros(n, dtype=bool)
    if max_rejection_idx >= 0:
        reject[sorted_indices[: max_rejection_idx + 1]] = True

    # Adjusted p-values (step-down)
    adjusted_p = np.maximum.accumulate(sorted_p * (n - np.arange(n)))
    adjusted_p = np.minimum(adjusted_p, 1.0)

    # Unsort
    unsorted_adjusted_p = np.zeros(n)
    unsorted_adjusted_p[sorted_indices] = adjusted_p

    return reject, unsorted_adjusted_p


def apply_fdr_correction(results_file, method="benjamini-hochberg", alpha=0.05):
    """
    Apply FDR correction to feature testing results.

    Args:
        results_file: Path to IC or feature analysis JSON
        method: 'benjamini-hochberg', 'bonferroni', or 'holm-bonferroni'
        alpha: Significance level

    Returns:
        DataFrame with corrected results
    """
    with open(results_file) as f:
        results = json.load(f)

    # Extract p-values
    features = []
    p_values = []
    original_stats = []

    for feature, data in results.items():
        # Handle different result formats
        if "10bar" in data:
            # IC metrics format
            p_val = data["10bar"]["overall"]["p_value"]
            ic = data["10bar"]["overall"]["ic"]
            t_stat = data["10bar"]["overall"]["t_stat"]
            original_stats.append({"ic": ic, "t_stat": t_stat})
        elif "spread" in data:
            # Quintile format
            p_val = data["spread"]["statistical_significance"]["p_value"]
            spread = data["spread"]["q5_minus_q1"]
            original_stats.append({"spread": spread})
        else:
            continue

        features.append(feature)
        p_values.append(p_val)

    p_values = np.array(p_values)

    # Apply correction
    if method == "benjamini-hochberg":
        reject, adjusted_p = benjamini_hochberg(p_values, alpha)
    elif method == "bonferroni":
        reject, adjusted_p = bonferroni(p_values, alpha)
    elif method == "holm-bonferroni":
        reject, adjusted_p = holm_bonferroni(p_values, alpha)
    else:
        raise ValueError(f"Unknown method: {method}")

    # Create results DataFrame
    df = pd.DataFrame(
        {
            "feature": features,
            "p_value": p_values,
            "adjusted_p": adjusted_p,
            "reject_null": reject,
            "significant_after_correction": reject,
        }
    )

    # Add original stats
    for i, stats in enumerate(original_stats):
        for key, value in stats.items():
            df.loc[i, key] = value

    # Sort by adjusted p-value
    df = df.sort_values("adjusted_p")

    return df


def main():
    parser = argparse.ArgumentParser(description="Apply FDR correction to feature testing results")
    parser.add_argument(
        "--results", required=True, help="Path to feature IC or quintile results JSON"
    )
    parser.add_argument(
        "--method",
        choices=["benjamini-hochberg", "bonferroni", "holm-bonferroni"],
        default="benjamini-hochberg",
        help="FDR correction method",
    )
    parser.add_argument(
        "--alpha", type=float, default=0.05, help="Significance level (default: 0.05)"
    )
    parser.add_argument("--output", default="results/fdr_correction", help="Output directory")

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("FALSE DISCOVERY RATE (FDR) CORRECTION")
    print("=" * 80)
    print(f"Method: {args.method}")
    print(f"Alpha: {args.alpha}")

    # Apply correction
    df = apply_fdr_correction(Path(args.results), method=args.method, alpha=args.alpha)

    print(f"\n[CORRECTION] Tested {len(df)} features")

    n_significant_before = (df["p_value"] < args.alpha).sum()
    n_significant_after = df["significant_after_correction"].sum()

    print("\nSignificant features:")
    print(f"  Before correction: {n_significant_before}/{len(df)}")
    print(f"  After correction:  {n_significant_after}/{len(df)}")
    print(f"  False discoveries prevented: {n_significant_before - n_significant_after}")

    # Show results
    print("\n" + "=" * 80)
    print("FDR-CORRECTED RESULTS")
    print("=" * 80)

    print(f"\n{'Feature':<25s} {'p-value':>10s} {'Adjusted p':>12s} {'Significant':>12s}")
    print("-" * 80)

    for _, row in df.iterrows():
        feature = row["feature"][:24]
        p_val = row["p_value"]
        adj_p = row["adjusted_p"]
        sig = "[YES]" if row["significant_after_correction"] else "[NO]"

        print(f"{feature:<25s} {p_val:>10.4f} {adj_p:>12.4f} {sig:>12s}")

    # Assessment
    print("\n" + "=" * 80)
    print("ASSESSMENT")
    print("=" * 80)

    if n_significant_after > 0:
        print(f"\n[+] {n_significant_after} features remain significant after FDR correction")
        print("\nSignificant features:")
        for _, row in df[df["significant_after_correction"]].iterrows():
            feature = row["feature"]
            adj_p = row["adjusted_p"]
            print(f"  - {feature} (adjusted p={adj_p:.4f})")
    else:
        print("\n[-] NO features remain significant after FDR correction!")
        print("\n    This suggests:")
        print("      1. Features have no true predictive power")
        print("      2. Any apparent significance was due to chance")
        print("      3. Model should NOT be deployed")
        print("\n    Recommendation: Add new features and retest")

    # Save results
    results_name = Path(args.results).stem
    output_path = output_dir / f"{results_name}_fdr_corrected.csv"
    df.to_csv(output_path, index=False)

    output_json = output_dir / f"{results_name}_fdr_corrected.json"
    df.to_json(output_json, orient="records", indent=2)

    print(f"\n[SAVED] CSV: {output_path}")
    print(f"[SAVED] JSON: {output_json}")

    print("\n" + "=" * 80)
    print("[SUCCESS] FDR correction complete!")
    print("=" * 80)

    # Exit code based on result
    sys.exit(0 if n_significant_after > 0 else 1)


if __name__ == "__main__":
    main()
