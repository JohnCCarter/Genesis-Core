# Why More Concurrent Workers Increase Optuna Duplicates

**Date**: 2025-11-11
**Analysis**: Deep dive into parallel optimization and duplicate parameter generation

## Executive Summary

When using multiple concurrent workers (`n_jobs > 1`) with Optuna, the duplicate rate increases significantly. This is caused by **race conditions in parameter sampling**, where multiple workers request parameters simultaneously without seeing each other's choices, combined with **discrete/rounded search spaces** that reduce the effective parameter space size.

## The Core Problem

### Sequential vs. Parallel Sampling

**Sequential (n_jobs=1)**:
```
Worker 1: Request params → Get {A} → Evaluate → Report result
Worker 1: Request params → Get {B} → Evaluate → Report result
Worker 1: Request params → Get {C} → Evaluate → Report result
```
Each request happens AFTER the previous trial completes and reports. The TPE sampler sees all previous results and avoids them.

**Parallel (n_jobs=4)**:
```
Worker 1: Request params → Get {A} → Evaluate...
Worker 2: Request params → Get {B} → Evaluate...
Worker 3: Request params → Get {C} → Evaluate...
Worker 4: Request params → Get {D} → Evaluate...

[Race Condition Window: All 4 workers requested at nearly same time]
[None of them see what the others got yet]
```

## Root Causes of Concurrency-Induced Duplicates

### 1. Race Condition in Parameter Sampling ⚠️ PRIMARY CAUSE

**Problem**: Multiple workers request parameters from Optuna's sampler **before any of them complete**

**How it happens**:
```python
# In Optuna's study.optimize() with n_jobs=4

# Time T=0: Study asks sampler for 4 trials simultaneously
trial_1 = sampler.sample_independent(...)  # Worker 1
trial_2 = sampler.sample_independent(...)  # Worker 2 (doesn't see trial_1 yet)
trial_3 = sampler.sample_independent(...)  # Worker 3 (doesn't see trial_1 or 2)
trial_4 = sampler.sample_independent(...)  # Worker 4 (doesn't see any others)

# Time T=10: Trials start evaluating in parallel
# Time T=100: Trials finish and report results
# Time T=101: Now sampler learns about trials 1-4
```

**Why duplicates occur**:
- TPESampler makes decisions based on **completed trials only**
- During parallel execution, multiple workers are in-flight simultaneously
- Each worker's trial is NOT visible to others until it completes
- If search space is discrete/small, multiple workers can sample identical parameters

**Example with narrow search space**:
```yaml
parameters:
  param_a:
    type: grid
    values: [1, 2, 3]  # Only 3 choices
  param_b:
    type: grid
    values: [0.3, 0.4]  # Only 2 choices

# Total combinations: 3 × 2 = 6

# With 4 concurrent workers:
# All 4 request parameters at once
# Sampler has no completed trials yet (or few)
# Sampler uses random sampling (startup phase)
# Probability of duplicate = 4 workers / 6 combinations = 67%!
```

### 2. Startup Trials Phase ⚠️ AMPLIFIES RACE CONDITIONS

**Problem**: During `n_startup_trials`, TPESampler uses **pure random sampling**

```python
# Current default in our code
TPESampler(
    n_startup_trials=25,  # First 25 trials are RANDOM
    multivariate=True,
    constant_liar=True,
)
```

**Why this increases duplicates**:
- Random sampling doesn't avoid previous parameters
- With 4 concurrent workers, 4 random samples are drawn simultaneously
- No coordination between workers
- High collision probability in discrete spaces

**Example**:
```
Startup phase with n_jobs=4:

Batch 1 (trials 0-3):  All 4 drawn randomly, no history → high duplicate chance
Batch 2 (trials 4-7):  Still random, only 4 previous → duplicates likely
Batch 3 (trials 8-11): Still random, only 8 previous → duplicates possible
...
Batch 7 (trials 24-27): Last random batch

After trial 28: TPE modeling starts, but damage already done
```

### 3. Discrete/Rounded Search Space ⚠️ REDUCES EFFECTIVE SPACE

**Problem**: Integer parameters and float rounding reduce unique combinations

