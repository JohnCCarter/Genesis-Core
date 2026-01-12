# Optuna Optimization Best Practices

This guide helps you avoid common issues when running Optuna hyperparameter optimization.

## Quick Checklist

Before starting a long optimization run (>1 hour):

- [ ] Run preflight checks: `python scripts/preflight_optuna_check.py config.yaml`
- [ ] Validate config: `python scripts/validate_optimizer_config.py config.yaml`
- [ ] Run a smoke test (2-5 trials) to verify search space produces trades
- [ ] Check search space size (aim for >10 discrete combinations or continuous params)
- [ ] Review TPE sampler settings (use recommended defaults)
- [ ] Set appropriate `OPTUNA_MAX_DUPLICATE_STREAK` (≥200 for large runs)

## Common Issues and Solutions

### 1. Too Many Duplicate Parameters

**Symptoms:**

- Optuna keeps suggesting the same parameters
- Most trials marked as "duplicate_within_run"
- Study terminates early with "Duplicate parameter suggestions limit reached"

**Causes:**

- Search space too narrow (too few combinations)
- Float step sizes causing rounding to same values
- TPE sampler degenerating without proper configuration

**Solutions:**

#### Widen Search Space

```yaml
# ❌ Too narrow - only 4 combinations
parameters:
  entry_conf:
    type: float
    low: 0.35
    high: 0.40
    step: 0.05  # Only 2 values: 0.35, 0.40

  exit_conf:
    type: grid
    values: [0.4, 0.5]  # Only 2 values

# ✅ Better - 25+ combinations
parameters:
  entry_conf:
    type: float
    low: 0.25
    high: 0.45
    step: 0.02  # 11 values

  exit_conf:
    type: float
    low: 0.35
    high: 0.55
    step: 0.05  # 5 values
```

#### Improve TPE Sampler Configuration

```yaml
# ❌ Default/minimal TPE settings
optuna:
  sampler:
    name: tpe

# ✅ Better TPE configuration (applied automatically now)
optuna:
  sampler:
    name: tpe
    kwargs:
      multivariate: true
      constant_liar: true
      n_startup_trials: 25  # More random trials before modeling
      n_ei_candidates: 48   # More candidates per iteration
```

**Note:** As of the recent fix, these better defaults are applied automatically if not specified.

#### Remove or Loosen Step Constraints

```yaml
# ❌ Very fine steps can cause duplicate rounding
parameters:
  threshold:
    type: float
    low: 0.5
    high: 0.9
    step: 0.001  # May round to same values

# ✅ Coarser steps or continuous
parameters:
  threshold:
    type: float
    low: 0.5
    high: 0.9
    step: 0.01  # OR remove step entirely for continuous
```

#### Increase Duplicate Streak Limit

PowerShell (Windows):

```powershell
# Allow more consecutive duplicates before failing
$Env:OPTUNA_MAX_DUPLICATE_STREAK='200'
python -m core.optimizer.runner config.yaml
```

Bash (Linux/macOS):

```bash
export OPTUNA_MAX_DUPLICATE_STREAK=200
python -m core.optimizer.runner config.yaml
```

### 2. Too Many Zero-Trade Trials

**Symptoms:**

- Most trials complete but produce 0 trades
- Scores around -95 to -100 (hard failure penalty)
- Warning: "High zero-trade rate (>50%)"

**Causes:**

- Entry confidence thresholds too high
- Fibonacci gates too strict (small tolerance_atr)
- Multi-timeframe filtering too aggressive
- Search space doesn't include viable parameters

**Solutions:**

#### Lower Entry Thresholds

```yaml
# ❌ Too strict - blocks most signals
parameters:
  thresholds:
    entry_conf_overall:
      type: float
      low: 0.55
      high: 0.70  # Too high

# ✅ More permissive
parameters:
  thresholds:
    entry_conf_overall:
      type: float
      low: 0.25
      high: 0.45  # Allow more entries
```

#### Widen Fibonacci Tolerances

```yaml
# ❌ Too strict - rejects most entries
parameters:
  htf_fib:
    entry:
      tolerance_atr:
        type: float
        low: 0.3
        high: 0.5  # Narrow range

# ✅ More permissive
parameters:
  htf_fib:
    entry:
      tolerance_atr:
        type: float
        low: 0.2
        high: 0.8  # Wider range
```

#### Enable LTF Override

