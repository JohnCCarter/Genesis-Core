# ADVANCED VALIDATION & PRODUCTION ML GUIDE

## Production-Grade Model Validation för Trading Systems

**Skapad:** 2025-10-09
**Senast uppdaterad:** 2025-10-09
**Status:** Enterprise Production Standards
**Prioritet:** P0 - KRITISK för production deployment

---

## 📊 IMPLEMENTATION STATUS

### ✅ IMPLEMENTERAT (Phase-5)

| Komponent                           | Status  | Fil                                | Testad |
| ----------------------------------- | ------- | ---------------------------------- | ------ |
| Purged WFCV                         | ✅ KLAR | `scripts/validate_purged_wfcv.py`  | ✅     |
| Provenance Tracking                 | ✅ KLAR | `src/core/utils/provenance.py`     | ✅     |
| Feature Drift (PSI/K-S)             | ✅ KLAR | `scripts/monitor_feature_drift.py` | ✅     |
| Overfit Detection (Deflated Sharpe) | ✅ KLAR | `src/core/ml/overfit_detection.py` | ✅     |
| Overfit Detection (PBO)             | ✅ KLAR | `src/core/ml/overfit_detection.py` | ✅     |
| Regime Gates                        | ✅ KLAR | `scripts/validate_regime_gates.py` | ✅     |
| Validation Config                   | ✅ KLAR | `config/validation_config.json`    | ✅     |

### 📝 DOKUMENTERAT (Redo att implementera)

| Komponent                    | Status          | Prioritet |
| ---------------------------- | --------------- | --------- |
| Hysteresis & Cooldown        | 📝 Dokumenterad | P1        |
| Transaction Costs Model      | 📝 Dokumenterad | P1        |
| Latency Simulation           | 📝 Dokumenterad | P2        |
| Model Card Generator         | 📝 Dokumenterad | P1        |
| Championship Ticket          | 📝 Dokumenterad | P1        |
| Canary Deployment            | 📝 Dokumenterad | P0        |
| Complete Validation Pipeline | 📝 Dokumenterad | P0        |

---

## 📋 Executive Summary

Detta dokument beskriver **enterprise-grade validation** och production practices för ML trading models. Täcker allt från Purged WFCV till Canary deployments.

**Baserat på:**

- Marcos López de Prado: "Advances in Financial Machine Learning"
- David Aronson: "Evidence-Based Technical Analysis"
- Production ML best practices från quant hedge funds

---

## 🎯 ADVANCED VALIDATION TECHNIQUES

---

## 1. PURGED WFCV (Walk-Forward Cross-Validation med Embargo)

### ✅ STATUS: IMPLEMENTERAT (`scripts/validate_purged_wfcv.py`)

### Problem med Vanlig WFCV

```python
# Standard WFCV (FARLIGT för time-series!)
Train: [0:1000]
Test:  [1000:1200]  # ← Data leakage! Features beror på närmaste data
```

**Leakage sources:**

- Features använder indicators (EMA, RSI) som "blöder" över tid
- Labels kan innehålla information från framtiden
- Autocorrelation i time-series

### Lösning: Purged WFCV med Embargo

```python
# scripts/validate_purged_wfcv.py

def create_purged_splits(
    n_samples: int,
    n_splits: int = 5,
    train_ratio: float = 0.6,
    embargo_pct: float = 0.02  # 2% embargo period
):
    """
    Purged Walk-Forward CV med embargo period.

    Embargo = H (holding period) för att eliminera overlap.
    För 1h timeframe med avg holding 36h → embargo = 36 bars

    Args:
        n_samples: Total samples
        n_splits: Number of splits
        train_ratio: Training window size
        embargo_pct: Embargo as % of total data (default 2%)

    Returns:
        List of (train_indices, test_indices, embargo_indices)
    """
    window_size = n_samples // n_splits
    embargo_size = int(n_samples * embargo_pct)

    splits = []
    for i in range(n_splits):
        # Window start
        start = i * (window_size // 2)
        end = start + window_size

        if end > n_samples:
            break

        # Train window
        train_size = int(window_size * train_ratio)
        train_end = start + train_size

        # EMBARGO PERIOD (kritiskt!)
        # Ingen data används mellan train och test
        embargo_start = train_end
        embargo_end = train_end + embargo_size

        # Test window (efter embargo)
        test_start = embargo_end
        test_end = min(end, n_samples)

        if test_start >= test_end:
            continue

        # PURGE overlapping samples
        # Ta bort samples från train som överlappar med test
        # (om features/labels beror på framtida data)

        train_indices = list(range(start, train_end))
        test_indices = list(range(test_start, test_end))
        embargo_indices = list(range(embargo_start, embargo_end))

        splits.append({
            'train': train_indices,
            'test': test_indices,
            'embargo': embargo_indices,
            'embargo_size': embargo_size
        })

    return splits


def purge_overlapping_labels(train_indices, test_indices, label_dependency_window):
    """
    Purge train samples vars labels beror på test data.

    Om lookahead = 10 bars, ta bort sista 10 samples från train
    om de överlappar med test period.
    """
    # Identify train samples too close to test
    max_train_idx = max(train_indices)
    min_test_idx = min(test_indices)

    # Purge window
    purge_threshold = min_test_idx - label_dependency_window

    purged_train = [
        idx for idx in train_indices
        if idx < purge_threshold
    ]

    return purged_train


# Exempel användning:
splits = create_purged_splits(10000, n_splits=6, embargo_pct=0.02)

for split in splits:
    # Purge train data
    purged_train = purge_overlapping_labels(
        split['train'],
        split['test'],
        label_dependency_window=10  # lookahead bars
    )

    # Train on purged data
    model.fit(X[purged_train], y[purged_train])

    # Test on test data (efter embargo)
    score = model.score(X[split['test']], y[split['test']])
```

### Varför detta är KRITISKT

- ✅ Eliminerar data leakage
- ✅ Ger realistiska performance estimates
- ✅ Embargo förhindrar autocorrelation bias
- ✅ Production-ready validation

---

## 2. DEFLATED SHARPE RATIO & PBO-CHECK

### ✅ STATUS: IMPLEMENTERAT (`src/core/ml/overfit_detection.py`)

### Problem med Vanlig Sharpe

```python
# Sharpe Ratio ser bra ut → 1.8
# MEN: Efter 1000 backtests kan detta vara ren tur!
```

### A. Deflated Sharpe Ratio

```python
# scripts/calculate_deflated_sharpe.py

def calculate_deflated_sharpe(returns, n_trials, skewness, kurtosis):
    """
    Bailey & López de Prado (2014) Deflated Sharpe Ratio.

    Justerar Sharpe för:
    - Antal testade strategier (multiple testing)
    - Non-normala returns (skewness, kurtosis)
    - Variance inflation från trials

    Args:
        returns: Array av returns
        n_trials: Antal strategier testade innan denna
        skewness: Skewness av returns
        kurtosis: Excess kurtosis av returns

    Returns:
        Deflated Sharpe Ratio
    """
    # Standard Sharpe
    mean_ret = np.mean(returns)
    std_ret = np.std(returns)
    sharpe = mean_ret / std_ret * np.sqrt(252)

    # Variance inflation från multiple trials
    n = len(returns)
    V_sharpe = (1 / (n - 1)) * (
        1 +
        (1/2) * sharpe**2 -
        skewness * sharpe +
        (kurtosis - 1) / 4 * sharpe**2
    )

    # Deflation factor
    # Baserat på antal trials (Bonferroni correction)
    z_score = (sharpe - 0) / np.sqrt(V_sharpe)

    # Expected maximum Sharpe från n_trials random strategies
    expected_max_sharpe = (
        (1 - np.euler_gamma) * norm.ppf(1 - 1/n_trials) +
        np.euler_gamma * norm.ppf(1 - 1/(n_trials * np.e))
    )

    # Deflated Sharpe
    deflated_sharpe = (sharpe - expected_max_sharpe) / np.sqrt(V_sharpe)

    return {
        'sharpe': sharpe,
        'deflated_sharpe': deflated_sharpe,
        'variance_inflation': V_sharpe,
        'p_value': 1 - norm.cdf(deflated_sharpe),
    }


# Användning:
result = calculate_deflated_sharpe(
    returns=backtest_returns,
    n_trials=50,  # Ni testade 50 strategier innan ni hittade denna
    skewness=stats.skew(backtest_returns),
    kurtosis=stats.kurtosis(backtest_returns)
)

if result['deflated_sharpe'] < 1.0:
    print("⚠️ WARNING: Sharpe ratio är statistiskt insignifikant!")
    print("Risk för överanpassning!")
```

