# Feature Attribution v1 — implementation slice 3 packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / behavior-touching / explicit-opt-in only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice touches `src/core/strategy/decision.py` in the high-sensitivity strategy path and extends the explicit internal attribution request handling with one additional admitted row, while default behavior must remain unchanged when no request is present. The target seam is stateful because active cooldown blocking is consumed from `state_in["cooldown_remaining"]`, even though the baseline config seam is anchored at `cfg.gates.cooldown_bars`.
- **Required Path:** `Full`
- **Objective:** Implement the next smallest executable Feature Attribution v1 slice by supporting default-off, explicit opt-in neutralization of the admitted Phase 1 row `Cooldown gate seam` only.
- **Candidate:** `Cooldown gate seam`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** `src/core/strategy/decision.py`; `tests/utils/test_decision_edge.py`; exact extension of the internal explicit request handling to the admitted row `Cooldown gate seam` only; slice-local override of `cfg.gates.cooldown_bars = 0` for the explicit opt-in path only; slice-local masked post-fib state view that neutralizes the derived active cooldown blocker by treating `cooldown_remaining` as `0` for the explicit opt-in path only; fail-closed invalid-request behavior preserved; targeted tests for default-off cooldown blocking, valid request neutralization of an active cooldown block, preserved non-target blockers, top-level input immutability, and nested `cfg.gates` immutability.
- **Scope OUT:** no changes to `config/strategy/champions/**`; no runner/CLI/env wiring; no artifact generation; no schema/report logic; no changes under `results/**`; no changes to `src/core/strategy/decision_gates.py` default cooldown semantics; no changes to `src/core/strategy/components/cooldown.py` or its tests because that is not the canonical route for this v1 attribution seam; no changes to paper-trading runner state persistence; no changes to min-edge or hysteresis semantics beyond preserving the already-existing slices; no other Phase 1 rows; no cluster support; no fib reopening; no default behavior change.
- **Expected changed files:** `docs/decisions/feature_attribution_v1_impl_slice3_cooldown_neutralization_packet_2026-03-31.md`, `src/core/strategy/decision.py`, `tests/utils/test_decision_edge.py`
- **Max files touched:** `3`

### Gates required

- file diagnostics / lint sanity on touched files
- targeted pytest for `tests/utils/test_decision_edge.py`
- targeted pytest for `tests/utils/test_decision_gates_contract.py`
- targeted pytest for `tests/utils/test_decision.py`
- determinism replay: `tests/backtest/test_backtest_determinism_smoke.py`
- feature cache invariance: `tests/utils/test_features_asof_cache_key_deterministic.py`
- pipeline invariant: `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- smoke / import sanity for touched decision path
- manual review that default behavior remains unchanged when no explicit opt-in request is present
- manual review that cooldown neutralization does not edit `src/core/strategy/decision_gates.py` default semantics and instead remains a slice-local explicit-request override in `src/core/strategy/decision.py`
- manual review that valid-request execution does not mutate the original nested `cfg.gates` mapping or the caller-provided `state`

### Skill Usage

- Exact repo-local skill coverage for this internal decision-gate attribution seam is **not införd**.
- Supporting SPEC anchors only:
  - `.github/skills/backtest_run.json` — execution-discipline reference only; not adopted by reference for this slice
  - `.github/skills/feature_parity_check.json` — parity/default-off anchor only; it informs verification discipline for unchanged default behavior but does not replace the required slice-local gates
  - `.github/skills/ri_off_parity_artifact_check.json` — artifact-integrity anchor only; not in scope for this implementation slice because no artifact surface is introduced
- These SPEC anchors do **not** replace the required determinism replay, feature-cache invariance, pipeline-invariant, or targeted decision-gate verification for this slice.

### Stop Conditions

- scope drift to any row other than `Cooldown gate seam`
- any change that alters default behavior without explicit request
- any need to edit `src/core/strategy/decision_gates.py` default cooldown semantics instead of using a slice-local override/masked-state view
- any need to touch persistent runner state wiring, paper/live state handoff, or component cooldown routing
- any move toward runner/CLI/env/config-surface authority
- any change that reopens fib or citation-only / excluded rows
- any need to touch champion/config authority paths
- any need to broaden beyond the cooldown seam itself

### Output required

- minimal executable opt-in slice for one admitted row only
- targeted tests proving default-off and explicit-opt-in behavior
- concise implementation report with residual risks

## Intent of this slice

This slice is the third executable Feature Attribution v1 implementation step.

It is intentionally narrower than:

- a generic attribution framework
- multi-row selection
- cluster support
- runner wiring
- artifact/report generation
- governance review automation

The only newly admitted row in scope for this slice is:

- `Cooldown gate seam`

The only allowed executable behavior in scope is:

- explicit opt-in neutralization of the cooldown seam by using a slice-local cooldown override in `decision.py` only

## Default behavior lock

If no explicit Feature Attribution request is present, behavior must remain identical to current behavior.

If a valid explicit request is present, the only allowed behavior change in this slice is slice-local neutralization of the cooldown seam for `Cooldown gate seam`.

If an explicit request is present but invalid or unsupported for this slice, the slice must fail closed on the explicit request path.
Invalid explicit request includes any wrong row label, wrong mode, missing required key, or unsupported request shape.

## Neutralization semantics lock for this slice

The implementation must neutralize the cooldown seam only for the explicit opt-in path by keeping the default gate code untouched and applying both of the following slice-local behaviors inside `decision.py`:

- force `cfg.gates.cooldown_bars = 0` in a slice-local overridden config used by the explicit opt-in path only, so a successful opt-in entry does not reseed future cooldown state from this seam
- treat the derived active cooldown blocker as neutralized for the explicit opt-in path only by presenting a slice-local masked gate-state view in which `cooldown_remaining` is evaluated as `0`

Rationale:

- the admitted Phase 1 seam is anchored at `cfg.gates.cooldown_bars`
- current active cooldown blocking is consumed in `src/core/strategy/decision_gates.py::apply_post_fib_gates` from `state_in["cooldown_remaining"]`
- current cooldown state is seeded in `src/core/strategy/decision.py::decide` from `cfg.gates.cooldown_bars` after a successful entry
- therefore a config-only override would be insufficient to neutralize an already-active cooldown block inherited from prior bars
- therefore a direct edit of default cooldown gate semantics in `decision_gates.py` would be broader than necessary for this slice

No other gate keys or state keys may be changed as part of this slice.

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
- base entry confidence neutralization
- generic gate-neutralization helpers
- adoption of `src/core/strategy/components/cooldown.py`
