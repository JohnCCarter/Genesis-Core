# Regime intelligence champion compatibility findings

Date: 2026-03-18
Branch: `feature/ri-optuna-train-validate-blind-v1`
Scope: analytical finding only; no runtime/champion/default changes.

## Executive summary

Yes — this finding should be documented.

The evidence shows that the currently active `tBTCUSD_3h` champion is **not RI-compatible as a simple overlay**. When the full champion surface is replayed on the 2024-07-01..2024-12-31 validation window, it trades and scores positively. When only RI authority is overlaid onto that same complete champion surface, trading collapses to zero. In contrast, the previously observed RI-positive path comes from a different runtime-shaped surface, not from the active champion.

Terminology note: the overlay/migration wording in this analysis is preserved as historical evidence about a rejected compatibility probe. It does **not** redefine the current canonical family model, where `strategy_family` is `legacy` or `ri` and hybrid surfaces fail closed rather than being stored as a third family label.

Working conclusion: this is better treated as a **strategy-topology finding** than as a small additive tuning note.

## Evidence chain

### 1. Baseline champion trades on validation

Source: `tmp/champion_validation_20260318.log`

- Return: `0.45%`
- Trades: `37`
- Win rate: `67.6%`
- Sharpe: `0.202`
- Max drawdown: `1.47%`
- Profit factor: `1.72`
- Score: `0.2617`

### 2. Champion + authority-only overlay collapses immediately

Source: `tmp/champion_complete_authority_only_validation_20260318.log`

- Return: `0.00%`
- Trades: `0`
- Score: `-100.1436`

This isolates the failure to the authority switch layer before clarity/risk-state become necessary explanatory variables.

### 3. Optuna RI candidate still trades, but is not the same config family

Sources: `tmp/trial_025_validation_replay_20260318.log`, `results/hparam_search/run_20260318_112046/best_trial.json`

Validation replay of `trial_025`:

- Return: `1.27%`
- Trades: `62`
- Win rate: `53.2%`
- Sharpe: `0.175`
- Max drawdown: `2.88%`
- Profit factor: `1.63`
- Score: `0.2273`

Important config facts from the frozen best-trial artifact:

- `meta.skip_champion_merge = true`
- `authority_mode = regime_module`
- `clarity_score.enabled = false`
- `risk_state.enabled = true`
- `signal_adaptation.atr_period = 14`
- gates `hysteresis_steps = 3`, `cooldown_bars = 2`
- `ltf_override_threshold = 0.4`

### 4. The earlier RI-positive path came from a runtime-shaped config surface

Sources: `results/backtests/tBTCUSD_3h_20260318_102831.json`, `config/runtime.json`

Observed from the RI-positive backtest artifact:

- `used_runtime_merge = true`
- Trades: `143`
- Total return: `2.2328%`
- Profit factor: `1.9867`
- Max drawdown: `2.3121%`

Key effective runtime-like inputs in that path:

- `thresholds.entry_conf_overall = 0.6`
- zone entry thresholds `0.22 / 0.26 / 0.30`
- `signal_adaptation.atr_period = 14`
- gates `hysteresis_steps = 3`, `cooldown_bars = 2`
- `ltf_override_threshold = 0.85`
- `htf_fib = null`
- `ltf_fib = null`

## Why this matters

The active champion surface and the RI-positive runtime surface differ in multiple interacting places:

- authority/calibration path
- ATR adaptation period
- gating cadence (`3/2` vs `2/0`)
- LTF override policy
- Fib entry surface present on champion, absent on runtime path
- exit surface differences

Because the champion already fails at **authority-only**, the result should not be framed as “champion + a small RI patch underperformed.”

The more accurate interpretation is:

1. RI can work on a runtime-shaped surface.
2. The current champion does not tolerate a direct RI authority overlay.
3. Therefore the RI candidate behaves like a **different strategy family / topology**, not like a simple champion migration candidate.

## Current classification

### Recommended label

`new strategy family`

### Why not `migration candidate`?