**Integer parameters**:
```yaml
# Only 11 possible values
max_hold_bars:
  type: int
  low: 10
  high: 20
  step: 1  # Values: 10, 11, 12, ..., 20
```

**Rounded floats**:
```yaml
# Only 21 possible values
entry_conf:
  type: float
  low: 0.30
  high: 0.50
  step: 0.01  # Values: 0.30, 0.31, 0.32, ..., 0.50
```

**Combined effect**:
```yaml
parameters:
  entry_conf:
    type: float
    low: 0.30
    high: 0.50
    step: 0.01  # 21 values

  htf_tolerance:
    type: float
    low: 0.3
    high: 0.7
    step: 0.1  # 5 values

  max_hold_bars:
    type: int
    low: 15
    high: 25
    step: 5  # 3 values

# Total combinations: 21 × 5 × 3 = 315

# With n_jobs=8:
# First batch requests 8 parameters
# Probability of at least one duplicate ≈ 1 - (315/315 × 314/315 × ... × 308/315)
# ≈ 8.8%

# After 50 trials (6-7 batches), 50 of 315 used = 16% consumed
# Next batch has even higher collision rate
```

### 4. Constant Liar Strategy ⚠️ MITIGATION PARTIALLY WORKS

**What is Constant Liar?**

`constant_liar=True` tells TPESampler to **predict** the result of in-flight trials:
- When worker requests parameters, sampler marks previous in-flight trials
- Assumes they will all return a constant value (typically median of history)
- This prevents new samples from being identical to in-flight ones

**Why it's not perfect**:
1. **Only works if sampler is aware of in-flight trials**
   - Requires proper study synchronization
   - May not work with all storage backends
   - Database locking issues can cause stale views

2. **Prediction may be wrong**
   - If constant value is far from actual result, doesn't guide sampler well
   - All in-flight trials get same predicted value, reducing information

3. **Doesn't prevent duplicates in startup phase**
   - Random sampling ignores constant liar predictions
   - First `n_startup_trials` are vulnerable

### 5. Storage Backend and Locking Issues

**Problem**: Different storage backends have different synchronization guarantees

**In-memory storage (None)**:
```python
study = optuna.create_study(storage=None)  # SQLite in memory
```
- No cross-process synchronization
- Each worker has independent view
- **WORST case for duplicates in parallel mode**

**SQLite file storage**:
```python
study = optuna.create_study(storage="sqlite:///optuna.db")
```
- File-based locking
- Workers compete for database access
- Race conditions still possible during reads
- **Better but not perfect**

**PostgreSQL/MySQL with heartbeat**:
```python
study = optuna.create_study(
    storage="postgresql://...",
    # Heartbeat mechanism for better synchronization
)
```
- Better transaction isolation
- Heartbeat detects stale workers
- **Best for parallel optimization** but still has race windows

## Quantifying the Duplicate Rate

### Formula for Expected Duplicates

For a search space with `N` total combinations and `k` concurrent workers:

**First batch (no history)**:
```
P(at least 1 duplicate) ≈ 1 - (N/N × (N-1)/N × (N-2)/N × ... × (N-k+1)/N)
                         ≈ 1 - e^(-k²/2N)  [approximation]
```

**After `m` batches (m×k trials completed)**:
```
Remaining space: N - m×k
P(duplicate in next batch) ≈ 1 - e^(-k²/2(N-m×k))
```

### Example Calculations

**Scenario 1: Narrow space, high concurrency**
```
N = 100 combinations
k = 8 workers
m = 0 (first batch)

P(duplicate) ≈ 1 - e^(-64/200) ≈ 1 - 0.73 ≈ 27%
```

**Scenario 2: Wide space, moderate concurrency**
```
N = 1000 combinations
k = 4 workers
m = 0

P(duplicate) ≈ 1 - e^(-16/2000) ≈ 1 - 0.992 ≈ 0.8%
```

**Scenario 3: Narrow space after many trials**
```
N = 100 combinations
k = 4 workers
m = 20 (80 trials completed)

Remaining: 100 - 80 = 20
P(duplicate) ≈ 1 - e^(-16/40) ≈ 1 - 0.67 ≈ 33%
```

