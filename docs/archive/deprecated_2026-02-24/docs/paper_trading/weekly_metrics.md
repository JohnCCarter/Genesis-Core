# Weekly Metrics Report - Paper Trading

## Overview

Weekly metrics reports are generated using `scripts/calculate_paper_trading_metrics.py` to validate champion performance during the 6-week paper trading period (2026-02-04 to 2026-03-17).

## Schedule

**Week 1:** 2026-02-04 to 2026-02-10
**Week 2:** 2026-02-11 to 2026-02-17
**Week 3:** 2026-02-18 to 2026-02-24
**Week 4:** 2026-02-25 to 2026-03-03
**Week 5:** 2026-03-04 to 2026-03-10
**Week 6:** 2026-03-11 to 2026-03-17

## Running Weekly Report

**Command:**
```bash
cd /c/Users/fa06662/Projects/Genesis-Core
. .venv/Scripts/activate

# Generate report for specific week
python scripts/calculate_paper_trading_metrics.py \
  --start-date 2026-02-04 \
  --end-date 2026-02-10 \
  --week-num 1 \
  --output-dir docs/paper_trading/weekly_reports
```

**Automated weekly (cron/Task Scheduler):**
```bash
# Run every Monday at 00:00
0 0 * * 1 /c/Users/fa06662/Projects/Genesis-Core/scripts/run_weekly_report.sh
```

## Report Contents

**Generated file:** `docs/paper_trading/weekly_reports/week_N_YYYY-MM-DD.md`

**Sections:**
1. **Summary metrics**
   - Total trades
   - Win rate
   - Profit factor
   - Max drawdown
   - Total commission %

2. **Primary criteria evaluation**
   - Profit Factor ≥ 1.3
   - Max Drawdown ≤ 3%
   - Win Rate ≥ 50%
   - Min Trades ≥ 10/week

3. **Secondary criteria**
   - Sharpe Ratio ≥ 1.0 (if calculable)
   - Return/DD ≥ 5.0
   - Commission % ≤ 2%

4. **Pass/Fail status**
   - Primary criteria: PASS/FAIL
   - Overall: PASS/FAIL

## Primary Criteria (Required)

| Metric | Target | Action on Fail |
|--------|--------|----------------|
| Profit Factor | ≥ 1.3 | Monitor, flag if 2 weeks consecutive |
| Max Drawdown | ≤ 3% | Immediate review if exceeded |
| Win Rate | ≥ 50% | Monitor trend |
| Min Trades | ≥ 10/week | Investigate if < 10 |

**Red flags (stop paper trading):**
- 2 consecutive weeks fail primary criteria
- Single week with DD > 5%
- Champion loading fails (baseline fallback detected)
- Unexpected errors in strategy pipeline

## Secondary Criteria (Monitor)

| Metric | Target | Notes |
|--------|--------|-------|
| Sharpe Ratio | ≥ 1.0 | May not be calculable for short periods |
| Return/DD | ≥ 5.0 | Risk-adjusted return quality |
| Commission % | ≤ 2% | Trading frequency efficiency |

## Data Sources

**Trade data:** Extracted from server logs or database (TBD based on implementation)

**Expected location:**
- `logs/paper_trading/trades_YYYYMMDD.jsonl` (if logged)
- OR: Query API endpoint for trade history
- OR: Manual collection from Bitfinex TEST account

## Manual Report Generation

If automated script not working:

1. **Collect trade data** for the week
2. **Calculate metrics manually:**
   - Total trades
   - Win/loss split
   - Total P&L
   - Max drawdown
   - Commission

3. **Create report file:** `docs/paper_trading/weekly_reports/week_N_manual.md`

4. **Include:**
   - Date range
   - Raw data (trade list)
   - Calculated metrics
   - Pass/fail evaluation
   - Notes/observations

## Example Report Structure

```markdown
# Week 1 Report: 2026-02-04 to 2026-02-10

**Status:** PASS/FAIL

## Metrics

- Total Trades: 12
- Win Rate: 58.3% (7/12)
- Profit Factor: 1.45
- Max Drawdown: 1.2%
- Total Commission: 0.8%

## Primary Criteria

✅ Profit Factor ≥ 1.3: PASS (1.45)
✅ Max Drawdown ≤ 3%: PASS (1.2%)
✅ Win Rate ≥ 50%: PASS (58.3%)
✅ Min Trades ≥ 10: PASS (12)

**Primary Criteria: PASS**

## Secondary Criteria

✅ Commission % ≤ 2%: PASS (0.8%)
⚠️ Sharpe Ratio: Not calculable (insufficient data)
⚠️ Return/DD: Not calculable

## Observations

- Champion loaded correctly all week
- No errors in strategy pipeline
- Trade frequency within expected range
- Commission impact minimal

## Recommendation

Continue paper trading. No red flags detected.
```

## Archive

**Location:** `docs/paper_trading/weekly_reports/`

**Retention:** Keep all reports for audit trail

**Files:**
- `week_1_20260210.md`
- `week_2_20260217.md`
- ...
- `week_6_20260317.md`
- `final_summary_20260317.md`

## Final Report (End of Period)

**Due:** 2026-03-17

**Content:**
- Aggregate metrics (all 6 weeks)
- Week-by-week trend analysis
- Primary/secondary criteria summary
- Champion promotion decision: PROMOTE / ITERATE
- Lessons learned
- Recommendations for next phase