### B. Probability of Backtest Overfitting (PBO)

```python
# scripts/calculate_pbo.py

def calculate_pbo(backtest_results, n_splits=16):
    """
    Bailey et al. (2015) - Probability of Backtest Overfitting.

    Mäter sannolikheten att IS (in-sample) performance
    är bättre än OOS (out-of-sample) performance.

    PBO > 0.5 → Risk för overfit!
    PBO < 0.3 → Robust strategi

    Args:
        backtest_results: Results från combinatorial split
        n_splits: Antal sätt att dela data (default 16)

    Returns:
        PBO score (0-1)
    """
    # Combinatorially split data i IS/OOS pairs
    # För varje split:
    #   - Optimera på IS
    #   - Testa på OOS

    is_sharpes = []
    oos_sharpes = []

    for split in generate_combinatorial_splits(data, n_splits):
        # Optimize på IS
        optimal_params = optimize_on_data(split['is_data'])
        is_sharpe = evaluate(split['is_data'], optimal_params)

        # Test på OOS
        oos_sharpe = evaluate(split['oos_data'], optimal_params)

        is_sharpes.append(is_sharpe)
        oos_sharpes.append(oos_sharpe)

    # Count hur många gånger IS > OOS
    n_overfit = sum(1 for is_sr, oos_sr in zip(is_sharpes, oos_sharpes) if is_sr > oos_sr)

    # PBO = probability that IS > OOS
    pbo = n_overfit / n_splits

    return {
        'pbo': pbo,
        'is_sharpes': is_sharpes,
        'oos_sharpes': oos_sharpes,
        'assessment': (
            'ROBUST' if pbo < 0.3 else
            'MARGINAL' if pbo < 0.5 else
            'OVERFIT RISK'
        )
    }


# Användning:
pbo_result = calculate_pbo(backtest_data)

if pbo_result['pbo'] > 0.5:
    print("🚨 HIGH OVERFIT RISK!")
    print(f"PBO = {pbo_result['pbo']:.2%}")
    print("Strategy is likely overfit to in-sample data")
    REJECT_MODEL()
```

---

## 3. PROBABILITY CALIBRATION

### ✅ STATUS: REDAN IMPLEMENTERAT (`core/ml/calibration.py`)

### A. Isotonic Regression Calibration

```python
# Redan implementerat i core/ml/calibration.py!

from core.ml.calibration import calibrate_model

# Isotonic regression är PERFEKT för trading:
# - Non-parametrisk (inga antaganden)
# - Monotonisk (bevarar ranking)
# - Flexibel (fångar icke-linjära patterns)

calibrated = calibrate_model(
    y_true,
    y_pred_proba,
    method='isotonic'  # eller 'platt', 'beta'
)
```

### B. Temperature Scaling (för neural nets)

```python
# Om ni byter till neural networks senare

def temperature_scaling(logits, temperature=1.5):
    """
    Skala logits med temperature för bättre kalibrering.

    T > 1: Mjukare probabilities (mer osäkerhet)
    T < 1: Hårdare probabilities (mer säker)
    T = 1: Ingen scaling
    """
    scaled_logits = logits / temperature
    probs = softmax(scaled_logits)
    return probs

# Find optimal temperature på validation set
def find_optimal_temperature(val_logits, val_labels):
    from scipy.optimize import minimize

    def nll_loss(T):
        probs = temperature_scaling(val_logits, T[0])
        return -np.mean(np.log(probs[np.arange(len(val_labels)), val_labels]))

    result = minimize(nll_loss, x0=[1.5], bounds=[(0.1, 10.0)])
    return result.x[0]
```

---

## 4. FEATURE & LABEL DRIFT MONITORING

### ✅ STATUS: IMPLEMENTERAT (`scripts/monitor_feature_drift.py`)

### A. Population Stability Index (PSI)

```python
# scripts/monitor_feature_drift.py

def calculate_psi(expected, actual, bins=10):
    """
    Population Stability Index - detektera feature distribution drift.

    PSI < 0.1:  No significant shift
    PSI 0.1-0.25: Moderate shift
    PSI > 0.25: Significant shift → RETRAIN!

    Args:
        expected: Feature distribution från training
        actual: Feature distribution från production
        bins: Number of bins for discretization

    Returns:
        PSI score
    """
    # Discretize into bins
    expected_percents, bin_edges = np.histogram(expected, bins=bins)
    expected_percents = expected_percents / len(expected)

    actual_percents, _ = np.histogram(actual, bins=bin_edges)
    actual_percents = actual_percents / len(actual)

    # Add small epsilon to avoid log(0)
    epsilon = 1e-6
    expected_percents = np.maximum(expected_percents, epsilon)
    actual_percents = np.maximum(actual_percents, epsilon)

    # PSI calculation
    psi = np.sum(
        (actual_percents - expected_percents) *
        np.log(actual_percents / expected_percents)
    )

    return psi


def monitor_all_features(training_features, production_features):
    """Monitor PSI för alla features."""
    psi_results = {}

    for feature_name in training_features.columns:
        psi = calculate_psi(
            training_features[feature_name].values,
            production_features[feature_name].values
        )

        psi_results[feature_name] = {
            'psi': psi,
            'status': (
                'OK' if psi < 0.1 else
                'WARNING' if psi < 0.25 else
                'CRITICAL'
            )
        }

    return psi_results


# Användning:
psi_report = monitor_all_features(train_features, live_features)

for feature, result in psi_report.items():
    if result['status'] == 'CRITICAL':
        print(f"🚨 {feature}: PSI={result['psi']:.3f} - RETRAIN NEEDED!")
```

### B. Kolmogorov-Smirnov Test (K-S)

```python
from scipy.stats import ks_2samp

def ks_drift_test(training_dist, production_dist, alpha=0.05):
    """
    K-S test för distribution drift.

    Args:
        training_dist: Distribution från training
        production_dist: Distribution från production
        alpha: Significance level (default 5%)

    Returns:
        Dict med test results
    """
    statistic, p_value = ks_2samp(training_dist, production_dist)

    return {
        'statistic': statistic,
        'p_value': p_value,
        'drifted': p_value < alpha,
        'interpretation': (
            'DISTRIBUTIONS DIFFER' if p_value < alpha else
            'NO SIGNIFICANT DRIFT'
        )
    }


# Monitor label distribution drift
ks_result = ks_drift_test(
    train_labels,
    live_labels
)

if ks_result['drifted']:
    print("⚠️ Label distribution has shifted!")
    print(f"K-S statistic: {ks_result['statistic']:.4f}")
    print(f"p-value: {ks_result['p_value']:.4f}")
    print("→ Market regime may have changed")
```

---

## 5. HYSTERESIS & COOLDOWN vid Champion-byte

### 📝 STATUS: DOKUMENTERAD (Ej implementerad)

### Problem