A migration candidate would normally survive a minimal compatibility overlay and then require tuning refinement. Here, the active champion loses all trades at the first authority step. That is too large a topology break to treat as a minor migration delta.

## Ranked minimal diff

Below, “impact” means explanatory power for the observed topology break: champion trades as-is, but champion + authority-only drops to zero trades.

### Rank 1 — calibration-sensitive regime path

**Status:** required for RI, but not sufficient on its own
**Fields:**

- `multi_timeframe.regime_intelligence.enabled = true`
- `multi_timeframe.regime_intelligence.version = "v2"`
- `multi_timeframe.regime_intelligence.authority_mode = "regime_module"`

Why this ranks first:

- The zero-trade collapse appears immediately when the champion keeps its full native surface and only swaps authority to `regime_module`.
- The replay with authority-only and the replay with authority + mild `risk_state` both remain at `0` trades and `-100.1436` score.
- This means the topology break begins at the regime-authority / regime-aware calibration path, before sizing-only RI features can matter.

Interpretation:

- RI authority is the trigger for the new behavior family.
- But authority alone is **not** a migration patch; it must travel with an RI-compatible decision surface.

### Rank 2 — threshold and zone surface

**Status:** required compatibility cluster
**Fields:**

- Champion base thresholds:
  - `entry_conf_overall = 0.26`
  - `regime_proba.balanced = 0.50`
  - zone entry thresholds `0.24 / 0.30 / 0.36`
  - zone regime thresholds `0.36 / 0.44 / 0.56`
- RI candidate thresholds:
  - `entry_conf_overall = 0.25`
  - `regime_proba.balanced = 0.36`
  - zone entry thresholds `0.16 / 0.40 / 0.32`
  - zone regime thresholds `0.33 / 0.51 / 0.57`
- RI-positive runtime surface:
  - `entry_conf_overall = 0.6`
  - zone entry thresholds `0.22 / 0.26 / 0.30`
  - zone regime thresholds roughly `0.46-0.55` by zone/regime

Why this ranks second:

- Once authority changes the regime path, the decision gates consume a different calibrated probability stream.
- The champion’s native threshold surface was not built for that RI authority path.
- Both successful RI surfaces (`trial_025` and the RI-positive runtime path) use non-champion threshold families.

Interpretation:

- The smallest evidenced compatibility unit is not “authority only”.
- It is “authority + RI-native threshold surface”.

### Rank 3 — signal adaptation period

**Status:** likely required for compatibility
**Fields:**

- Champion: `thresholds.signal_adaptation.atr_period = 28`
- RI candidate: `thresholds.signal_adaptation.atr_period = 14`
- RI-positive runtime surface: `thresholds.signal_adaptation.atr_period = 14`

Why this ranks third:

- This is one of the cleanest common denominators across both working RI surfaces.
- ATR-zone assignment feeds directly into which threshold bucket is applied.
- Keeping the champion’s `28`-bar adaptation while switching authority likely compounds the mismatch between regime path and gate surface.

Interpretation:

- `atr_period = 14` should be treated as part of the RI-compatible prep surface, not as an afterthought.

### Rank 4 — gating cadence

**Status:** likely required as family-level shape, but secondary to the threshold/calibration cluster
**Fields:**

- Champion: `hysteresis_steps = 2`, `cooldown_bars = 0`
- RI candidate: `hysteresis_steps = 3`, `cooldown_bars = 2`
- RI-positive runtime surface: `hysteresis_steps = 3`, `cooldown_bars = 2`

Why this ranks fourth:

- Both working RI surfaces converge on `3/2` rather than the champion’s `2/0`.
- However, cooldown/hysteresis cannot by themselves explain a total zero-trade collapse as cleanly as the authority + threshold mismatch does.

Interpretation:

- Gating cadence looks like a family trait of the RI surface.
- It should be migrated together with the threshold surface if we want an RI-compatible baseline.

### Rank 5 — fib / entry surface

**Status:** optional tuning for now; not proven as the primary compatibility blocker
**Fields:**