```yaml
# Allow LTF to override HTF blocks
parameters:
  multi_timeframe:
    allow_ltf_override:
      type: grid
      values: [true, false]
    ltf_override_threshold:
      type: float
      low: 0.60
      high: 0.85
      step: 0.05
```

#### Run Smoke Test First

```yaml
# Create smoke test config with 2-5 trials
meta:
  runs:
    max_trials: 5 # Quick test
    strategy: optuna
```

```bash
python -m core.optimizer.runner config_smoke.yaml --run-id smoke_test
python scripts/diagnose_optuna_issues.py smoke_test
```

If smoke test produces 0 trades for all trials, widen search space before long run.

### 3. Search Space Too Small

**Symptoms:**

- Warning: "Search space very small (<10 combinations)"
- Duplicates appear quickly
- Study exhausts parameter space before timeout

**Solutions:**

#### Add More Parameters

```yaml
# ❌ Only 2 parameters = limited exploration
parameters:
  entry_conf:
    type: grid
    values: [0.3, 0.4, 0.5]
  exit_conf:
    type: fixed
    value: 0.4

# ✅ More parameters for richer search
parameters:
  thresholds:
    entry_conf_overall:
      type: float
      low: 0.25
      high: 0.45
      step: 0.05

  exit:
    exit_conf_threshold:
      type: float
      low: 0.35
      high: 0.55
      step: 0.05

    max_hold_bars:
      type: int
      low: 15
      high: 30
      step: 5
```

#### Use Continuous Parameters

### 4. Different Parameters But Identical Outcomes

**Symptoms:**

- Two trials have different parameter payloads, but produce identical trades/metrics.

**First question to answer:** Are the trials actually running different _effective configs_?

**How to verify (authoritatively):**

- Check `backtest_info.effective_config_fingerprint` in the backtest artifact JSON.
  - If the fingerprint is the same, the _effective config_ was the same (override/caching/merge).
  - If the fingerprint differs, the configs truly differed — the parameter may simply be inert.

**Common cause of “inert” parameters:**

- In `decision.py`, if `regime_proba` is a dict, the regime-specific threshold is used.
  In that case, changing a zoned `entry_conf_overall` may not affect the final threshold.

**Practical recommendation:**

- Prefer tuning parameters that are demonstrably on the active decision path.
- When in doubt, run a tiny GRID smoke test (2–5 combos) and confirm that trades/metrics diverge.

```yaml
# Discrete only - limited
parameters:
  threshold:
    type: grid
    values: [0.3, 0.4, 0.5]  # Only 3 values

# Add continuous params - infinite space
parameters:
  threshold:
    type: float
    low: 0.25
    high: 0.55  # No step = continuous
```

#### Check Estimation Before Running

```python
from core.optimizer.runner import _estimate_optuna_search_space

spec = {...}  # Your parameters spec
diagnostics = _estimate_optuna_search_space(spec)
print(diagnostics)
```

The optimizer now automatically prints this before starting.

## Diagnostic Tools

### Analyze Completed Runs

```bash
# Comprehensive diagnosis
python scripts/diagnose_optuna_issues.py run_20251103_110227

# Check run metadata
cat results/hparam_search/run_*/run_meta.json | jq '.optuna.diagnostics'
```

### Preflight Checks

```bash
# Validate before running
python scripts/preflight_optuna_check.py config.yaml
python scripts/validate_optimizer_config.py config.yaml
```

## Recommended Workflow

1. **Design Search Space**

   - Start wide, narrow down later
   - Aim for 50+ discrete combinations or include continuous params
   - Include champion parameters in ranges

2. **Validate Configuration**

   ```bash
   python scripts/preflight_optuna_check.py config.yaml
   python scripts/validate_optimizer_config.py config.yaml
   ```

3. **Run Smoke Test (2-5 trials)**

   ```bash
   python -m core.optimizer.runner config.yaml --run-id smoke_test
   python scripts/diagnose_optuna_issues.py smoke_test
   ```

4. **Check Smoke Results**

   - At least 1-2 trials should produce >0 trades
   - No excessive duplicates
   - Scores not all heavily negative

5. **Full Optimization**

PowerShell (Windows):

```powershell
# Set environment for performance
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_MAX_CONCURRENT='2'
$Env:OPTUNA_MAX_DUPLICATE_STREAK='200'

python -m core.optimizer.runner config.yaml
```

Bash (Linux/macOS):

