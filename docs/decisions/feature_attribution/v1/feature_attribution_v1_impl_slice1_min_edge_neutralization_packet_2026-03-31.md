# Feature Attribution v1 — implementation slice 1 packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / behavior-touching / explicit-opt-in only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice touches `src/core/strategy/decision.py` in the high-sensitivity strategy path and introduces a new explicit opt-in request path, while keeping default behavior unchanged when absent.
- **Required Path:** `Full`
- **Objective:** Implement the smallest executable Feature Attribution v1 slice by supporting default-off, explicit opt-in neutralization of the admitted Phase 1 row `Minimum-edge gate seam` only.
- **Candidate:** `Minimum-edge gate seam`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** `src/core/strategy/decision.py`; `tests/utils/test_decision_edge.py`; exact default-off policy-level opt-in request handling for `Minimum-edge gate seam` only; seam-local in-memory override for the post-fib min-edge gate only; fail-closed invalid-request behavior for this slice only; targeted tests for opt-in neutralization, invalid request handling, preserved non-target blockers, and input immutability.
- **Scope OUT:** no changes to `config/strategy/champions/**`; no runner/CLI/env wiring; no artifact generation; no schema/report logic; no other Phase 1 rows; no cluster support; no changes under `results/**`; no fib reopening; no default behavior change.
- **Expected changed files:** `docs/decisions/feature_attribution/v1/feature_attribution_v1_impl_slice1_min_edge_neutralization_packet_2026-03-31.md`, `src/core/strategy/decision.py`, `tests/utils/test_decision_edge.py`
- **Max files touched:** `3`

### Gates required

- file diagnostics / lint sanity on touched files
- targeted pytest for `tests/utils/test_decision_edge.py`
- targeted pytest for `tests/utils/test_decision.py`
- determinism replay: `tests/backtest/test_backtest_determinism_smoke.py`
- feature cache invariance: `tests/utils/test_features_asof_cache_key_deterministic.py`
- pipeline invariant: `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- smoke / import sanity for touched decision path
- manual review that default behavior remains unchanged when no explicit opt-in request is present

### Skill Usage

- Exact repo-local skill coverage for this internal decision-gate attribution seam is **not införd**.
- Supporting SPEC anchors only:
  - `.github/skills/backtest_run.json` — execution-discipline reference only; not adopted by reference for this slice
  - `.github/skills/feature_parity_check.json` — conditional parity anchor only; not expected to be required unless feature-computation surfaces drift into scope
  - `.github/skills/ri_off_parity_artifact_check.json` — artifact-integrity anchor only; not in scope for this slice because no artifact surface is introduced
- These SPEC anchors do **not** replace the required determinism replay, feature-cache invariance, pipeline-invariant, or targeted decision-gate verification for this slice.

### Stop Conditions

- scope drift to any row other than `Minimum-edge gate seam`
- any change that alters default behavior without explicit request
- any move toward runner/CLI/env/config-surface authority
- any change that reopens fib or citation-only / excluded rows
- any need to touch champion/config authority paths
- any need to broaden beyond the post-fib min-edge gate itself

### Output required

- minimal executable opt-in slice for one admitted row only
- targeted tests proving default-off and explicit-opt-in behavior
- concise implementation report with residual risks

## Intent of this slice

This slice is the first executable Feature Attribution v1 implementation step.

It is intentionally narrower than:

- a generic attribution framework
- multi-row selection
- cluster support
- runner wiring
- artifact/report generation
- governance review automation

The only row in scope is:

- `Minimum-edge gate seam`

The only allowed executable behavior in scope is:

- explicit opt-in neutralization of `cfg.thresholds.min_edge` for one request path only

## Default behavior lock

If no explicit Feature Attribution request is present, behavior must remain identical to current behavior.

If a valid explicit request is present, the only allowed behavior change is slice-local neutralization of the post-fib `min_edge` gate for `Minimum-edge gate seam`.

If an explicit request is present but invalid or unsupported for this slice, the slice must fail closed on the explicit request path.
Invalid explicit request includes any wrong row label, wrong mode, missing required key, or unsupported request shape.

## Explicit invocation boundary for this slice

This slice may use an internal request surface only.
It must not introduce runner, CLI, env-var, or champion/config-authority surfaces.

The temporary internal request surface must remain:

- policy-level only
- non-serializing for artifacts and reports
- non-authoritative for config/champion state
- exact-match only for the single row in scope
- exact-shape only: `selected_row_label` plus `mode` and no broader selector/request form

## Out of scope by design

This slice does not implement:

- generic unit-id registry
- cluster support
- report generation
- baseline artifact production
- review package generation
- comparison or promotion semantics
