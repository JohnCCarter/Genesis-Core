# Phase 3: Paper Trading Setup - Champion Freeze Protocol

**Date**: 2026-02-03
**Branch**: `feature/composable-strategy-phase2`
**Champion**: v5a_sizing_exp1 (composable strategy baseline)
**Freeze Period**: 2026-02-03 to 2026-03-17 (6 weeks)

---

## Executive Summary

This document addresses the three required adjustments before promoting v5a to paper trading:

1. **Champion File Format**: Proper JSON structure with metadata (not YAML→JSON copy)
2. **Mechanical Enforcement**: GitHub Actions workflow to freeze champion on ALL branches
3. **Enhanced Metrics**: Expectancy and median PnL per trade tracking

**Status**: Ready for promotion after implementing these adjustments.

---

## Adjustment 1: Champion File Format

### Current Format (Existing Champions)

Existing champion files in `config/strategy/champions/*.json` use a rich metadata structure:

```json
{
  "created_at": "2026-02-03T00:00:00Z",
  "run_id": "milestone3_v5a",
  "trial_id": "sizing_exp1",
  "git_commit": "<current_commit_hash>",
  "snapshot_id": "snap_tBTCUSD_2024-01-01_2024-12-31_phase3",
  "symbol": "tBTCUSD",
  "timeframe": "1h",
  "score": 0.0,
  "metrics": {
    "total_return": -0.00030890013698881377,
    "profit_factor": 1.450201270477175,
    "max_drawdown": 0.01249676919291543,
    "win_rate": 0.6561743341404357,
    "num_trades": 413,
    "sharpe_ratio": null,
    "return_to_dd": null,
    "total_commission": 141.29943276990008,
    "total_commission_pct": 0.014129943276990008
  },
  "constraints": {
    "hard_failures": [],
    "raw": {
      "source": "phase3_milestone3",
      "run_dir": "results/milestone3",
      "results_path": "results/milestone3/v5a_sizing_exp1_full2024_20260203_110625.json"
    }
  },
  "metadata": {
    "note": "Phase 3 Milestone 3 baseline. Composable strategy with risk_map threshold 0.53. Paper trading champion from 2026-02-03.",
    "phase": "phase3_milestone3",
    "baseline": "v5a_sizing_exp1",
    "robustness": {
      "pf_without_top1": 1.40,
      "pf_without_top3": 1.30,
      "top1_concentration_pct": 11.0,
      "top5_concentration_pct": 50.8
    },
    "quarterly": {
      "Q1_2024": {"pf": 1.57, "trades": 80},
      "Q2_2024": {"pf": 1.35, "trades": 104},
      "Q3_2024": {"pf": 1.30, "trades": 120},
      "Q4_2024": {"pf": 1.69, "trades": 86}
    }
  },
  "cfg": {
    "components": [
      {
        "type": "ml_confidence",
        "params": {"threshold": 0.24}
      },
      {
        "type": "regime_filter",
        "params": {
          "allowed_regimes": ["trending", "bull", "balanced", "bear", "ranging"]
        }
      },
      {
        "type": "ev_gate",
        "params": {"min_ev": 0.0}
      },
      {
        "type": "cooldown",
        "params": {"min_bars_between_trades": 24}
      }
    ],
    "risk": {
      "risk_map": [
        [0.53, 0.005],
        [0.7, 0.008],
        [0.8, 0.01],
        [0.9, 0.012]
      ],
      "risk_cap_pct": 0.012,
      "symbol_portfolio_cap_pct": 0.025
    }
  }
}
```

### Key Structure Elements

1. **Metadata Section**: Provenance, git commit, phase, baseline name
2. **Metrics Section**: Full backtest metrics (PF, MaxDD, trades, win rate, etc.)
3. **Robustness Section**: Custom robustness metrics (PF utan top-3, concentration)
4. **Quarterly Section**: Breakdown by quarter for validation
5. **cfg Section**: Complete strategy configuration (components + risk)

### Conversion Process

**Do NOT** simply copy YAML to JSON. Instead:

1. Load v5a YAML configuration
2. Load v5a backtest results (Full 2024)
3. Calculate robustness metrics from trades
4. Assemble complete champion JSON with all metadata
5. Validate structure matches existing champions

**Script needed**: `scripts/promote_v5a_to_champion.py` (creates proper champion JSON)

---

## Adjustment 2: Mechanical Enforcement (GitHub Actions)

### Champion Freeze Guard Workflow

Created: `.github/workflows/champion-freeze-guard.yml`

**Purpose**: Block ANY changes to `config/strategy/champions/` during paper trading freeze period.

**Enforcement**: ALL branches (not just main/master)

**Configuration**:

