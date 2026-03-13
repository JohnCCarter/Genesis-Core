# Risk State Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `risk_state` multiplier to position sizing that reduces size during equity drawdowns and regime transitions, making Phase D Optuna optimization possible.

**Architecture:** Two new persistent state keys (`equity_drawdown_pct`, `bars_since_regime_change`) are injected from `engine.py` each bar. A new `compute_risk_state_multiplier()` function in `regime_intelligence.py` reads these keys and returns a float multiplier (0.0–1.0) that is multiplied into `combined_mult` inside `decision_sizing.py`. Config is driven by `multi_timeframe.regime_intelligence.risk_state` YAML block.

**Tech Stack:** Python 3.13, existing Genesis-Core architecture (decision_sizing.py, regime_intelligence.py, engine.py). No new dependencies.

---

## Chunk 1: Engine Injection + State Persistence

### Task 1: Inject equity drawdown into engine state

**Files:**
- Modify: `src/core/backtest/engine.py` (~line 888, before `evaluate_pipeline` call)

**Background:** `self.position_tracker.current_equity` is available in the engine loop. We need to inject `equity_drawdown_pct` (0.0 = no drawdown, 0.05 = 5% below peak) and `peak_equity` into `self.state` before calling `evaluate_pipeline`. The pipeline then carries it into `state_in` via `{**state, ...}` merge in `evaluate.py`.

- [ ] **Step 1: Read the relevant engine section**

Read `src/core/backtest/engine.py` lines 860–900 to confirm the injection point.

- [ ] **Step 2: Add equity drawdown injection**

In `engine.py`, just before the `evaluate_pipeline(...)` call (currently line ~890), add:

```python
# Inject equity risk state for risk_state multiplier
_cur_eq = self.position_tracker.current_equity
_peak_eq = self.state.get("_peak_equity", _cur_eq)
if _cur_eq > _peak_eq:
    _peak_eq = _cur_eq
self.state["_peak_equity"] = _peak_eq
self.state["equity_drawdown_pct"] = (
    (_peak_eq - _cur_eq) / _peak_eq if _peak_eq > 0 else 0.0
)
```

- [ ] **Step 3: Write test for equity injection**

**Test file:** `tests/utils/test_risk_state_engine.py`

```python
"""Test that engine injects equity_drawdown_pct into state each bar."""
from unittest.mock import MagicMock, patch
import pytest


def test_equity_drawdown_pct_injected_into_state():
    """equity_drawdown_pct is 0.0 when equity equals peak."""
    from core.backtest.engine import BacktestEngine

    engine = BacktestEngine.__new__(BacktestEngine)
    engine.state = {}
    mock_pt = MagicMock()
    mock_pt.current_equity = 10000.0
    engine.position_tracker = mock_pt

    # Simulate the injection logic directly
    _cur_eq = engine.position_tracker.current_equity
    _peak_eq = engine.state.get("_peak_equity", _cur_eq)
    if _cur_eq > _peak_eq:
        _peak_eq = _cur_eq
    engine.state["_peak_equity"] = _peak_eq
    engine.state["equity_drawdown_pct"] = (
        (_peak_eq - _cur_eq) / _peak_eq if _peak_eq > 0 else 0.0
    )

    assert engine.state["equity_drawdown_pct"] == 0.0
    assert engine.state["_peak_equity"] == 10000.0


def test_equity_drawdown_pct_reflects_loss():
    """equity_drawdown_pct is 0.05 when equity dropped 5% from peak."""
    from core.backtest.engine import BacktestEngine

    engine = BacktestEngine.__new__(BacktestEngine)
    engine.state = {"_peak_equity": 10000.0}
    mock_pt = MagicMock()
    mock_pt.current_equity = 9500.0
    engine.position_tracker = mock_pt

    _cur_eq = engine.position_tracker.current_equity
    _peak_eq = engine.state.get("_peak_equity", _cur_eq)
    if _cur_eq > _peak_eq:
        _peak_eq = _cur_eq
    engine.state["_peak_equity"] = _peak_eq
    engine.state["equity_drawdown_pct"] = (
        (_peak_eq - _cur_eq) / _peak_eq if _peak_eq > 0 else 0.0
    )

    assert abs(engine.state["equity_drawdown_pct"] - 0.05) < 1e-9
```

- [ ] **Step 4: Run test**

```bash
cd Genesis-Core
PYTHONPATH=src pytest tests/utils/test_risk_state_engine.py -v
```

