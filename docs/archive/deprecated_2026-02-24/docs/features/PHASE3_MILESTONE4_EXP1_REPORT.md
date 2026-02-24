# Phase 3 Milestone 4 - Experiment 4.1: EVGate Tuning - REPORT

**Date**: 2026-02-03
**Branch**: `feature/composable-strategy-phase2`
**Config**: `v6a_evgate_exp1.yaml`
**Change**: EVGate min_ev 0.0 → 0.05 (config-only)

---

## Executive Summary

**Result**: **MILESTONE-4-FAIL** ❌

**Both primary criteria FAILED**:
- ❌ PF: 1.34 < 1.50 target (decreased from v5a 1.45)
- ❌ PF utan top-3: 1.23 < 1.25 threshold (decreased from v5a 1.30)

**Critical Finding**: EVGate min_ev=0.05 is **TOO AGGRESSIVE**. Filters out 44.8% of signals, including GOOD trades. Result: Lower PF AND lower robustness.

**Verdict**: **Reject v6a**, do NOT accept this experiment.

---

## Comparison: v5a Baseline vs v6a Experiment 4.1

| Metric | v5a Baseline | v6a Exp 4.1 | Change | Assessment |
|--------|--------------|-------------|--------|------------|
| **Trades/year** | 413 | 272 | -34% | ⚠️ Significant reduction |
| **Full year PF** | 1.45 | 1.34 | -8% | ❌ **WORSE** |
| **PF utan top-1** | 1.40 | 1.30 | -7% | ⚠️ Worse |
| **PF utan top-3** | 1.30 | 1.23 | -5% | ❌ **FAIL** (<1.25) |
| **Top-1 PnL %** | 11.0% | 11.3% | +0.3pp | ✅ Unchanged (good) |
| **Top-5 PnL %** | 50.8% | 50.7% | -0.1pp | ✅ Unchanged |
| **MaxDD** | 1.25% | 1.36% | +9% | ⚠️ Slightly worse |
| **Fees/trade** | $0.34 | $0.33 | -3% | ✅ Marginal improvement |
| **EVGate veto rate** | 0% | 44.8% | +44.8pp | ⚠️ Very aggressive |

---

## Milestone 4 Goals Assessment

| Goal | Target | v5a | v6a | Status |
|------|--------|-----|-----|--------|
| **PF recovery** | >= 1.50 | 1.45 | 1.34 | ❌ **FAIL** (worse) |
| **Robustness maintained** | >= 1.25 | 1.30 | 1.23 | ❌ **FAIL** (<1.25) |
| Concentration | < 30% | 11.0% | 11.3% | ✅ PASS |
| MaxDD | <= 3.5% | 1.25% | 1.36% | ✅ PASS |

**Overall**: 2/4 goals pass, **2/4 FAIL** (both primary goals failed)

---

## (1) Profit Factor Overview

**Full 2024**: PF = 1.34 (272 trades)
- vs v5a: 1.45 → 1.34 (-0.11, 8% decrease) ❌

**Quarterly Breakdown**:
- Q1 2024: PF = 1.21 (58 trades) ⚠️ Below 1.3 target
- Q2 2024: PF = 1.14 (65 trades) ⚠️ Below 1.3 target
- Q3 2024: PF = 1.00 (76 trades) ❌ **Break-even quarter**
- Q4 2024: PF = 2.00 (54 trades) ✅ Strong

**Interpretation**: Q3 became break-even (PF 1.00), Q1 and Q2 fell below 1.3 threshold. Only Q4 remains strong. EVGate filtering degraded consistency.

---

## (2) PnL Concentration

**Top-1 Trade**: $15.08 (11.3% of total PnL) ✅
- vs v5a: 11.0% → 11.3% (+0.3pp, unchanged)

**Top-5 Trades**: $67.75 (50.7% of total PnL)
- vs v5a: 50.8% → 50.7% (-0.1pp, unchanged)

**Interpretation**: Concentration metrics unchanged. EVGate filtering did not improve or worsen concentration.

---

## (3) PF Robustness

**PF without top-1**: 1.30 (was 1.34)
- Drop: 0.04 (3.0%)
- vs v5a: 1.40 → 1.30 (-0.10, 7% worse)

**PF without top-3**: 1.23 (was 1.34) ❌ **FAIL threshold 1.25**
- Drop: 0.11 (8.2%)
- vs v5a: 1.30 → 1.23 (-0.07, 5% worse)

**Interpretation**: **Robustness DEGRADED**. PF utan top-3 fell from 1.30 → 1.23, now **BELOW 1.25 threshold**. This is a critical failure - we lost the robustness gain from Milestone 3.

---

## (4) Component Attribution

**Total decisions**: 8639
**Allowed**: 1750 (20.3%)
**Vetoed**: 6889 (79.7%)

**Veto Breakdown**:
- ml_confidence: 0 (0.0%)
- RegimeFilter: 0 (0.0%)
- **EVGate**: 3868 (44.8%) ← **Primary filter**
- CooldownComponent: 3021 (35.0%)

**Interpretation**: EVGate with min_ev=0.05 filters out 44.8% of signals. This is very aggressive filtering, but it's filtering out GOOD trades along with bad ones, resulting in lower overall PF.

---

## (5) Risk Sanity

- **Max Drawdown**: 1.36% (was 1.25% in v5a) ⚠️ +9%
- **Fees per trade**: $0.33 (was $0.34 in v5a) ✅ -3%

**Interpretation**: MaxDD increased slightly by 9%. Still well below 3.5% threshold, but moving in wrong direction.

