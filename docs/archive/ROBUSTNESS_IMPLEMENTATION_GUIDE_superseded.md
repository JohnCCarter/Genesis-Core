# ROBUSTNESS IMPLEMENTATION GUIDE
## Eliminera Falska Champions & Säkerställ Stabil Production

**Skapad:** 2025-10-09  
**Status:** Implementation Roadmap  
**Prioritet:** KRITISK för production

---

## 📋 Executive Summary

Nuvarande champion selection saknar **kritiska robustness-checks** som kan leda till:
- Falska champions (overfit på träningsdata)
- Instabila modeller (fungerar en månad, failar nästa)
- Dålig live-prestanda (backtest ≠ production)
- Ingen drift detection (modellen degraderar utan varning)

**Detta dokument beskriver kompletta lösningar för att säkerställa robust production.**

---

## ⚠️ PROBLEM: Nuvarande Gaps

### 1. Träning och Evaluation på Samma Data
```python
# NUVARANDE PROBLEM:
train_model.py → använder ALL data för training
select_champion.py → evaluerar på SAMMA data
# Resultat: Optimistiska metrics, risk för overfit
```

### 2. Ingen Temporal Validation
```python
# Modell tränad på Q1 2024 data
# Används i Q2 2024 → prestanda okänd
# Risk: Market regime förändras, modellen failar
```

### 3. Ingen Stability Check
```python
# Modell kan vara "lucky" på just denna data
# Inga checks för konsistent prestanda över tid
# Risk: Väljer modell med hög varians
```

### 4. Ingen Production Feedback Loop
```python
# Ingen jämförelse backtest vs live
# Ingen drift detection
# Risk: Modellen degraderar utan varning
```

---

## ✅ LÖSNINGAR

---

## LÖSNING 1: Walk-Forward Validation

### Koncept
Träna på period N, testa på period N+1. Upprepa framåt i tiden för att säkerställa temporal robustness.

### Implementation

#### Skapa: `scripts/validate_walk_forward.py`