Expected: 2 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/core/backtest/engine.py tests/utils/test_risk_state_engine.py
git commit -m "feat(engine): inject equity_drawdown_pct into state each bar"
```

---

### Task 2: Persist regime transition counter in state_out

**Files:**
- Modify: `src/core/strategy/decision_sizing.py` (end of function, before `return`)

**Background:** `regime` is passed as an argument to `apply_sizing`. We track `last_regime` from the previous bar (persisted in `state_in`) and count `bars_since_regime_change`. Both are written to `state_out` to persist across bars.

- [ ] **Step 1: Add regime transition tracking to apply_sizing**

In `decision_sizing.py`, just before `return size, conf_val_gate` (currently last line), add:

```python
# Regime transition tracking for risk_state
_last_regime = state_in.get("last_regime")
_cur_regime = str(regime or "")
if _last_regime is None or _last_regime == _cur_regime:
    _bars_since_change = int(state_in.get("bars_since_regime_change", 0))
else:
    _bars_since_change = 0  # reset on transition
state_out["last_regime"] = _cur_regime
state_out["bars_since_regime_change"] = _bars_since_change + 1
```

- [ ] **Step 2: Write test**

Add to `tests/utils/test_risk_state_engine.py`:

```python
def test_bars_since_regime_change_resets_on_transition():
    """bars_since_regime_change resets to 1 when regime changes."""
    state_in = {"last_regime": "bull", "bars_since_regime_change": 5}
    state_out = {}

    _last_regime = state_in.get("last_regime")
    _cur_regime = "bear"
    if _last_regime is None or _last_regime == _cur_regime:
        _bars_since_change = int(state_in.get("bars_since_regime_change", 0))
    else:
        _bars_since_change = 0
    state_out["last_regime"] = _cur_regime
    state_out["bars_since_regime_change"] = _bars_since_change + 1

    assert state_out["bars_since_regime_change"] == 1
    assert state_out["last_regime"] == "bear"


def test_bars_since_regime_change_increments_on_stable():
    """bars_since_regime_change increments when regime is stable."""
    state_in = {"last_regime": "bull", "bars_since_regime_change": 5}
    state_out = {}

    _last_regime = state_in.get("last_regime")
    _cur_regime = "bull"
    if _last_regime is None or _last_regime == _cur_regime:
        _bars_since_change = int(state_in.get("bars_since_regime_change", 0))
    else:
        _bars_since_change = 0
    state_out["last_regime"] = _cur_regime
    state_out["bars_since_regime_change"] = _bars_since_change + 1

    assert state_out["bars_since_regime_change"] == 6
```

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src pytest tests/utils/test_risk_state_engine.py -v
```

Expected: 4 PASSED

- [ ] **Step 4: Commit**

```bash
git add src/core/strategy/decision_sizing.py tests/utils/test_risk_state_engine.py
git commit -m "feat(sizing): persist regime transition counter in state_out"
```

---

## Chunk 2: Risk State Multiplier Function

### Task 3: Add compute_risk_state_multiplier to regime_intelligence.py

**Files:**
- Modify: `src/core/strategy/regime_intelligence.py`
- Test: `tests/utils/test_risk_state_multiplier.py`

**Background:** This function reads `equity_drawdown_pct` and `bars_since_regime_change` from state and returns a float multiplier in [0.0, 1.0]. Config structure:

```yaml
multi_timeframe:
  regime_intelligence:
    risk_state:
      enabled: true
      drawdown_guard:
        soft_threshold: 0.03    # -3% from peak -> scale to soft_mult
        hard_threshold: 0.06    # -6% from peak -> scale to hard_mult
        soft_mult: 0.70         # size multiplier at soft threshold
        hard_mult: 0.40         # size multiplier at hard threshold
      transition_guard:
        enabled: true
        guard_bars: 4           # bars after regime change to apply multiplier
        mult: 0.60              # size multiplier during transition window
```

The multiplier logic:
- Start at 1.0
- Apply drawdown guard: linearly interpolate between 1.0 and hard_mult based on drawdown pct
- Apply transition guard: if bars_since_regime_change <= guard_bars, multiply by transition mult
- Both are multiplicative (not additive)
- Clamp result to [0.05, 1.0]

- [ ] **Step 1: Write the failing tests first**

Create `tests/utils/test_risk_state_multiplier.py`:

