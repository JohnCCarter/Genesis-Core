# GENESIS_WORKING_CONTRACT.md

> Working anchor for day-start and resumed sessions.
> This file is **not SSOT** and must not override repo governance documents.

## Purpose

This file exists to prevent session drift.
Before starting new work, the agent should re-anchor against the latest validated lane, known blockers, and next admissible step.

## Non-purpose

This file does **not**:

- authorize new implementation work by itself
- grant execution authority by itself
- override `.github/copilot-instructions.md`, `docs/governance_mode.md`, `AGENTS.md`, or explicit user instructions
- replace packets, reports, or verified evidence artifacts

## Authority order

1. Explicit user request for the current task
2. `.github/copilot-instructions.md`
3. `docs/governance_mode.md`
4. `docs/OPUS_46_GOVERNANCE.md`
5. `AGENTS.md`
6. This file (`GENESIS_WORKING_CONTRACT.md`)

## Current branch and mode anchor

- Branch: `feature/ri-role-map-implementation-2026-03-24`
- Expected mode on this branch: `RESEARCH`
- RESEARCH allows the smallest reproducible, traceable step
- RESEARCH does **not** authorize drift into strict-only surfaces, runtime-default authority, promotion, or champion claims without the required lane/packet

## Core conceptual lock

Genesis must be treated as a **deterministic policy-selection system**.
It is **not** an adaptive system.
It selects among predefined policies based on observable state, and any switching must remain exact, traceable, and reproducible.

## Current validated lane

Active focus right now:

- the bounded default-off RI-local runtime policy-router lane is now implemented and validated; the authoritative runtime packet for that slice remains `docs/governance/ri_policy_router_runtime_integration_packet_2026-04-23.md`
- the current active lane has moved forward from candidate preservation into one bounded `RESEARCH` runtime tuning slice for the enabled-only router path, and the active implementation packet for that work is now `docs/governance/ri_policy_router_aged_weak_continuation_guard_implementation_packet_2026-04-24.md`
- the current tuning focus is late-December continuation-entry substitution / timing drift on the same `3h` runtime bridge subject, not broader global router retuning
- the first preserved tuning candidate is intentionally narrow: an `aged weak continuation guard` hypothesis aimed only at the continuation-admission seam below default/champion/family authority
- the active implementation hypothesis is now explicit: when the router is enabled, the existing strong continuation predicate has already failed, and the weak continuation branch would otherwise be selected, block that weak continuation by returning router-local no-trade only when `bars_since_regime_change >= 16.0`
- the first bounded fail-set evidence pass for that guard is now complete and recorded in `docs/governance/ri_policy_router_aged_weak_continuation_guard_failset_evidence_2026-04-24.md`
- the fail-set result is negative: the guard worsened both the local December window and the micro-window anchor, and it did not remove the intended late continuation entries on `2023-12-22 15:00` and `2023-12-24 21:00`
- the observed guard-only delta vs the prior router-enabled December artifact was confined to later bars on `2023-12-28 06:00` and `2023-12-30 18:00` plus their cooldown propagation, which means the current guard misses the intended seam
- the bounded read-only seam replay now explains why: `2023-12-22 15:00` is weak continuation but only `7` bars into regime age, while `2023-12-24 21:00` is already strong continuation (`mandate_level 3`, `stable_continuation_state`) at `13` bars, so the current `aged weak continuation` predicate cannot remove both rows
- the split-seam direction freeze is now recorded in `docs/governance/ri_policy_router_continuation_split_seam_direction_packet_2026-04-24.md`, which locks the next candidate to explicitly choose either the `weak-pre-aged continuation` seam or the `already-strong continuation` seam before any new runtime authoring begins
- the cheapest next seam-A candidate is now preserved in `docs/governance/ri_policy_router_weak_pre_aged_release_candidate_packet_2026-04-24.md`, which frames the next continuation-local question as a `weak pre-aged continuation release` problem around `2023-12-22 15:00` rather than as another generic aged-threshold tweak
- the seam-A implementation slice is now complete under `docs/governance/ri_policy_router_weak_pre_aged_release_implementation_packet_2026-04-24.md`; the bounded runtime change in `ri_policy_router.py` passed its focused tests, required gate bundle, and post-diff audit
- the first seam-A fail-set evidence pass is now recorded in `docs/governance/ri_policy_router_weak_pre_aged_release_failset_evidence_2026-04-24.md`
- that fail-set result is negative: the candidate does hit the intended `2023-12-22 15:00` weak pre-aged release seam, but both December fail windows still worsen and `2023-12-24 21:00` remains a later continuation entry on the enabled path
- the observed row-level delta is materially broader than the intended one-row seam correction: `34` action diffs on the full December fail window and `10` on the micro-window, including blocked earlier baseline longs and replacement continuation entries from `2023-12-23` onward
- the new analysis note `docs/governance/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md` now sharpens that fail-set result: the guard is state-carrying, so one seam-A veto can persist as a repeated `RI_no_trade_policy` pocket before later continuation release occurs
- the observed loss mechanism is now more precise than generic churn: there are `12` substitution episodes on the full fail window, all with replacement continuation entries exactly `2` bars after blocked baseline longs, which matches a cooldown-displacement loop rather than a one-row correction
- keep-set (`2024`, `2025`) and stress-set (`2018`, `2020 H1`) verification are therefore not admissible for this candidate in its current form
- the first repo-native strategy candidate lifecycle slice is now implemented and validated across `registry/schemas/strategy_candidate_manifest.schema.json`, `registry/manifests/strategy_candidates.dev.json`, `src/core/governance/registry.py`, `tests/governance/test_registry_validator.py`, and `config/strategy/candidates/README.md`
- this slice preserves candidate identity, lifecycle status, lineage, and governance/evidence refs as **archival metadata only** and does not create runtime-selection, promotion, champion, readiness, cutover, or live-near authority
- the first seeded lifecycle entries now preserve the fixed RI runtime bridge candidate as `candidate` and the defensive-transition bridge variant as `research`
- the earlier paired no-divergence diagnostic is no longer an open next-step blocker for today; the first relevant high-zone near-miss rows already appeared only at `bars_since_regime_change >= 5`, which explains why the `guard_bars: 3` defensive-transition override produced no row-level divergence on the frozen paired surface
- the widened candidate-gate carrier slice is now implemented and validated in `src/core/strategy/decision_gates.py` plus bounded support in `src/core/config/schema.py` and `src/core/config/authority.py`
- the current verified conclusion remains that defensive starvation is better localized to raw defensive candidate formation than to generic hysteresis, min-dwell, or downstream sizing semantics
- default-path protection is now proven for the new `research_defensive_transition_override` leaf: absent leaf and explicit disabled leaf are canonically identical, and untouched authority/default outputs do not materialize the leaf
- the separate candidate bridge artifact now exists at `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json` and differs from the fixed baseline bridge only by explicit materialization of `multi_timeframe.research_defensive_transition_override`
- the paired launch-boundary packet now fixes the exact baseline/candidate no-save command targets for the explicit suppressed-write surface that sets `GENESIS_PRECOMPUTE_CACHE_WRITE=0` while remaining non-authorizing
- the separate launch-authorization packet now records `AUTHORIZED NOW` for the exact paired pre-execution surface only when that explicit suppressed-write command shape is preserved
- the repo now contains one explicit bounded containment mechanism in `src/core/backtest/engine.py`: `GENESIS_PRECOMPUTE_CACHE_WRITE=0` suppresses `cache/precomputed/` directory creation and `.npz` writes on cache miss while preserving existing-cache reads and in-memory precompute for the current run
- default behavior remains unchanged when `GENESIS_PRECOMPUTE_CACHE_WRITE` is absent, so canonical behavior is not silently widened or altered on untouched paths
- the actual paired execution has now been completed on the exact authorized suppressed-write surface, and the emitted baseline/candidate decision-row artifacts were bit-for-bit identical on this frozen window
- the next admissible step is no longer launch preparation, lifecycle-seeding, or seam-A implementation; it is a separate bounded analysis/refinement slice that explains why the new seam-A guard now hits `2023-12-22 15:00` but still worsens December through broader action churn across the `2023-12-21 -> 2023-12-25` pocket
- that bounded analysis/refinement slice is now complete at the docs level and points specifically to a chained no-trade pocket plus a recurring two-bar cooldown displacement loop as the current loss mechanism
- the earlier explanatory split-seam slice remains complete at the docs level, and the next honest move is still not generic continuation tuning; it is one fresh bounded candidate/analysis step that stays explicit about whether it is solving seam-A trade-off drift or reopening seam-B / strong continuation semantics
- the weakest-cost follow-up now remains continuation-local candidate-framing first: any next seam-A packet must explain how it avoids repeated `previous_policy = RI_no_trade_policy` chaining and the observed two-bar displacement loop before any keep-set, stress-set, or broader runtime packet is attempted
- a minimal repo-native findings-bank seed now exists under `artifacts/bundles/findings/` and `artifacts/research_ledger/`; it is research support only: `ArtifactRecord` identity remains authoritative, finding bundles remain descriptive evidence payloads, and `artifacts/research_ledger/indexes/findings_index.json` is a derived, rebuildable projection rather than a policy, readiness, or promotion gate
- that seed preserves both positive and negative RI-router findings plus the split-seam direction lock so later candidate framing can reuse resolved conclusions instead of repeating already-falsified or already-confirmed work

