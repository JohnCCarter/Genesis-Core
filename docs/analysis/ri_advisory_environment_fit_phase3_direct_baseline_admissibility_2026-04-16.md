# RI advisory environment-fit — Phase 3 direct-baseline admissibility

This memo is docs-only and fail-closed.
It decides whether the roadmap may open a direct RI deterministic advisory-baseline slice now.

Governance packet: `docs/governance/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_packet_2026-04-16.md`

## Source surface used

This memo uses only already tracked surfaces:

- `docs/analysis/ri_advisory_environment_fit_phase1_observability_inventory_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `src/core/strategy/run_intent.py`
- already tracked trace/capture patterns cited during the current lane

## Decision question

May the roadmap open a direct RI deterministic advisory-baseline slice now?

## Short answer

**No — direct Phase 3 is not admissible yet.**

The lane first needs a separate RI evidence-capture slice.

## Why direct Phase 3 is blocked

### 1. The strongest current supportive/hostile evidence chain is on a legacy-family surface

The current-ATR evidence used to shape the advisory question is materially useful, but its bounded config artifacts are explicitly:

- `strategy_family = legacy`

This is true for both:

- `candidate_900_cfg.json`
- the paired baseline `0.90` config artifact

That matters because the roadmap was explicitly constrained to:

- `ri` only

So the current-ATR evidence can justify the **question**, but it cannot by itself serve as the direct RI baseline training/capture surface.

### 2. A direct RI baseline needs row-level RI observability on an RI surface, not just legacy outcome evidence

Phase 1 established that useful RI observability already exists in tracked code:

- clarity fields
- transition-risk proxy fields
- authoritative-vs-shadow mismatch

Phase 2 then defined the allowed outcome labels and state tags.

But a direct deterministic baseline still needs one thing that is not yet present on the same fixed RI evidence surface:

- row-level RI observability joined to later bounded outcome labels on an RI-family execution surface

The current lane has partial capture patterns and diagnostics, but not yet one fixed RI evidence surface that cleanly joins:

- RI observability inputs
- allowed outcome labels
- contradiction-year evaluation discipline

### 3. The nearest fixed RI bridge surface is useful, but still not sufficient by itself

The nearest obvious RI runtime-valid candidate is:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

That file is explicitly:

- `strategy_family = ri`
- `authority_mode = regime_module`
- a backtest-only runtime bridge, not promotion evidence

That makes it a plausible future RI evidence carrier.

But it still leaves an important limitation:

- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`

So even the nearest fixed RI bridge does not automatically materialize the full advisory ingredient set the roadmap wants to study.

This does **not** block the entire lane.
It blocks only the shortcut of pretending that a direct RI deterministic baseline can be opened immediately.

## Admissibility decision

Direct Phase 3 deterministic-baseline implementation is:

- **blocked / not admissible now**

Conservative basis:

1. the strongest supportive/hostile evidence chain is legacy, not RI
2. the RI lane requires row-level observability on an RI-family surface
3. the nearest fixed RI bridge is useful but does not yet guarantee the full advisory ingredient set on its own
4. opening a score implementation now would risk mixing:
   - legacy outcome evidence
   - RI observability ingredients
   - no single fixed RI evidence carrier

That would violate the lane’s own RI-only discipline.

## Exact next admissible step

The next admissible move is narrower than a direct baseline implementation:

- one bounded RI evidence-capture slice on a fixed RI research surface

That later slice should do only enough to materialize a clean RI evidence table for later scoring work, for example:

- fixed RI config carrier
- row-level RI observability fields
- bounded join to admissible outcome labels / contradiction-year evaluation
- no runtime authority change
- no score implementation yet

What that next slice should **not** do:

- no direct score implementation
- no ML comparison
- no promotion/readiness framing

## Consequence for the roadmap

The roadmap should therefore be interpreted as:

- Phase 1: complete
- Phase 2: complete
- direct Phase 3: blocked for now
- prerequisite: RI evidence-capture slice

So the lane is still alive, but it has reached an honest evidence-surface boundary.

## Bottom line

The lane should **not** jump directly from labels to a deterministic RI baseline on the current evidence surface.

The reason is precise:

- the current strongest outcome evidence is `legacy`
- the future lane is explicitly `ri`
- and the nearest fixed RI bridge still needs a separate bounded evidence-capture step before a direct deterministic baseline is admissible

So the correct closeout here is:

- **direct Phase 3 is blocked**
- **the next admissible step is a bounded RI evidence-capture slice, not a score implementation slice**