```bash
export GENESIS_FAST_WINDOW=1
export GENESIS_PRECOMPUTE_FEATURES=1
export GENESIS_MAX_CONCURRENT=2
export OPTUNA_MAX_DUPLICATE_STREAK=200

python -m core.optimizer.runner config.yaml
```

**Canonical mode note: 2025-12-18** Optuna/Validate/champion decisions run in canonical "1/1" mode.
If you run a manual debug backtest in 0/0, treat it as debug-only and do not compare it to Optuna results.
To allow 0/0 explicitly, set `GENESIS_MODE_EXPLICIT=1` and use the backtest CLI flags
(e.g. `--no-fast-window --no-precompute-features`).

6. **Post-Run Analysis**
   ```bash
   python scripts/diagnose_optuna_issues.py run_20251103_110227
   python scripts/optimizer.py summarize run_20251103_110227 --top 10
   ```

## Interpreting Diagnostic Output

### Duplicate Ratio

- **< 10%**: Healthy - good exploration
- **10-30%**: Acceptable - TPE is converging
- **30-50%**: Warning - may need wider space
- **> 50%**: Problem - search space likely too narrow

### Zero-Trade Ratio

- **< 10%**: Excellent - gating is appropriate
- **10-30%**: Good - some strict parameter sets
- **30-50%**: Warning - gates may be too strict
- **> 50%**: Problem - search space doesn't produce viable strategies

### Example Good Run

```
SUMMARY:
  Total trials:      100
  Skipped:           5 (5.0%)
  - Duplicates:      5
  Errors:            2
  Zero trades:       15
  Valid (>0 trades): 78

DUPLICATE ANALYSIS:
  Unique param sets appearing >1 time: 2

ZERO TRADE ANALYSIS:
  Trials with 0 trades: 15

VALID TRIALS:
  Count: 78
  Score range: -45.23 to 234.56
  Average: 78.92
```

### Example Problem Run

```
SUMMARY:
  Total trials:      50
  Skipped:           28 (56.0%)  # ⚠️ Too many duplicates
  - Duplicates:      28
  Errors:            2
  Zero trades:       18  # ⚠️ High zero-trade rate
  Valid (>0 trades): 2   # ⚠️ Too few valid trials

⚠️  WARNING: High duplicate rate (56.0%)
⚠️  WARNING: High zero-trade rate (36.0%)
```

## Advanced Tips

### Parallel Runs with Different Strategies

Run multiple optimizations in parallel with different approaches:

```bash
# Terminal 1: Wide coarse grid
python -m core.optimizer.runner config_coarse.yaml

# Terminal 2: Focused Optuna with champion neighborhood
python -m core.optimizer.runner config_fine.yaml

# Terminal 3: Fibonacci-specific grid
python -m core.optimizer.runner config_fib.yaml
```

### Seeding from Previous Best

Use champion parameters as the center of your search:

```yaml
parameters:
  thresholds:
    entry_conf_overall:
      type: float
      low: 0.33 # Champion ± 0.05
      high: 0.43
      step: 0.01
```

### Multi-Stage Optimization

1. **Stage 1**: Coarse grid to identify regions
2. **Stage 2**: Optuna on promising region (2-3 month window)
3. **Stage 3**: Fine-tune on full 6-month window

## Monitoring Long Runs

Check progress periodically:

```bash
# Count completed trials
ls results/hparam_search/run_*/trial_*.json | wc -l

# Quick summary
python scripts/optimizer.py summarize run_20251103_110227 --top 5

# Full diagnosis
python scripts/diagnose_optuna_issues.py run_20251103_110227
```

## Troubleshooting

### Study Terminates Early

```
optuna.exceptions.OptunaError: Duplicate parameter suggestions limit reached
```

**Solution**: Increase `OPTUNA_MAX_DUPLICATE_STREAK` or widen search space.

### All Trials Score Around -100

This indicates hard failures (zero trades, bad constraints, etc.).

**Solution**: Lower entry thresholds, widen fibonacci tolerances, run diagnostic script.

### TPE Sampler Not Improving

After many trials, scores stay flat or degenerate.

**Solution**: Check if `multivariate=true` and `constant_liar=true` are set (now automatic).

### Out of Memory

Large concurrent runs can exhaust memory.

**Solution**: Reduce `max_concurrent` or enable `gc_after_trial=true` (now default).

## References

- [Optuna Documentation](https://optuna.readthedocs.io/)
- [TPE Sampler Details](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html)
- Project: `AGENTS.md` section 20 for detailed issue history
- Project: `scripts/preflight_optuna_check.py` for validation
