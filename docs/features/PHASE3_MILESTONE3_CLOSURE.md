# Phase 3 Milestone 3: Sizing Policy Review - CLOSURE

**Date**: 2026-02-03
**Branch**: `feature/composable-strategy-phase2`
**Status**: ✅ CLOSED - v5a accepted as baseline
**Baseline Config**: `v5a_sizing_exp1.yaml`

---

## Executive Summary

**Milestone 3 (Sizing Policy Review) is COMPLETE** with v5a established as Phase 3 baseline.

**Primary Goal ACHIEVED**: PF robustness (PF utan top-3 >= 1.2) ✅
- Result: 1.30 (was 1.07 in v4a)
- Concentration risk eliminated: top-1 = 11.0% (was 40.7%)

**Baseline Performance** (Full 2024, v5a):
- Trades: 413 (was 63 in v4a)
- Profit Factor: 1.45 (was 1.59 in v4a)
- Win Rate: Not recorded (focus on PF)
- Max Drawdown: 1.25% (was 2.18% in v4a)
- PF utan top-3: 1.30 (was 1.07 in v4a) ✅ **PASS**
- Top-1 PnL: 11.0% (was 40.7% in v4a) ✅ **PASS**

---

## What Changed: v4a → v5a

**Single Config Change**: risk.risk_map first threshold 0.6 → 0.53

**Impact**:

| Metric | v4a Baseline | v5a Sizing Exp1 | Change | Assessment |
|--------|--------------|-----------------|--------|------------|
| **Trades/year** | 63 | 413 | +550% | ✅ Goal achieved |
| **size>0 rate** | 1.4% | 58.3% | +4057% | ✅ Bottleneck fixed |
| **PF helår** | 1.59 | 1.45 | -9% | ⚠️ Trade-off |
| **PF utan top-1** | 1.35 | 1.40 | +4% | ✅ Improved |
| **PF utan top-3** | 1.07 | 1.30 | +21% | ✅ **PRIMARY GOAL** |
| **Top-1 PnL %** | 40.7% | 11.0% | -73% | ✅ Risk eliminated |
| **Top-5 PnL %** | 120.4% | 50.8% | -58% | ✅ Better diversification |
| **MaxDD** | 2.18% | 1.25% | -43% | ✅ Improved |
| **Fees/trade** | $1.43 | $0.34 | -76% | ✅ Smaller positions |

---

## Why This Was The Right Move

### 1. Robustness > Peak PF

**v4a problem**: High PF (1.59) but **fragile** - collapsed to 1.07 when top-3 trades removed.

**v5a solution**: Slightly lower PF (1.45) but **robust** - maintains 1.30 when top-3 trades removed.

**For production**: Consistency and robustness matter more than peak performance. A strategy that holds up under stress is more valuable than one that depends on rare outliers.

### 2. Statistical Stability

**v4a**: 63 trades/year → high variance, insufficient sample size
**v5a**: 413 trades/year → low variance, statistically significant

More trades = better confidence in metrics, easier to detect degradation, more stable in live trading.

### 3. Eliminated Concentration Risk

**v4a**: Top-1 trade = 40.7% of yearly PnL → extreme risk
**v5a**: Top-1 trade = 11.0% of yearly PnL → acceptable risk

Strategy no longer depends on capturing rare 10%+ moves.

### 4. Diversification Improved MaxDD

Despite 6.5x more trades, MaxDD **improved** from 2.18% → 1.25%. More trades = better diversification = smoother equity curve.

### 5. Component Chain Now Meaningful

**v4a**: 63 trades → cannot afford component filtering (would starve strategy)
**v5a**: 413 trades → can afford 20-30% component veto rate for quality improvement

This enables Milestone 4 (Component Quality Tuning).

---

## Trade-off: Quality vs Quantity

**Accepted trade-off**: Lower average PF per trade (1.59 → 1.45) in exchange for:
- Better robustness (1.07 → 1.30 without top-3)
- Lower concentration risk (40.7% → 11.0% top-1)
- More statistical stability (63 → 413 trades)
- Better MaxDD (2.18% → 1.25%)

**This is the correct direction for production deployment**.

---

## HQT-Pass Criteria Assessment

| # | Criterion | Target | v4a | v5a | Verdict |
|---|-----------|--------|-----|-----|---------|
| 1 | Helår PF | >= 1.5 | 1.59 ✅ | 1.45 ❌ | Close (0.05 miss) |
| 2 | 3/4 kvartal PF | >= 1.3 | 4/4 ✅ | 4/4 ✅ | PASS |
| 3 | Inget kvartal | < 1.0 | 1.67 ✅ | 1.30 ✅ | PASS |
| 4 | **PF utan top-3** | **>= 1.2** | **1.07 ❌** | **1.30 ✅** | **PASS** ✅ |
| 5 | **Top-1 PnL** | **< 30%** | **40.7% ❌** | **11.0% ✅** | **PASS** ✅ |
| 6 | MaxDD | <= 3.5% | 2.18% ✅ | 1.25% ✅ | PASS |