- Champion:
  - `htf_fib.entry.enabled = true`
  - `htf_fib.entry.tolerance_atr = 3.0`
  - `ltf_fib.entry.enabled = true`
  - `ltf_fib.entry.tolerance_atr = 1.25`
- RI candidate:
  - HTF/LTF Fib still enabled, but looser (`4.0` / `1.5`)
- RI-positive runtime surface:
  - `htf_fib = null`
  - `ltf_fib = null`

Why this ranks fifth:

- The runtime RI-positive path works without Fib entry blocks.
- But `trial_025` still trades with Fib entries enabled.
- Therefore Fib configuration is not the cleanest universal explanation for the topology split.

Interpretation:

- Fib surface may still matter for performance and compatibility margins.
- It is not yet evidenced as the first required migration unit.

### Rank 6 — LTF override policy

**Status:** optional tuning, not a required compatibility anchor
**Fields:**

- Champion: `ltf_override_threshold = 0.45`
- RI candidate: `ltf_override_threshold = 0.4`
- RI-positive runtime surface: `ltf_override_threshold = 0.85`

Why this ranks sixth:

- All three surfaces differ materially.
- There is no stable RI consensus value here.

Interpretation:

- This looks like downstream tuning, not the minimal explanation for the topology break.

### Rank 7 — risk_state and clarity_score

**Status:** optional tuning for the current compatibility question
**Fields:**

- `clarity_score.enabled`
- `risk_state.*`

Why this ranks seventh:

- `trial_025` works with `risk_state.enabled = true` and `clarity_score.enabled = false`.
- Earlier ablation already suggested clarity was neutral/slightly negative.
- Most importantly, adding mild `risk_state` on top of champion + authority did **not** restore trading.

Interpretation:

- These are not primary compatibility levers for the zero-trade failure.

### Rank 8 — exit surface

**Status:** optional tuning for this specific question
**Fields:**

- `exit.max_hold_bars`
- `trailing_stop_pct`
- `stop_loss_pct`
- `htf_exit_config.*`

Why this ranks eighth:

- Exit settings can materially change return shape once entries exist.
- They do not explain a replay with zero entries.

Interpretation:

- Exit tuning belongs later in the process than restoring an RI-compatible entry/decision surface.

## Required vs optional for RI compatibility

### Required for an RI-compatible baseline

The current evidence supports the following as the **minimum migration cluster**:

1. RI authority path:
   - `regime_intelligence.enabled = true`
   - `version = "v2"`
   - `authority_mode = "regime_module"`
2. RI-native threshold family:
   - non-champion threshold surface aligned to the RI path
3. `signal_adaptation.atr_period = 14`
4. RI-family gating cadence:
   - `hysteresis_steps = 3`
   - `cooldown_bars = 2`

### Optional / downstream tuning

- `risk_state.*`
- `clarity_score.*`
- `ltf_override_threshold`
- Fib entry enablement/tolerances
- exit and HTF-exit details

## Minimal RI-compatible config surface

This is the smallest surface that is supported by the current evidence, without claiming retuned optimality:

- `multi_timeframe.regime_intelligence.enabled = true`
- `multi_timeframe.regime_intelligence.version = "v2"`
- `multi_timeframe.regime_intelligence.authority_mode = "regime_module"`
- `thresholds.signal_adaptation.atr_period = 14`
- adopt an RI-native threshold surface rather than the champion threshold family
- `gates.hysteresis_steps = 3`
- `gates.cooldown_bars = 2`
- keep `clarity_score.enabled = false` as the default compatibility stance
- treat `risk_state` as optional once the entry surface trades again

## Final decision framing

The smallest evidenced compatibility unit is **not one parameter**.

It is a **cluster**:

- authority path
- threshold family
- ATR adaptation period
- gating cadence

That is why the current evidence continues to support the label:

- `new strategy family`

rather than:

- `migration candidate`

If the topology break had been recoverable by authority-only plus a single narrow patch, `migration candidate` would still be plausible. The current evidence does not support that narrower interpretation.

## Status note

This note is an analysis artifact only. It does **not** approve promotion, default cutover, or champion replacement.
