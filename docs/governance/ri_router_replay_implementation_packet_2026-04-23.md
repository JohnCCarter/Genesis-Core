# RI router replay implementation packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded research-only implementation / results-only / default unchanged`

This packet opens the next smallest runnable step after:

- `docs/governance/ri_router_replay_evidence_slice_precode_packet_2026-04-23.md`

It authorizes one fresh RI-local replay slice on research surfaces only.
It does **not** authorize runtime integration, default changes, family authority, promotion claims, or inherited implementation authority from the older SCPE replay lineage.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only replay from frozen evidence inputs with a fresh output root; no runtime/config/default/authority mutation allowed.
- **Required Path:** `Full`
- **Lane:** `Research-evidence` — the concept is already chosen; the next admissible step is one reproducible runnable slice below runtime/family/default authority.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** materialize one deterministic RI-local router replay from already frozen Phase C evidence rows, writing only approved research artifacts under a fresh output root and proving deterministic rerun stability without inheriting authority from `scpe_v1_ri`.
- **Candidate:** `RI router replay implementation`
- **Base SHA:** `578112c1`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/analysis/ri_router_replay_concept_case_2026-04-23.md`
  - `docs/governance/ri_router_replay_evidence_slice_precode_packet_2026-04-23.md`
  - `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`
  - `docs/governance/scpe_ri_v1_research_closeout_report_2026-04-20.md` (boundary proof only)
  - frozen historical comparison surfaces under `results/research/scpe_v1_ri/`
- **Candidate / comparison surface:**
  - one fresh deterministic RI-local router replay reported separately for `2024` and `2025`, with explicit comparison against the frozen SCPE replay trace/metric contract rather than against runtime behavior.
- **Vad ska förbättras:**
  - fresh subject discipline, clear non-inheritance, deterministic trace output, and contradiction-year honesty on a new replay root.
- **Vad får inte brytas / drifta:**
  - runtime behavior
  - default path semantics
  - family/runtime authority boundaries
  - cross-family separation
  - leakage boundary between decision-time fields and realized outcomes
  - the frozen historical `results/research/scpe_v1_ri/` root
- **Reproducerbar evidens som måste finnas:**
  - fixed input manifest and hashes
  - deterministic approved output hashes across repeated reruns
  - explicit containment proof for the fresh output root
  - explicit `2024` / `2025` comparison
  - explicit PASS / FAIL / inconclusive framing

### Scope

- **Scope IN:**
  - `docs/governance/ri_router_replay_implementation_packet_2026-04-23.md`
  - one isolated replay script under `tmp/ri_router_replay_v1_20260423.py`
  - approved result artifacts only under `results/research/ri_router_replay_v1/`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - `scripts/**` (read-only historical reference only)
  - existing `results/**` outside `results/research/ri_router_replay_v1/`
  - any runtime integration
  - any backtest execution integration
  - any cross-family routing
  - any default-on or authority-surface change
  - any import from `src/core/**`
  - any use of realized outcome columns in router/state/policy/veto/hysteresis/dwell logic
  - any claim that the older SCPE replay implementation grants inherited approval
  - any promotion, readiness, or runtime-improvement claim
- **Expected changed files:**
  - `docs/governance/ri_router_replay_implementation_packet_2026-04-23.md`
  - `tmp/ri_router_replay_v1_20260423.py`
  - `results/research/ri_router_replay_v1/input_manifest.json`
  - `results/research/ri_router_replay_v1/routing_trace.ndjson`
  - `results/research/ri_router_replay_v1/state_trace.json`
  - `results/research/ri_router_replay_v1/policy_trace.json`
  - `results/research/ri_router_replay_v1/veto_trace.json`
  - `results/research/ri_router_replay_v1/replay_metrics.json`
  - `results/research/ri_router_replay_v1/summary.md`
  - `results/research/ri_router_replay_v1/manifest.json`
- **Max files touched:** `10`

### Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per `docs/governance_mode.md`.
- **What RESEARCH allows here:** one bounded, reproducible, research-only replay slice with explicit artifacts and deterministic verification, as long as it remains below runtime/default/authority surfaces.
- **What remains forbidden here:** runtime integration, family-rule surfaces, comparison/readiness/promotion surfaces, champion surfaces, and any default behavior change.
- **What would force STRICT escalation:** touching `config/strategy/champions/`, `.github/workflows/champion-freeze-guard.yml`, runtime-default authority surfaces, family-rule surfaces, comparison surfaces, or promotion/readiness surfaces.

## Fixed inputs and authority boundaries

### Contract / boundary inputs

- `docs/analysis/ri_router_replay_concept_case_2026-04-23.md`
- `docs/governance/ri_router_replay_evidence_slice_precode_packet_2026-04-23.md`
- `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`
- `docs/governance/ri_router_replay_implementation_packet_2026-04-23.md`

These define the governance and semantic contract only.
They do not authorize runtime integration or broaden the replay input surface.

### Data inputs the script may consume directly

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`

The implementation must consume those frozen research inputs only.
It must not discover new inputs implicitly through globbing, CWD-relative scanning, runtime imports, or fallback heuristics.

### Historical comparison surfaces

- `results/research/scpe_v1_ri/`
- `scripts/analyze/scpe_ri_v1_router_replay.py`

These may inform shape, schema, and comparison only.
They do **not** grant inherited authority, and the fresh slice must not import or execute the older replay script as a dependency.

## Determinism and isolation constraints

The new script must remain fully deterministic and isolated.

- no imports from `src/core/**`
- no imports from `scripts/analyze/scpe_ri_v1_router_replay.py`
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

### Observational-only fields

These may be read only after final routing is complete:

- `total_pnl`
- `total_commission`
- `entry_atr`
- `fwd_4_atr`
- `fwd_8_atr`
- `fwd_16_atr`
- `mfe_16_atr`
- `mae_16_atr`
- `continuation_score`

### Allowed derived fields

The script may derive only bounded deterministic helper fields from the allowlisted inputs above, for example:

- absolute edge magnitude
- clarity bucket
- confidence bucket
- transition-pressure bucket
- volatility bucket

Derived fields must be recomputable from allowlisted columns alone and must not consume any realized outcome column.

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

## Approved outputs

The slice may write only the following files under `results/research/ri_router_replay_v1/`:

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

## Gates required

1. `pre-commit run --files docs/governance/ri_router_replay_implementation_packet_2026-04-23.md tmp/ri_router_replay_v1_20260423.py`
2. `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
3. `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
4. first execution of `tmp/ri_router_replay_v1_20260423.py` treated as:
   - smoke test
   - input/schema/allowlist check
   - approved-output inventory check
5. second identical execution of `tmp/ri_router_replay_v1_20260423.py` treated as:
   - determinism replay
   - canonical hash equality proof for all approved output files
6. independent containment proof outside the script's self-reported manifest:
   - before/after inventory of the approved output root
   - explicit proof of zero write events outside approved files

## Stop Conditions

- any attempt to import `src/core/**`
- any attempt to import or execute the older SCPE replay script as a dependency
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
- one approved replay output root under `results/research/ri_router_replay_v1/`
- one implementation report suitable for post-diff governance audit

## Bottom line

This packet authorizes one narrow next step only:

- replay the already frozen RI evidence rows through a deterministic family-local RI router on research surfaces only, using a fresh output root and explicit non-inheritance boundaries

It does not authorize runtime integration, backtest execution integration, cross-family routing, or any readiness / promotion claim.