**v4a Overall**: HQT-FAIL (robustness + concentration fail)
**v5a Overall**: HQT-FAIL (only full year PF 1.45 < 1.5 fails, 5/6 pass)

**Milestone 3 Primary Goal**: PF utan top-3 >= 1.2 → **ACHIEVED** ✅

---

## Mechanism: Why Did This Work?

**Root cause of v4a fragility**: ATR sizing bottleneck
- 98.6% of component-allowed signals had size==0
- Only 1.4% got non-zero size (66 attempts → 63 executions)
- Low trade count → high outlier dependence

**v5a fix**: Lower risk_map threshold (0.6 → 0.53)
- More signals qualify for non-zero size (conf >= 0.53 vs >= 0.6)
- size>0 rate: 1.4% → 58.3% (41x improvement)
- Trade attempts: 66 → 1167 (17.7x increase)
- Executions: 63 → 413 (6.5x increase)
- More trades → diversification → robustness

**Why PF decreased slightly**: Lower confidence signals have lower average edge, but the diversification benefit outweighs the individual trade quality decrease.

---

## Experiments Run

### Experiment 3.1: risk_map threshold 0.6 → 0.53 ✅ ACCEPTED

**Config**: `config/strategy/composable/phase2/v5a_sizing_exp1.yaml`

**Results**:
- Primary goal achieved (PF utan top-3: 1.30 >= 1.2)
- Concentration eliminated (top-1: 11.0% < 30%)
- Trade frequency sufficient (413 trades)
- Trade-off acceptable (PF 1.45 vs 1.59)

**Decision**: Accepted as Milestone 3 baseline (2026-02-03)

---

## Artifacts

**Configs Created**:
- `config/strategy/composable/phase2/v5a_sizing_exp1.yaml` (accepted baseline)

**Results**:
- `results/milestone3/v5a_sizing_exp1_full2024_20260203_110625.json`

**Scripts**:
- `scripts/run_milestone3_exp1.py` (experiment runner with HQT audit)

**Documentation**:
- `docs/features/PHASE3_MILESTONE3_EXP1_REPORT.md` (detailed experiment report)
- `docs/features/PHASE3_MILESTONE3_CLOSURE.md` (this file)

---

## Lessons Learned

### 1. risk_map Threshold is Powerful

Single parameter change (0.6 → 0.53) increased trades by 6.5x. This was the correct lever to address the sizing bottleneck.

### 2. More Trades = Better Robustness

413 trades eliminated outlier dependence. PF without top-3 improved from 1.07 → 1.30 purely through diversification.

### 3. Quality-Quantity Trade-off is Real

Lower threshold → more "medium quality" trades → slightly lower overall PF (1.59 → 1.45). But the robustness gain (1.07 → 1.30) more than compensates.

### 4. MaxDD Improved with More Trades

Despite 6.5x more trades, MaxDD improved by 43% (2.18% → 1.25%). Diversification smooths equity curve.

### 5. Component Chain Now Unlocked

With 413 trades, we can afford component filtering (20-30% veto rate) without starving the strategy. This enables quality tuning in Milestone 4.

### 6. Fees Per Trade Decreased

Lower confidence signals → smaller positions → lower fees per trade ($1.43 → $0.34). Cost efficiency improved.

---

## Next Steps: Milestone 4 (Component Quality Tuning)

**Goal**: Improve PF from 1.45 → 1.50+ via component filtering without sacrificing robustness.

**Constraints**:
- Do NOT touch sizing again (v5a risk_map is locked)
- Config-only
- One component/knob per experiment
- Maintain PF utan top-3 >= 1.25 (buffer from 1.2 threshold)

**Approach**:
1. Start with EVGate tuning (percentile-based threshold)
2. Then ml_confidence tuning if needed
3. Validate each experiment with HQT audit before accepting

**Expected outcome**: 413 trades with 20-30% component filtering → ~300 trades at higher quality → PF 1.50+

---

## Milestone 3 Closure Checklist

- ✅ Experiment 3.1 completed (risk_map tuning)
- ✅ HQT audit passed primary goal (PF utan top-3 >= 1.2)
- ✅ Concentration risk eliminated (top-1 < 30%)
- ✅ Trade frequency sufficient (413 trades)
- ✅ MaxDD sanity check passed (1.25% < 3.5%)
- ✅ Decision made: Accept v5a as baseline
- ✅ Artifacts saved with clear naming
- ✅ Documentation updated
- ✅ Lessons learned captured

**Status**: CLOSED - v5a baseline locked, ready for Milestone 4

---

**Milestone 3 Closed**: 2026-02-03
**Next Milestone**: Component Quality Tuning (starting immediately)
**Baseline**: v5a_sizing_exp1.yaml (413 trades, PF 1.45, robust)
