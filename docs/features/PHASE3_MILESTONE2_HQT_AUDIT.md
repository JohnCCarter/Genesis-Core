# Phase 3 Milestone 2: HQT Audit (PF-First) - COMPLETE

**Date**: 2026-02-03
**Branch**: `feature/composable-strategy-phase2`
**Status**: ✅ COMPLETE - HQT-FAIL verdict
**Baseline**: `v4a_ml_regime_relaxed.yaml` (63 trades, PF 1.59)

---

## Executive Summary

**Milestone 2 redefined as HQT (High Quality Trade) Audit** with PF-first criteria on v4a baseline.

**Result**: v4a baseline **FAILS HQT-pass criteria** due to PF robustness vulnerability.

**Critical Finding**: PF collapses to 1.07 when top-3 trades are removed (fails threshold of 1.2). Top-1 trade accounts for 40.7% of total PnL, indicating high concentration risk.

**Verdict**: HQT-FAIL (3/4 checks pass, 1/4 fail)

---

## HQT-Pass Criteria (PF-First)

| # | Criterion | Target | Result | Status |
|---|-----------|--------|--------|--------|
| 1 | Helår PF | >= 1.5 | 1.59 | ✅ PASS |
| 2 | Minst 3/4 kvartal PF | >= 1.3 | 4/4 | ✅ PASS |
| 3 | Inget kvartal | < 1.0 | min=1.67 | ✅ PASS |
| 4 | PF utan top-3 | >= 1.2 | 1.07 | ❌ FAIL |

**Overall**: HQT-FAIL (robustness criterion not met)

---

## (1) Profit Factor Overview

**Full 2024**: PF = 1.59 (63 trades)

**Quarterly Breakdown**:
- Q1 2024: PF = 2.65 (18 trades) ✅
- Q2 2024: PF = 1.77 (15 trades) ✅
- Q3 2024: PF = 1.67 (16 trades) ✅
- Q4 2024: PF = 1.75 (13 trades) ✅

**Interpretation**: All quarters exceed 1.3 threshold. Q1 is strongest, Q3 is weakest (but still solid).

---

## (2) PnL Concentration

**Top-1 Trade**: $123.75 (40.7% of total PnL)
- Entry: 2024-03-05 19:00 → Exit: 2024-03-07 17:00
- Side: CLOSE_LONG
- PnL%: 10.08%
- **Risk**: Single trade accounts for >40% of yearly profit

**Top-5 Trades**: $366.46 (120.4% of total PnL)

**Top-5 Breakdown**:
1. $123.75 (40.7%) - 2024-03-05 to 2024-03-07
2. $85.49 (28.1%) - 2024-12-05 to 2024-12-06
3. $59.58 (19.6%) - 2024-08-07 to 2024-08-08
4. $52.32 (17.2%) - 2024-02-23 to 2024-02-27
5. $45.32 (14.9%) - 2024-03-11 to 2024-03-13

**Interpretation**: Extreme concentration. Top-5 trades exceed 100% of total PnL (losses offset remaining trades). High vulnerability to outlier removal.

---

## (3) PF Robustness (Remove Top Trades)

**PF without top-1 trade**: 1.35 (was 1.59)
- Drop: 0.24 (15.1%)
- Status: Still above 1.2 threshold (acceptable)

**PF without top-3 trades**: 1.07 (was 1.59)
- Drop: 0.52 (32.9%)
- Status: **BELOW 1.2 threshold** ❌ FAIL

**Interpretation**: Strategy is **NOT robust** to outlier removal. Removing top-3 trades causes PF to collapse from 1.59 → 1.07 (32.9% drop). This indicates dependence on rare outsized winners.

---

## (4) Bonus: Fees Analysis

- Total commission: $89.92
- Total slippage: $0.00
- **Total fees**: $89.92
- **Fees per trade**: $1.43
- **Fees burden**: 11.0% of gross profit

**Interpretation**: Fees are reasonable at $1.43/trade. 11% burden is acceptable for this trade frequency.

---

## Root Cause Analysis

**Why does v4a fail HQT-pass?**

1. **Low trade frequency** (63 trades/year):
   - Fewer trades → higher variance → more outlier dependence
   - Strategy relies on capturing occasional large moves

2. **ATR sizing bottleneck** (from Milestone 1):
   - 98.6% of allowed signals have size==0 due to ATR zone sizing
   - Only 66 size>0 attempts → 55 executed (83.3% fill rate)
   - Low trade count amplifies impact of individual outliers

3. **Component chain is toothless** (from Milestone 1):
   - 0% component veto rate under permissive baseline
   - No quality filtering at signal level
   - All allowed signals pass through (if size>0)

**Conclusion**: Low trade frequency + no quality filtering → high outlier dependence → PF robustness failure.

---

## Implications for Milestone 2 Strategy

**Original Milestone 2 Proposal**: Sizing Policy Review (increase to 100-150 trades/year)

**HQT Audit confirms this direction**:
- ✅ More trades → reduced outlier dependence → better PF robustness
- ✅ Addresses root cause (low trade frequency)
- ⚠️ Must maintain PF quality (not just inflate trade count with low-edge trades)

**Alternative approach** (if sizing can't be config-only):
- Tighten component thresholds to improve trade quality
- BUT: This would REDUCE trade count further (opposite of goal)
- NOT RECOMMENDED given current state

**Recommended**: Proceed with original Milestone 2 (Sizing Policy Review) to increase trade frequency.

---

## Artifacts

**Script Created**:
- `scripts/hqt_audit_pf_first.py` (HQT audit tool)

**Results**:
- `results/hqt_audit/v4a_hqt_audit_20260203.txt` (audit output)

**Source Data**:
- `results/extended_validation/v4a_ml_regime_relaxed_full2024_20260203_092718.json`

**Documentation**:
- `docs/features/PHASE3_MILESTONE2_HQT_AUDIT.md` (this file)

---

## Lessons Learned

1. **PF robustness is critical for production**: A strategy with PF 1.59 that collapses to 1.07 on outlier removal is NOT production-ready.

2. **Low trade frequency amplifies outlier risk**: 63 trades/year is too few to smooth variance. Need 100+ trades for statistical stability.

3. **PnL concentration is a red flag**: Top-1 trade = 40.7% of total PnL is unacceptable concentration risk.

4. **HQT audit should be standard gate**: Any baseline must pass HQT criteria before tuning proceeds.

---

## Next Steps

**Option A**: Proceed with Sizing Policy Review (Milestone 2 original proposal)
- Goal: 100-150 trades/year
- Method: Config-only if possible (adjust ATR zone multipliers)
- Expected: Improved PF robustness due to increased trade count

**Option B**: Abandon v4a baseline, restart with tighter component thresholds
- Risk: Would reduce trade count further (BAD)
- Not recommended given current findings

**Recommendation**: Option A (Sizing Policy Review)

---

## Milestone 2 Closure Checklist

- ✅ HQT audit script created and tested
- ✅ PF helår + per kvartal computed
- ✅ PnL concentration analyzed (top-1, top-5)
- ✅ PF robustness tested (without top-1, top-3)
- ✅ Fees analysis completed (bonus)
- ✅ HQT-pass criteria evaluated
- ✅ Verdict: HQT-FAIL (robustness failure)
- ✅ Root cause identified (low trade frequency + outlier dependence)
- ✅ Recommendations documented
- ✅ Artifacts saved

**Status**: COMPLETE (read-only audit as requested)

---

**Milestone 2 Closed**: 2026-02-03
**Next Milestone**: Sizing Policy Review (TBD, pending decision)
