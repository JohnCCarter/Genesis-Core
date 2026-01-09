# Summary: Optuna Duplicate and Zero-Trade Fix

**Date**: 2025-11-11
**Issue**: Many Optuna trials are duplicates (penalized to −1e6) or produce 0 trades, leaving few valid backtests.

## Problem Analysis

### 1. Duplicate Parameters

**Root Cause**: The duplicate streak counter was reset too aggressively (on any non-duplicate skip), allowing the TPE sampler to degenerate and suggest the same parameters repeatedly.

**Impact**:

- Studies would terminate early with "Duplicate parameter suggestions limit reached"
- Wasted computation on repeated parameter sets
- TPE sampler unable to explore effectively

### 2. Zero Trades

**Root Cause**: Multiple factors:

- Entry confidence thresholds set too high (>0.5)
- Fibonacci gate tolerances too strict
- Multi-timeframe filtering too aggressive
- Search space didn't include champion's viable parameters

**Impact**:

- Most trials completed but produced no trades
- Scores around -95 to -100 (hard failure penalties)
- Few valid trials to compare

### 3. TPE Sampler Defaults

**Root Cause**: Default Optuna TPE settings without `multivariate=true` and `constant_liar=true` can degenerate in high-dimensional spaces.

**Impact**:

- Poor exploration of parameter space
- Convergence to local optima
- Increased duplicate suggestions

## Solution Implemented

### Code Changes

#### 1. Enhanced Duplicate Tracking (`src/core/optimizer/runner.py`)

```python
# Before: Reset on any non-duplicate skip
if payload.get("skipped"):
    if reason != "duplicate_within_run":
        duplicate_streak = 0  # Reset too early!

# After: Only reset on successful trials with trades
if num_trades > 0:
    duplicate_streak = 0  # Reset only on valid trials
```

Added counters:

- `total_trials_attempted`
- `duplicate_count`
- `zero_trade_count`

#### 2. Diagnostic Warnings

```python
if duplicate_ratio > 0.5:
    print(warning_with_recommendations)

if zero_trade_ratio > 0.5:
    print(warning_with_recommendations)
```

#### 3. Improved TPE Sampler Defaults

```python
if "multivariate" not in kwargs:
    kwargs["multivariate"] = True
if "constant_liar" not in kwargs:
    kwargs["constant_liar"] = True
if "n_startup_trials" not in kwargs:
    kwargs["n_startup_trials"] = 25  # Up from ~10
if "n_ei_candidates" not in kwargs:
    kwargs["n_ei_candidates"] = 48   # Up from 24
```

#### 4. Search Space Validation

```python
def _estimate_optuna_search_space(spec: dict[str, Any]) -> dict[str, Any]:
    """Estimate the size and diversity of the Optuna search space."""
    # Calculate discrete combinations
    # Detect potential issues:
    # - Too small (<10 combinations)
    # - Too many narrow parameters (≤2 choices)
    # Returns diagnostics and warnings
```

#### 5. Diagnostics Persistence

Diagnostics now stored in `run_meta.json`:

```json
{
  "optuna": {
    "diagnostics": {
      "total_trials_attempted": 100,
      "duplicate_count": 5,
      "zero_trade_count": 15,
      "duplicate_ratio": 0.05,
      "zero_trade_ratio": 0.15
    }
  }
}
```

### New Tools

#### 1. Diagnostic Script (`scripts/diagnose_optuna_issues.py`)

```bash
python scripts/diagnose_optuna_issues.py run_20251103_110227
```

Analyzes:

- Duplicate parameter sets
- Zero-trade trials
- Score distributions
- Provides actionable recommendations

#### 2. Best Practices Documentation (`OPTUNA_BEST_PRACTICES.md`)

Comprehensive guide covering:

- Pre-run checklist
- Common issues and solutions
- Recommended workflows
- Diagnostic tool usage
- Examples of good vs. problem runs

#### 3. Smoke Test (`scripts/smoke_test_fixes.py`)

Quick validation that fixes are working:

- Tests search space validation
- Verifies TPE defaults
- Confirms diagnostic tracking