```python
# Utan hysteresis:
# Dag 1: Model A är champion (score: 7.2)
# Dag 2: Model B är champion (score: 7.21) ← +0.01 diff!
# Dag 3: Model A är champion (score: 7.22)
# → Konstant switching = instabilitet, execution costs
```

### Lösning: Hysteresis Mechanism

```python
# scripts/select_champion_with_hysteresis.py

class ChampionSelector:
    """Champion selection med hysteresis och cooldown."""

    def __init__(
        self,
        hysteresis_threshold: float = 0.5,  # Minst 0.5 poäng bättre
        cooldown_days: int = 7,  # Minst 7 dagar mellan byten
        min_confidence: float = 0.8  # Minst 80% confidence i byte
    ):
        self.hysteresis_threshold = hysteresis_threshold
        self.cooldown_days = cooldown_days
        self.min_confidence = min_confidence
        self.current_champion = None
        self.last_change_date = None

    def should_switch_champion(
        self,
        current_score: float,
        challenger_score: float,
        current_date
    ) -> dict:
        """
        Besluta om champion ska bytas.

        Returns:
            Dict med decision info
        """
        # 1. Check cooldown period
        if self.last_change_date:
            days_since_change = (current_date - self.last_change_date).days
            if days_since_change < self.cooldown_days:
                return {
                    'switch': False,
                    'reason': f'COOLDOWN ({days_since_change}/{self.cooldown_days} days)',
                    'score_diff': challenger_score - current_score
                }

        # 2. Check hysteresis threshold
        score_improvement = challenger_score - current_score

        if score_improvement < self.hysteresis_threshold:
            return {
                'switch': False,
                'reason': f'INSUFFICIENT_IMPROVEMENT ({score_improvement:.2f} < {self.hysteresis_threshold})',
                'score_diff': score_improvement
            }

        # 3. Check confidence (baserat på validation)
        # Beräkna confidence i att challenger är verkligen bättre
        # Använd bootstrap eller t-test
        confidence = self._calculate_switch_confidence(current_score, challenger_score)

        if confidence < self.min_confidence:
            return {
                'switch': False,
                'reason': f'LOW_CONFIDENCE ({confidence:.2%} < {self.min_confidence:.2%})',
                'score_diff': score_improvement,
                'confidence': confidence
            }

        # ALL CHECKS PASSED → SWITCH!
        return {
            'switch': True,
            'reason': 'APPROVED',
            'score_diff': score_improvement,
            'confidence': confidence
        }

    def _calculate_switch_confidence(self, current_score, challenger_score):
        """
        Bootstrap confidence att challenger är bättre.

        Använd bootstrap sampling av validation results för att
        beräkna sannolikheten att challenger verkligen är bättre.
        """
        # Bootstrap 1000 times
        # Räkna hur ofta challenger > current
        # Return fraction
        return 0.95  # Placeholder


# Användning:
selector = ChampionSelector(
    hysteresis_threshold=0.5,
    cooldown_days=7,
    min_confidence=0.8
)

decision = selector.should_switch_champion(
    current_score=7.2,
    challenger_score=7.4,  # +0.2 improvement
    current_date=datetime.now()
)

if decision['switch']:
    print(f"✓ SWITCHING to challenger (improvement: {decision['score_diff']:.2f})")
    switch_to_challenger()
else:
    print(f"✗ KEEPING current champion: {decision['reason']}")
```

### Konfiguration

```json
// config/champion_switching_policy.json
{
  "hysteresis": {
    "score_threshold": 0.5,
    "description": "Challenger must be 0.5+ points better"
  },
  "cooldown": {
    "days": 7,
    "description": "Minimum 7 days between champion changes"
  },
  "confidence": {
    "minimum": 0.8,
    "method": "bootstrap",
    "n_bootstrap": 1000,
    "description": "80% confidence that challenger is truly better"
  },
  "emergency_override": {
    "enabled": true,
    "conditions": [
      "current_champion_sharpe < 0",
      "current_champion_drawdown > 0.30",
      "drift_detected == true"
    ]
  }
}
```

---

## 6. REGIME-ROBUSTNESS SOM HÅRDA GATES

### ✅ STATUS: IMPLEMENTERAT (`scripts/validate_regime_gates.py`)

### Koncept: Champion måste PASSA alla gates

```python
# scripts/validate_regime_gates.py

class RegimeGates:
    """Hårda requirements per regime - modell måste passa ALLA."""

    GATES = {
        'bull': {
            'min_sharpe': 1.0,
            'min_win_rate': 0.52,
            'max_drawdown': -0.20,
            'min_profit_factor': 1.3,
            'description': 'Must capitalize on bull trends'
        },
        'bear': {
            'min_sharpe': 0.0,  # KRITISKT: Minst break-even!
            'min_win_rate': 0.48,
            'max_drawdown': -0.15,
            'min_profit_factor': 0.95,
            'description': 'MUST protect capital in bear markets'
        },
        'ranging': {
            'min_sharpe': 0.3,
            'min_win_rate': 0.50,
            'max_drawdown': -0.18,
            'min_profit_factor': 1.1,
            'description': 'Must survive sideways markets'
        },
        'balanced': {
            'min_sharpe': 0.5,
            'min_win_rate': 0.50,
            'max_drawdown': -0.20,
            'min_profit_factor': 1.2,
            'description': 'Baseline performance in neutral conditions'
        }
    }

    @classmethod
    def validate_model(cls, model_metrics_by_regime):
        """
        Validera modell mot alla regime gates.

        Args:
            model_metrics_by_regime: Dict med metrics per regime

        Returns:
            Dict med pass/fail per gate
        """
        results = {}
        all_passed = True

        for regime, gates in cls.GATES.items():
            if regime not in model_metrics_by_regime:
                results[regime] = {'status': 'NO_DATA', 'passed': False}
                all_passed = False
                continue

            metrics = model_metrics_by_regime[regime]
            regime_results = {}
            regime_passed = True

            # Check varje gate
            if metrics['sharpe'] < gates['min_sharpe']:
                regime_results['sharpe'] = f"FAIL ({metrics['sharpe']:.2f} < {gates['min_sharpe']})"
                regime_passed = False
            else:
                regime_results['sharpe'] = f"PASS ({metrics['sharpe']:.2f})"

            if metrics['win_rate'] < gates['min_win_rate']:
                regime_results['win_rate'] = f"FAIL ({metrics['win_rate']:.2%} < {gates['min_win_rate']:.2%})"
                regime_passed = False
            else:
                regime_results['win_rate'] = f"PASS ({metrics['win_rate']:.2%})"

            if metrics['drawdown'] < gates['max_drawdown']:
                regime_results['drawdown'] = f"FAIL ({metrics['drawdown']:.1%} < {gates['max_drawdown']:.1%})"
                regime_passed = False
            else:
                regime_results['drawdown'] = f"PASS ({metrics['drawdown']:.1%})"

            if metrics['profit_factor'] < gates['min_profit_factor']:
                regime_results['profit_factor'] = f"FAIL ({metrics['profit_factor']:.2f} < {gates['min_profit_factor']})"
                regime_passed = False
            else:
                regime_results['profit_factor'] = f"PASS ({metrics['profit_factor']:.2f})"

            results[regime] = {
                'status': 'PASS' if regime_passed else 'FAIL',
                'passed': regime_passed,
                'details': regime_results
            }

            if not regime_passed:
                all_passed = False

        return {
            'all_gates_passed': all_passed,
            'per_regime': results,
            'production_ready': all_passed
        }


# Användning i champion selection:
gate_results = RegimeGates.validate_model(model_regime_metrics)

if not gate_results['production_ready']:
    print("🚨 MODEL REJECTED: Failed regime gates")
    for regime, result in gate_results['per_regime'].items():
        if result['status'] == 'FAIL':
            print(f"\n{regime.upper()} REGIME:")
            for gate, status in result['details'].items():
                print(f"  {gate}: {status}")

    REJECT_MODEL()
else:
    print("✓ ALL REGIME GATES PASSED - Production ready")
```