```python
"""
Walk-forward validation för robust champion selection.

Usage:
    python scripts/validate_walk_forward.py --symbol tBTCUSD --timeframe 1h
    python scripts/validate_walk_forward.py --symbol tBTCUSD --timeframe 1h --n-splits 6
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score

from core.ml.labeling import align_features_with_labels, generate_labels
from core.utils.data_loader import load_features


def create_temporal_splits(n_samples, n_splits=5, train_ratio=0.6):
    """
    Skapa överlappande tränings- och testfönster över tid.
    
    Args:
        n_samples: Total antal samples
        n_splits: Antal valideringsperioder
        train_ratio: Andel av varje window för training
        
    Returns:
        List of (train_start, train_end, test_start, test_end) tuples
        
    Example:
        n_samples=1000, n_splits=5, train_ratio=0.6
        
        Split 1: Train [0:120],    Test [120:200]
        Split 2: Train [100:220],  Test [220:300]
        Split 3: Train [200:320],  Test [320:400]
        ...
    """
    window_size = n_samples // n_splits
    overlap = window_size // 2
    
    splits = []
    for i in range(n_splits):
        start = i * overlap
        end = start + window_size
        
        if end > n_samples:
            break
        
        train_size = int(window_size * train_ratio)
        train_end = start + train_size
        
        if train_end >= end:
            continue
            
        splits.append((start, train_end, train_end, end))
    
    return splits


def train_and_evaluate_split(X, y, train_idx, test_idx, feature_names):
    """Träna och evaluera på en split."""
    X_train = X[train_idx[0]:train_idx[1]]
    y_train = y[train_idx[0]:train_idx[1]]
    X_test = X[test_idx[0]:test_idx[1]]
    y_test = y[test_idx[0]:test_idx[1]]
    
    # Handle NaN
    train_mask = ~np.isnan(X_train).any(axis=1) & ~np.isnan(y_train)
    test_mask = ~np.isnan(X_test).any(axis=1) & ~np.isnan(y_test)
    
    X_train = X_train[train_mask]
    y_train = y_train[train_mask]
    X_test = X_test[test_mask]
    y_test = y_test[test_mask]
    
    if len(X_train) < 50 or len(X_test) < 20:
        return None
    
    # Train buy model
    buy_model = LogisticRegression(max_iter=1000, random_state=42)
    buy_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_proba = buy_model.predict_proba(X_test)[:, 1]
    
    return {
        "auc": roc_auc_score(y_test, y_pred_proba),
        "accuracy": accuracy_score(y_test, y_pred_proba > 0.5),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }


def calculate_stability_metrics(results):
    """Beräkna stability metrics från walk-forward results."""
    if not results:
        return None
        
    aucs = [r["auc"] for r in results]
    accs = [r["accuracy"] for r in results]
    
    return {
        "mean_auc": np.mean(aucs),
        "std_auc": np.std(aucs),
        "min_auc": np.min(aucs),
        "max_auc": np.max(aucs),
        "mean_accuracy": np.mean(accs),
        "std_accuracy": np.std(accs),
        "stability_score": 1.0 - (np.std(aucs) / (np.mean(aucs) + 1e-6)),
        "worst_case_auc": np.min(aucs),
        "consistency": 1.0 - (np.std(aucs) / np.mean(aucs)) if np.mean(aucs) > 0 else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description="Walk-forward validation")
    parser.add_argument("--symbol", type=str, required=True, help="Symbol (e.g., tBTCUSD)")
    parser.add_argument("--timeframe", type=str, required=True, help="Timeframe (e.g., 1h)")
    parser.add_argument("--n-splits", type=int, default=5, help="Number of temporal splits")
    parser.add_argument("--lookahead", type=int, default=10, help="Lookahead bars")
    parser.add_argument("--output", type=str, default="results/validation", help="Output dir")
    
    args = parser.parse_args()
    
    print(f"[WALK-FORWARD] Validating {args.symbol} {args.timeframe}")
    print(f"[CONFIG] {args.n_splits} splits, lookahead={args.lookahead}")
    
    # Load data
    print("\n[DATA] Loading features and candles...")
    features_df = load_features(args.symbol, args.timeframe)
    
    candles_path = Path("data/candles") / f"{args.symbol}_{args.timeframe}.parquet"
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].tolist()
    
    # Generate labels
    print("[LABELS] Generating labels...")
    labels = generate_labels(close_prices, args.lookahead, threshold_pct=0.0)
    
    # Align
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)
    features_aligned = features_df.iloc[start_idx:end_idx]
    labels_aligned = np.array(labels[start_idx:end_idx])
    
    # Extract features
    feature_cols = [c for c in features_aligned.columns if c != "timestamp"]
    X = features_aligned[feature_cols].values
    y = labels_aligned
    
    print(f"[DATA] Total samples: {len(X)}")
    
    # Create temporal splits
    splits = create_temporal_splits(len(X), n_splits=args.n_splits)
    print(f"\n[SPLITS] Created {len(splits)} temporal splits")
    
    # Walk-forward validation
    results = []
    for i, (train_start, train_end, test_start, test_end) in enumerate(splits, 1):
        print(f"\n[SPLIT {i}/{len(splits)}] Train: [{train_start}:{train_end}], "
              f"Test: [{test_start}:{test_end}]")
        
        result = train_and_evaluate_split(
            X, y,
            (train_start, train_end),
            (test_start, test_end),
            feature_cols
        )
        
        if result:
            print(f"  AUC: {result['auc']:.4f}, "
                  f"Accuracy: {result['accuracy']:.4f}, "
                  f"N_train: {result['n_train']}, N_test: {result['n_test']}")
            results.append(result)
        else:
            print("  SKIPPED (insufficient data)")
    
    # Calculate stability metrics
    print("\n" + "=" * 80)
    print("WALK-FORWARD VALIDATION RESULTS")
    print("=" * 80)
    
    if results:
        stability = calculate_stability_metrics(results)
        
        print(f"\nPerformance Metrics:")
        print(f"  Mean AUC:       {stability['mean_auc']:.4f}")
        print(f"  Std AUC:        {stability['std_auc']:.4f}")
        print(f"  Min AUC:        {stability['min_auc']:.4f} (worst case)")
        print(f"  Max AUC:        {stability['max_auc']:.4f}")
        print(f"\nStability Metrics:")
        print(f"  Stability Score: {stability['stability_score']:.4f} (higher is better)")
        print(f"  Consistency:     {stability['consistency']:.4f}")
        
        # Assessment
        print(f"\n{'='*80}")
        print("ASSESSMENT:")
        print(f"{'='*80}")
        
        if stability['stability_score'] > 0.85:
            print("✓ EXCELLENT: Model is highly stable across time periods")
        elif stability['stability_score'] > 0.70:
            print("✓ GOOD: Model shows acceptable stability")
        elif stability['stability_score'] > 0.50:
            print("⚠ WARNING: Model stability is marginal")
        else:
            print("✗ FAIL: Model is too unstable for production")
        
        if stability['worst_case_auc'] < 0.55:
            print("✗ FAIL: Worst case performance is too poor")
        elif stability['worst_case_auc'] < 0.65:
            print("⚠ WARNING: Worst case performance is concerning")
        else:
            print("✓ PASS: Worst case performance is acceptable")
        
        # Save results
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{args.symbol}_{args.timeframe}_walk_forward.json"
        with open(output_path, "w") as f:
            json.dump({
                "symbol": args.symbol,
                "timeframe": args.timeframe,
                "n_splits": len(results),
                "stability_metrics": stability,
                "per_split_results": results,
            }, f, indent=2)
        
        print(f"\n[SAVED] Results saved to: {output_path}")
    else:
        print("✗ FAIL: No valid results obtained")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

#### Användning

```bash
# Basic validation
python scripts/validate_walk_forward.py --symbol tBTCUSD --timeframe 1h