```python
"""Tests for compute_risk_state_multiplier in regime_intelligence."""
import pytest


def _cfg(
    enabled=True,
    soft_threshold=0.03,
    hard_threshold=0.06,
    soft_mult=0.70,
    hard_mult=0.40,
    transition_enabled=True,
    guard_bars=4,
    transition_mult=0.60,
):
    return {
        "enabled": enabled,
        "drawdown_guard": {
            "soft_threshold": soft_threshold,
            "hard_threshold": hard_threshold,
            "soft_mult": soft_mult,
            "hard_mult": hard_mult,
        },
        "transition_guard": {
            "enabled": transition_enabled,
            "guard_bars": guard_bars,
            "mult": transition_mult,
        },
    }


def test_disabled_returns_one():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    result = compute_risk_state_multiplier(
        cfg=_cfg(enabled=False),
        equity_drawdown_pct=0.10,
        bars_since_regime_change=1,
    )
    assert result["multiplier"] == 1.0
    assert result["enabled"] is False


def test_no_drawdown_no_transition_returns_one():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.0,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == 1.0


def test_soft_drawdown_reduces_size():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    # At soft_threshold (0.03), mult should be soft_mult (0.70)
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.03,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == pytest.approx(0.70, abs=0.01)


def test_hard_drawdown_reduces_size_to_hard_mult():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.06,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == pytest.approx(0.40, abs=0.01)


def test_drawdown_beyond_hard_clamped():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.20,
        bars_since_regime_change=10,
    )
    assert result["multiplier"] == pytest.approx(0.40, abs=0.01)


def test_transition_within_guard_window_reduces_size():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.0,
        bars_since_regime_change=2,  # within guard_bars=4
    )
    assert result["multiplier"] == pytest.approx(0.60, abs=0.01)


def test_transition_outside_guard_window_no_effect():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.0,
        bars_since_regime_change=5,  # outside guard_bars=4
    )
    assert result["multiplier"] == 1.0


def test_drawdown_and_transition_are_multiplicative():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    # soft drawdown (0.70) * transition (0.60) = 0.42
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.03,
        bars_since_regime_change=2,
    )
    assert result["multiplier"] == pytest.approx(0.70 * 0.60, abs=0.01)


def test_result_contains_debug_keys():
    from core.strategy.regime_intelligence import compute_risk_state_multiplier
    result = compute_risk_state_multiplier(
        cfg=_cfg(),
        equity_drawdown_pct=0.04,
        bars_since_regime_change=2,
    )
    assert "multiplier" in result
    assert "drawdown_mult" in result
    assert "transition_mult" in result
    assert "equity_drawdown_pct" in result
    assert "bars_since_regime_change" in result
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
PYTHONPATH=src pytest tests/utils/test_risk_state_multiplier.py -v
```

Expected: all FAIL with `ImportError` or `AttributeError`

- [ ] **Step 3: Implement compute_risk_state_multiplier**

Add to the end of `src/core/strategy/regime_intelligence.py`:

```python
def compute_risk_state_multiplier(
    *,
    cfg: dict[str, Any],
    equity_drawdown_pct: float,
    bars_since_regime_change: int,
) -> dict[str, Any]:
    """Compute position size multiplier based on current risk state.

    Returns a dict with 'multiplier' (float in [0.05, 1.0]) plus debug keys.
    """
    if not cfg or not bool(cfg.get("enabled", False)):
        return {
            "enabled": False,
            "multiplier": 1.0,
            "drawdown_mult": 1.0,
            "transition_mult": 1.0,
            "equity_drawdown_pct": equity_drawdown_pct,
            "bars_since_regime_change": bars_since_regime_change,
        }

    dd_cfg = dict(cfg.get("drawdown_guard") or {})
    soft_thr = float(dd_cfg.get("soft_threshold", 0.03))
    hard_thr = float(dd_cfg.get("hard_threshold", 0.06))
    soft_mult = float(dd_cfg.get("soft_mult", 0.70))
    hard_mult = float(dd_cfg.get("hard_mult", 0.40))

    # Linear interpolation between thresholds
    dd = float(equity_drawdown_pct)
    if dd <= 0.0:
        drawdown_mult = 1.0
    elif dd >= hard_thr:
        drawdown_mult = hard_mult
    elif dd >= soft_thr:
        t = (dd - soft_thr) / max(hard_thr - soft_thr, 1e-9)
        drawdown_mult = soft_mult + t * (hard_mult - soft_mult)
    else:
        t = dd / max(soft_thr, 1e-9)
        drawdown_mult = 1.0 + t * (soft_mult - 1.0)

    tr_cfg = dict(cfg.get("transition_guard") or {})
    transition_mult = 1.0
    if bool(tr_cfg.get("enabled", True)):
        guard_bars = int(tr_cfg.get("guard_bars", 4))
        if 0 < bars_since_regime_change <= guard_bars:
            transition_mult = float(tr_cfg.get("mult", 0.60))

    multiplier = max(0.05, min(1.0, drawdown_mult * transition_mult))

    return {
        "enabled": True,
        "multiplier": multiplier,
        "drawdown_mult": drawdown_mult,
        "transition_mult": transition_mult,
        "equity_drawdown_pct": dd,
        "bars_since_regime_change": bars_since_regime_change,
    }
```

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH=src pytest tests/utils/test_risk_state_multiplier.py -v
```

Expected: all 9 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/core/strategy/regime_intelligence.py tests/utils/test_risk_state_multiplier.py
git commit -m "feat(ri): add compute_risk_state_multiplier for drawdown + transition guard"
```

