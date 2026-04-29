# SCPE RI V1 router replay implementation packet

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded research-only implementation / results-only / default unchanged`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only SCPE router replay over an already frozen RI evidence surface; no runtime/config/default/authority mutation.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** materialize a deterministic RI-only SCPE V1 router replay from the already frozen Phase C evidence table, producing only research artifacts under a dedicated output root and proving deterministic rerun stability.
- **Candidate:** `SCPE RI V1 router replay implementation`
- **Base SHA:** `ef16cf539b45`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`

### Scope

- **Scope IN:**
  - `docs/decisions/scpe_ri_v1_router_replay_implementation_packet_2026-04-20.md`
  - `tmp/scpe_ri_v1_router_replay_20260420.py`
  - approved result artifacts only under `results/research/scpe_v1_ri/`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - existing `results/**` outside `results/research/scpe_v1_ri/`
  - any runtime integration
  - any backtest execution integration
  - any cross-family routing
  - any default-on or authority-surface change
  - any import from `src/core/**`
  - any use of realized outcome columns in router/state/policy/veto/hysteresis/dwell logic
  - any promotion, readiness, or runtime-improvement claim
- **Expected changed files:**
  - `docs/decisions/scpe_ri_v1_router_replay_implementation_packet_2026-04-20.md`
  - `tmp/scpe_ri_v1_router_replay_20260420.py`
  - `results/research/scpe_v1_ri/input_manifest.json`
  - `results/research/scpe_v1_ri/routing_trace.ndjson`
  - `results/research/scpe_v1_ri/state_trace.json`
  - `results/research/scpe_v1_ri/policy_trace.json`
  - `results/research/scpe_v1_ri/veto_trace.json`
  - `results/research/scpe_v1_ri/replay_metrics.json`
  - `results/research/scpe_v1_ri/summary.md`
  - `results/research/scpe_v1_ri/manifest.json`
- **Max files touched:** `10`

### Skill coverage

- Repo-local skill loaded: `.github/skills/python_engineering.json`
- Repo-local skill loaded: `.github/skills/genesis_backtest_verify.json`
- `genesis_backtest_verify` is used only as deterministic verification discipline for this replay slice; it does not authorize any trading-artifact mutation outside the approved research output root.

### Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per `docs/governance_mode.md`.
- **What RESEARCH allows here:** a bounded, reproducible, research-only replay slice with explicit artifacts and deterministic verification, as long as it remains below runtime/default/authority surfaces.
- **What remains forbidden here:** runtime integration, family-rule surfaces, comparison/readiness/promotion surfaces, champion surfaces, and any default behavior change.
- **What would force STRICT escalation:** touching `config/strategy/champions/`, `.github/workflows/champion-freeze-guard.yml`, runtime-default authority surfaces, family-rule surfaces, comparison surfaces, or promotion/readiness surfaces.

## Fixed inputs and authority boundaries

### Contract / boundary inputs

- `docs/scpe_ri_v1_architecture.md`
- `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`
- `docs/decisions/scpe_ri_v1_router_replay_implementation_packet_2026-04-20.md`

These define the governance and semantic contract only.
They do not authorize runtime integration or broaden the replay input surface.