# Med fler splits (mer granulär validering)
python scripts/validate_walk_forward.py \
  --symbol tBTCUSD --timeframe 1h \
  --n-splits 8

# Custom output directory
python scripts/validate_walk_forward.py \
  --symbol tBTCUSD --timeframe 1h \
  --output results/walk_forward_validation
```

#### Exempel Output

```
[WALK-FORWARD] Validating tBTCUSD 1h
[CONFIG] 5 splits, lookahead=10

[SPLIT 1/5] Train: [0:1200], Test: [1200:2000]
  AUC: 0.7450, Accuracy: 0.6823, N_train: 1150, N_test: 780

[SPLIT 2/5] Train: [1000:2200], Test: [2200:3000]
  AUC: 0.7320, Accuracy: 0.6745, N_train: 1180, N_test: 790

[SPLIT 3/5] Train: [2000:3200], Test: [3200:4000]
  AUC: 0.7580, Accuracy: 0.6912, N_train: 1165, N_test: 775

================================================================================
WALK-FORWARD VALIDATION RESULTS
================================================================================

Performance Metrics:
  Mean AUC:       0.7450
  Std AUC:        0.0110
  Min AUC:        0.7320 (worst case)
  Max AUC:        0.7580

Stability Metrics:
  Stability Score: 0.9852 (higher is better)
  Consistency:     0.9852

================================================================================
ASSESSMENT:
================================================================================
✓ EXCELLENT: Model is highly stable across time periods
✓ PASS: Worst case performance is acceptable
```

---

## LÖSNING 2: Holdout Test Set

### Koncept
Reservera 20% av data som "holdout" som ALDRIG används i training. Final champion evaluation görs ENDAST på denna data.

### Implementation

#### Uppdatera: `scripts/train_model.py`

```python
# Lägg till i train_model.py

def split_data_chronological_with_holdout(
    features: np.ndarray,
    labels: np.ndarray,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    # holdout_ratio = 0.2 (implicit)
) -> tuple:
    """
    Dela data kronologiskt i train/val/holdout.
    
    VIKTIGT: Holdout data RÜHRS INTE under training!
    Används ENDAST för final champion evaluation.
    
    Args:
        features: Feature matrix
        labels: Label array
        train_ratio: Andel för training (default 0.6)
        val_ratio: Andel för validation (default 0.2)
        
    Returns:
        X_train, X_val, X_holdout, y_train, y_val, y_holdout
    """
    n = len(features)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    X_train = features[:train_end]
    X_val = features[train_end:val_end]
    X_holdout = features[val_end:]  # HOLY GRAIL - DO NOT TOUCH!
    
    y_train = labels[:train_end]
    y_val = labels[train_end:val_end]
    y_holdout = labels[val_end:]
    
    print(f"[SPLIT] Train: {len(X_train)} samples")
    print(f"[SPLIT] Validation: {len(X_val)} samples")
    print(f"[SPLIT] Holdout: {len(X_holdout)} samples (UNTOUCHED)")
    
    return X_train, X_val, X_holdout, y_train, y_val, y_holdout


