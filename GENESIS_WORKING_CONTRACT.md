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

- Branch: `feature/next-slice-2026-04-29`
- Expected mode on this branch: `RESEARCH`
- RESEARCH allows the smallest reproducible, traceable step
- RESEARCH does **not** authorize drift into strict-only surfaces, runtime-default authority, promotion, or champion claims without the required lane/packet

## Core conceptual lock

Genesis must be treated as a **deterministic policy-selection system**.
It is **not** an adaptive system.
It selects among predefined policies based on observable state, and any switching must remain exact, traceable, and reproducible.

## Current validated lane

Active focus right now:

- the RI-router tuning chain remains parked after the positive bars-7 closeout, the negative aged-weak closeouts, and the fixed-window phase-ordering reread; there is currently no active admissible RI-router runtime packet on this chain
- the only retained positive runtime slice in the recent chain is `docs/governance/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md`
- the aged-weak second-hit and aged-weak plus stability families are both closed negative / reverted, and the active-carrier handoff is now recorded in `docs/governance/ri_policy_router_aged_weak_active_carrier_truth_parked_handoff_2026-04-27.md`
- the bounded default-off RI-local runtime policy-router lane remains historically implemented and validated under `docs/governance/ri_policy_router_runtime_integration_packet_2026-04-23.md`, but it is not the active tuning lane today
- the tiny findings-bank hardening slice is now re-verified green on `HEAD` `3d8bfcaf`: live-checkout validator pass, packet-starter smoke, focused tests, and detached-worktree clean-checkout-like proof all passed without widening CI or `artifacts/**`
- the next honest move is no longer another findings-bank proof or wider RI-router evidence pass; it is either a docs-only `defensive_probe` concept/precode slice or a pivot to another research lane
- any future reopen on the aged-weak surface must start with fresh docs-only evidence anchored to the active carrier truth rather than reuse of the falsified `2023-12-30 21:00` residual-row premise
- this file is only a drift anchor; detailed closeout logic belongs in the governance notes above rather than here

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
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_candidate_packet_2026-04-27.md` now preserves the next seam-A-only follow-up candidate after the cooldown-displacement diagnosis without granting runtime authority by itself
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_implementation_packet_2026-04-27.md` now records the approved-with-notes runtime contract for the single-veto seam-A follow-up inside the exact bounded seam-A scope
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md` now records the first paired December fail-set evidence pass for the single-veto seam-A candidate, including the now-removed two-bar displacement loop and the remaining residual blocked-long set
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md` now records that the remaining residual blocked-long set is split across raw `insufficient_evidence` / no-trade-floor behavior and the older `AGED_WEAK_CONTINUATION_GUARD` seam, rather than one remaining seam-A issue
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_low_zone_insufficient_evidence_diagnosis_2026-04-27.md` now records that the chosen low-zone residual rows fail `confidence_floor` and `edge_floor` while clarity remains healthy, making them an evidence-floor surface rather than a seam-A latch surface
- `docs/governance/ri_policy_router_low_zone_near_floor_insufficient_evidence_residual_hypothesis_packet_2026-04-27.md` now preserves the next docs-only low-zone follow-up candidate as one bounded near-floor insufficient-evidence residual hypothesis, not as a runtime-authoritative threshold carve-out
- `docs/governance/ri_policy_router_low_zone_near_floor_insufficient_evidence_downstream_handoff_implementation_packet_2026-04-27.md` now records the attempted enabled-only runtime handoff packet, but its first implementation attempt was reverted after focused fail-B verification invalidated the packet's locked residual-envelope assumptions
- `docs/governance/ri_policy_router_low_zone_bars8_evidence_floor_candidate_packet_2026-04-27.md` now preserves the next docs-only low-zone candidate on the exact two-row post-filter bars-8 evidence-floor surface while explicitly keeping the blocked three-row packet non-authoritative
- `docs/governance/ri_policy_router_bars7_continuation_persistence_candidate_packet_2026-04-27.md` now preserves the separate bars-7 continuation-persistence seam that was previously bundled inside the low-zone family
- `docs/governance/ri_policy_router_bars7_continuation_persistence_runtime_packet_2026-04-27.md` now records the implemented bounded bars-7 runtime slice, its exact helper-hit proof, and its green gate bundle
- `docs/governance/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md` now closes that bars-7 slice positive and hands the remaining work to the aged-weak residual seam only
- `docs/governance/ri_policy_router_aged_weak_second_hit_release_candidate_packet_2026-04-27.md` now preserves the next docs-only aged-weak residual candidate on the exact `2023-12-28 09:00` / `2023-12-30 21:00` row-set
- `docs/governance/ri_policy_router_aged_weak_second_hit_release_runtime_packet_2026-04-27.md` now serves as the historical bounded runtime packet for that aged-weak residual seam, and `docs/governance/ri_policy_router_aged_weak_second_hit_release_runtime_closeout_2026-04-27.md` records its negative feasibility verdict and revert
- `docs/governance/ri_policy_router_enabled_vs_absent_annual_evidence_2026-04-28.md` records the frozen annual verdict as mixed and already frames `2024` regression-pocket isolation as the next honest read-only follow-up if the line is reopened
- `docs/governance/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md` now extends that annual picture onto the broader curated `2016-06-07 .. 2026-04-15` surface and records the full-year split: positive `2018/2020/2022/2025`, negative `2019/2021/2024`, mixed `2017/2023`
- `docs/governance/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md` now records the first read-only negative-pocket summary and shows that the clearly negative curated years are dominated by late low-zone `LONG -> NONE` suppression plus later `NONE -> LONG` continuation displacement rather than by a dominant early defensive pocket
- `docs/governance/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md` now compares that pocket shape against clearly positive curated years and records that the broad suppression+continuation pattern is shared rather than unique to negative years
- `docs/governance/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md` now adds the first timestamp-close observational outcome proxy pass and says the clearest year-group split appears on the blocked baseline-long cohort rather than on a clean continuation-substitution superiority story
- `docs/governance/ri_policy_router_substituted_continuation_tail_dispersion_2026-04-28.md` now localizes the continuation cohort by year and shows that continuation quality is itself year-heterogeneous: `2020` is clearly continuation-friendly, while `2018`, `2022`, and `2025` are materially weaker on the same descriptive proxy surface
- `docs/governance/ri_policy_router_substituted_continuation_local_tail_windows_2026-04-28.md` now adds a fixed `<=24h` descriptive window view and shows that `2020` concentrates its bad continuation rows into a few acute windows, while `2018` and `2022` revisit continuation-hostile multi-row windows repeatedly across the year and `2025` is weaker in a more fragmented way
- `docs/governance/ri_policy_router_blocked_vs_substituted_same_windows_2026-04-28.md` now compares the two cohorts inside two pre-fixed mixed local windows and shows that the local blocked-vs-substituted balance flips across the windows: blocked rows look locally stronger in the mixed March 2020 union window but locally weaker in the recurrent hostile March 2018 window, which means the same-window surface is phase-sensitive rather than a universal cohort-ranking rule
- `docs/governance/ri_policy_router_blocked_vs_substituted_same_window_phase_ordering_2026-04-29.md` now rereads those same two fixed windows as explicit chronology: `2020` is substituted-early / blocked-later with a mixed rebound and blocked terminal timestamp, while `2018` is blocked-early / substituted-middle / blocked-relapse / substituted-late, so the same-window sign flip is best read as segment occupancy and handoff timing rather than a universal cohort winner
- the latest RI local-window findings are now also registered in the repo-native findings bank as `FIND-2026-0006` (`substituted_continuation_local_window_shape`) and `FIND-2026-0007` (`blocked_vs_substituted_same_window_phase_ordering`), and the narrow findings-bank persistence surface is now git-trackable on this checkout through the findings bundles, their exact ArtifactRecords, the findings schema, and `artifacts/research_ledger/indexes/findings_index.json`; these remain research-only `direction_lock` findings rather than runtime or promotion authority
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
- the frozen annual enabled-vs-absent note is now explicit that `2024` is the negative annual year and that the next honest follow-up is a read-only `2024` regression-pocket isolation slice rather than fresh tuning
- the curated annual enabled-vs-absent note now broadens that picture: the router leaf is materially active across `2016-06-07 .. 2026-04-15`, but full-year benefit remains mixed with negative years `2019`, `2021`, and `2024`, so any reopen should isolate those negative pockets before proposing runtime work
- the first negative-pocket isolation note now says the negative full years are dominated by late low-zone suppression plus later continuation displacement, but it does not yet prove that this shape is unique to negative years without comparison against clearly positive years
- the new positive-vs-negative pocket comparison note now says that the broad suppression+continuation shape is shared across both clearly negative and clearly positive curated years, so the next honest read-only question is outcome quality inside the shared shape rather than pocket presence alone
- the new shared-pocket outcome-quality proxy note now says the first descriptive signal is stronger on the blocked baseline-long cohort: blocked longs look directionally weaker in the positive year group than in the negative year group, while the substituted continuation cohort does not yet separate cleanly on the same proxy surface
- the new substituted-continuation tail-dispersion note now says the continuation cohort does not align cleanly with the annual positive-vs-negative split either: `2020` is continuation-friendly, `2018` is heavy-left-tail skewed, and `2022/2025` are broadly weak on the current proxy surface, which further strengthens the blocked-baseline cohort as the clearer annual divider
- the new local-tail-window note now sharpens that story again: `2020` still has severe continuation-tail windows, but mostly as a few acute concentrations, whereas `2018` and `2022` show recurrent multi-row continuation-hostile windows across the year and `2025` looks weaker in a more fragmented form; annual group labels remain too coarse for continuation interpretation
- the new same-window note now shows that even inside fixed mixed local windows there is no single blocked-versus-substituted winner: the March 2020 mixed window is continuation-left-tail-loaded early and blocked-stronger later, while the March 2018 recurrent hostile window points the other way, so local comparison is best treated as phase-ordering evidence rather than universal cohort ranking
- the two newest RI findings now sit on the narrow tracked findings-bank persistence surface and remain discoverable by preflight lookup, while the rest of `artifacts/` stays ignored; this resolves the earlier `.gitignore` mismatch without widening runtime, promotion, or general generated-artifact semantics
- `scripts/preflight/findings_preflight_lookup.py` now also exposes an explicit `--validate-index-projection` mode that derives the expected `artifacts/research_ledger/indexes/findings_index.json` from the committed findings bundles plus their ArtifactRecords and fails loudly when the local materialized index is missing or diverges; default lookup behavior remains unchanged and packet-starter import/usage still passes on the current checkout
- on `feature/next-slice-2026-04-29` at `HEAD` `3d8bfcaf`, both the live checkout and a detached temporary worktree pass `scripts/preflight/findings_preflight_lookup.py --validate-index-projection`, packet-starter smoke, and the focused preflight test selectors, so the findings-bank validator is re-verified on a clean-checkout-like surface without relying on the earlier archived proof folder
- the first repo-native candidate lifecycle registry slice has now passed focused registry validation, import smoke, determinism smoke, feature-cache invariance selectors, and pipeline fast-hash guard selectors without widening runtime/default/champion authority
- `src/core/governance/registry.py` now validates optional `strategy_candidates*.json` manifests additively, including duplicate candidate-id checks, duplicate `config_path` checks, and existence checks for referenced candidate configs
- the current closed schema intentionally allows only `research`, `candidate`, `promotion_compare`, and `champion_freeze`, and fences `config_path` to `config/strategy/candidates/**/*.json`
- the bounded policy-router implementation lane remains RESEARCH-valid so long as it stays inside `ri_policy_router.py`, `decision.py`, `schema.py`, `authority.py`, and the exact test/doc surfaces named in the packet, with absent-vs-disabled parity proven and no drift into `family_registry.py`, `family_admission.py`, `decision_gates.py`, or `decision_sizing.py`

## Next admissible steps

Choose the smallest valid next step that matches the user request:

1. use `docs/governance/ri_policy_router_reanchor_post_aged_weak_closeouts_2026-04-27.md` and `docs/governance/ri_policy_router_aged_weak_active_carrier_truth_parked_handoff_2026-04-27.md` as the current truthful state anchors for this chain
2. do **not** reopen the findings-bank hardening proof unless a concrete CI discrepancy appears; the live-checkout and detached-worktree proof bundle is already green on this branch
3. if the user wants another RI-router slice, keep it docs-only and re-anchor it to fresh active-carrier evidence plus the annual evidence notes before proposing any new candidate family or runtime packet; the cleanest next candidate is a conceptual `defensive_probe` precode slice, not more years/windows and not any new runtime tuning
4. otherwise leave the RI-router chain parked and move to another research lane; no Optuna or aged-weak runtime reopening is admissible from the current state alone

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
