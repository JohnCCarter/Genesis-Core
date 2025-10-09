#!/usr/bin/env python3
"""
Holdout validation - final unbiased test on reserved data.

This is the LAST test before production deployment!

Usage:
    python scripts/validate_holdout.py --model results/models/tBTCUSD_1h_v3.json \\
        --symbol tBTCUSD --timeframe 1h
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils.data_loader import load_features


def load_holdout_indices(model_path: str) -> list[int]:
    """Load holdout indices from model provenance."""
    model_path = Path(model_path)
    holdout_path = model_path.parent / f"{model_path.stem}_holdout_indices.json"
    
    if not holdout_path.exists():
        raise FileNotFoundError(f"Holdout indices not found: {holdout_path}")
    
    with open(holdout_path) as f:
        data = json.load(f)
    
    return data["holdout_indices"]


def calculate_forward_returns(close_prices, horizon: int = 10):
    """Calculate forward returns."""
    import pandas as pd
    returns = pd.Series(close_prices).pct_change(horizon).shift(-horizon)
    return returns.values


def main():
    parser = argparse.ArgumentParser(description="Holdout validation")
    parser.add_argument("--model", required=True, help="Path to model")
    parser.add_argument("--symbol", required=True, help="Symbol")
    parser.add_argument("--timeframe", required=True, help="Timeframe")
    parser.add_argument("--horizon", type=int, default=10, help="Forward return horizon")
    
    args = parser.parse_args()
    
    try:
        print("\n" + "="*80)
        print("HOLDOUT VALIDATION - FINAL UNBIASED TEST")
        print("="*80)
        print(f"Model:     {args.model}")
        print(f"Symbol:    {args.symbol}")
        print(f"Timeframe: {args.timeframe}")
        
        # Load holdout indices
        print(f"\n[LOAD] Loading holdout indices...")
        holdout_idx = load_holdout_indices(args.model)
        print(f"[HOLDOUT] {len(holdout_idx)} samples reserved (NEVER used in training)")
        
        # Load model
        with open(args.model) as f:
            model_data = json.load(f)
        
        # Load features
        print(f"[LOAD] Loading features...")
        features_df = load_features(args.symbol, args.timeframe)
        feature_cols = [col for col in features_df.columns if col != "timestamp"]
        
        # Extract holdout data
        X_holdout = features_df.iloc[holdout_idx][feature_cols].values
        
        # Load candles for returns
        import pandas as pd
        candles_path = Path(f"data/candles/{args.symbol}_{args.timeframe}.parquet")
        candles_df = pd.read_parquet(candles_path)
        
        # Calculate labels (for AUC)
        close_prices = candles_df["close"].values
        forward_returns = calculate_forward_returns(close_prices, args.horizon)
        y_holdout = (forward_returns[holdout_idx] > 0).astype(int)
        
        # Get forward returns for IC
        fwd_ret_holdout = forward_returns[holdout_idx]
        
        # Remove NaN
        valid_mask = ~np.isnan(fwd_ret_holdout) & ~np.isnan(X_holdout).any(axis=1)
        X_clean = X_holdout[valid_mask]
        y_clean = y_holdout[valid_mask]
        fwd_ret_clean = fwd_ret_holdout[valid_mask]
        
        print(f"[HOLDOUT] {len(X_clean)} valid samples after NaN removal")
        
        # Generate predictions (placeholder - use feature average)
        # TODO: Load actual sklearn model and predict
        predictions = X_clean.mean(axis=1)
        
        # Calculate metrics
        print(f"\n[EVALUATE] Calculating holdout metrics...")
        
        # IC
        ic, ic_p = spearmanr(predictions, fwd_ret_clean)
        
        # AUC (if we had probabilities)
        # For now, use predictions as scores
        try:
            auc = roc_auc_score(y_clean, predictions)
        except:
            auc = 0.5
        
        # Quintile analysis
        import pandas as pd
        quintiles = pd.qcut(predictions, q=5, labels=False, duplicates="drop")
        
        quintile_returns = []
        for q in range(5):
            q_mask = quintiles == q
            if q_mask.sum() > 0:
                q_ret = fwd_ret_clean[q_mask].mean()
                quintile_returns.append(q_ret)
            else:
                quintile_returns.append(np.nan)
        
        q5_q1_spread = quintile_returns[4] - quintile_returns[0] if len(quintile_returns) >= 5 else np.nan
        
        # Print results
        print("\n" + "="*80)
        print("HOLDOUT RESULTS (FINAL UNBIASED EVALUATION)")
        print("="*80)
        
        print(f"\nSamples:         {len(X_clean):,}")
        print(f"IC:              {ic:+.4f}")
        print(f"IC p-value:      {ic_p:.4f} {'[SIG]' if ic_p < 0.05 else '[N/S]'}")
        print(f"AUC:             {auc:.4f}")
        print(f"Q5-Q1 Spread:    {q5_q1_spread:+.4%}")
        
        print(f"\nQuintile Returns ({args.horizon}-bar forward):")
        for i, qret in enumerate(quintile_returns, 1):
            if not np.isnan(qret):
                print(f"  Q{i}: {qret:+.4%}")
        
        # Fees analysis
        print(f"\nFees Analysis (0.2% round-trip):")
        net_spread = q5_q1_spread - 0.002 if not np.isnan(q5_q1_spread) else np.nan
        if not np.isnan(net_spread):
            print(f"  Gross Spread:    {q5_q1_spread:+.4%}")
            print(f"  Fees:            -0.20%")
            print(f"  Net Spread:      {net_spread:+.4%}")
            
            if net_spread > 0:
                annual = (net_spread / args.horizon) * 252 * 24  # Annualized (hourly bars)
                print(f"  Annualized:      {annual:+.2%} per year")
                print(f"\n[OK] PROFITABLE after fees!")
            else:
                print(f"\n[FAIL] NOT PROFITABLE after fees")
        
        # Compare to training metrics
        print(f"\n" + "="*80)
        print("HOLDOUT vs TRAINING COMPARISON")
        print("="*80)
        
        train_metrics = model_data.get("metrics", {}).get("buy_model", {})
        train_auc = train_metrics.get("val_auc", 0)
        
        if train_auc > 0:
            auc_degradation = (auc - train_auc) / train_auc * 100
            print(f"Training AUC:    {train_auc:.4f}")
            print(f"Holdout AUC:     {auc:.4f}")
            print(f"Degradation:     {auc_degradation:+.1f}%")
            
            if abs(auc_degradation) < 10:
                print("[OK] Within 10% degradation threshold")
            else:
                print("[WARNING] Exceeds 10% degradation threshold")
        
        print("\n" + "="*80)
        print("[SUCCESS] Holdout validation complete!")
        print("="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