---

## 7. REALISTISK BACKTEST

### 📝 STATUS: DOKUMENTERAD (Ej implementerad)

### A. Transaction Costs Model

```python
# src/core/backtest/costs.py

@dataclass
class TransactionCosts:
    """Realistiska trading costs."""

    # Bitfinex maker/taker fees
    maker_fee: float = 0.0010  # 0.10% (maker)
    taker_fee: float = 0.0020  # 0.20% (taker)

    # Slippage model
    base_slippage_bps: float = 2.0  # 2 basis points base
    volume_impact_factor: float = 0.5  # Ökar med order size

    # Latency
    execution_delay_bars: int = 1  # 1 bar delay för execution

    # Partial fills
    fill_probability: float = 0.95  # 95% fill rate
    partial_fill_factor: float = 0.7  # Genomsnitt 70% av order fylls

    def calculate_total_cost(
        self,
        order_size_usd: float,
        avg_daily_volume: float,
        is_maker: bool = False
    ) -> float:
        """
        Beräkna total transaction cost.

        Returns:
            Total cost as % of order size
        """
        # Fee
        fee = self.maker_fee if is_maker else self.taker_fee

        # Slippage (ökar med order size / volume)
        volume_ratio = order_size_usd / avg_daily_volume
        slippage = self.base_slippage_bps * (1 + self.volume_impact_factor * volume_ratio)
        slippage_pct = slippage / 10000

        # Total cost
        total_cost = fee + slippage_pct

        return total_cost


# Integration i backtest:
def simulate_trade_with_costs(
    entry_price: float,
    exit_price: float,
    position_size_usd: float,
    costs: TransactionCosts
):
    """Simulera trade med realistiska costs."""

    # Entry cost
    entry_cost_pct = costs.calculate_total_cost(
        position_size_usd,
        avg_daily_volume=5_000_000,  # $5M average volume
        is_maker=True  # Assume limit orders
    )
    effective_entry = entry_price * (1 + entry_cost_pct)

    # Execution delay (pris kan ha rört sig)
    # Simulera 1-bar delay
    slippage_bars = 1
    price_movement = calculate_price_movement(entry_price, slippage_bars)
    effective_entry += price_movement

    # Exit cost
    exit_cost_pct = costs.calculate_total_cost(
        position_size_usd,
        avg_daily_volume=5_000_000,
        is_maker=False  # Assume market orders vid exit
    )
    effective_exit = exit_price * (1 - exit_cost_pct)

    # Partial fill simulation
    if np.random.random() > costs.fill_probability:
        # Partial fill
        fill_ratio = costs.partial_fill_factor
        actual_size = position_size_usd * fill_ratio
    else:
        actual_size = position_size_usd

    # PnL calculation
    pnl_pct = (effective_exit - effective_entry) / effective_entry
    pnl_usd = actual_size * pnl_pct

    return {
        'pnl_usd': pnl_usd,
        'pnl_pct': pnl_pct,
        'entry_cost': entry_cost_pct,
        'exit_cost': exit_cost_pct,
        'fill_ratio': actual_size / position_size_usd,
        'effective_entry': effective_entry,
        'effective_exit': effective_exit
    }
```

### B. Latency Simulation

```python
def simulate_signal_to_execution_latency():
    """
    Simulera real-world latency.

    Signal generated → Order sent → Order filled
    """
    # Component latencies (milliseconds)
    latencies = {
        'strategy_compute': np.random.normal(50, 10),  # 50ms ± 10ms
        'risk_check': np.random.normal(20, 5),
        'network_to_exchange': np.random.normal(100, 30),
        'exchange_matching': np.random.normal(50, 20),
    }

    total_latency_ms = sum(latencies.values())

    # Convert to bars (för 1h bar = 3600000 ms)
    # För 1 min bar = 60000 ms
    bars_timeframe_ms = 60000  # 1min
    latency_bars = total_latency_ms / bars_timeframe_ms

    return {
        'total_ms': total_latency_ms,
        'latency_bars': latency_bars,
        'components': latencies
    }


# I backtest:
if signal_generated_at_bar_i:
    latency = simulate_signal_to_execution_latency()
    execution_bar = i + ceil(latency['latency_bars'])
    execution_price = candles[execution_bar]['close']  # Slippage!
```

---

## 8. REPRODUCERBARHET via Data/Config Hashar

### ✅ STATUS: IMPLEMENTERAT (`src/core/utils/provenance.py`)

### Problem

```python
# "Model v11 presterade bra i backtest"
# 6 månader senare: "Vilken data användes? Vilka parametrar?"
# → KAN INTE REPRODUCERA!
```

### Lösning: Complete Provenance Tracking

```python
# src/core/utils/provenance.py

import hashlib
import json
from pathlib import Path

def hash_dataframe(df: pd.DataFrame) -> str:
    """Skapa deterministisk hash av DataFrame."""
    # Sort columns and rows för konsistens
    df_sorted = df.sort_index(axis=1).sort_index(axis=0)

    # Convert to bytes
    data_bytes = df_sorted.to_csv(index=False).encode('utf-8')

    # SHA256 hash
    return hashlib.sha256(data_bytes).hexdigest()[:16]


def hash_config(config: dict) -> str:
    """Hash av konfiguration."""
    # Sort keys för deterministisk output
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode('utf-8')).hexdigest()[:16]


def create_provenance_record(
    features_df: pd.DataFrame,
    labels: list,
    config: dict,
    model_path: Path
) -> dict:
    """
    Skapa komplett provenance record för reproducerbarhet.

    Returns:
        Provenance dict med all information för att reproducera
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'data_hash': hash_dataframe(features_df),
        'labels_hash': hashlib.sha256(
            json.dumps(labels).encode()
        ).hexdigest()[:16],
        'config_hash': hash_config(config),
        'model_path': str(model_path),
        'data_info': {
            'n_samples': len(features_df),
            'n_features': len(features_df.columns),
            'date_range': {
                'start': features_df['timestamp'].min().isoformat(),
                'end': features_df['timestamp'].max().isoformat()
            },
            'feature_names': list(features_df.columns)
        },
        'config': config,
        'environment': {
            'python_version': sys.version,
            'sklearn_version': sklearn.__version__,
            'pandas_version': pd.__version__,
            'numpy_version': np.__version__
        }
    }


# Vid training:
provenance = create_provenance_record(features_df, labels, training_config, model_path)

# Spara tillsammans med modell
provenance_path = model_path.parent / f"{model_path.stem}_provenance.json"
with open(provenance_path, 'w') as f:
    json.dump(provenance, f, indent=2)

print(f"[PROVENANCE] Data hash: {provenance['data_hash']}")
print(f"[PROVENANCE] Config hash: {provenance['config_hash']}")


# Vid reproducering (6 månader senare):
def verify_reproducibility(model_path):
    """Verifiera att vi kan reproducera model training."""
    # Load provenance
    provenance_path = model_path.parent / f"{model_path.stem}_provenance.json"
    with open(provenance_path) as f:
        original_provenance = json.load(f)

    # Load current data
    features_df = load_features(symbol, timeframe)

    # Verify data hash
    current_hash = hash_dataframe(features_df)

    if current_hash != original_provenance['data_hash']:
        print("⚠️ WARNING: Data has changed since training!")
        print(f"Original hash: {original_provenance['data_hash']}")
        print(f"Current hash:  {current_hash}")
        print("Results may not be reproducible")
        return False

    print("✓ Data verified - identical to training data")
    return True
```

---

## 9. MODEL CARD & CHAMPIONSHIP TICKET

