# Regime Intelligence challenger family — DECISION EV/edge slice1 launch authorization packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `launch-candidate / research-only / not promotion authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this packet authorizes exactly one research-only full run from a config-only Decision slice after validator, preflight, smoke, and invariant gates passed.
- **Required Path:** `Full`
- **Objective:** Decide whether the Decision EV/edge slice1 canonical YAML is authorized for one full research-only execution.
- **Candidate:** `tBTCUSD 3h RI Decision EV/edge slice1 canonical full run`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Skill Usage

- No repository skill is treated as sole launch authority in this packet.
- This authorization is based on the explicit validator, preflight, test, smoke, and docs/YAML hygiene evidence listed below.

### Scope

- **Scope IN:** one docs-only launch authorization decision for the already-defined canonical Decision EV/edge slice1 YAML, including smoke proof and exact run subject.
- **Scope OUT:** no source-code changes, no test changes, no config changes, no launch of any second config, no comparison/readiness/promotion/writeback, no runtime/default/champion change.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_decision_ev_edge_slice1_launch_authorization_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates reviewed before this packet

- canonical YAML validator: `PASS with warnings only`
- smoke YAML validator: `PASS with warnings only`
- canonical preflight: `PASS / overall [OK]`
- targeted decision + determinism + cache + pipeline tests: `PASS`
- bounded smoke execution: `PASS`

Reviewer boundary:

- this authorization is based on already collected evidence listed in this packet
- Opus review did not rerun those gates in-session
- if canonical YAML, run id, or search surface changes, validator, preflight, and smoke evidence must be rerun before launch

### Stop Conditions

- any missing smoke artifact
- any evidence that `thresholds.min_edge = 0.00` was normalized away or rejected
- any ambiguity about the exact canonical run subject
- any wording that upgrades this packet into comparison, readiness, promotion, or writeback authority

## Subject proposed for launch

### Canonical full-run subject

- config:
  `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_2024_v1.yaml`
- proposed run id:
  `ri_decision_ev_edge_slice1_launch_20260327`
- search surface:
  - `ev.R_default ∈ {1.6, 1.8, 2.0}`
  - `thresholds.min_edge ∈ {0.00, 0.01, 0.02}`
- exact grid cardinality:
  `3 × 3 = 9`

## Evidence reviewed

### 1. Packet and roadmap discipline

- `docs/governance/regime_intelligence_optuna_decision_roadmap_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_decision_ev_edge_slice1_precode_command_packet_2026-03-27.md`

### 2. Config validation discipline

- canonical validator returned warnings only and no hard failure
- smoke validator returned warnings only and no hard failure
- canonical preflight returned overall `[OK]`
- canonical preflight confirmed exactly `2` searchable parameters and family admission pass for `run_intent=research_slice`

### 3. Invariant gates

The following focused tests passed:

- `tests/utils/test_decision_edge.py`
- `tests/utils/test_decision_gates_contract.py`
- `tests/backtest/test_backtest_determinism_smoke.py`
- `tests/utils/test_features_asof_cache_key_deterministic.py`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### 4. Smoke proof

Smoke subject:

- config:
  `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_smoke_20260327.yaml`
- run id:
  `ri_decision_ev_edge_slice1_smoke_20260327`
- artifact root:
  `results/hparam_search/ri_decision_ev_edge_slice1_smoke_20260327/`

Verified smoke facts:

- `run_meta.json` exists
- exactly `9` `trial_00x.json` artifacts exist
- exactly `9` `trial_00x_config.json` artifacts exist
- exactly `9` `tBTCUSD_3h_trial_00x.json` result artifacts exist
- repository search found no `Traceback`, `ERROR`, `FAILED`, or `SKIPPED` markers in the smoke tree
- non-zero trades were observed across the smoke grid (`12`, `13`, and `14` trades depending on tuple)
- `thresholds.min_edge = 0.0` survived as an explicit serialized literal in emitted artifacts such as:
  - `trial_001.json`
  - `trial_004.json`
  - `trial_007.json`

Observed smoke geometry:

- smoke did **not** collapse into one single score tuple across all nine combinations
- three repeated score tiers were observed, keyed by the searched EV/edge combinations on the bounded smoke window
- this is treated as launch-supporting differentiation only, not as full-window improvement evidence

## Authorization decision

Decision: `AUTHORIZED NOW`

Reason:

1. the canonical config exists in the approved optimizer zone
2. validator and canonical preflight passed without hard failure
3. invariance gates passed
4. smoke produced a complete 9-trial artifact set with non-zero trades
5. the explicit `0.00` edge-literal survived into emitted artifacts
6. no evidence currently blocks one bounded full research-only run

Exact authorization lock:

- this packet authorizes exactly one research-only full run
- authorized run id: `ri_decision_ev_edge_slice1_launch_20260327`
- authorized config only:
  `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_2024_v1.yaml`
- authorized search surface only:
  - `ev.R_default ∈ {1.6, 1.8, 2.0}`
  - `thresholds.min_edge ∈ {0.00, 0.01, 0.02}`

## Interpretation boundary

This authorization means only:

- one canonical full Decision EV/edge slice1 run may now be executed under the approved research flags and exact config above

This authorization does **not** mean:

- improvement is already proven
- comparison is open
- readiness is open
- promotion is open
- writeback is allowed
- runtime/default/champion authority changed

## Bottom line

The Decision EV/edge slice1 lane has passed packet, validator, preflight, invariant, and smoke gates.

Therefore exactly one canonical research-only full run is now authorized for:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_ev_edge_slice1_2024_v1.yaml`
- `run_id = ri_decision_ev_edge_slice1_launch_20260327`

All downstream interpretation remains research-only until a later separate signoff says otherwise.
