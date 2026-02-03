# Phase 3: Paper Trading Adjustments - Implementation Summary

**Date**: 2026-02-03
**Status**: ✅ All three adjustments COMPLETE, ready for champion promotion

---

## Three Required Adjustments

### ✅ Adjustment 1: Champion File Format (PROPER JSON)

**Requirement**: Champion file must be proper JSON with metadata, not YAML→JSON direct copy.

**Solution**: Created `scripts/promote_v5a_to_champion.py` that:

1. Loads v5a YAML config
2. Loads v5a backtest results (Full 2024)
3. Calculates robustness metrics (PF utan top-3, concentration)
4. Assembles complete champion JSON with:
   - Metadata (created_at, run_id, git_commit, phase)
   - Metrics (PF, MaxDD, trades, win rate, commission)
   - Robustness (PF utan top-3, concentration)
   - Quarterly breakdown (Q1-Q4 PF and trades)
   - Complete cfg (components + risk config)

**Output**: `config/strategy/champions/tBTCUSD_1h_composable_v5a.json`

**Format matches existing champions**: ✅ Yes (same structure as `tBTCUSD_1h.json`)

**Ready to run**: ✅ Script ready, will generate proper champion JSON

---

### ✅ Adjustment 2: Mechanical Enforcement (CI GUARD)

**Requirement**: Frozen champion must be enforced mechanically via CI, not just policy.

**Solution**: Created `.github/workflows/champion-freeze-guard.yml` that:

1. **Freeze Period**: Configurable dates (FREEZE_START, FREEZE_END)
   - Default: 2026-02-03 to 2026-03-17 (6 weeks)
2. **Enforcement Scope**: ALL branches (not just main/master)
3. **Detection**: Checks any changes to `config/strategy/champions/` via git diff
4. **Failure Mode**: CI fails with clear error message if changes detected during freeze
5. **Override**: Update FREEZE_END date in workflow for emergency changes

