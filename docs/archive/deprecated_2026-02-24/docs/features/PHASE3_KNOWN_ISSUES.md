# Phase 3: Known Issues and Limitations

**Status**: Paper trading validation period (2026-02-03 to 2026-03-17)
**Champion**: v5a_sizing_exp1 (FROZEN)

---

## Known Issue 1: Concentration Metric Uses Net PnL (Can Be Negative)

**Issue ID**: PHASE3-KI-001
**Severity**: Low (cosmetic)
**Status**: Logged, fix deferred until after freeze period

### Problem

Champion promotion script (`scripts/promote_v5a_to_champion.py`) calculates top-1 concentration using **net PnL** (after fees), which can produce negative percentages when total net PnL < 0.

**Example** (v5a baseline):
```
Total net PnL: -$3.09 (after $141 in fees)
Top-1 trade PnL: +$15.08
Concentration: 100 * 15.08 / -3.09 = -488% (INCORRECT)
```

**Root cause**:
```python
# Line ~47 in promote_v5a_to_champion.py
total_pnl = summary["total_return_usd"]  # Uses net PnL (after fees)
top1_pct = 100.0 * top1_pnl / total_pnl  # Division by negative = negative %
```

### Why This Happens

v5a has **positive gross PnL** (PF 1.45 > 1.0) but **negative net PnL** after fees:
- Gross wins: $914.85
- Gross losses: $630.82
- **Gross PnL**: $284.03 (positive)
- Fees: $141.30
- **Net PnL**: -$3.09 (negative)

When net PnL is negative, concentration becomes mathematically negative.

### Impact

**Affected artifact**: `config/strategy/champions/tBTCUSD_1h_composable_v5a.json`
- Metadata field: `metadata.robustness.top1_concentration_pct` = -1014.7%
- Metadata field: `metadata.robustness.top5_concentration_pct` = -4542.7%

**Does NOT affect**:
- Strategy execution logic ✅
- Backtest results ✅
- Paper trading validation ✅
- CI/freeze-guard operation ✅

**Only affects**: Champion metadata display (cosmetic)

### Correct Behavior

Concentration should use **gross PnL** (before fees) to avoid negative percentages:

```python
# Correct calculation:
gross_pnl = sum(t["pnl"] + t.get("commission", 0) for t in trades)
top1_pct = 100.0 * top1_pnl / gross_pnl if gross_pnl != 0 else 0.0

# For v5a:
# Gross PnL: $284.03
# Top-1: $15.08
# Concentration: 100 * 15.08 / 284.03 = 5.3% (CORRECT)
```

### Resolution Plan

**NOT fixing now** because:
1. Champion is FROZEN during paper trading validation (2026-02-03 to 2026-03-17)
2. Regenerating champion JSON would break freeze semantics
3. Would contaminate baseline artifact with post-freeze modification
4. Issue is cosmetic only (does not affect validation)

**Fix timeline**:
- **After freeze period ends** (2026-03-18+): Update `promote_v5a_to_champion.py` to use gross PnL
- **For future champions**: Fixed script will apply to all new promotions
- **For v5a artifact**: Leave as-is (historical record, known limitation documented)

**Alternative**: Create separate research tooling for concentration analysis using gross PnL, without modifying frozen champion artifact.

---

## Known Issue 2: UTC Date Edge Case (Low Risk)

**Issue ID**: PHASE3-KI-002
**Severity**: Low (edge case)
**Status**: Documented, mitigation in place

### Description

Freeze-guard workflow uses UTC dates for freeze period detection. Local timezone differences can cause confusion about when freeze activates/deactivates.

**Example**:
- FREEZE_START = "2026-02-03"
- Local time: 2026-02-03 01:00 CET (UTC: 2026-02-02 23:00)
- Workflow sees: "2026-02-02" → freeze NOT active yet
- User expects: Freeze active on "2026-02-03"

### Mitigation

Workflow explicitly uses UTC (`date -u +%Y-%m-%d`) and documents this:
```yaml
# Format: YYYY-MM-DD (UTC dates)
FREEZE_START="2026-02-03"
FREEZE_END="2026-03-17"
```

**Resolution**: Document in setup guide that freeze dates are UTC, inclusive.

---

## Known Issue 3: FREEZE_END Is Inclusive (Low Risk)

**Issue ID**: PHASE3-KI-003
**Severity**: Low (documentation)
**Status**: Documented

### Description

Freeze period comparison uses `<=` (less-than-or-equal), making FREEZE_END **inclusive**:

```bash
if [ "$CURRENT_EPOCH" -ge "$FREEZE_START_EPOCH" ] && [ "$CURRENT_EPOCH" -le "$FREEZE_END_EPOCH" ]; then
```

**Behavior**:
- FREEZE_END="2026-03-17" → Freeze active THROUGH entire day 2026-03-17
- Freeze deactivates at midnight UTC 2026-03-18 (AFTER 2026-03-17)

**Impact**: If user wants freeze to end BEFORE 2026-03-17, set FREEZE_END="2026-03-16"

**Resolution**: Document inclusive behavior in setup guide.

---

## Issue Tracking

| ID | Issue | Severity | Fix Timeline | Impact |
|----|-------|----------|--------------|--------|
| PHASE3-KI-001 | Concentration uses net PnL | Low | After freeze (2026-03-18+) | Cosmetic only |
| PHASE3-KI-002 | UTC date edge case | Low | Documented | Edge case |
| PHASE3-KI-003 | FREEZE_END inclusive | Low | Documented | Clarity |

**No blocking issues for paper trading deployment.** ✅

---

**Document Status**: Active during paper trading freeze (2026-02-03 to 2026-03-17)
**Next Review**: 2026-03-18 (after freeze period ends)