## Current Implementation Analysis

### What We Already Have

```python
# From src/core/optimizer/runner.py

# 1. Better TPE defaults (helps with modeling quality)
TPESampler(
    multivariate=True,      # ✅ Considers parameter interactions
    constant_liar=True,     # ✅ Handles in-flight trials
    n_startup_trials=25,    # ⚠️  Still vulnerable in startup phase
    n_ei_candidates=48,     # ✅ More candidates per suggestion
)

# 2. Duplicate detection in objective function
def objective(trial):
    parameters = _suggest_parameters(trial, parameters_spec)
    key = _trial_key(parameters)

    if key in existing_trials:
        # ✅ Detects duplicates from previous runs (resume)
        return -1e6

    # ⚠️ Does NOT prevent duplicates within current parallel batch
```

### What's Missing

1. **No in-batch duplicate prevention**: Current code only checks `existing_trials` (from previous runs), not in-flight trials within current run

2. **No concurrency-aware warnings**: Diagnostics don't explain that high `n_jobs` increases duplicates

3. **No adaptive startup trials**: `n_startup_trials=25` is fixed, should scale with concurrency

## Solutions and Mitigations

### Solution 1: Reduce Concurrency ⭐ MOST EFFECTIVE

**Simple fix**: Lower `n_jobs` when space is discrete/narrow

```yaml
# Before
runs:
  max_concurrent: 8  # High parallelism

# After (for discrete space)
runs:
  max_concurrent: 2  # Lower parallelism, fewer duplicates
```

**Rule of thumb**:
```
Recommended n_jobs = min(
    available_cores,
    sqrt(total_combinations) / 2
)

Examples:
- 100 combinations → n_jobs ≤ 5
- 500 combinations → n_jobs ≤ 11
- 1000 combinations → n_jobs ≤ 15
```

### Solution 2: Increase Search Space Size ⭐ RECOMMENDED

**Remove unnecessary discretization**:
```yaml
# Before: Only 21 values
entry_conf:
  type: float
  low: 0.30
  high: 0.50
  step: 0.01  # DON'T use step if not necessary

# After: Continuous (infinite values)
entry_conf:
  type: float
  low: 0.30
  high: 0.50
  # No step = continuous sampling
```

**Use continuous parameters where possible**:
- Remove `step` from float parameters
- Use wider ranges
- Avoid grid search in parallel mode

### Solution 3: Adaptive Startup Trials

**Scale startup trials with concurrency**:
```python
# Proposed improvement
n_startup_trials = max(25, 5 * concurrency)

# Examples:
# n_jobs=1  → n_startup=25  (5 batches of random)
# n_jobs=4  → n_startup=25  (6 batches of random)
# n_jobs=8  → n_startup=40  (5 batches of random)
# n_jobs=16 → n_startup=80  (5 batches of random)
```

**Why this helps**:
- Ensures at least 5 batches of pure random sampling
- More diverse initial exploration
- Better seed for TPE modeling phase

### Solution 4: In-Batch Duplicate Prevention (Advanced)

**Add thread-safe tracking of in-flight parameters**:

```python
from threading import Lock

# Track parameters currently being evaluated
in_flight_params: set[str] = set()
in_flight_lock = Lock()

def objective(trial):
    parameters = _suggest_parameters(trial, parameters_spec)
    key = _trial_key(parameters)

    # Check if already in-flight
    with in_flight_lock:
        if key in in_flight_params:
            # This is a duplicate within current batch
            return -1e6
        in_flight_params.add(key)

    try:
        # Run trial
        result = make_trial(...)
        return result["score"]
    finally:
        # Remove from in-flight when done
        with in_flight_lock:
            in_flight_params.discard(key)
```

**Caveat**: This doesn't prevent Optuna from suggesting duplicates, just detects them earlier.

### Solution 5: Better Storage Backend

**Use proper database with transactions**:

```yaml
# Before: SQLite (file locking issues)
optuna:
  storage: "sqlite:///optuna.db"

# After: PostgreSQL (better concurrency)
optuna:
  storage: "postgresql://user:pass@localhost/optuna"
```