### Data inputs the script may consume directly

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`

The implementation must consume those frozen research inputs only.
It must not discover new inputs implicitly through globbing, CWD-relative scanning, runtime imports, or fallback heuristics.

### Determinism and isolation constraints

The script must remain fully deterministic and isolated.

- no imports from `src/core/**`
- no network access
- no environment-variable reads
- no randomness
- no wall-clock timestamps inside hashed payloads
- no globbing or current-working-directory discovery for source selection
- no mutation of upstream capture files in place

If an additional source is required, the slice must stop rather than silently expand scope.

## Allowed router/state surface

### CoreDecisionState allowlist

Only these row fields may enter `CoreDecisionState` directly:

- `timestamp`
- `year`
- `side`
- `zone`
- `htf_regime`
- `current_atr_used`
- `atr_period_used`

### RIDecisionState allowlist

Only these row fields may enter `RIDecisionState` directly:

- `ri_clarity_score`
- `ri_clarity_raw`
- `bars_since_regime_change`
- `proba_edge`
- `conf_overall`

### Allowed derived fields

The script may derive only bounded deterministic helper fields from the allowlisted inputs above, for example:

- absolute edge magnitude
- clarity bucket
- confidence bucket
- transition-pressure bucket
- volatility bucket

Derived fields must be recomputable from allowlisted columns alone and must not consume any realized outcome column.

## Realized outcome boundary

Realized outcome columns are observational only.
They may be read exclusively after final policy routing has been computed and may not influence state construction, policy selection, switching, veto, thresholds, hysteresis, dwell logic, or any other routing decision path.

Forbidden in routing/state/policy/veto logic:

- `total_pnl`
- `total_commission`
- `entry_atr`
- `fwd_*`
- `mfe_*`
- `mae_*`
- `continuation_score`
- any future cohort membership
- any other post-entry or outcome-linked field

## Allowed implementation work

The script may do only the following:

1. freeze input hashes and script hash into `input_manifest.json`
2. materialize `CoreDecisionState` from the allowlisted fields only
3. derive `RIDecisionState` from the allowlisted RI fields only
4. apply a deterministic RI-only router over exactly:
   - `RI_continuation_policy`
   - `RI_defensive_transition_policy`
   - `RI_no_trade_policy`
5. apply explicit stability controls:
   - switch threshold
   - hysteresis
   - minimum dwell
6. apply a downstream veto layer that may only:
   - pass
   - reduce
   - cap
   - veto
   - force no-trade
7. emit one canonical routing trace row per eligible input row
8. compute derived summaries and observational metrics only after final routing is complete
9. record containment snapshots and fail closed on unexpected writes

## Explicitly forbidden operations

- any write under `src/**`, `tests/**`, `config/**`, or `artifacts/**`
- any import from `src/core/**`
- any runtime code path, runtime API path, or runtime config authority mutation
- any backtest execution rerun or engine invocation
- any model fitting, optimization, or hidden score learning
- any use of realized outcome columns in router/state/policy/veto/stability logic
- any cross-family decision or `Legacy` reference inside routing logic
- any hidden weakening of no-behavior-change scope
- any claim of runtime readiness, integrated performance improvement, or promotion readiness

## Approved outputs

The slice may write only the following files under `results/research/scpe_v1_ri/`:

- `input_manifest.json`
- `routing_trace.ndjson`
- `state_trace.json`
- `policy_trace.json`
- `veto_trace.json`
- `replay_metrics.json`
- `summary.md`
- `manifest.json`

The output directory itself may be created if absent.
Once created, the allowlist is strict: no file other than those eight approved outputs may be created, modified, or deleted inside that folder or elsewhere in watched mutable surfaces.

## Required output semantics

### `input_manifest.json`

Must include at minimum:

- canonical source paths
- input hashes
- script hash
- field allowlist version
- router parameter version
- approved output file allowlist

### `routing_trace.ndjson`

Canonical replay trace SSOT. Every row must include at minimum:

- `timestamp`
- `year`
- `family_tag = "RI"`
- compact `core_state`
- compact `ri_state`
- `selected_policy`
- `previous_policy`
- `switch_reason`
- `switch_proposed`
- `switch_blocked`
- `mandate_level`
- `confidence`
- `no_trade_flag`
- `dwell_duration`
- `veto_action`
- `final_routed_action`

### Derived summaries

- `state_trace.json` must summarize state buckets and coverage
- `policy_trace.json` must summarize policy counts, switches, and dwell behavior
- `veto_trace.json` must summarize pass/reduce/cap/veto/no-trade actions
- `replay_metrics.json` must summarize routing metrics and observational per-policy / per-year outcomes
- `summary.md` must state exact scope, exclusions, stability findings, `2024` vs `2025`, key risks, and one recommendation among:
  - `APPROACH_PROMISING`
  - `NEEDS_REVISION`
  - `NOT_READY`

### `manifest.json`

Must include at minimum:

- approved output directory
- approved output file allowlist
- written files
- output hashes
- input hashes
- script hash
- containment verdict and diff events
- no external write verdict across watched mutable surfaces

## Gates required

1. `pre-commit run --files docs/decisions/scpe_ri_v1_router_replay_implementation_packet_2026-04-20.md tmp/scpe_ri_v1_router_replay_20260420.py`
2. `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
3. `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
4. first execution of `tmp/scpe_ri_v1_router_replay_20260420.py` treated as:
   - smoke test
   - input/schema/allowlist check
   - approved-output inventory check
5. second identical execution of `tmp/scpe_ri_v1_router_replay_20260420.py` treated as:
   - determinism replay
   - canonical hash equality proof for all approved output files
6. independent containment proof outside the script's self-reported manifest:
   - before/after inventory of the approved output root
   - explicit proof of zero write events outside approved files

## Stop Conditions

- any attempt to import `src/core/**`
- any missing required allowlisted field
- any need to consume realized outcome fields before final routing is complete
- any uncontrolled write outside the approved output root
- any nondeterministic output hash across identical reruns
- any need to widen scope into runtime/backtest/cross-family surfaces
- any policy overlap so strong that the three policy states are not materially distinguishable in routed posture
- any veto dominance so strong that router-selected policy is rarely decisive

## Output required

- one governance packet
- one bounded isolated `tmp/` implementation script
- one approved replay output root under `results/research/scpe_v1_ri/`
- one implementation report suitable for post-diff governance audit

## Bottom line

This packet authorizes one narrow next step only:

- replay the already frozen RI evidence rows through a deterministic family-local SCPE router on research surfaces only

It does not authorize runtime integration, backtest execution integration, cross-family routing, or any readiness / promotion claim.