### 📝 STATUS: DOKUMENTERAD (Ej implementerad)

### Model Card (ML Documentation Standard)

```python
# Skapa: scripts/generate_model_card.py

def generate_model_card(model_path, validation_results):
    """
    Generera standardiserad Model Card enligt Google/Microsoft standard.

    https://arxiv.org/abs/1810.03993
    """
    card = {
        "model_details": {
            "name": model_path.stem,
            "version": "v11_robust",
            "date": datetime.now().isoformat(),
            "type": "Logistic Regression (Binary Classification)",
            "training_data": {
                "symbol": "tBTCUSD",
                "timeframe": "1h",
                "period": "2024-01-01 to 2024-06-30",
                "n_samples": 4320,
                "features": ["bb_position", "trend_confluence", "rsi"]
            }
        },

        "intended_use": {
            "primary": "Paper trading signal generation for BTC/USD 1h",
            "out_of_scope": [
                "Live trading without human oversight",
                "Other symbols without retraining",
                "Timeframes other than 1h"
            ]
        },

        "performance": {
            "validation_auc": 0.75,
            "holdout_auc": 0.73,
            "walk_forward_stability": 0.82,
            "worst_case_auc": 0.68,
            "deflated_sharpe": 1.2,
            "pbo_score": 0.28  # < 0.3 = robust
        },

        "regime_performance": {
            "bull": {"sharpe": 1.4, "status": "PASS"},
            "bear": {"sharpe": 0.3, "status": "PASS"},
            "ranging": {"sharpe": 0.5, "status": "PASS"}
        },

        "risks_and_limitations": [
            "Model trained only on 6 months data",
            "Performance may degrade in unprecedented market conditions",
            "Requires monitoring for drift (PSI check weekly)",
            "Not tested on black swan events",
            "Assumes liquid market (may fail in low volume)"
        ],

        "ethical_considerations": {
            "fairness": "N/A - financial model",
            "privacy": "No personal data used",
            "safety": "Paper trading only, risk limits enforced"
        },

        "maintenance": {
            "monitoring_frequency": "Daily drift check",
            "retraining_trigger": [
                "PSI > 0.25 on any feature",
                "Live Sharpe degradation > 25%",
                "Regime gate failure"
            ],
            "expected_lifetime": "1-3 months before retraining"
        },

        "provenance": {
            "data_hash": "<data_hash>",
            "config_hash": "<config_hash>",
            "training_script": "scripts/train_model.py v2.1.0",
            "reproducible": True
        }
    }

    return card


# Spara Model Card
model_card = generate_model_card(model_path, validation_results)

card_path = model_path.parent / f"{model_path.stem}_MODEL_CARD.json"
with open(card_path, 'w') as f:
    json.dump(model_card, f, indent=2)

# Generera också human-readable version
card_md_path = model_path.parent / f"{model_path.stem}_MODEL_CARD.md"
with open(card_md_path, 'w') as f:
    f.write(format_model_card_markdown(model_card))
```

### Championship Ticket (Production Approval)

```python
# Skapa: scripts/create_championship_ticket.py

def create_championship_ticket(
    model_path,
    validation_results,
    gate_results,
    pbo_results,
    deflated_sharpe
):
    """
    Generera Championship Ticket - formell godkännande för production.

    Fungerar som en "checklist" som måste godkännas innan deploy.
    """
    ticket = {
        "ticket_id": f"CHAMP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "model": str(model_path),
        "status": "PENDING_APPROVAL",
        "created_at": datetime.now().isoformat(),

        "validation_checklist": {
            "walk_forward": {
                "completed": True,
                "stability_score": validation_results['stability_score'],
                "status": "PASS" if validation_results['stability_score'] > 0.70 else "FAIL"
            },
            "holdout_test": {
                "completed": True,
                "holdout_auc": validation_results['holdout_auc'],
                "degradation": abs(validation_results['val_auc'] - validation_results['holdout_auc']) / validation_results['val_auc'],
                "status": "PASS" if abs(...) < 0.10 else "FAIL"
            },
            "regime_gates": {
                "completed": True,
                "all_passed": gate_results['all_gates_passed'],
                "failed_regimes": [
                    r for r, res in gate_results['per_regime'].items()
                    if not res['passed']
                ],
                "status": "PASS" if gate_results['all_gates_passed'] else "FAIL"
            },
            "overfit_checks": {
                "pbo_score": pbo_results['pbo'],
                "pbo_status": "PASS" if pbo_results['pbo'] < 0.5 else "FAIL",
                "deflated_sharpe": deflated_sharpe,
                "sharpe_status": "PASS" if deflated_sharpe > 1.0 else "FAIL"
            },
            "drift_monitoring": {
                "completed": True,
                "psi_max": 0.08,  # Från feature drift monitoring
                "status": "PASS"
            }
        },

        "approval_criteria": {
            "required_passes": [
                "walk_forward",
                "regime_gates",
                "overfit_checks"
            ],
            "all_passed": None,  # Beräknas nedan
            "approved_by": None,
            "approved_at": None
        },

        "deployment_plan": {
            "phase_1_canary": {
                "duration": "3 days",
                "allocation": "10% of capital",
                "success_criteria": "Sharpe > 0.5, No drift"
            },
            "phase_2_paper": {
                "duration": "7 days",
                "allocation": "50% of capital",
                "success_criteria": "Sharpe > 0.8, PSI < 0.1"
            },
            "phase_3_full": {
                "duration": "Ongoing",
                "allocation": "100% of capital",
                "success_criteria": "Continuous monitoring"
            }
        },

        "rollback_plan": {
            "trigger_conditions": [
                "Live Sharpe < 0 for 3 consecutive days",
                "Drawdown > 15%",
                "PSI > 0.25 on any feature",
                "Drift degradation > 30%"
            ],
            "rollback_model": "config/models/tBTCUSD_1h_backup_conservative.json",
            "notification": ["team@email.com", "risk@email.com"]
        }
    }

    # Calculate overall approval
    checklist = ticket['validation_checklist']
    all_passed = all(
        checklist[check]['status'] == 'PASS'
        for check in ticket['approval_criteria']['required_passes']
    )

    ticket['approval_criteria']['all_passed'] = all_passed
    ticket['status'] = 'APPROVED' if all_passed else 'REJECTED'

    return ticket


# Generera ticket
ticket = create_championship_ticket(
    model_path,
    validation_results,
    gate_results,
    pbo_results,
    deflated_sharpe
)

# Spara
ticket_path = Path("results/championship_tickets") / f"{ticket['ticket_id']}.json"
ticket_path.parent.mkdir(parents=True, exist_ok=True)
with open(ticket_path, 'w') as f:
    json.dump(ticket, f, indent=2)

# Print summary
print("\n" + "="*80)
print(f"CHAMPIONSHIP TICKET: {ticket['ticket_id']}")
print("="*80)
print(f"Status: {ticket['status']}")
print(f"Model: {ticket['model']}")

if ticket['status'] == 'APPROVED':
    print("\n✓ ALL VALIDATION CHECKS PASSED")
    print("\n→ Model approved for canary deployment")
else:
    print("\n✗ VALIDATION FAILED")
    print("\nFailed checks:")
    for check_name, check in ticket['validation_checklist'].items():
        if check.get('status') == 'FAIL':
            print(f"  - {check_name}")
```

---

## 10. CANARY & PHASED DEPLOYMENT

### 📝 STATUS: DOKUMENTERAD (Ej implementerad)

### Canary Deployment Strategy