# I main():
# Använd den nya split-funktionen
X_train, X_val, X_holdout, y_train, y_val, y_holdout = \
    split_data_chronological_with_holdout(X, aligned_labels)

# Träna ENDAST på train+val
# Spara holdout data separat för senare evaluation
```

#### Skapa: `scripts/evaluate_on_holdout.py`

```python
"""
Evaluera champion på holdout data.

Detta är den SLUTGILTIGA evalueringen som visar
modellens SANNA prestanda på osedd data.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss

from core.utils.data_loader import load_features


def load_holdout_indices(model_path: Path):
    """Ladda holdout indices från model training."""
    # Holdout indices sparas vid training
    holdout_file = model_path.parent / f"{model_path.stem}_holdout_indices.json"
    
    if not holdout_file.exists():
        raise FileNotFoundError(
            f"Holdout indices not found: {holdout_file}\n"
            "Model must be trained with holdout split!"
        )
    
    with open(holdout_file) as f:
        return json.load(f)


def evaluate_on_holdout(symbol, timeframe, model_path):
    """Evaluera modell på holdout data."""
    print(f"[HOLDOUT] Evaluating {model_path.name} on UNSEEN holdout data")
    
    # Load model
    with open(model_path) as f:
        model_json = json.load(f)
    
    # Recreate sklearn model
    buy_model = LogisticRegression()
    buy_model.coef_ = np.array([model_json["buy"]["w"]])
    buy_model.intercept_ = np.array([model_json["buy"]["b"]])
    buy_model.classes_ = np.array([0, 1])
    
    # Load holdout data
    holdout_info = load_holdout_indices(model_path)
    start_idx = holdout_info["start"]
    end_idx = holdout_info["end"]
    
    # Load features
    features_df = load_features(symbol, timeframe)
    feature_cols = model_json["schema"]
    
    X_holdout = features_df.iloc[start_idx:end_idx][feature_cols].values
    
    # Load labels (måste regenereras med samma params)
    # ... (load candles and generate labels)
    
    # Evaluate
    y_pred_proba = buy_model.predict_proba(X_holdout)[:, 1]
    
    results = {
        "auc": roc_auc_score(y_holdout, y_pred_proba),
        "accuracy": accuracy_score(y_holdout, y_pred_proba > 0.5),
        "log_loss": log_loss(y_holdout, y_pred_proba),
        "n_samples": len(X_holdout),
    }
    
    print("\n" + "=" * 80)
    print("HOLDOUT EVALUATION (TRUE PERFORMANCE)")
    print("=" * 80)
    print(f"AUC:      {results['auc']:.4f}")
    print(f"Accuracy: {results['accuracy']:.4f}")
    print(f"Log Loss: {results['log_loss']:.4f}")
    print(f"Samples:  {results['n_samples']}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate on holdout set")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--model", required=True, help="Path to model JSON")
    
    args = parser.parse_args()
    
    model_path = Path(args.model)
    results = evaluate_on_holdout(args.symbol, args.timeframe, model_path)
    
    # Save
    output_path = model_path.parent / f"{model_path.stem}_holdout_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[SAVED] {output_path}")


if __name__ == "__main__":
    main()
```

---

## LÖSNING 3: Stability Metrics i Decision Matrix

### Uppdatera: `src/core/ml/decision_matrix.py`

```python
# Lägg till nya metrics i ModelMetrics

@dataclass
class ModelMetrics:
    """Container for all model evaluation metrics."""
    
    # Existing metrics
    auc: float
    accuracy: float
    log_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_trade_duration: float
    num_trades: int
    consistency: float
    
    # NYA STABILITY METRICS
    performance_std: float = 0.0  # Varians över walk-forward splits
    worst_case_auc: float = 0.5  # Värsta perioden
    stability_score: float = 0.7  # Overall stability (0-1)
    recovery_factor: float = 1.0  # Återhämtning från drawdown
```

### Uppdatera: `config/champion_weights.json`

```json
{
  "profiles": {
    "robust": {
      "description": "Production-ready with focus on stability and robustness",
      "weights": {
        "auc": 0.15,
        "sharpe_ratio": 0.15,
        "profit_factor": 0.10,
        "max_drawdown": 0.20,
        "stability_score": 0.25,
        "worst_case_auc": 0.10,
        "consistency": 0.05
      }
    },
    "ultra_conservative": {
      "description": "Maximum safety - prioritizes stability above all",
      "weights": {
        "max_drawdown": 0.30,
        "stability_score": 0.25,
        "worst_case_auc": 0.20,
        "sharpe_ratio": 0.15,
        "auc": 0.10
      }
    }
  }
}
```

---

## LÖSNING 4: Production Monitoring & Drift Detection

### Skapa: `scripts/monitor_production_drift.py`

```python
"""
Monitor live model performance och detektera drift.

