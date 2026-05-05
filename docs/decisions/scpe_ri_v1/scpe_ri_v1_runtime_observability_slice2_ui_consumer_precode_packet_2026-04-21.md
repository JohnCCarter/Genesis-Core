# SCPE RI V1 runtime-observability slice2 UI consumer pre-code packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded UI consumer implementation / default-off / no server-authority change`

This document defines the next bounded implementation slice after runtime-observability slice1 and the follow-up smoke/evidence lane.
It remains in `RESEARCH`, preserves `NO BEHAVIOR CHANGE`, and stays strictly on the client-side consumer surface for the already implemented opt-in observability payload.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded embedded-UI consumer slice touching request composition and client-side display for an already existing observability payload, with the main risks being accidental default-on activation or widening into non-observational semantics.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** let the embedded `/ui` page explicitly request the existing `meta["observability"]["scpe_ri_v1"]` payload through a default-off control and display a bounded summary when present, without changing server authority or default evaluate behavior.
- **Candidate:** `SCPE RI V1 runtime-observability slice2 UI consumer lane`
- **Base SHA:** `48a939cd`
- **Skill Usage:** repo-local `python_engineering` applies to the bounded Python/embedded-UI implementation slice; repo-local `repo_clean_refactor` applies as scope/minimal-diff discipline only. No skill in this packet is treated as runtime/integration authorization by itself.

### Done criteria

- `/ui` renders one RI runtime-observability opt-in consumer control that is OFF by default
- the embedded UI script only sends `state["observability"]["scpe_ri_v1"] = true` when that control is enabled
- the default `/strategy/evaluate` route contract remains unchanged when the control is left OFF
- the UI consumes only the already allowlisted `meta["observability"]["scpe_ri_v1"]` fields and does not reinterpret them as decision, policy, readiness, or recommendation output
- all listed gates pass, including default-parity selectors, feature parity selectors, determinism/invariance guards, and file-scoped validation
- the implementation report records exact commands, outcomes, residual risks, and the explicit fact that the pre-existing dirty slice1 report file remained out of scope

### Scope

- **Scope IN:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice2_ui_consumer_precode_packet_2026-04-21.md`
  - `src/core/api/ui.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice2_ui_consumer_implementation_report_2026-04-21.md`
- **Scope OUT:**
  - all edits under `src/core/strategy/**`
  - `src/core/api/strategy.py`
  - `src/core/server.py`
  - `config/**`
  - `scripts/**`
  - `results/**`
  - `artifacts/**`
  - edits to `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md`
  - any widening of `meta["observability"]["scpe_ri_v1"]`
  - any runtime-config/default-on activation surface
  - any router/policy/paper-shadow/readiness/promotion semantics
- **Expected changed files:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice2_ui_consumer_precode_packet_2026-04-21.md`
  - `src/core/api/ui.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice2_ui_consumer_implementation_report_2026-04-21.md`
- **Max files touched:** `4`

### Exact UI opt-in boundary

The UI may request the RI runtime-observability payload only through one explicit default-OFF control on `/ui`.

If the control is OFF:

- the embedded UI must continue to send `state = {}` on its `/strategy/evaluate` requests
- no new UI summary line for RI runtime observability may be rendered

If the control is ON:

- the embedded UI may send only `state["observability"]["scpe_ri_v1"] = true`
- the UI may display a bounded summary using only the already emitted allowlisted payload fields

### Exact consumer boundary

The UI may consume only these existing fields from `meta["observability"]["scpe_ri_v1"]`:

- `family_tag`
- `lane`
- `observational_only`
- `decision_input`
- `enabled_via`
- `authority_mode`
- `authority_mode_source`
- `authoritative_regime`
- `shadow_regime`
- `regime_mismatch`

The UI must not derive or display any new score, policy recommendation, veto, readiness, or action semantics from those values.

### Allowed implementation work

The future implementation may do only the following:

1. add one default-OFF RI observability opt-in control in `src/core/api/ui.py`
2. add one small client-side helper that injects `state["observability"]["scpe_ri_v1"] = true` only when that control is enabled
3. add one bounded summary rendering path when the existing RI payload is present
4. add integration assertions proving the UI renders the control default-OFF and that the embedded script gates the opt-in request behind the control
5. write one bounded implementation report

### Explicitly forbidden operations

- any change to `/strategy/evaluate` server behavior or payload shape
- any change to `src/core/api/strategy.py`, `src/core/server.py`, or `src/core/strategy/**`
- any default-ON activation of RI runtime observability from the UI
- any reinterpretation of `scpe_ri_v1` values as decision input, recommendation, or readiness signal
- any widening of the RI payload field set
- any edits to the already dirty slice1 implementation report

### Required gates

1. `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice2_ui_consumer_precode_packet_2026-04-21.md docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice2_ui_consumer_implementation_report_2026-04-21.md src/core/api/ui.py tests/integration/test_ui_endpoints.py`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/integration/test_ui_endpoints.py`
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
6. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
7. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- any default-on request drift from the UI
- any need to touch server-side runtime authority or payload production code
- any UI rendering that implies recommendation, policy, readiness, or promotion semantics
- any widening beyond the existing RI payload allowlist
- any need to edit the already dirty slice1 implementation report

### Output required

- one reviewable pre-code packet
- one bounded embedded-UI implementation diff on the exact files above only
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice2_ui_consumer_implementation_report_2026-04-21.md` with gate outcomes and bounded consumer evidence

## Why this is the smallest honest next slice

This slice stays below any new server-side runtime authority work.
It consumes an already bounded, already smoke-checked observability payload and keeps activation explicit and default-OFF.
It is therefore narrower than any further payload widening, any server-side runtime instrumentation change, and any paper-shadow or behavior-changing lane.

## Bottom line

This packet opens one bounded next step only:

- a default-OFF UI consumer lane for the already existing RI runtime-observability payload.

Nothing in this packet authorizes server-side widening, runtime-default changes, paper-shadow, behavior change, readiness, cutover, or promotion.