```yaml
# In workflow file:
FREEZE_START="2026-02-03"  # Paper trading start date
FREEZE_END="2026-03-17"    # 6 weeks later (adjustable)
```

**Behavior**:

- **During freeze period**: CI fails if any champion file is modified
- **Outside freeze period**: No restrictions
- **All branches**: Works on PRs and direct pushes to any branch
- **Error messages**: Clear explanation of freeze violation and how to resolve

**Updating freeze period**: Edit dates in `.github/workflows/champion-freeze-guard.yml`

**Emergency override**: Update `FREEZE_END` date if urgent changes needed

### Workflow Details

The workflow:

1. Checks current date against freeze period
2. For PRs: Compares PR branch against base branch
3. For pushes: Compares current commit against previous commit
4. Detects any changes in `config/strategy/champions/`
5. Fails with clear error message if changes found during freeze

**Status**: Workflow created, ready to commit.

---

## Adjustment 3: Enhanced Metrics Tracking

### Standard Paper Trading Metrics

**Weekly tracking** (every Monday):

1. **Profit Factor**: Wins / Losses
2. **PF Robustness**: PF utan top-3 trades
3. **Concentration**: Top-1 trade as % of total PnL
4. **Max Drawdown**: Peak-to-trough % drop
5. **Trade Count**: Total trades executed
6. **Win Rate**: % winning trades

### New Metrics (Addressing Volatility)

**Expectancy** (expected value per trade):

```
Expectancy = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
```

- More stable than PF on small samples
- Shows average $ per trade
- Less sensitive to outliers

**Median PnL per Trade**:

- Robust to outliers (unlike mean)
- Shows "typical" trade outcome
- Complements expectancy

### Tracking Template

**Weekly Report Format** (save as `docs/paper_trading/weekly_YYYY-MM-DD.md`):

```markdown
# Paper Trading Weekly Report: YYYY-MM-DD

**Week**: N/6
**Period**: YYYY-MM-DD to YYYY-MM-DD
**Champion**: v5a_sizing_exp1
**Symbol**: tBTCUSD (TEST symbol: tTESTBTC:TESTUSD)

## Metrics Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **PF** | X.XX | >= 1.30 | ✅/❌ |
| **PF utan top-3** | X.XX | >= 1.20 | ✅/❌ |
| **Expectancy** | $X.XX | > $0 | ✅/❌ |
| **Median PnL/trade** | $X.XX | > $0 | ✅/❌ |
| **Top-1 concentration** | X.X% | < 30% | ✅/❌ |
| **MaxDD** | X.XX% | <= 2.0% | ✅/❌ |
| **Trade count** | N | ~60-80/6wks | ✅/❌ |
| **Win rate** | XX.X% | > 55% | ✅/❌ |

## Trade Details

- **Total trades**: N
- **Winning trades**: N (XX.X%)
- **Losing trades**: N (XX.X%)
- **Avg win**: $X.XX
- **Avg loss**: -$X.XX
- **Largest win**: $X.XX
- **Largest loss**: -$X.XX

## Notes

- Any anomalies, issues, or observations
- Execution quality (slippage, fill rate)
- Market conditions

## Action Items

- [ ] Continue monitoring
- [ ] Investigate any anomalies
- [ ] Update freeze period if needed
```

### Calculation Script

**Script needed**: `scripts/calculate_paper_trading_metrics.py`

Should:
1. Read trades from paper trading results
2. Calculate all metrics (PF, expectancy, median PnL, etc.)
3. Generate weekly report markdown
4. Compare against targets (pass/fail)
5. Alert if any metric fails threshold

---

## Success Criteria (6-Week Paper Trading)

### Primary Goals (Must Pass)

- **PF >= 1.30**: Overall profit factor meets minimum threshold
- **PF utan top-3 >= 1.20**: Robustness maintained (strategy survives outlier removal)
- **Expectancy > $0**: Positive expected value per trade
- **MaxDD <= 2.0%**: Drawdown controlled (tighter than backtest 3.5% limit)

### Secondary Goals (Nice-to-Have)

- **Median PnL/trade > $0**: More than half of trades profitable
- **Top-1 concentration < 30%**: No single trade dominates
- **Trade count ~60-80**: Sufficient sample size (expected: 413/year → ~48/6wks, but paper may differ)
- **Win rate > 55%**: Majority of trades profitable

### Pass/Fail Decision

**After 6 weeks**:

- If ALL primary goals pass → Promote to live trading (small allocation)
- If ANY primary goal fails → Extend paper trading or return to research
- If expectancy/median PnL negative → Stop immediately, investigate

---

## Champion Promotion Checklist

### Pre-Promotion (Before 2026-02-03)

**CRITICAL**: Follow CI-safe commit order (champion BEFORE freeze-guard)

