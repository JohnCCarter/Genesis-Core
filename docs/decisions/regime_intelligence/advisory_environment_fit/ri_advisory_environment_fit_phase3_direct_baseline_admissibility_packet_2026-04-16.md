# RI advisory environment-fit Phase 3 direct-baseline admissibility packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `blocked / docs-only / admissibility decision / no implementation opened`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only admissibility decision on whether the roadmap may open a direct RI deterministic-baseline slice now, using already tracked configs, artifacts, and analysis notes only.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide fail-closed whether a direct Phase 3 deterministic advisory baseline is admissible now, or whether the lane must first open a separate RI evidence-capture slice.
- **Candidate:** `RI advisory environment-fit Phase 3 direct baseline opening decision`
- **Base SHA:** `45fecbeb`

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_packet_2026-04-16.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - any score implementation
  - any capture script implementation
  - any runtime/shadow integration
  - any ML/model work
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_packet_2026-04-16.md`
  - `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_packet_2026-04-16.md docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`

### Stop Conditions

- any wording that opens direct implementation despite family-surface mismatch
- any wording that treats legacy current-ATR evidence as if it were already RI evidence
- any wording that turns the nearest RI bridge config into a promotion/readiness surface
- any wording that authorizes score implementation or capture execution from this packet alone

### Output required

- one docs-only blocker/admissibility packet
- one bounded memo explaining the blocker basis and exact next admissible step

## Purpose

This slice answers one narrow question only:

> may the roadmap open a direct RI deterministic advisory-baseline implementation slice now?

This packet does **not** decide:

- what the score formula should be
- which capture script should be written
- which years should be executed in a later capture slice

## Allowed evidence inputs

This slice may cite only already tracked surfaces needed for the admissibility decision:

- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase1_observability_inventory_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_selective_900_validation_2026-04-15/candidate_900_cfg.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `src/core/strategy/run_intent.py`
- existing trace/capture surfaces cited in chat during the current lane

## Required admissibility questions

The memo must answer at minimum:

1. is the current best supportive/hostile evidence chain already on an `ri` family surface?
2. does the nearest fixed RI candidate surface already materialize the observability fields needed for a direct baseline?
3. if not, what is the exact next admissible step?

## Exact next admissible step

If direct Phase 3 is blocked, the next admissible move is limited to:

- one separate bounded RI evidence-capture slice on a fixed RI research surface

That later slice may decide a capture surface and materialize row-level observability, but it is not opened by this packet itself.

## Bottom line

This packet authorizes one docs-only admissibility/blocker decision and nothing more.
Its job is to keep the lane honest if the current evidence surface is not yet suitable for a direct RI deterministic baseline.