---

## Chunk 3: Wire Into Sizing + Phase D Config

### Task 4: Wire risk_state multiplier into decision_sizing.py

**Files:**
- Modify: `src/core/strategy/decision_sizing.py`

**Background:** `combined_mult` is currently `size_scale * regime_mult * htf_regime_mult * vol_size_mult`. We multiply `risk_state_mult` into it. The risk_state config lives at `ri_cfg["risk_state"]`. Input data comes from `state_in["equity_drawdown_pct"]` and `state_in["bars_since_regime_change"]`.

- [ ] **Step 1: Read decision_sizing.py lines 100-130**

Confirm the `combined_mult` calculation and `state_out` assignment block.

- [ ] **Step 2: Add risk_state_mult computation**

In `decision_sizing.py`, after `vol_size_mult` calculation (currently ~line 115), add:

```python
risk_state_mult = 1.0
risk_state_payload: dict[str, Any] = {"enabled": False, "multiplier": 1.0}
risk_state_cfg = dict(ri_cfg.get("risk_state") or {})
if ri_enabled and bool(risk_state_cfg.get("enabled", False)):
    _eq_dd = float(state_in.get("equity_drawdown_pct", 0.0))
    _bars_rc = int(state_in.get("bars_since_regime_change", 99))
    risk_state_payload = _regime_intelligence.compute_risk_state_multiplier(
        cfg=risk_state_cfg,
        equity_drawdown_pct=_eq_dd,
        bars_since_regime_change=_bars_rc,
    )
    risk_state_mult = float(risk_state_payload.get("multiplier", 1.0))
risk_state_mult = max(0.0, min(1.0, risk_state_mult))
```

Then update the `combined_mult` line (currently `size_scale * regime_mult * htf_regime_mult * vol_size_mult`):

```python
combined_mult = size_scale * regime_mult * htf_regime_mult * vol_size_mult * risk_state_mult
```

Then add to the `state_out` block:

```python
state_out["ri_risk_state_enabled"] = bool(risk_state_payload.get("enabled"))
state_out["ri_risk_state_multiplier"] = risk_state_payload.get("multiplier")
state_out["ri_risk_state_drawdown_mult"] = risk_state_payload.get("drawdown_mult")
state_out["ri_risk_state_transition_mult"] = risk_state_payload.get("transition_mult")
```

- [ ] **Step 3: Run existing sizing tests to confirm no regression**

```bash
PYTHONPATH=src pytest tests/ -k "sizing or decision" -v --tb=short
```

Expected: all existing tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/core/strategy/decision_sizing.py
git commit -m "feat(sizing): wire risk_state multiplier into combined_mult"
```

---

### Task 5: Phase D YAML config

**Files:**
- Create: `config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml`

**Background:** All Phase A + B params are fixed. Only 5-6 `risk_state` params are tunable. 75 trials is sufficient for this small search space.

- [ ] **Step 1: Create Phase D YAML**

```yaml
description: "Phase D: Risk State optimisation -- drawdown_guard + transition_guard"
#
# Phase A + B best params fixed. Only risk_state params tunable.
# Run: PYTHONIOENCODING=utf-8 TQDM_DISABLE=1 PYTHONPATH="$(pwd)/src" python -m core.optimizer.runner config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml

meta:
  symbol: tBTCUSD
  timeframe: 3h
  snapshot_id: snap_tBTCUSD_3h_2024-01-02_2024-12-31_v1
  warmup_bars: 120
  score_version: "v2"
  base_phase_path: "config/optimizer/phased_v3_best_trials/phaseC_oos_trial.json"
  runs:
    strategy: optuna
    score_version: "v2"
    use_sample_range: true
    sample_start: "2024-01-01"
    sample_end: "2024-12-31"
    validation:
      enabled: true
      start_date: "2025-01-01"
      end_date:   "2025-12-31"
    resume: false
    max_trials: 75
    max_concurrent: 1
    promotion:
      enabled: false
    constraints:
      include_scoring_failures: false
      min_trades: 30
      min_profit_factor: 1.10
      max_max_dd: 0.30
    optuna:
      study_name: "phased_v3_phaseD_riskstate_3h_2024"
      storage: "sqlite:///results/hparam_search/storage/phased_v3_phaseD_3h.db"
      n_jobs: 1
      timeout_seconds: 7200
      bootstrap_random_trials: 20
      bootstrap_seed: 42
      pruner:
        type: "none"
      sampler:
        type: "tpe"
        kwargs:
          n_startup_trials: 20
          multivariate: true

# All Phase A + B params fixed (from phaseC_oos_trial.json via base_phase_path)
# Only risk_state params are tunable
parameters:
  multi_timeframe.regime_intelligence.risk_state.enabled:
    type: fixed
    value: true

  multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold:
    type: float
    low: 0.02
    high: 0.06
    step: 0.01

  multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold:
    type: float
    low: 0.04
    high: 0.12
    step: 0.02

  multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult:
    type: float
    low: 0.50
    high: 0.90
    step: 0.10

  multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult:
    type: float
    low: 0.20
    high: 0.60
    step: 0.10

  multi_timeframe.regime_intelligence.risk_state.transition_guard.enabled:
    type: fixed
    value: true

  multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars:
    type: int
    low: 2
    high: 8
    step: 1

  multi_timeframe.regime_intelligence.risk_state.transition_guard.mult:
    type: float
    low: 0.40
    high: 0.80
    step: 0.10
```

- [ ] **Step 2: Validate YAML parses correctly**

```bash
python -c "import yaml; yaml.safe_load(open('config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml'))"
```

Expected: no output (no errors)

- [ ] **Step 3: Commit**

```bash
git add config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml
git commit -m "feat(optimizer): add Phase D YAML for risk_state optimisation"
```

---

## Chunk 4: Dry-run Verification

### Task 6: Verify end-to-end with dry run (3 trials)

**Files:** None (verification only)

- [ ] **Step 1: Run 3-trial dry run**

Temporarily set `max_trials: 3` in Phase D YAML and run:

```bash
PYTHONIOENCODING=utf-8 TQDM_DISABLE=1 PYTHONPATH="$(pwd)/src" python -m core.optimizer.runner config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml 2>&1 | grep -E "Trial|score=|risk_state|ERROR|error"
```

Expected output contains lines like:
```
[Runner] Trial trial_001 klar på ...s (score=..., trades=..., ...)
[Runner] Trial trial_002 klar ...
[Runner] Trial trial_003 klar ...
```

**No** `ERROR` or `KeyError` lines.

- [ ] **Step 2: Verify risk_state keys in trial JSON**

```bash
python -c "
import json, os, glob
d = sorted(glob.glob('results/hparam_search/run_*/trial_001.json'))[-1]
t = json.load(open(d))
keys = list((t.get('merged_config') or t).keys())
print('Has risk_state:', any('risk_state' in str(k) for k in keys))
print('ri_risk_state_multiplier in state:', 'ri_risk_state_multiplier' in str(t))
"
```

Expected: `Has risk_state: True`

- [ ] **Step 3: Restore max_trials: 75 and commit**

```bash
git add config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml
git commit -m "chore(optimizer): restore max_trials=75 in Phase D after dry-run"
```

- [ ] **Step 4: Push branch**

```bash
git push
```

---

## Summary

| Task | Files | Tests |
|------|-------|-------|
| 1 — Engine equity injection | `engine.py` | `test_risk_state_engine.py` |
| 2 — Regime transition counter | `decision_sizing.py` | `test_risk_state_engine.py` |
| 3 — compute_risk_state_multiplier | `regime_intelligence.py` | `test_risk_state_multiplier.py` |
| 4 — Wire into combined_mult | `decision_sizing.py` | existing tests |
| 5 — Phase D YAML | `phaseD.yaml` | YAML parse check |
| 6 — Dry-run | — | integration smoke test |

**Run command for full Phase D after implementation:**
```bash
PYTHONIOENCODING=utf-8 TQDM_DISABLE=1 PYTHONPATH="$(pwd)/src" python -m core.optimizer.runner config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml
```