**Workflow triggers**:
- Pull requests (compares PR branch vs base branch)
- Direct pushes (compares current commit vs previous commit)
- Ignored: archive/** branches

**Error message example**:
```
CHAMPION FREEZE VIOLATION detected!
The following champion files were modified during paper trading freeze period:
  - config/strategy/champions/tBTCUSD_1h_composable_v5a.json
Freeze period: 2026-02-03 to 2026-03-17
Champion configs are FROZEN during paper trading. All changes must wait until freeze ends.
If you need to make urgent changes, update FREEZE_END date in .github/workflows/champion-freeze-guard.yml
```

**Ready to deploy**: ✅ Workflow file created, ready to commit

---

### ✅ Adjustment 3: Enhanced Metrics (EXPECTANCY + MEDIAN PNL)

**Requirement**: Add expectancy and median PnL per trade as complementary metrics (PF volatile on 4-6 weeks).

**Solution**: Created `scripts/calculate_paper_trading_metrics.py` that calculates:

**Standard Metrics**:
- Profit Factor (PF)
- PF utan top-3 (robustness)
- Top-1 concentration (risk)
- Max Drawdown (risk)
- Win rate
- Trade count

**New Metrics (Volatility-Resistant)**:

1. **Expectancy** (expected value per trade):
   ```
   Expectancy = (Win Rate × Avg Win) + (Loss Rate × Avg Loss)
   ```
   - Shows average $/trade
   - More stable than PF on small samples
   - Less sensitive to outliers
   - Target: > $0 (positive edge)

2. **Median PnL per Trade**:
   - Robust to outliers (unlike mean)
   - Shows "typical" trade outcome
   - If median > $0, then >50% of trades are profitable
   - Target: > $0 (majority profitable)

**Script features**:
- Loads paper trading results JSON
- Calculates all metrics
- Evaluates pass/fail against criteria
- Generates weekly report markdown
- Tracks primary vs secondary goals

**Output**: Weekly reports in `docs/paper_trading/weekly_YYYY-MM-DD.md`

**Ready to use**: ✅ Script ready, can run immediately after paper trading starts

---

## Success Criteria Confirmed

### Primary Goals (Must Pass)

| Goal | Target | Rationale |
|------|--------|-----------|
| **PF >= 1.30** | 1.30 | Lower than backtest 1.45, but sufficient for production |
| **PF utan top-3 >= 1.20** | 1.20 | Robustness maintained (backtest: 1.30) |
| **Expectancy > $0** | > $0 | Positive expected value per trade |
| **MaxDD <= 2.0%** | 2.0% | Tighter than backtest 3.5%, realistic paper trading control |

### Secondary Goals (Nice-to-Have)

| Goal | Target | Rationale |
|------|--------|-----------|
| **Median PnL > $0** | > $0 | Majority of trades profitable |
| **Top-1 < 30%** | 30% | No single trade dominates (backtest: 11.0%) |
| **Trade count ~60-80** | 60-80 | Expected: 413/year → ~48/6wks, paper may differ |
| **Win rate > 55%** | 55% | Majority of trades win (backtest: 65.6%) |

---

## Implementation Checklist

### Files Created

- ✅ `.github/workflows/champion-freeze-guard.yml` (CI enforcement)
- ✅ `scripts/promote_v5a_to_champion.py` (champion promotion)
- ✅ `scripts/calculate_paper_trading_metrics.py` (metrics calculation)
- ✅ `docs/features/PHASE3_PAPER_TRADING_SETUP.md` (complete protocol)
- ✅ `docs/features/PHASE3_ADJUSTMENTS_SUMMARY.md` (this file)

### Ready to Execute (CI-SAFE ORDER)

**CRITICAL**: Champion file MUST be committed BEFORE freeze-guard to avoid CI failure.

1. **Run champion promotion script** (generates champion JSON locally)
   ```bash
   python scripts/promote_v5a_to_champion.py
   ```
   - Output: `config/strategy/champions/tBTCUSD_1h_composable_v5a.json`

2. **Commit CHAMPION file FIRST** (before freeze activates)
   ```bash
   git add config/strategy/champions/tBTCUSD_1h_composable_v5a.json
   git commit -m "feat: promote v5a to champion baseline for paper trading"
   ```

3. **Commit FREEZE-GUARD SECOND** (activates freeze)
   ```bash
   git add .github/workflows/champion-freeze-guard.yml
   git commit -m "feat: add champion freeze guard for paper trading"
   ```

4. **Create paper trading directory**
   ```bash
   mkdir -p docs/paper_trading
   ```

5. **Create research branch**
   ```bash
   git checkout -b feature/composable-research
   git push -u origin feature/composable-research
   git checkout master
   ```

6. **Start paper trading** (2026-02-03)
   - Configure API to use champion config
   - Set symbol mapping to TEST symbols
   - Begin weekly monitoring

7. **Weekly metrics reports** (every Monday)
   ```bash
   python scripts/calculate_paper_trading_metrics.py \
     <results_file> \
     --week 1 \
     --period-start 2026-02-03 \
     --period-end 2026-02-10 \
     --output docs/paper_trading/weekly_2026-02-10.md
   ```

---

## Validation Tests

### Test 1: Champion Freeze Enforcement

**Test scenario**: Try to modify champion file during freeze period

**Expected behavior**: CI fails with freeze violation error

**Verification**:
1. Create test branch
2. Modify `config/strategy/champions/tBTCUSD_1h_composable_v5a.json`
3. Push to GitHub
4. CI should FAIL with clear error message

### Test 2: Champion Promotion

**Test scenario**: Run promotion script

**Expected behavior**: Generates proper champion JSON with all metadata

**Verification**:
1. Run `python scripts/promote_v5a_to_champion.py`
2. Check output file structure matches existing champions
3. Verify metrics match v5a results
4. Confirm robustness metrics calculated correctly

### Test 3: Metrics Calculation

**Test scenario**: Run metrics script on v5a results

**Expected behavior**: Calculates expectancy, median PnL, generates report

**Verification**:
1. Run `python scripts/calculate_paper_trading_metrics.py results/milestone3/v5a_sizing_exp1_full2024_20260203_110625.json --output test_report.md`
2. Verify expectancy calculation
3. Verify median PnL calculation
4. Check report format

---

## Questions Answered

**Q: Why can't we just copy YAML to JSON?**

A: Existing champions have rich metadata structure:
- Provenance (run_id, git_commit, created_at)
- Metrics (PF, MaxDD, trades, commission)
- Robustness (PF utan top-3, concentration)
- Quarterly breakdown (validation)
- Complete cfg (reproducibility)

Direct YAML→JSON copy loses all this context and breaks tooling expectations.

---

**Q: Why enforce freeze on ALL branches?**

A: Paper trading validation requires stable baseline. If research branches can modify champion, they might accidentally:
- Merge changes to main during freeze
- Push champion changes that contaminate paper trading
- Break reproducibility of paper trading results

ALL branches enforced = mechanical guarantee of stability.

---

**Q: Why expectancy instead of just PF?**

A: PF is volatile on small samples:
- 6 weeks paper trading = ~48-80 trades (vs 413 in backtest)
- One large win/loss can swing PF dramatically
- Expectancy is more stable (average $/trade)
- Shows clear edge: Expectancy > $0 = positive edge

Example:
- PF can be 2.0 with negative expectancy (if large losses)
- PF can be 1.2 with high expectancy (consistent small wins)

Expectancy + median PnL give clearer picture of strategy edge.

---

**Q: Why median PnL?**

A: Median is robust to outliers:
- Mean PnL affected by single large wins/losses
- Median shows "typical" trade outcome
- If median > $0, then >50% of trades are profitable
- Complements expectancy (mean-based metric)

Together: Expectancy (mean) + Median = complete picture of trade distribution.

---

**Q: Why must champion be committed BEFORE freeze-guard?**

A: CI-safety requirement:
- If freeze-guard is committed first → freeze activates immediately
- Next commit with champion file → CI FAILS (champion file change during freeze period)
- Correct order: Champion first (no freeze yet), then freeze-guard (activates freeze)
- Alternative: Set FREEZE_START to day after promotion (e.g., "2026-02-04")

---

## Next Actions (CI-SAFE ORDER)

**Champion BEFORE freeze-guard to avoid CI failure:**

1. **Run promotion script**: Generate champion JSON locally
2. **Commit champion FIRST**: `config/strategy/champions/tBTCUSD_1h_composable_v5a.json`
3. **Commit freeze-guard SECOND**: `.github/workflows/champion-freeze-guard.yml`
4. **Create research branch**: `feature/composable-research`
5. **Start paper trading**: 2026-02-03
6. **Weekly monitoring**: Run metrics script every Monday

---

**Status**: ✅ ALL ADJUSTMENTS COMPLETE

All three required adjustments are implemented and ready to deploy:
- Champion file format: Proper JSON with metadata ✅
- Mechanical enforcement: CI freeze guard on all branches ✅
- Enhanced metrics: Expectancy + median PnL tracking ✅

Ready to proceed with champion promotion and paper trading setup.