## Explicitly not active by default

Unless the user reopens them explicitly with the needed authority, do **not** treat these as active:

- the earlier `3h` historical validation lane from the prior working anchor
- inherited runtime/integration authority from RI research docs
- runtime-default changes
- paper-shadow follow-up fixes
- promotion/champion claims from isolated research evidence

## Key anchors already verified

- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md` is the canonical practical definition of concept / research-evidence / runtime-integration lanes
- `.github/copilot-instructions.md` already says to prefer the cheapest admissible lane before proposing durable runtime structure
- `docs/OPUS_46_GOVERNANCE.md` treats lane classification as workflow framing, not new authority
- `docs/governance/ri_router_replay_evidence_slice_precode_packet_2026-04-23.md` freezes the first fresh RI router replay subject without granting execution authority
- `scripts/analyze/scpe_ri_v1_router_replay.py` and `results/research/scpe_v1_ri/` exist as tracked historical reference surfaces, not inherited authority for the fresh slice
- `docs/governance/ri_router_replay_counterfactual_closeout_report_2026-04-23.md` closes the bounded counterfactual lane and records the current blocker ordering without granting semantics or runtime approval
- `docs/governance/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md` opens the next bounded semantics question without authorizing execution or runtime follow-up by itself
- `docs/governance/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md` defines the first exact bounded backtest subject for the mandate-2 candidate without authorizing execution by itself
- `docs/governance/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md` defines the setup-only backtest surface and records that the candidate run still lacks a bounded repo-visible carrier
- `docs/governance/ri_router_replay_defensive_transition_candidate_carrier_precode_packet_2026-04-23.md` narrows the candidate-carrier hypothesis to the transition-state propagation seam and treats `risk_state.py` as downstream sizing evidence, not as the carrier itself
- `docs/governance/ri_router_replay_defensive_transition_candidate_carrier_implementation_packet_2026-04-23.md` defines the smallest high-sensitivity code-slice contract and its required Full-path gates before any code may begin
- `docs/governance/ri_router_replay_defensive_transition_candidate_gate_carrier_precode_packet_2026-04-23.md` re-packets the next honest widened carrier hypothesis around `decision_gates.py::select_candidate(...)` and explicit config-authority support if a new default-off research leaf is required
- `docs/governance/ri_router_replay_defensive_transition_candidate_gate_carrier_implementation_packet_2026-04-23.md` defines the implemented bounded carrier slice for `decision_gates.py` plus explicit config-authority support and default-off parity/backcompat proof
- `docs/governance/ri_router_replay_defensive_transition_bridge_activation_precode_packet_2026-04-23.md` defines the next docs-only future config slice that would make the new carrier expressible as a separate candidate bridge artifact without reopening launch authority
- `docs/governance/ri_router_replay_defensive_transition_bridge_activation_implementation_packet_2026-04-23.md` defines the completed config-only candidate-artifact creation slice for the defensive-transition bridge path while keeping baseline and launch surfaces separate
- `docs/governance/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md` now defines the exact paired baseline/candidate no-save command targets for the explicit suppressed-write surface that sets `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- `docs/governance/ri_router_replay_defensive_transition_backtest_launch_authorization_packet_2026-04-23.md` now records `AUTHORIZED NOW` for the exact paired pre-execution surface only when that explicit suppressed-write command shape is preserved
- `docs/governance/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md` now records the completed bounded paired execution and the observed no-divergence outcome on the exact authorized surface
- `docs/governance/ri_router_replay_defensive_transition_backtest_precompute_containment_implementation_packet_2026-04-23.md` defines the bounded high-sensitivity runtime slice that introduces an explicit opt-in suppression path for precompute disk writes without changing the default canonical path
- `docs/governance/ri_policy_router_runtime_integration_packet_2026-04-23.md` now defines the bounded default-off runtime slice for RI-local policy switching, dwell/hysteresis state carry, and explicit return-to-continuation semantics below family/champion authority
- `registry/schemas/strategy_candidate_manifest.schema.json` defines the closed archival schema for strategy-candidate lifecycle metadata only
- `registry/manifests/strategy_candidates.dev.json` seeds the first preserved RI candidate identities without creating promotion or runtime authority
- `config/strategy/candidates/README.md` now documents the candidate-bank lifecycle manifest and explicitly keeps `promotion_compare`, `champion_freeze`, `readiness`, `cutover`, and live-near authority out of ordinary runtime selection semantics

