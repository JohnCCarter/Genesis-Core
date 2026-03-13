# Phased Optuna v3 Results — tBTCUSD 3h

Run date: 2026-03-11
Branch: `feature/Optuna-Phased-Claude`
Score version: v2 (Sharpe-first with capped bonuses)

## Phase A: Threshold + Exit Optimisation

- **13 tunable parameters**, 150 trials, TPE sampler
- IS: 2024-01-02 to 2024-12-31 | OOS: 2025-01-01 to 2025-12-31
- Run ID: `phaseA_full_150t`

### Best Trial (trial_043)

| Metric | In-Sample (2024) | OOS (2025) |
|--------|-----------------|------------|
| Score | 0.1432 | 0.1031 |
| Return | -3.09% | -9.86% |
| Profit Factor | 1.37 | 1.30 |
| Max Drawdown | 7.68% | 12.28% |
| Sharpe Ratio | 0.112 | 0.088 |
| Win Rate | 62.5% | 62.3% |
| Trades | 216 | 204 |

### Best Parameters

```yaml
thresholds:
  entry_conf_overall: 0.25  # fixed (inert with zones)
  regime_proba.balanced: 0.36
  zones:
    low:  { entry_conf_overall: 0.16, regime_proba: 0.33 }
    mid:  { entry_conf_overall: 0.40, regime_proba: 0.51 }
    high: { entry_conf_overall: 0.32, regime_proba: 0.57 }
exit:
  exit_conf_threshold: 0.42
  max_hold_bars: 8
  trailing_stop_pct: 0.022
risk:
  htf_regime_size_multipliers.bear: 0.30
  volatility_sizing.high_vol_multiplier: 0.80
multi_timeframe:
  ltf_override_threshold: 0.40
```

---

## Phase B v2: Regime Intelligence Clarity + Sizing

- **7 tunable parameters** (+ 32 fixed from Phase A best)
- 100 trials, TPE sampler
- Phase A best pinned directly as fixed values in YAML
- Run ID: `phaseB_v2_100t`

### Best Trial (trial_001)

| Metric | In-Sample (2024) | OOS (2025) |
|--------|-----------------|------------|
| Score | 0.3331 | 0.1619 |
| Return | +3.63% | -2.93% |
| Profit Factor | 2.04 | 1.46 |
| Max Drawdown | 1.88% | 5.47% |
| Sharpe Ratio | 0.251 | 0.124 |
| Win Rate | 61.1% | 64.8% |
| Trades | 108 | 122 |

### Best Parameters (RI-specific)

```yaml
regime_intelligence:
  authority_mode: regime_module  # dominant factor
  clarity_score:
    weights:
      confidence: 0.40
      edge: 0.30
      ev: 0.10
      regime_alignment: 0.20  # Dirichlet remainder
  size_multiplier:
    min: 0.30
    max: 1.00
risk:
  htf_regime_size_multipliers.bear: 0.60  # re-tuned higher with RI
```

---

## Phase A vs Phase B v2 Comparison

### In-Sample (2024)

| Metric | Phase A | Phase B v2 | Delta |
|--------|---------|------------|-------|
| Score | 0.1432 | **0.3331** | **+133%** |
| Return | -3.09% | **+3.63%** | +6.72pp |
| PF | 1.37 | **2.04** | +49% |
| Max DD | 7.68% | **1.88%** | **-75%** |
| Sharpe | 0.112 | **0.251** | +124% |
| Trades | 216 | 108 | -50% |

### OOS Validation (2025)

| Metric | Phase A | Phase B v2 | Delta |
|--------|---------|------------|-------|
| Score | 0.1031 | **0.1619** | **+57%** |
| Return | -9.86% | **-2.93%** | +6.93pp |
| PF | 1.30 | **1.46** | +12% |
| Max DD | 12.28% | **5.47%** | **-55%** |
| Sharpe | 0.088 | **0.124** | +41% |
| Trades | 204 | 122 | -40% |

---

## Key Finding

**`authority_mode=regime_module` is the dominant factor.** All 100 trials
in Phase B produced only two distinct outcomes — one per authority_mode value.
Clarity weights (confidence/edge/ev) had zero observable effect on results.

### Root Cause: Two Config Key Bugs in `decision.py`

Investigation revealed two bugs that caused clarity weights and size_multiplier
to be silently ignored:

**Bug 1 — Weights key mismatch (`decision.py:1258`):**
Code read `clarity_cfg.get("weights_v1")` but config stores weights under key
`"weights"`. Result: `weights=None` passed to `compute_clarity_score_v1`, which
fell back to hardcoded defaults `{confidence: 0.5, edge: 0.2, ev: 0.2,
regime_alignment: 0.1}` for ALL trials regardless of Optuna suggestions.

**Bug 2 — Size multiplier wrong lookup (`decision.py:1244-1245`):**
Code read `clarity_cfg.get("size_multiplier_min")` (inside `clarity_score` dict)
but `size_multiplier` is a sibling of `clarity_score` under `regime_intelligence`.
Result: always used defaults `min=0.5, max=1.0` instead of configured values.

**Fix:** Both bugs fixed in commit (see below). `weights` key now read correctly,
`size_multiplier` now read from `ri_cfg` instead of `clarity_cfg`.

**Impact on Phase B v2 results:** These results only reflect the
`authority_mode` difference. Clarity weights and size_multiplier had no effect.
Phase B should be re-run after the fix to get valid results.

Phase A results are unaffected (RI was disabled, `authority_mode=legacy`).
