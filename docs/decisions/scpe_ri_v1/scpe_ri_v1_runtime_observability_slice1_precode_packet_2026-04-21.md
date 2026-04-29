# SCPE RI V1 runtime-observability slice1 pre-code packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded runtime-adjacent observational implementation / request-scoped / default unchanged`

This document defines the exact first implementation-adjacent slice that may open after the completed phase-2 shadow-backtest bridge lane.
It remains in `RESEARCH`, must preserve `NO BEHAVIOR CHANGE`, and must stay explicitly below runtime authority, paper-shadow, behavior-change, readiness, cutover, and promotion semantics.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded runtime-adjacent observational slice touching request/response handling in the evaluation path, with the main risks being default response-shape drift, hidden authority creep, or unintended decision-path mutation.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** materialize one request-scoped, additive, RI-only runtime-observability payload under `meta["observability"]["scpe_ri_v1"]` for `/strategy/evaluate`, using only already-available decision-time observability and preserving identical default behavior when opt-in is absent.
- **Candidate:** `SCPE RI V1 runtime-observability slice1`
- **Base SHA:** `b475736d`
- **Skill Usage:** repo-local `python_engineering` applies to the future bounded Python implementation slice; repo-local `repo_clean_refactor` applies as scope/minimal-diff discipline only. No skill in this packet is treated as runtime/integration authorization by itself.

### Done criteria

- opt-in absent => default `/strategy/evaluate` response projection remains unchanged on reviewed selectors
- opt-in present => `meta["observability"]["scpe_ri_v1"]` is emitted with only the allowlisted fields in this packet
- existing `meta["observability"]["shadow_regime"]` payload remains unchanged
- no action/regime/confidence/decision drift is observed on reviewed selectors
- all listed gates pass, including explicit default-parity proof and the listed determinism/invariance guards
- implementation report records exact commands, outcomes, and residual risks without any runtime-readiness or promotion claim

### Scope

- **Scope IN:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_precode_packet_2026-04-21.md`
  - `src/core/strategy/evaluate.py`
  - `tests/backtest/test_evaluate_pipeline.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md`
- **Scope OUT:**
  - `src/core/api/config.py`
  - `src/core/server.py`
  - `src/core/backtest/**`
  - `scripts/paper_trading_runner.py`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - runtime-config authority
  - champion merge semantics
  - action/size/reasons/confidence/regime outputs
  - `meta["observability"]["shadow_regime"]` contract shape
  - paper-shadow or behavior-change work
- **Expected changed files:**
  - `docs/decisions/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_precode_packet_2026-04-21.md`
  - `src/core/strategy/evaluate.py`
  - `tests/backtest/test_evaluate_pipeline.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md`
- **Max files touched:** `5`

### Exact opt-in boundary

The future implementation may emit the new RI payload only when the incoming request state includes:

- `state["observability"]["scpe_ri_v1"] = true`

If that request-scoped opt-in is absent or false:

- `/strategy/evaluate` response shape must remain unchanged from current default behavior
- no `meta["observability"]["scpe_ri_v1"]` key may be added

This request-scoped flag is chosen because `state` is already part of the existing request flow and does not reopen runtime-config authority.

### Exact additive output boundary

When opt-in is present, the slice may add exactly one new payload only at:

- `meta["observability"]["scpe_ri_v1"]`

The new payload may contain only the following fields:

- `family_tag = "ri"`
- `lane = "runtime_observability"`
- `observational_only = true`
- `decision_input = false`
- `enabled_via = "state.observability.scpe_ri_v1"`
- `authority_mode`
- `authority_mode_source`
- `authoritative_regime`
- `shadow_regime`
- `regime_mismatch`

Field provenance constraints:

- `authority_mode` must be copied from the already-computed runtime observability context
- `authority_mode_source` must be copied from the already-computed runtime observability context
- `authoritative_regime` must reflect the already-computed authoritative regime for the current request
- `shadow_regime` must be copied from the already-computed `shadow_regime` payload
- `regime_mismatch` must be copied from the already-computed mismatch state

No new score, router, policy, veto, or trade-advice field may be added in this slice.

### Allowed implementation work

The future implementation may do only the following:

1. read the request-scoped opt-in from `state["observability"]["scpe_ri_v1"]`
2. preserve current evaluation behavior exactly when opt-in is absent
3. emit one additive RI-only observational payload at `meta["observability"]["scpe_ri_v1"]` when opt-in is present
4. derive that payload only from already-computed request-local observability and regime values already available inside `evaluate_pipeline`
5. add tests proving:
   - default parity when opt-in is absent
   - payload presence and stable shape when opt-in is present
   - unchanged `shadow_regime` contract
   - unchanged endpoint behavior aside from the opt-in additive payload

### Explicitly forbidden operations

- any change to `result`
- any change to action, size, reasons, confidence, regime, or HTF regime
- any mutation of the existing `shadow_regime` payload keys or semantics
- any introduction of router-selected policy, veto action, mandate level, or RI score outputs into the runtime response
- any use of runtime config, champion config writeback, or default-on env/config toggles as activation surface
- any change to endpoint path, status code, or default response shape
- any paper-runner, backtest-runner, or cross-family wiring
- any readiness, cutover, launch, deployment, or promotion claim

### Required gates

1. `pre-commit run --files docs/decisions/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_precode_packet_2026-04-21.md docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md src/core/strategy/evaluate.py tests/backtest/test_evaluate_pipeline.py tests/integration/test_ui_endpoints.py`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_evaluate_pipeline.py`
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/integration/test_ui_endpoints.py::test_ui_get_and_evaluate_post tests/integration/test_ui_endpoints.py::test_strategy_evaluate_delegates_with_current_defaults`
4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
6. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
7. targeted parity proof showing that with opt-in absent, the response projection remains identical to the pre-slice behavior on reviewed selectors

### Stop Conditions

- any default response-shape drift when opt-in is absent
- any action/regime/confidence/decision drift on reviewed selectors
- any need to widen the payload beyond the exact field allowlist above
- any need to touch runtime-config authority, champion merge semantics, paper-runner surfaces, or backtest execution surfaces
- any need to reinterpret the slice as advisory routing, policy recommendation, or readiness evidence
- any API-contract weakening hidden behind additive defaults

### Output required

- one reviewable pre-code packet
- one bounded implementation diff on the exact files above only
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md` with gate outcomes and default-parity evidence

## Why this is the smallest honest implementation slice

This slice is intentionally smaller than:

- a new runtime score or router payload
- any policy-selection projection
- any runtime-config integration
- any paper-shadow lane
- any behavior-changing lane

It only formalizes one request-scoped RI observational projection from already available, already non-authoritative runtime state.

## Bottom line

This packet opens one bounded next step only:

- a request-scoped, additive, RI-only runtime-observability slice on `/strategy/evaluate` that preserves default behavior when opt-in is absent and remains explicitly non-authoritative.

Nothing in this packet authorizes paper-shadow, behavior change, runtime default changes, readiness, cutover, or promotion.