---

## Root Cause Analysis: Why Did This Fail?

**Hypothesis**: EVGate min_ev=0.05 would filter out bottom ~20% of signals by EV, improving average trade quality → higher PF.

**Result**: Hypothesis **REJECTED**

**What actually happened**:
1. EVGate filtered out 44.8% of signals (more than expected 20%)
2. Trade count dropped from 413 → 272 (-34%)
3. **BUT**: Average trade quality DECREASED, not increased
   - PF: 1.45 → 1.34 (-8%)
   - PF utan top-3: 1.30 → 1.23 (-5%)

**Why did this happen?**

### Theory 1: EV Calculation is Noisy

Expected Value (EV) might be a **noisy predictor** of actual trade quality. Filtering by EV could be removing trades with low predicted EV but high actual outcome.

Evidence:
- Q3 became break-even (PF 1.00) - suggests we removed profitable trades
- PF decreased despite filtering supposedly "bad" trades

### Theory 2: EV Threshold is Too High

min_ev=0.05 might be filtering too aggressively. We expected ~20% veto rate but got 44.8%. This suggests the EV distribution is heavily skewed toward low values, and a threshold of 0.05 is too high.

Evidence:
- 44.8% veto rate (more than double expected 20%)
- From Milestone 1: EV distribution had mean=0.064, so 0.05 is close to median

### Theory 3: Lower Confidence Signals Have Different EV Distribution

v5a baseline uses risk_map threshold 0.53 (lower than original 0.6). These lower-confidence signals might have systematically different EV characteristics than higher-confidence ones.

Evidence:
- v5a has 413 trades with lower confidence threshold
- EVGate filtering might be removing the "medium confidence" trades that actually perform well

---

## Interpretation: Quality-Quantity Trade-off

**v5a strategy**: Lower confidence threshold (0.53) → more trades (413) → robust but slightly lower PF (1.45)

**v6a strategy**: Add EVGate filtering (min_ev=0.05) → fewer trades (272) → **worse PF (1.34) AND worse robustness (1.23)**

**Conclusion**: EVGate min_ev=0.05 is the WRONG direction. We got the worst of both worlds:
- Fewer trades (272 vs 413) → less diversification
- Lower PF (1.34 vs 1.45) → worse quality
- Lower robustness (1.23 vs 1.30) → fails Milestone 3 achievement

---

## Decision Framework

**Option A**: Try lower EVGate threshold (0.02 or 0.03)
- Goal: Reduce veto rate from 44.8% to ~15-20%
- Hope: Filter only truly bad trades, keep good ones
- Risk: Might still have noisy EV problem

**Option B**: Abandon EVGate tuning, try ml_confidence threshold instead
- Goal: Filter by confidence directly (more direct signal quality proxy)
- Threshold: Increase from 0.24 to ~0.26-0.28 (careful)
- Expected: 15-20% veto rate, better quality filtering

**Option C**: Accept v5a as final baseline, move to production
- Rationale: v5a already achieves Milestone 3 goals (robustness)
- PF 1.45 is acceptable (only 0.05 below 1.50 target)
- Further tuning risks breaking robustness

**Option D**: Combine sizing + EVGate adjustments (NOT config-only)
- Adjust risk_map back toward 0.55-0.56 (slightly higher)
- Use EVGate 0.02-0.03 to compensate
- Goal: 320-350 trades with PF 1.50+
- Risk: Requires re-tuning multiple parameters, breaks Milestone 4 rules

---

## Recommendation

**Recommendation**: **Option B** (try ml_confidence threshold instead)

**Rationale**:
1. EVGate appears to be a noisy filter (EV prediction doesn't match actual outcomes)
2. ml_confidence is a more direct proxy for trade quality
3. Still config-only (within Milestone 4 rules)
4. If ml_confidence also fails, fall back to Option C (accept v5a)

**Alternative if pressed for time**: **Option C** (accept v5a as final)
- v5a PF 1.45 is only 3.3% below 1.50 target
- v5a robustness 1.30 is 8.3% above 1.25 threshold (buffer)
- Further tuning risks breaking Milestone 3 achievement
- "Perfect is the enemy of good"

---

## Artifacts

**Config**: `config/strategy/composable/phase2/v6a_evgate_exp1.yaml`

**Script**: `scripts/run_milestone4_exp1.py`

**Results**: `results/milestone4/v6a_evgate_exp1_full2024_20260203_112500.json`

**Report**: `docs/features/PHASE3_MILESTONE4_EXP1_REPORT.md` (this file)

---

## Lessons Learned

1. **EV is a noisy predictor**: Filtering by expected value doesn't guarantee better actual outcomes. The EV calculation might not capture all factors that determine trade quality.

2. **Aggressive filtering can backfire**: 44.8% veto rate removed too many trades, including good ones. Less is sometimes more.

3. **Robustness is fragile**: Milestone 3 achievement (PF utan top-3 = 1.30) was hard-won. Aggressive filtering broke it (1.23). Must guard robustness carefully.

4. **Component interaction matters**: v5a uses lower confidence threshold (0.53). EVGate filtering on these signals might behave differently than on higher-confidence signals.

5. **Q3 break-even is a red flag**: When a quarter hits PF 1.00, it's a strong signal that filtering is removing profitable trades.

---

**Experiment 4.1 Status**: COMPLETE - **REJECTED**, do NOT accept v6a
**Next Step**: Awaiting decision on Option A/B/C (retry EVGate / try ml_confidence / accept v5a)