**Benefits**:
- Better transaction isolation
- Heartbeat mechanism for stale worker detection
- Reduced race condition window

### Solution 6: Sequential Batch Mode (Hybrid)

**Run multiple sequential studies with parallelism**:

```python
# Instead of:
# One study with n_jobs=16, max_trials=100

# Do:
# 10 sequential studies with n_jobs=4, max_trials=10 each
for batch in range(10):
    study.optimize(objective, n_trials=10, n_jobs=4)
    # Between batches, all workers synchronized
```

**Benefits**:
- Lower concurrency per batch = fewer duplicates
- Still gets total parallelism benefit
- Natural synchronization points

## Diagnostic Improvements

### Enhanced Warning Messages

Add concurrency-aware diagnostics:

```python
if duplicate_ratio > 0.3 and concurrency > 4:
    print(
        f"\n⚠️  WARNING: High duplicate rate ({duplicate_ratio*100:.1f}%) "
        f"with {concurrency} concurrent workers\n"
        f"   This is expected behavior with parallel optimization.\n"
        f"   RECOMMENDATIONS:\n"
        f"   - Reduce max_concurrent to {max(2, concurrency//2)}\n"
        f"   - Remove 'step' from float parameters (use continuous)\n"
        f"   - Use wider parameter ranges\n"
        f"   - Consider sequential batch mode\n"
    )
```

### Pre-Run Concurrency Check

Add to search space validator:

```python
def _estimate_duplicate_risk(
    total_combinations: int,
    concurrency: int,
    n_startup_trials: int
) -> dict[str, Any]:
    """Estimate duplicate probability with given concurrency."""

    # Risk in first batch
    first_batch_risk = 1 - math.exp(-concurrency**2 / (2 * total_combinations))

    # Risk after startup phase
    remaining = max(1, total_combinations - n_startup_trials)
    post_startup_risk = 1 - math.exp(-concurrency**2 / (2 * remaining))

    return {
        "first_batch_duplicate_prob": first_batch_risk,
        "post_startup_duplicate_prob": post_startup_risk,
        "recommended_max_concurrent": int(math.sqrt(total_combinations * 2)),
    }
```

## Recommendations

### For Users

1. **Discrete spaces**: Use `n_jobs=2-4` (not 8-16)
2. **Continuous spaces**: Can use higher `n_jobs=8-16`
3. **Narrow spaces** (<100 combinations): Use `n_jobs=1-2`
4. **Wide spaces** (>1000 combinations): Can use `n_jobs=8+`

### For Implementation

1. ✅ **Already done**: Better TPE defaults (`multivariate`, `constant_liar`)
2. ✅ **Already done**: Duplicate detection and penalties
3. ✅ **Already done**: Search space size warnings
4. ⚠️ **TODO**: Add concurrency-specific warnings
5. ⚠️ **TODO**: Adaptive `n_startup_trials` based on concurrency
6. ⚠️ **TODO**: Pre-run concurrency risk estimation
7. ⚠️ **TODO**: In-batch duplicate prevention (advanced)

## Testing Validation

To verify concurrency effects:

```bash
# Test 1: Sequential (baseline)
n_jobs=1, max_trials=50
Expected duplicates: <5%

# Test 2: Moderate parallelism
n_jobs=4, max_trials=50
Expected duplicates: 10-20%

# Test 3: High parallelism
n_jobs=16, max_trials=64
Expected duplicates: 30-50%

# All with same search space configuration
```

## Conclusion

**Concurrency increases duplicates** because:
1. Race conditions during parameter sampling
2. Startup trials use random sampling (no coordination)
3. Discrete spaces have limited unique combinations
4. Storage backends have synchronization limitations

**Mitigation strategies**:
1. Lower `n_jobs` for discrete/narrow spaces
2. Use continuous parameters (remove `step`)
3. Scale `n_startup_trials` with concurrency
4. Add concurrency-aware warnings
5. Consider sequential batch mode

The duplicate issue is **inherent to parallel optimization** with discrete spaces, not a bug. The solution is to **match concurrency level to search space size** and **use continuous parameters where possible**.