```python
# src/core/deployment/canary.py

class CanaryDeployment:
    """
    Staged deployment med gradvis capital allocation.

    Phase 1: Canary (10% capital, 3 days)
    Phase 2: Paper-Live (50% capital, 7 days)
    Phase 3: Full Deploy (100% capital, ongoing)
    """

    PHASES = {
        'canary': {
            'duration_days': 3,
            'capital_allocation': 0.10,
            'min_trades': 10,
            'success_criteria': {
                'min_sharpe': 0.5,
                'max_drawdown': -0.10,
                'min_win_rate': 0.48,
                'max_psi': 0.15
            }
        },
        'paper_live': {
            'duration_days': 7,
            'capital_allocation': 0.50,
            'min_trades': 30,
            'success_criteria': {
                'min_sharpe': 0.8,
                'max_drawdown': -0.12,
                'min_win_rate': 0.50,
                'max_psi': 0.10
            }
        },
        'full_deploy': {
            'duration_days': None,  # Ongoing
            'capital_allocation': 1.00,
            'monitoring': 'continuous'
        }
    }

    def __init__(self, model_path, championship_ticket):
        self.model_path = model_path
        self.ticket = championship_ticket
        self.current_phase = None
        self.phase_start_date = None

    def start_canary(self):
        """Start canary deployment phase."""
        if self.ticket['status'] != 'APPROVED':
            raise ValueError("Cannot deploy unapproved model!")

        self.current_phase = 'canary'
        self.phase_start_date = datetime.now()

        print(f"🐤 CANARY DEPLOYMENT STARTED")
        print(f"Capital allocation: {self.PHASES['canary']['capital_allocation']:.0%}")
        print(f"Duration: {self.PHASES['canary']['duration_days']} days")
        print(f"Min trades required: {self.PHASES['canary']['min_trades']}")

        # Log deployment event
        self._log_deployment_event('canary_started')

    def evaluate_canary_phase(self, live_trades):
        """Evaluera om canary phase var successful."""
        phase_config = self.PHASES['canary']

        # Calculate metrics från live trades under canary
        sharpe = calculate_sharpe(live_trades)
        drawdown = calculate_max_drawdown(live_trades)
        win_rate = calculate_win_rate(live_trades)

        # Check minimum trades
        if len(live_trades) < phase_config['min_trades']:
            return {
                'passed': False,
                'reason': f'Insufficient trades ({len(live_trades)} < {phase_config["min_trades"]})'
            }

        # Check success criteria
        criteria = phase_config['success_criteria']
        checks = {
            'sharpe': sharpe >= criteria['min_sharpe'],
            'drawdown': drawdown >= criteria['max_drawdown'],
            'win_rate': win_rate >= criteria['min_win_rate'],
        }

        all_passed = all(checks.values())

        return {
            'passed': all_passed,
            'metrics': {
                'sharpe': sharpe,
                'drawdown': drawdown,
                'win_rate': win_rate,
                'n_trades': len(live_trades)
            },
            'checks': checks,
            'ready_for_next_phase': all_passed
        }

    def promote_to_paper_live(self):
        """Promote från canary till paper-live."""
        print(f"📈 PROMOTING TO PAPER-LIVE")
        print(f"Capital allocation: {self.PHASES['paper_live']['capital_allocation']:.0%}")

        self.current_phase = 'paper_live'
        self.phase_start_date = datetime.now()

        self._log_deployment_event('promoted_to_paper_live')

    def rollback(self, reason):
        """Rollback deployment och revert till backup."""
        print(f"🚨 ROLLBACK TRIGGERED: {reason}")

        # Switch to backup model
        backup_model = self.ticket['rollback_plan']['rollback_model']

        print(f"→ Reverting to backup: {backup_model}")

        # Notify team
        self._send_alert(
            f"Model rollback: {reason}",
            self.ticket['rollback_plan']['notification']
        )

        self._log_deployment_event('rollback', {'reason': reason})


# Användning:
canary = CanaryDeployment(model_path, championship_ticket)

# Phase 1: Canary
canary.start_canary()
# ... wait 3 days ...
canary_results = canary.evaluate_canary_phase(live_trades)

if canary_results['passed']:
    # Phase 2: Paper-Live
    canary.promote_to_paper_live()
    # ... wait 7 days ...
    paper_results = canary.evaluate_paper_live_phase(live_trades)

    if paper_results['passed']:
        # Phase 3: Full Deploy
        canary.promote_to_full()
    else:
        canary.rollback("Paper-live criteria not met")
else:
    canary.rollback("Canary criteria not met")
```

### Canary Metrics Dashboard

```python
# Daglig rapport under canary phase

def generate_canary_report(canary_deployment, current_trades):
    """Generera daglig rapport för canary phase."""

    days_running = (datetime.now() - canary_deployment.phase_start_date).days
    phase_config = canary_deployment.PHASES[canary_deployment.current_phase]

    print(f"\n{'='*80}")
    print(f"CANARY DEPLOYMENT REPORT - Day {days_running}/{phase_config['duration_days']}")
    print(f"{'='*80}")

    # Current metrics
    metrics = calculate_current_metrics(current_trades)
    criteria = phase_config['success_criteria']

    print(f"\nCurrent Performance:")
    print(f"  Sharpe:    {metrics['sharpe']:.2f} (need: ≥{criteria['min_sharpe']})")
    print(f"  Drawdown:  {metrics['drawdown']:.1%} (need: ≥{criteria['max_drawdown']:.1%})")
    print(f"  Win Rate:  {metrics['win_rate']:.1%} (need: ≥{criteria['min_win_rate']:.1%})")
    print(f"  Trades:    {len(current_trades)} (need: ≥{phase_config['min_trades']})")

    # Progress
    print(f"\nProgress:")
    print(f"  Days:   {days_running}/{phase_config['duration_days']}")
    print(f"  Trades: {len(current_trades)}/{phase_config['min_trades']}")

    # Status
    if all([
        metrics['sharpe'] >= criteria['min_sharpe'],
        metrics['drawdown'] >= criteria['max_drawdown'],
        metrics['win_rate'] >= criteria['min_win_rate']
    ]):
        print(f"\n✓ ON TRACK for promotion")
    else:
        print(f"\n⚠ AT RISK - monitoring closely")
```

---

## 11. KOMPLETT VALIDATION PIPELINE

### 📝 STATUS: DOKUMENTERAD (Ej implementerad)

### Master Validation Script