### Testing

Created comprehensive test suite (`tests/test_optimizer_duplicate_fixes.py`):

- 8 new tests covering all fixes
- Tests search space estimation
- Tests duplicate and zero-trade tracking
- Tests TPE sampler defaults
- Tests warning generation

**Results**: All 28 optimizer tests passing ✅

## Usage Guide

### Before Running Optimization

1. **Validate Configuration**

```bash
python scripts/preflight_optuna_check.py config.yaml
python scripts/validate_optimizer_config.py config.yaml
```

2. **Run Smoke Test**

```yaml
# config_smoke.yaml - Quick 2-5 trial test
meta:
  runs:
    max_trials: 5
```

```bash
python -m core.optimizer.runner config_smoke.yaml
python scripts/diagnose_optuna_issues.py <run_id>
```

3. **Check Results**

- At least 1-2 trials should produce >0 trades
- Duplicate ratio should be <30%
- No excessive warnings

### During Optimization

The runner now automatically:

- Warns about narrow search spaces before starting
- Tracks duplicates and zero-trades during execution
- Displays warnings when ratios exceed 50%

### After Optimization

```bash
# Analyze results
python scripts/diagnose_optuna_issues.py run_20251103_110227

# Summarize top trials
python scripts/optimizer.py summarize run_20251103_110227 --top 10

# Check diagnostics
cat results/hparam_search/run_*/run_meta.json | jq '.optuna.diagnostics'
```

## Impact

### Expected Improvements

1. **Fewer Duplicates**
   - Streak counter only resets on valid trials
   - Better TPE exploration with multivariate mode
   - Higher n_startup_trials for better space coverage

2. **More Valid Trials**
   - Early warning about zero-trade issues
   - Recommendations guide users to widen search space
   - Validation catches problems before long runs

3. **Better Debugging**
   - Diagnostic script identifies specific issues
   - Stored metrics enable post-run analysis
   - Best practices documentation reduces trial-and-error

### Backward Compatibility

- All changes are backward compatible
- Existing configs work without modification
- New defaults improve results automatically
- Users can override defaults if needed

## Recommendations for Users

### If Experiencing Duplicates

1. Check search space size: `python scripts/smoke_test_fixes.py`
2. Widen parameter ranges
3. Remove or loosen step constraints
4. Increase `OPTUNA_MAX_DUPLICATE_STREAK=200`
5. Ensure TPE sampler has proper settings (automatic now)

### If Experiencing Zero Trades

1. Lower entry confidence thresholds (try 0.25-0.35)
2. Widen fibonacci tolerances (0.2-0.8 range)
3. Enable LTF override in multi-timeframe settings
4. Run smoke test to verify trades before long run
5. Check that champion parameters are in search space

### General Best Practices

1. Always run preflight checks before long runs (>1 hour)
2. Start with smoke test (2-5 trials) to validate search space
3. Use continuous parameters when possible (no step size)
4. Aim for >50 discrete combinations or include continuous params
5. Monitor first 10-20 trials and adjust if issues appear
6. Read `OPTUNA_BEST_PRACTICES.md` for detailed guidance

## Files Changed

1. `src/core/optimizer/runner.py` - Core fixes
2. `scripts/diagnose_optuna_issues.py` - Diagnostic tool (new)
3. `tests/test_optimizer_duplicate_fixes.py` - Tests (new)
4. `OPTUNA_BEST_PRACTICES.md` - Documentation (new)
5. `scripts/smoke_test_fixes.py` - Validation (new)

## Next Steps

For future improvements:

1. Add automatic search space adjustment based on early trials
2. Implement adaptive duplicate streak limits
3. Add more sophisticated zero-trade prediction
4. Create interactive search space designer
5. Add warm-start from previous runs

## References

- Issue: "Many Optuna trials are duplicates (penalized to −1e6) or produce 0 trades"
- `AGENTS.md` section 20 - Original documentation of the issue
- [Optuna TPESampler Documentation](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html)

---

**Status**: ✅ Complete and tested
**Ready for**: Production use