## Last verified facts relevant to today

- the fresh pre-code RI replay packet already freezes the allowed future input/output envelope and explicit non-inheritance rule
- the frozen Phase C evidence inputs exist locally under `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/`
- the historical SCPE replay script and approved eight-file replay root exist locally as comparison/reference context only
- the baseline fresh replay surface still shows raw defensive `30` versus selected defensive `3`
- `switch_threshold: 2 -> 1` and `defensive_transition_state mandate/confidence: 1 -> 2` are behavior-equivalent on the current frozen surface
- `min_dwell: 3 -> 1` increases continuation dominance rather than improving defensive separation
- `hysteresis: 1 -> 0` is a no-op on the baseline surface, and the apparent hysteresis blocker reduces to raw mandate `1` versus continuation mandate `2/3`
- the first bounded backtest subject is now fixed to `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json` on `tBTCUSD`, `3h`, `2024-01-02 -> 2024-12-31`, warmup `120`, canonical 1/1 mode, and seed `42`
- `scripts/run/run_backtest.py` plus the fixed bridge config can express the baseline run on current repo-visible surfaces, but do not expose a dedicated config/CLI carrier for `defensive_transition_state mandate/confidence 2`
- current backtest result saving remains timestamp-driven under `results/backtests/` and `results/trades/`, so exact materialized filenames remain a launch-time review item rather than a pre-fixed CLI surface
- `src/core/strategy/decision_sizing.py` is the currently visible seam that propagates `last_regime` / `bars_since_regime_change`
- `src/core/intelligence/regime/risk_state.py` consumes that state for `transition_mult` sizing only and does not, on current repo-visible evidence, provide the missing mandate carrier by itself
- the bounded candidate-gate carrier slice has now been implemented, passed its required gates, and cleared post-diff audit on the current branch
- `src/core/strategy/decision_gates.py::select_candidate(...)` now exposes one explicit default-off research path keyed by `multi_timeframe.research_defensive_transition_override`
- `src/core/config/schema.py` now canonicalizes the leaf away when absent or disabled, and `src/core/config/authority.py` explicitly whitelists only `enabled`, `guard_bars`, and `max_probability_gap`
- `tests/utils/test_decision_gates_contract.py`, `tests/utils/test_decision_scenario_behavior.py`, `tests/governance/test_config_schema_backcompat.py`, and `tests/integration/test_golden_trace_runtime_semantics.py` now prove enabled-path behavior plus default-off parity/backcompat for the leaf
- the fixed bridge config `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json` remains unchanged on the current branch
- the separate candidate bridge artifact `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json` now exists and validates through both `ConfigAuthority().validate(...)` and the current `run_backtest.py` config-file merge path
- the config-only bridge-artifact slice passed targeted pre-commit validation, explicit baseline immutability proof, `tests/governance/test_config_schema_backcompat.py`, config-authority lifecycle selectors, determinism replay, feature-cache invariance, and pipeline invariant selectors
- the `config_authority_lifecycle_check` skill is now evidenced for this slice by the green lifecycle selectors listed above
- `scripts/run/run_backtest.py` currently exposes the paired no-save boundary surfaces needed for the exact subject: `--config-file`, `--warmup`, `--data-source-policy`, `--fast-window`, `--precompute-features`, `--decision-rows-out`, `--decision-rows-format`, and `--no-save`
- the paired launch-boundary packet now fixes the exact explicit suppressed-write command surface by adding `GENESIS_PRECOMPUTE_CACHE_WRITE=0` to the paired target shape while keeping outputs bounded to `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`, `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`, and a later human-written execution summary
- `src/core/backtest/engine.py` now supports one explicit suppression path: when `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, canonical precompute may still read an existing cache entry and build in-memory precomputed features, but it does not create `cache/precomputed/` and does not attempt `_np.savez_compressed(...)` on cache miss
- the launch-authorization packet now records that the explicit suppressed-write surface is authorized for pre-execution, but that authorization does not imply execution already happened
- the bounded paired execution is now complete on `HEAD` `efdce46b`, and the emitted baseline/candidate decision-row files are bit-for-bit identical (`D75471906D9C82E981B51D7281F41A7F1CA71DC00779751C707872CEECF9D804`, `2793` lines each)
- top-line stdout metrics were also identical across the pair (`6.40%` return, `118` trades, `58.5%` win rate, `0.261` Sharpe, `1.43%` max drawdown, `2.27` profit factor, `0.3567` score)
- the first repo-native candidate lifecycle registry slice has now passed focused registry validation, import smoke, determinism smoke, feature-cache invariance selectors, and pipeline fast-hash guard selectors without widening runtime/default/champion authority
- `src/core/governance/registry.py` now validates optional `strategy_candidates*.json` manifests additively, including duplicate candidate-id checks, duplicate `config_path` checks, and existence checks for referenced candidate configs
- the current closed schema intentionally allows only `research`, `candidate`, `promotion_compare`, and `champion_freeze`, and fences `config_path` to `config/strategy/candidates/**/*.json`
- the bounded policy-router implementation lane remains RESEARCH-valid so long as it stays inside `ri_policy_router.py`, `decision.py`, `schema.py`, `authority.py`, and the exact test/doc surfaces named in the packet, with absent-vs-disabled parity proven and no drift into `family_registry.py`, `family_admission.py`, `decision_gates.py`, or `decision_sizing.py`

## Next admissible steps

Choose the smallest valid next step that matches the user request:

1. use `docs/governance/ri_policy_router_weak_pre_aged_release_failset_evidence_2026-04-24.md` as the current evidence anchor for why the seam-A candidate is fail-set-negative despite hitting the intended `2023-12-22 15:00` seam
2. use `docs/governance/ri_policy_router_continuation_split_seam_direction_packet_2026-04-24.md` as the direction lock that still forbids bundling `weak but not aged` and `already strong continuation` under the same next candidate without explicit justification
3. use `docs/governance/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md` as the current mechanism-level anchor for why the loss is a chained no-trade pocket plus a two-bar cooldown displacement loop rather than a simple missed target row
4. do not advance this candidate to keep-set or stress-set verification unless a new bounded slice first removes or honestly bounds that repeated release-veto chaining / displacement mechanism
5. if the next candidate remains on seam A, keep it continuation-local and explicit about how it differs from the now-vetoed weak-release guard
6. if the next candidate needs to affect the already-strong seam around `2023-12-24 21:00`, stop and reopen governance review before any runtime edit because that is no longer the old weak-continuation-only question

## Hard stops

Stop and re-anchor before proceeding if any of the following happens:

- the next step starts relying on memory instead of cited anchors
- concept or research language starts implying runtime/family/authority status
- runtime/paper work starts to creep in without explicit authority
- a task touches strict-only surfaces or champion/promotion semantics
- the lane is no longer obvious from the latest user request

## Required day-start / resume ritual

At the start of a new day or resumed session, do this before reasoning forward:

1. read this file
2. read persistent user memory relevant to workflow
3. read current repo memory items relevant to the active lane
4. identify the latest validated lane and the latest non-active lanes
5. state the next smallest admissible step before making claims

## Update rule

Update this file only when one of these changes:

- active lane
- blocked/not-active lane status
- known verified blocker
- next admissible action

Keep it short. If detail is needed, point to the authoritative doc instead of copying it here.