```python
# scripts/validate_champion_complete.py

"""
Komplett validation pipeline som kör ALLA checks.

Detta är den ENDA vägen till production.
"""

import argparse
import json
from pathlib import Path

def complete_validation_pipeline(symbol, timeframe, model_path, config):
    """
    Kör ALLA validation checks i korrekt ordning.

    Returns:
        Championship ticket (approved eller rejected)
    """
    print("="*80)
    print("COMPLETE CHAMPION VALIDATION PIPELINE")
    print("="*80)

    results = {}

    # 1. Purged WFCV
    print("\n[1/8] Running Purged Walk-Forward CV...")
    wfcv_results = run_purged_wfcv(symbol, timeframe, model_path)
    results['wfcv'] = wfcv_results

    if wfcv_results['stability_score'] < 0.70:
        return reject_model("Failed WFCV stability check")
    print("  ✓ PASS")

    # 2. Holdout Evaluation
    print("\n[2/8] Evaluating on Holdout Set...")
    holdout_results = evaluate_on_holdout(symbol, timeframe, model_path)
    results['holdout'] = holdout_results

    if holdout_results['performance_degradation'] > 0.10:
        return reject_model("Holdout performance degradation > 10%")
    print("  ✓ PASS")

    # 3. Deflated Sharpe
    print("\n[3/8] Calculating Deflated Sharpe...")
    deflated = calculate_deflated_sharpe(
        holdout_results['returns'],
        n_trials=config['n_models_tested'],
        skewness=stats.skew(holdout_results['returns']),
        kurtosis=stats.kurtosis(holdout_results['returns'])
    )
    results['deflated_sharpe'] = deflated

    if deflated['deflated_sharpe'] < 1.0:
        return reject_model("Deflated Sharpe < 1.0 (statistically insignificant)")
    print("  ✓ PASS")

    # 4. PBO Check
    print("\n[4/8] Calculating Probability of Backtest Overfitting...")
    pbo = calculate_pbo(symbol, timeframe, model_path)
    results['pbo'] = pbo

    if pbo['pbo'] > 0.50:
        return reject_model(f"High overfit risk (PBO={pbo['pbo']:.2%})")
    print("  ✓ PASS")

    # 5. Regime Gates
    print("\n[5/8] Validating Regime Robustness Gates...")
    regime_results = validate_regime_gates(symbol, timeframe, model_path)
    results['regime_gates'] = regime_results

    if not regime_results['all_gates_passed']:
        failed = regime_results['failed_regimes']
        return reject_model(f"Failed regime gates: {failed}")
    print("  ✓ PASS")

    # 6. Feature Drift Check
    print("\n[6/8] Checking Feature Drift (PSI)...")
    psi_results = check_feature_drift(symbol, timeframe)
    results['feature_drift'] = psi_results

    max_psi = max(r['psi'] for r in psi_results.values())
    if max_psi > 0.25:
        return reject_model(f"Feature drift detected (PSI={max_psi:.3f})")
    print("  ✓ PASS")

    # 7. Probability Calibration
    print("\n[7/8] Verifying Probability Calibration...")
    calibration = verify_calibration(symbol, timeframe, model_path)
    results['calibration'] = calibration

    if calibration['ece'] > 0.15:  # Expected Calibration Error
        print("  ⚠ WARNING: Poor calibration (consider recalibration)")
    else:
        print("  ✓ PASS")

    # 8. Provenance & Reproducibility
    print("\n[8/8] Creating Provenance Record...")
    provenance = create_provenance_record(model_path, results)
    results['provenance'] = provenance
    print("  ✓ PASS")

    # Generate Championship Ticket
    print("\n" + "="*80)
    print("GENERATING CHAMPIONSHIP TICKET")
    print("="*80)

    ticket = create_championship_ticket(
        model_path,
        results['wfcv'],
        results['regime_gates'],
        results['pbo'],
        results['deflated_sharpe']['deflated_sharpe']
    )

    # Generate Model Card
    model_card = generate_model_card(model_path, results)

    # Save everything
    save_validation_results(model_path, results, ticket, model_card)

    # Final verdict
    print("\n" + "="*80)
    if ticket['status'] == 'APPROVED':
        print("🏆 CHAMPION APPROVED FOR DEPLOYMENT")
        print("="*80)
        print("\nNext steps:")
        print("1. Start canary deployment (10% capital, 3 days)")
        print("2. Monitor daily performance")
        print("3. Promote to paper-live if successful")
    else:
        print("🚫 CHAMPION REJECTED")
        print("="*80)
        print("\nReason: Model failed critical validation checks")
        print("→ Review failed checks and retrain")

    return ticket


def main():
    parser = argparse.ArgumentParser(
        description="Complete champion validation pipeline"
    )
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--config", default="config/validation_config.json")

    args = parser.parse_args()

    # Load validation config
    with open(args.config) as f:
        config = json.load(f)

    # Run complete pipeline
    ticket = complete_validation_pipeline(
        args.symbol,
        args.timeframe,
        Path(args.model),
        config
    )

    # Exit code baserat på approval
    sys.exit(0 if ticket['status'] == 'APPROVED' else 1)


if __name__ == "__main__":
    main()
```

### Canary Monitoring Script

```bash
# Kör DAGLIGEN under canary phase

python scripts/monitor_canary.py \
  --ticket results/championship_tickets/CHAMP-20251009-143022.json \
  --trades logs/live_trades.json

# Output:
# CANARY DAY 1/3
#   Trades: 3 (need 10)
#   Sharpe: 1.2 ✓
#   Drawdown: -3% ✓
#   Status: ON TRACK
```

---

## 📊 VALIDATION CONFIG

### Skapa: `config/validation_config.json`

```json
{
  "purged_wfcv": {
    "n_splits": 6,
    "train_ratio": 0.6,
    "embargo_pct": 0.02,
    "min_stability_score": 0.7,
    "min_worst_case_auc": 0.6
  },

  "holdout": {
    "size_pct": 0.2,
    "max_performance_degradation": 0.1
  },

  "overfit_detection": {
    "deflated_sharpe_threshold": 1.0,
    "pbo_threshold": 0.5,
    "n_trials_tested": 50
  },

  "drift_monitoring": {
    "psi_threshold": 0.25,
    "psi_warning": 0.1,
    "ks_alpha": 0.05,
    "monitoring_frequency_days": 1
  },

  "regime_gates": {
    "bull": { "min_sharpe": 1.0, "max_drawdown": -0.2 },
    "bear": { "min_sharpe": 0.0, "max_drawdown": -0.15 },
    "ranging": { "min_sharpe": 0.3, "max_drawdown": -0.18 }
  },

  "hysteresis": {
    "score_improvement_threshold": 0.5,
    "cooldown_days": 7,
    "min_switch_confidence": 0.8
  },

  "transaction_costs": {
    "maker_fee": 0.001,
    "taker_fee": 0.002,
    "base_slippage_bps": 2.0,
    "latency_bars": 1,
    "fill_probability": 0.95
  },

  "canary_deployment": {
    "phase_1_days": 3,
    "phase_1_capital": 0.1,
    "phase_2_days": 7,
    "phase_2_capital": 0.5,
    "rollback_conditions": {
      "consecutive_losses": 5,
      "max_drawdown": -0.15,
      "psi_critical": 0.25
    }
  }
}
```

---

## 🎯 COMPLETE WORKFLOW: Training → Production

### Komplett Command Sequence

```bash
# ============================================================================
# PHASE 1: DATA PREPARATION
# ============================================================================

# 1. Fetch historical data (minimum 6 months för 1h)
python scripts/fetch_historical.py \
  --symbol tBTCUSD --timeframe 1h --months 6

# 2. Precompute features (Feather format)
python scripts/precompute_features.py \
  --symbol tBTCUSD --timeframe 1h


# ============================================================================
# PHASE 2: MODEL TRAINING (med Holdout)
# ============================================================================

# 3. Tune triple-barrier parameters
python scripts/tune_triple_barrier.py \
  --symbol tBTCUSD --timeframe 1h

# 4. Generate meta-labels
python scripts/generate_meta_labels.py \
  --symbol tBTCUSD --timeframe 1h \
  --profit-multiplier 1.0 --stop-multiplier 0.6 --max-holding 36

# 5. Train model WITH HOLDOUT
python scripts/train_model.py \
  --symbol tBTCUSD --timeframe 1h \
  --version v12_production \
  --use-holdout \
  --save-provenance


# ============================================================================
# PHASE 3: VALIDATION (Complete Pipeline)
# ============================================================================

# 6. Run complete validation pipeline
python scripts/validate_champion_complete.py \
  --symbol tBTCUSD --timeframe 1h \
  --model config/models/tBTCUSD_1h_v12_production.json \
  --config config/validation_config.json

# Output: Championship ticket (APPROVED eller REJECTED)


# ============================================================================
# PHASE 4: DEPLOYMENT (om APPROVED)
# ============================================================================

# 7. Start canary deployment
python scripts/deploy_canary.py \
  --ticket results/championship_tickets/CHAMP-20251009-143022.json

# 8. Monitor canary (kör DAGLIGEN i 3 dagar)
python scripts/monitor_canary.py \
  --ticket results/championship_tickets/CHAMP-20251009-143022.json \
  --trades logs/live_trades.json

# 9. Evaluate och promote (efter 3 dagar)
python scripts/evaluate_canary.py \
  --ticket results/championship_tickets/CHAMP-20251009-143022.json

# Om successful → auto-promote to paper-live
# Om failed → auto-rollback


# ============================================================================
# PHASE 5: ONGOING MONITORING
# ============================================================================

# 10. Daily drift monitoring
python scripts/monitor_production_drift.py \
  --model config/models/tBTCUSD_1h_champion.json \
  --trades logs/live_trades.json

# 11. Weekly PSI check
python scripts/check_feature_drift.py \
  --symbol tBTCUSD --timeframe 1h

# 12. Monthly full validation
python scripts/validate_champion_complete.py \
  --symbol tBTCUSD --timeframe 1h \
  --model config/models/tBTCUSD_1h_champion.json
```