- [ ] Create promotion script (`scripts/promote_v5a_to_champion.py`)
- [ ] Create metrics calculation script (`scripts/calculate_paper_trading_metrics.py`)
- [ ] Run promotion script to generate champion JSON
- [ ] **COMMIT CHAMPION FILE FIRST** (`config/strategy/champions/tBTCUSD_1h_composable_v5a.json`)
- [ ] **COMMIT FREEZE-GUARD SECOND** (`.github/workflows/champion-freeze-guard.yml`)
- [ ] Create paper trading directory (`docs/paper_trading/`)
- [ ] Set up weekly report template
- [ ] Verify TEST symbol mapping works (`tTESTBTC:TESTUSD`)
- [ ] Configure paper trading API to use champion config
- [ ] Test champion load in pipeline (`ChampionLoader`)

### During Paper Trading (2026-02-03 to 2026-03-17)

- [ ] Weekly metrics reports (every Monday)
- [ ] Monitor execution quality (slippage, fills)
- [ ] Track any anomalies or issues
- [ ] NO changes to champion config
- [ ] Continue research in `feature/composable-research` branch

### Post-Paper Trading (After 2026-03-17)

- [ ] Calculate final 6-week metrics
- [ ] Run pass/fail evaluation against criteria
- [ ] If passed: Plan live deployment (small allocation)
- [ ] If failed: Analyze root causes, return to research
- [ ] Update freeze period end date in workflow
- [ ] Document results in `docs/paper_trading/FINAL_REPORT.md`

---

## Branch Strategy

### Main Branch (`master`)

- Contains frozen champion config
- NO strategy changes during paper trading
- Bug fixes and non-strategy changes allowed
- Champion freeze enforced by CI

### Feature Branch (`feature/composable-research`)

- Continues research and development
- HTF/LTF Fibonacci integration
- Optuna integration
- HysteresisComponent improvements
- All changes here, NOT on main

### Merge Strategy

- Do NOT merge `feature/composable-research` into `master` during freeze
- After paper trading: Merge only if research improves champion
- Keep branches separated to avoid contaminating production baseline

---

## File Locations

### Champion Config

- **Path**: `config/strategy/champions/tBTCUSD_1h_composable_v5a.json`
- **Format**: JSON with full metadata (see Adjustment 1)
- **Source**: v5a_sizing_exp1.yaml + backtest results

### GitHub Actions

- **Path**: `.github/workflows/champion-freeze-guard.yml`
- **Purpose**: Enforce frozen champion on all branches
- **Config**: FREEZE_START/FREEZE_END dates

### Paper Trading Reports

- **Directory**: `docs/paper_trading/`
- **Weekly**: `weekly_YYYY-MM-DD.md`
- **Final**: `FINAL_REPORT.md`

### Scripts

- **Promotion**: `scripts/promote_v5a_to_champion.py`
- **Metrics**: `scripts/calculate_paper_trading_metrics.py`

---

## Next Steps (CI-SAFE ORDER)

**CRITICAL**: Champion file MUST be committed BEFORE freeze-guard to avoid CI failure.

1. **Run promotion script** to generate champion JSON
   ```bash
   python scripts/promote_v5a_to_champion.py
   ```
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
4. **Create research branch** for continued development
   ```bash
   git checkout -b feature/composable-research
   git push -u origin feature/composable-research
   git checkout master
   ```
5. **Start paper trading** on 2026-02-03
6. **Weekly monitoring** for 6 weeks (run metrics script every Monday)

---

## Questions & Answers

**Q: Why must champion be committed BEFORE freeze-guard?**
A: CI-safety requirement. If freeze-guard is committed first, the freeze activates immediately and the next commit with the champion file will FAIL. Correct order: Champion first (no freeze yet), then freeze-guard (activates freeze). Alternative: Set FREEZE_START to day after promotion.

**Q: Can we change champion during paper trading?**
A: No. CI will block any changes to `config/strategy/champions/` on all branches during freeze period.

**Q: What if we need urgent fixes?**
A: Update `FREEZE_END` date in workflow, make changes, reset freeze.

**Q: Why expectancy instead of just PF?**
A: PF is volatile on small samples (6 weeks). Expectancy is more stable and shows $/trade directly.

**Q: Why median PnL?**
A: Median is robust to outliers. If median is positive, >50% of trades are profitable (good sign).

**Q: Can we continue research during paper trading?**
A: Yes, in `feature/composable-research` branch. Do NOT merge to main until after paper trading.

**Q: What happens after 6 weeks?**
A: Evaluate against criteria. If pass → plan live deployment. If fail → investigate and extend paper trading.

---

**Document Status**: DRAFT - Ready for review and implementation
**Next Action**: Commit workflow, create scripts, promote champion