Jämför live metrics mot förväntade metrics från backtest.
Alert när modellen börjar degradera.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def calculate_live_sharpe(trades_file: Path, window_days=30):
    """Beräkna Sharpe ratio från live trades."""
    # Load trades
    with open(trades_file) as f:
        trades = json.load(f)
    
    # Filter recent trades
    cutoff = datetime.now() - timedelta(days=window_days)
    recent_trades = [
        t for t in trades 
        if datetime.fromisoformat(t["timestamp"]) > cutoff
    ]
    
    if len(recent_trades) < 10:
        return None
    
    # Calculate returns
    returns = [t["pnl"] / t["capital"] for t in recent_trades]
    
    # Sharpe ratio (annualized)
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0
    
    # Assuming daily trading
    sharpe = (mean_return / std_return) * np.sqrt(252)
    
    return sharpe


def detect_drift(expected_metrics, live_metrics, threshold=0.30):
    """
    Detektera om modellen har drifted.
    
    Args:
        expected_metrics: Metrics från backtest
        live_metrics: Metrics från live trading
        threshold: Max tillåten degradation (30% default)
        
    Returns:
        dict med drift info
    """
    drift_info = {}
    
    for metric_name in ["sharpe_ratio", "win_rate", "profit_factor"]:
        expected = expected_metrics.get(metric_name, 0)
        live = live_metrics.get(metric_name, 0)
        
        if expected == 0:
            continue
        
        degradation = abs(expected - live) / expected
        
        drift_info[metric_name] = {
            "expected": expected,
            "live": live,
            "degradation": degradation,
            "drifted": degradation > threshold,
        }
    
    # Overall drift assessment
    max_degradation = max(
        d["degradation"] for d in drift_info.values()
    )
    
    drift_info["overall"] = {
        "max_degradation": max_degradation,
        "status": "DRIFTED" if max_degradation > threshold else "OK",
        "threshold": threshold,
    }
    
    return drift_info


