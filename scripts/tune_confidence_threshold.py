"""
Confidence threshold (τ) sweep for optimal risk-adjusted performance.

Evaluates multiple confidence thresholds τ ∈ [0.50, 0.75] to find
the sweet spot where:
- Higher τ = fewer trades
- Better Profit Factor (PF)
- Better Sharpe Ratio

Metrics:
- # Trades (total accepted trades)
- Expectancy (avg return per trade)
- Profit Factor (sum(wins) / sum(losses))
- Sharpe Ratio (mean / std of returns)
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_model(model_path: str) -> dict:
    """Load trained model."""
    with open(model_path, encoding="utf-8") as f:
        return json.load(f)


def load_features(symbol: str, timeframe: str) -> pd.DataFrame:
    """Load features."""
    from core.utils.data_loader import load_features as load_features_base

    features_df = load_features_base(symbol, timeframe)

    # Remove timestamp
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    features_df = features_df[numeric_cols]

    return features_df


def calculate_probabilities(X: np.ndarray, model: dict, side: str) -> np.ndarray:
    """
    Calculate probabilities using logistic regression formula.

    P(y=1) = 1 / (1 + exp(-z))
    where z = w0 + w1*x1 + w2*x2 + ... + wn*xn
    """
    weights = np.array(model[side]["w"])
    intercept = model[side]["b"]

    # Linear combination
    z = X @ weights + intercept

    # Logistic sigmoid
    proba = 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    return proba


def load_future_returns(symbol: str, timeframe: str, horizon: int = 36) -> np.ndarray:
    """
    Load candles and calculate future returns for horizon bars ahead.

    Returns:
        Array of returns (close[i+H] - close[i]) / close[i]
    """
    candles_path = Path(f"data/candles/{symbol}_{timeframe}.parquet")
    candles_df = pd.read_parquet(candles_path)

    close = candles_df["close"].values

    # Calculate forward returns
    future_returns = np.full(len(close), np.nan)
    for i in range(len(close) - horizon):
        future_returns[i] = (close[i + horizon] - close[i]) / close[i]

    return future_returns


def evaluate_threshold(
    tau: float,
    proba_buy: np.ndarray,
    proba_sell: np.ndarray,
    future_returns: np.ndarray,
) -> dict:
    """
    Evaluate performance at a specific confidence threshold.

    Strategy:
    - If P(buy) > τ and P(buy) > P(sell): LONG
    - If P(sell) > τ and P(sell) > P(buy): SHORT (inverted to LONG by negating return)
    - Else: NO TRADE

    Returns:
        dict with metrics (n_trades, expectancy, sharpe, profit_factor)
    """
    trades = []

    for i in range(len(proba_buy)):
        if np.isnan(future_returns[i]):
            continue

        p_buy = proba_buy[i]
        p_sell = proba_sell[i]

        # Long signal
        if p_buy > tau and p_buy > p_sell:
            trades.append(future_returns[i])
        # Short signal (convert to long return)
        elif p_sell > tau and p_sell > p_buy:
            trades.append(-future_returns[i])

    if len(trades) == 0:
        return {
            "n_trades": 0,
            "expectancy": 0.0,
            "sharpe": 0.0,
            "profit_factor": 0.0,
        }

    trades = np.array(trades)

    # Expectancy (mean return per trade)
    expectancy = np.mean(trades)

    # Sharpe Ratio
    sharpe = expectancy / (np.std(trades) + 1e-9)

    # Profit Factor (sum of wins / sum of losses)
    wins = trades[trades > 0]
    losses = trades[trades < 0]

    sum_wins = np.sum(wins) if len(wins) > 0 else 0.0
    sum_losses = np.abs(np.sum(losses)) if len(losses) > 0 else 1e-9
    profit_factor = sum_wins / sum_losses

    return {
        "n_trades": len(trades),
        "expectancy": expectancy,
        "sharpe": sharpe,
        "profit_factor": profit_factor,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Confidence threshold sweep for optimal risk-adjusted performance"
    )
    parser.add_argument("--model", type=str, required=True, help="Path to model JSON")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe (e.g., 1h)")
    parser.add_argument("--horizon", type=int, default=36, help="Holding period (bars)")
    parser.add_argument("--tau-min", type=float, default=0.50, help="Min confidence threshold")
    parser.add_argument("--tau-max", type=float, default=0.75, help="Max confidence threshold")
    parser.add_argument("--tau-step", type=float, default=0.01, help="Step size for τ")
    parser.add_argument("--output", type=str, default="results/confidence_sweep.csv")

    args = parser.parse_args()

    print(f"[LOAD] Loading model from {args.model}")
    model = load_model(args.model)

    print(f"[LOAD] Loading features for {args.symbol} {args.timeframe}")
    features_df = load_features(args.symbol, args.timeframe)

    # Ensure features match model schema
    model_features = model["schema"]
    X = features_df[model_features].values

    print("[COMPUTE] Calculating probabilities...")
    proba_buy = calculate_probabilities(X, model, "buy")
    proba_sell = calculate_probabilities(X, model, "sell")

    print(f"[LOAD] Loading future returns (H={args.horizon} bars)")
    future_returns = load_future_returns(args.symbol, args.timeframe, args.horizon)

    # Align arrays (remove NaN returns)
    valid_mask = ~np.isnan(future_returns)
    proba_buy = proba_buy[valid_mask]
    proba_sell = proba_sell[valid_mask]
    future_returns = future_returns[valid_mask]

    print(f"\n[SWEEP] Testing tau in [{args.tau_min:.2f}, {args.tau_max:.2f}]")

    tau_values = np.arange(args.tau_min, args.tau_max + args.tau_step, args.tau_step)
    results = []

    for tau in tau_values:
        metrics = evaluate_threshold(tau, proba_buy, proba_sell, future_returns)
        results.append({"tau": tau, **metrics})

        if tau in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]:
            print(
                f"  tau={tau:.2f}: "
                f"Trades={metrics['n_trades']:4d}, "
                f"Expectancy={metrics['expectancy']*100:+6.3f}%, "
                f"Sharpe={metrics['sharpe']:6.3f}, "
                f"PF={metrics['profit_factor']:6.3f}"
            )

    # Save results
    results_df = pd.DataFrame(results)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Results saved to {output_path}")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Expectancy vs tau
    axes[0, 0].plot(results_df["tau"], results_df["expectancy"] * 100, linewidth=2)
    axes[0, 0].axhline(0, color="red", linestyle="--", linewidth=1, alpha=0.5)
    axes[0, 0].set_title("Expectancy vs Confidence Threshold", fontsize=12, weight="bold")
    axes[0, 0].set_xlabel("tau")
    axes[0, 0].set_ylabel("Expectancy (%)")
    axes[0, 0].grid(True, alpha=0.3)

    # 2. # Trades vs tau
    axes[0, 1].plot(results_df["tau"], results_df["n_trades"], linewidth=2, color="orange")
    axes[0, 1].set_title("Trade Count vs Confidence Threshold", fontsize=12, weight="bold")
    axes[0, 1].set_xlabel("tau")
    axes[0, 1].set_ylabel("# Trades")
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Sharpe vs tau
    axes[1, 0].plot(results_df["tau"], results_df["sharpe"], linewidth=2, color="green")
    axes[1, 0].axhline(0, color="red", linestyle="--", linewidth=1, alpha=0.5)
    axes[1, 0].set_title("Sharpe Ratio vs Confidence Threshold", fontsize=12, weight="bold")
    axes[1, 0].set_xlabel("tau")
    axes[1, 0].set_ylabel("Sharpe Ratio")
    axes[1, 0].grid(True, alpha=0.3)

    # 4. Profit Factor vs tau
    axes[1, 1].plot(results_df["tau"], results_df["profit_factor"], linewidth=2, color="purple")
    axes[1, 1].axhline(1.0, color="red", linestyle="--", linewidth=1, alpha=0.5)
    axes[1, 1].set_title("Profit Factor vs Confidence Threshold", fontsize=12, weight="bold")
    axes[1, 1].set_xlabel("tau")
    axes[1, 1].set_ylabel("Profit Factor")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = output_path.parent / "confidence_sweep.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"[SUCCESS] Plot saved to {plot_path}")

    # Find optimal τ
    # Priority: Sharpe > 0.5, max Expectancy, min 50 trades
    valid_results = results_df[(results_df["sharpe"] > 0.5) & (results_df["n_trades"] >= 50)]

    if len(valid_results) > 0:
        optimal = valid_results.loc[valid_results["expectancy"].idxmax()]
        print(f"\n{'='*80}")
        print("OPTIMAL THRESHOLD")
        print(f"{'='*80}")
        print(f"tau_optimal = {optimal['tau']:.2f}")
        print(f"  Trades: {int(optimal['n_trades'])}")
        print(f"  Expectancy: {optimal['expectancy']*100:+.3f}%")
        print(f"  Sharpe: {optimal['sharpe']:.3f}")
        print(f"  Profit Factor: {optimal['profit_factor']:.3f}")
    else:
        print("\n[WARNING] No valid threshold found with Sharpe > 0.5 and trades >= 50")
        print("Consider lowering tau_min or adjusting model.")


if __name__ == "__main__":
    main()