---

## ✅ PRODUCTION READINESS CHECKLIST (ADVANCED)

### Pre-Deployment Validation

- [ ] **Purged WFCV completed**

  - [ ] Embargo period = max holding period
  - [ ] Minimum 5 splits
  - [ ] Stability score > 0.70
  - [ ] Worst case AUC > 0.60
  - [ ] Purged overlapping samples

- [ ] **Holdout evaluation completed**

  - [ ] 20% holdout set UNTOUCHED during training
  - [ ] Performance degradation < 10%
  - [ ] Holdout AUC > 0.65
  - [ ] Holdout Sharpe > 0.8

- [ ] **Overfit detection completed**

  - [ ] Deflated Sharpe > 1.0
  - [ ] PBO score < 0.50
  - [ ] Multiple testing correction applied

- [ ] **Regime gates passed**

  - [ ] Bear market Sharpe ≥ 0 (MUST protect capital)
  - [ ] Bull market Sharpe ≥ 1.0
  - [ ] Ranging market Sharpe ≥ 0.3
  - [ ] All regime gates PASSED

- [ ] **Calibration verified**

  - [ ] ECE (Expected Calibration Error) < 0.15
  - [ ] Reliability diagram reviewed
  - [ ] Isotonic/Temperature calibration applied

- [ ] **Drift monitoring setup**

  - [ ] PSI baseline calculated for all features
  - [ ] K-S test baseline established
  - [ ] Alert thresholds configured
  - [ ] Monitoring scripts scheduled

- [ ] **Realistic backtest completed**

  - [ ] Transaction costs included (fees + slippage)
  - [ ] Latency simulation (execution delay)
  - [ ] Partial fill simulation
  - [ ] Volume impact considered

- [ ] **Provenance & Reproducibility**

  - [ ] Data hash recorded
  - [ ] Config hash recorded
  - [ ] Environment captured
  - [ ] Reproducibility verified

- [ ] **Documentation completed**

  - [ ] Model Card generated
  - [ ] Championship Ticket approved
  - [ ] Deployment plan documented
  - [ ] Rollback plan defined

- [ ] **Deployment infrastructure ready**
  - [ ] Canary phase planned
  - [ ] Monitoring dashboard configured
  - [ ] Alert system tested
  - [ ] Backup model identified

### During Deployment

- [ ] **Canary phase (3 days)**

  - [ ] 10% capital allocation
  - [ ] Daily performance monitoring
  - [ ] PSI check after each day
  - [ ] Success criteria met

- [ ] **Paper-live phase (7 days)**

  - [ ] 50% capital allocation
  - [ ] Daily drift monitoring
  - [ ] Performance vs backtest comparison
  - [ ] No drift detected

- [ ] **Full deployment**
  - [ ] 100% capital allocation
  - [ ] Continuous monitoring
  - [ ] Weekly PSI checks
  - [ ] Monthly full revalidation

---

## 🚨 KRITISKA DECISION POINTS

### 1. REJECT Model if:

```
ANY of these are true:
- WFCV stability score < 0.70
- PBO > 0.50
- Deflated Sharpe < 1.0
- ANY regime gate fails (especially bear market)
- Holdout degradation > 10%
- PSI > 0.25 on any feature
```

### 2. ROLLBACK Deployment if:

```
ANY of these occur during canary/paper-live:
- 5 consecutive losing trades
- Drawdown > 15%
- Live Sharpe < 0 for 3 days
- PSI > 0.25 (feature drift)
- K-S test rejects (p < 0.05)
```

### 3. EMERGENCY STOP if:

```
IMMEDIATE stop trading if:
- Drawdown > 25%
- Live Sharpe < -1.0
- Unexpected error rate > 5%
- Exchange API issues
```

---

## 📚 ACADEMIC REFERENCES

1. **Bailey & López de Prado (2014)**: "The Deflated Sharpe Ratio"
2. **Bailey et al. (2015)**: "The Probability of Backtest Overfitting"
3. **López de Prado (2018)**: "Advances in Financial Machine Learning" - Chapter 7 (Cross-Validation), Chapter 11 (Backtesting)
4. **Niculescu-Mizil & Caruana (2005)**: "Predicting Good Probabilities With Supervised Learning"
5. **Guo et al. (2017)**: "On Calibration of Modern Neural Networks"

---

## 🎓 SUMMARY: Enterprise Production Standards

**10 kritiska områden med implementation status:**

### ✅ IMPLEMENTERAT (Phase-5 Complete)

1. ✅ **Purged WFCV** - Eliminera data leakage (`scripts/validate_purged_wfcv.py`)
2. ✅ **Deflated Sharpe + PBO** - Detektera overfit (`src/core/ml/overfit_detection.py`)
3. ✅ **Probability Calibration** - Redan implementerat! (`core/ml/calibration.py`)
4. ✅ **Feature/Label Drift** - PSI & K-S monitoring (`scripts/monitor_feature_drift.py`)
5. ✅ **Regime Gates** - Hårda robustness requirements (`scripts/validate_regime_gates.py`)
6. ✅ **Reproducerbarhet** - Data/config hashar (`src/core/utils/provenance.py`)

### 📝 DOKUMENTERAT (Redo att implementera - Phase 6)

5. 📝 **Hysteresis & Cooldown** - Stabil champion switching (Dokumenterad)
6. 📝 **Realistisk Backtest** - Costs, latency, partial fills (Dokumenterad)
7. 📝 **Model Card + Ticket** - Production documentation (Dokumenterad)
8. 📝 **Canary Deployment** - Phased rollout (Dokumenterad)

**Phase-5: SOLID FOUNDATION för Production ML! 🚀**
**Phase-6: Complete end-to-end production pipeline! 🎯**

---

## 🚀 NEXT STEPS

### ✅ Phase-5 COMPLETED

1. ✅ Implementera Purged WFCV script
2. ✅ Uppdatera train_model.py med holdout
3. ✅ Implementera deflated Sharpe calculation
4. ✅ Skapa PBO check
5. ✅ Setup PSI monitoring
6. ✅ Implementera regime gates validation
7. ✅ Skapa provenance tracking

### 🎯 Phase-6: Production Pipeline (Next Sprint)

1. **Immediate Priority (Week 1-2)**

   - [ ] Skapa complete validation pipeline script
   - [ ] Implementera model card generator
   - [ ] Implementera championship ticket system

2. **High Priority (Week 3-4)**

   - [ ] Implementera hysteresis & cooldown mechanism
   - [ ] Implementera transaction costs model
   - [ ] Setup canary deployment infrastructure

3. **Medium Priority (Month 2)**
   - [ ] Implementera latency simulation
   - [ ] Create production monitoring dashboard
   - [ ] Setup automated alerting system

---

**Phase-5 Status:** ✅ COMPLETE - Core validation infrastructure ready!
**Phase-6 Impact:** 🎯 COMPLETE production deployment pipeline
**ROI:** 🚀 MASSIVE - enterprise-grade ML operations