def main():
    parser = argparse.ArgumentParser(description="Monitor production drift")
    parser.add_argument("--model", required=True, help="Path to model JSON")
    parser.add_argument("--trades", required=True, help="Path to live trades JSON")
    parser.add_argument("--threshold", type=float, default=0.30, help="Drift threshold")
    
    args = parser.parse_args()
    
    # Load expected metrics från backtest
    model_path = Path(args.model)
    metrics_path = model_path.parent / f"{model_path.stem}_metrics.json"
    
    with open(metrics_path) as f:
        expected_metrics = json.load(f)
    
    # Calculate live metrics
    print("[MONITOR] Calculating live performance...")
    live_sharpe = calculate_live_sharpe(Path(args.trades))
    
    if live_sharpe is None:
        print("⚠ Insufficient live trades for analysis")
        return
    
    live_metrics = {
        "sharpe_ratio": live_sharpe,
        # ... other live metrics
    }
    
    # Detect drift
    drift_info = detect_drift(expected_metrics, live_metrics, args.threshold)
    
    # Report
    print("\n" + "=" * 80)
    print("PRODUCTION DRIFT MONITORING")
    print("=" * 80)
    
    for metric, info in drift_info.items():
        if metric == "overall":
            continue
        
        print(f"\n{metric.replace('_', ' ').title()}:")
        print(f"  Expected (backtest): {info['expected']:.4f}")
        print(f"  Live (30d):          {info['live']:.4f}")
        print(f"  Degradation:         {info['degradation']:.2%}")
        
        if info["drifted"]:
            print(f"  ⚠ WARNING: DRIFT DETECTED!")
    
    # Overall assessment
    print("\n" + "=" * 80)
    print(f"OVERALL STATUS: {drift_info['overall']['status']}")
    print(f"Max Degradation: {drift_info['overall']['max_degradation']:.2%}")
    print(f"Threshold: {drift_info['overall']['threshold']:.2%}")
    print("=" * 80)
    
    if drift_info['overall']['status'] == "DRIFTED":
        print("\n🚨 ALERT: MODEL DRIFT DETECTED!")
        print("Recommended actions:")
        print("  1. Review recent market conditions")
        print("  2. Consider retraining model")
        print("  3. Switch to backup model if available")
        print("  4. Reduce position sizes until resolved")
    else:
        print("\n✓ Model performance is within acceptable range")


if __name__ == "__main__":
    main()
```

#### Användning

```bash
# Check for drift
python scripts/monitor_production_drift.py \
  --model config/models/tBTCUSD_1h_champion.json \
  --trades logs/live_trades.json

# Med custom threshold (20% max degradation)
python scripts/monitor_production_drift.py \
  --model config/models/tBTCUSD_1h_champion.json \
  --trades logs/live_trades.json \
  --threshold 0.20
```

---

## LÖSNING 5: Regime-Aware Validation

### Skapa: `scripts/validate_by_regime.py`

```python
"""
Validera modell separat för olika marknadsregimer.

En robust champion måste prestera i ALLA regimer:
- Bull: Kapitalisera på uppgångar
- Bear: SKYDDA kapital
- Range: Överleva sideways
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from core.strategy.regime import classify_regime
from core.utils.data_loader import load_features


def validate_by_regime(symbol, timeframe, model_path):
    """Evaluera modell per regime."""
    print(f"[REGIME] Validating {model_path.name} across market regimes")
    
    # Load data
    features_df = load_features(symbol, timeframe)
    candles_path = Path("data/candles") / f"{symbol}_{timeframe}.parquet"
    candles_df = pd.read_parquet(candles_path)
    
    # Classify regimes
    regimes = classify_regime(
        candles_df["close"].values,
        candles_df["high"].values,
        candles_df["low"].values,
    )
    
    # Load model and evaluate per regime
    with open(model_path) as f:
        model_json = json.load(f)
    
    results = {}
    
    for regime_name in ["bull", "bear", "ranging", "balanced"]:
        mask = regimes == regime_name
        n_samples = mask.sum()
        
        if n_samples < 50:
            print(f"  {regime_name}: SKIPPED (only {n_samples} samples)")
            continue
        
        # Evaluate on regime data
        # ... (evaluation logic)
        
        results[regime_name] = {
            "auc": auc,
            "sharpe": sharpe,
            "n_samples": n_samples,
        }
        
        print(f"  {regime_name}: AUC={auc:.4f}, Sharpe={sharpe:.2f}, N={n_samples}")
    
    # Assessment
    print("\n" + "=" * 80)
    print("REGIME ROBUSTNESS ASSESSMENT")
    print("=" * 80)
    
    if results["bear"]["sharpe"] < 0:
        print("✗ FAIL: Model loses money in bear markets!")
        print("  → NOT suitable for production")
    elif results["bear"]["sharpe"] < 0.5:
        print("⚠ WARNING: Weak bear market performance")
    else:
        print("✓ PASS: Model protects capital in bear markets")
    
    if results["bull"]["sharpe"] < 1.0:
        print("⚠ WARNING: Model doesn't capitalize well on bull markets")
    else:
        print("✓ PASS: Model captures bull market opportunities")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Validate by regime")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--model", required=True)
    
    args = parser.parse_args()
    
    results = validate_by_regime(
        args.symbol,
        args.timeframe,
        Path(args.model)
    )
    
    # Save
    output_path = Path(args.model).parent / f"{Path(args.model).stem}_regime_validation.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[SAVED] {output_path}")


if __name__ == "__main__":
    main()
```

---

## 📊 IMPLEMENTATION ROADMAP

### Fas 1: AKUT (Nästa vecka) - KRITISKT

**Prioritet:** P0 - Blockerar production

```bash
# 1. Implementera walk-forward validation
# Status: Kod klar ovan
# Action: Kopiera script, testa, integrera i pipeline

# 2. Lägg till holdout split i train_model.py
# Status: Kod klar ovan
# Action: Uppdatera train_model.py, spara holdout indices

# 3. Testa nuvarande modeller med walk-forward
python scripts/validate_walk_forward.py --symbol tBTCUSD --timeframe 1h

# 4. Verifiera stabilitet innan production
```

**Acceptanskriterier:**
- [ ] Walk-forward validation script fungerar
- [ ] Holdout split implementerad i training
- [ ] Minst en modell validerad med stability_score > 0.70
- [ ] Dokumenterad process för validation

### Fas 2: KORTSIKTIG (Nästa månad) - VIKTIGT

**Prioritet:** P1 - Critical for production stability

```bash
# 5. Implementera production monitoring
# Status: Kod klar ovan
# Action: Deploy monitor script, setup alerts

# 6. Lägg till stability metrics i decision matrix
# Status: Specifikation klar ovan
# Action: Uppdatera ModelMetrics, lägg till weights

# 7. Regime-aware validation
# Status: Specifikation klar ovan
# Action: Implementera validate_by_regime.py

# 8. Create automated validation pipeline
python scripts/validate_champion_complete.py \
  --symbol tBTCUSD --timeframe 1h \
  --model config/models/champion.json
```

**Acceptanskriterier:**
- [ ] Production monitoring kör varje dag
- [ ] Drift alerts fungerar
- [ ] Stability metrics i champion selection
- [ ] Regime validation körs för alla champions

### Fas 3: LÅNGSIKTIG (Kontinuerligt) - OPTIMIZATION

**Prioritet:** P2 - Nice to have

```bash
# 9. Auto-retraining vid drift detection
# 10. Ensemble av stabila modeller
# 11. Adaptive weight adjustment baserat på marknad
# 12. A/B testing framework för modeller
```

---

## 🎯 ANVÄNDNING: Komplett Validation Workflow

### Steg 1: Träna med Holdout

```bash
python scripts/train_model.py \
  --symbol tBTCUSD --timeframe 1h \
  --version v11_robust \
  --use-holdout  # NYT FLAG
```

### Steg 2: Walk-Forward Validation

```bash
python scripts/validate_walk_forward.py \
  --symbol tBTCUSD --timeframe 1h \
  --n-splits 6 \
  --output results/validation
```

**Krav för att gå vidare:**
- Stability score > 0.70
- Worst case AUC > 0.60
- Std AUC < 0.10

### Steg 3: Regime Validation

```bash
python scripts/validate_by_regime.py \
  --symbol tBTCUSD --timeframe 1h \
  --model config/models/tBTCUSD_1h_v11_robust.json
```

**Krav för att gå vidare:**
- Bear market Sharpe > 0 (minst break-even)
- Bull market Sharpe > 1.0
- Range market Sharpe > 0.3

### Steg 4: Holdout Evaluation (Final Test)

```bash
python scripts/evaluate_on_holdout.py \
  --symbol tBTCUSD --timeframe 1h \
  --model config/models/tBTCUSD_1h_v11_robust.json
```

**Krav för production:**
- Holdout AUC within 10% of validation AUC
- Holdout Sharpe > 0.8

### Steg 5: Champion Selection med Robustness

```bash
python scripts/select_champion.py \
  --symbol tBTCUSD --timeframe 1h \
  --profile robust \  # NYA PROFILEN
  --visualize
```

### Steg 6: Production Monitoring

```bash
# Kör dagligen efter live trading
python scripts/monitor_production_drift.py \
  --model config/models/tBTCUSD_1h_champion.json \
  --trades logs/live_trades.json \
  --threshold 0.25
```

**Alert triggers:**
- Sharpe degradation > 25%
- Win rate degradation > 20%
- Consecutive losses > 5

---

## ✅ CHECKLISTA: Production Readiness

### Innan Production Launch

- [ ] **Walk-forward validation genomförd**
  - [ ] Minst 5 splits
  - [ ] Stability score > 0.70
  - [ ] Worst case performance acceptabel

- [ ] **Holdout evaluation genomförd**
  - [ ] Holdout performance inom 10% av validation
  - [ ] AUC > 0.65 på holdout
  - [ ] Sharpe > 0.8 på holdout

- [ ] **Regime validation genomförd**
  - [ ] Bear market Sharpe > 0
  - [ ] Bull market kapitalisering OK
  - [ ] Range market överlevnad OK

- [ ] **Production monitoring setup**
  - [ ] Drift detection script deployed
  - [ ] Alerts konfigurerade
  - [ ] Backup model identifierad

- [ ] **Risk management**
  - [ ] Max drawdown limits satta
  - [ ] Position sizing rules definierade
  - [ ] Stop-loss triggers implementerade

### Under Production

- [ ] **Daglig monitoring**
  - [ ] Kör drift detection
  - [ ] Review live metrics
  - [ ] Jämför mot backtest

- [ ] **Veckovis review**
  - [ ] Analyze trade log
  - [ ] Check for regime changes
  - [ ] Validate model performance

- [ ] **Månadsvis audit**
  - [ ] Full model evaluation
  - [ ] Consider retraining
  - [ ] Update risk parameters

---

## 📚 REFERENSER

### Relaterade Dokument

- `scripts/train_model.py` - Model training
- `scripts/select_champion.py` - Champion selection
- `src/core/ml/decision_matrix.py` - Decision matrix
- `config/champion_weights.json` - Weight profiles

### Akademiska Referenser

- **Walk-Forward Analysis:** Pardo (2008) - "The Evaluation and Optimization of Trading Strategies"
- **Model Stability:** Marcos López de Prado (2018) - "Advances in Financial Machine Learning"
- **Regime Detection:** Kritzman et al. (2012) - "Regime Shifts: Implications for Dynamic Strategies"

---

## 🚨 KRITISKA VARNINGAR

### 1. ALDRIG Deploy utan Validation
```
❌ WRONG:
train_model.py → select_champion.py → deploy
(ingen holdout, ingen walk-forward)

✓ CORRECT:
train_model.py (med holdout) →
validate_walk_forward.py →
validate_by_regime.py →
evaluate_on_holdout.py →
select_champion.py (robust profile) →
monitor_production_drift.py →
deploy
```

### 2. ALDRIG Ignorera Drift Signals

```
Om drift detection visar:
- Degradation > 30%: STOP trading omedelbart
- Degradation > 20%: Reducera position size 50%
- Degradation > 10%: Öka monitoring frequency
```

### 3. ALLTID Ha Backup Model

```
- Train 2-3 modeller samtidigt
- Ha en "safe" konservativ model standby
- Test backup quarterly
```

---

## 💡 BEST PRACTICES

### 1. Retraining Schedule

```
- Minimum: Quarterly (Q1, Q2, Q3, Q4)
- Recommended: Monthly
- Optimal: Efter significant market events
- Emergency: När drift > 25%
```

### 2. Data Requirements

```
Minimum training data:
- 1h timeframe: 6 months
- 15m timeframe: 3 months
- 1m timeframe: 1 month

Holdout size: 20% of total data
Walk-forward splits: Minimum 5
```

### 3. Performance Benchmarks

```
Production-ready model måste ha:
- Walk-forward stability > 0.70
- Worst case AUC > 0.60
- Bear market Sharpe > 0
- Holdout performance within 10% of validation
```

---

## 📧 SUPPORT & FEEDBACK

**Frågor?** Tag upp i team meeting  
**Problem?** Create GitHub issue  
**Förbättringar?** Submit pull request

---

**Version:** 1.0  
**Senast uppdaterad:** 2025-10-09  
**Nästa review:** Vid production launch

