# Feature Attribution v1 — implementation slice 5 packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / behavior-touching / explicit-opt-in only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice touches `src/core/strategy/decision.py` in the high-sensitivity strategy path and extends the explicit internal attribution request handling with one additional admitted row, while default behavior must remain unchanged when no request is present. The target seam sits in the fib-gating route and must remain separate from the admitted `LTF override cluster`.
- **Required Path:** `Full`
- **Objective:** Implement the next smallest executable Feature Attribution v1 slice by supporting default-off, explicit opt-in neutralization of the admitted Phase 1 row `HTF block seam` only.
- **Candidate:** `HTF block seam`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** `src/core/strategy/decision.py`; `tests/utils/test_decision_edge.py`; exact extension of the internal explicit request handling to the admitted row `HTF block seam` only; slice-local fib-gating override that forces `use_htf_block = False` for the explicit opt-in path only; fail-closed invalid-request behavior preserved; targeted tests for default-off HTF blocking, valid request neutralization of the HTF block, preserved non-target LTF blockers, top-level input immutability, and nested `cfg.multi_timeframe` immutability.
- **Scope OUT:** no changes to `config/strategy/champions/**`; no runner/CLI/env wiring; no artifact generation; no schema/report logic; no changes under `results/**`; no changes to `src/core/strategy/decision_fib_gating.py` or `src/core/strategy/decision_fib_gating_helpers.py` default semantics; no changes to `allow_ltf_override`, `ltf_override_threshold`, or `ltf_override_adaptive`; no changes to cooldown, hysteresis, min-edge, or threshold semantics; no other Phase 1 rows; no cluster support; no fib reopening; no default behavior change.
- **Expected changed files:** `docs/governance/feature_attribution_v1_impl_slice5_htf_block_neutralization_packet_2026-03-31.md`, `src/core/strategy/decision.py`, `tests/utils/test_decision_edge.py`
- **Max files touched:** `3`

### Gates required

- explicit lint / pre-commit gate on touched files
- file diagnostics / lint sanity on touched files
- targeted pytest for `tests/utils/test_decision_edge.py`
- targeted pytest selector `tests/utils/test_decision_edge.py::test_feature_attribution_default_off_preserves_htf_block`
- targeted pytest selector `tests/utils/test_decision_edge.py::test_feature_attribution_valid_request_neutralizes_htf_block_without_mutation`
- targeted pytest selector `tests/utils/test_decision_edge.py::test_feature_attribution_htf_block_neutralization_preserves_ltf_blocker`
- targeted pytest for `tests/utils/test_decision_fib_gating_contract.py`
- targeted pytest for `tests/utils/test_decision.py`
- focused smoke test for the explicit opt-in HTF seam path: `tests/utils/test_decision_edge.py::test_feature_attribution_valid_request_neutralizes_htf_block_without_mutation`
- determinism replay: `tests/backtest/test_backtest_determinism_smoke.py`
- feature cache invariance: `tests/utils/test_features_asof_cache_key_deterministic.py`
- pipeline invariant: `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- manual review that HTF block neutralization remains slice-local in `decision.py` and does not edit default fib-gating helper semantics
- targeted pytest evidence that default-off behavior remains unchanged when no explicit opt-in request is present
- targeted pytest evidence that valid-request execution does not mutate the original nested `cfg.multi_timeframe` mapping

### Skill Usage

- Repo-local SPEC invocation for governance evidence:
  - **Pre-code review:** invoke `.github/skills/feature_parity_check.json` as the explicit no-default-drift/parity anchor for this slice before implementation approval.
  - **Post-diff audit:** invoke `.github/skills/feature_parity_check.json` again when reviewing the landed diff to confirm that explicit opt-in handling did not broaden default behavior.
- Supporting SPEC anchors only:
  - `.github/skills/backtest_run.json` — execution-discipline reference only; not adopted by reference for this implementation slice
  - `.github/skills/ri_off_parity_artifact_check.json` — artifact-integrity anchor only; not in scope for this implementation slice because no artifact surface is introduced
- The parity SPEC anchor does **not** replace the required determinism replay, feature-cache invariance, pipeline-invariant, or targeted fib-gating verification for this slice.

### Stop Conditions

- scope drift to any row other than `HTF block seam`
- any change that alters default behavior without explicit request
- any need to edit `src/core/strategy/decision_fib_gating.py` or `src/core/strategy/decision_fib_gating_helpers.py` default semantics instead of using a slice-local override in `decision.py`
- any need to alter `allow_ltf_override`, `ltf_override_threshold`, or `ltf_override_adaptive`
- any move toward runner/CLI/env/config-surface authority
- any change that reopens fib or citation-only / excluded rows
- any need to touch champion/config authority paths
- any need to broaden beyond the HTF block seam itself

### Output required

- minimal executable opt-in slice for one admitted row only
- targeted tests proving default-off and explicit-opt-in behavior
- concise implementation report with residual risks

## Intent of this slice

This slice is the fifth executable Feature Attribution v1 implementation step.

It is intentionally narrower than:

- a generic attribution framework
- multi-row selection
- cluster support
- runner wiring
- artifact/report generation
- governance review automation

The only newly admitted row in scope for this slice is:

- `HTF block seam`

The only allowed executable behavior in scope is:

- explicit opt-in neutralization of the HTF fib block by forcing `use_htf_block = False` in a slice-local fib-gating call only

## Default behavior lock

If no explicit Feature Attribution request is present, behavior must remain identical to current behavior.

If a valid explicit request is present, the only allowed behavior change in this slice is slice-local neutralization of the HTF block seam for `HTF block seam`.

If an explicit request is present but invalid or unsupported for this slice, the slice must fail closed on the explicit request path.
Invalid explicit request includes any wrong row label, wrong mode, missing required key, or unsupported request shape.

## Neutralization semantics lock for this slice

The implementation must neutralize the HTF block seam only for the explicit opt-in path by keeping the default fib-gating helpers untouched and applying a slice-local override in `decision.py` only:

- force the `use_htf_block` argument passed into `apply_fib_gating(...)` to `False` for the explicit opt-in path only

Rationale:

- the admitted Phase 1 seam is anchored at `cfg.multi_timeframe.use_htf_block`
- current `decision.py` already materializes that exact boolean before calling `apply_fib_gating(...)`
- `Phase 1` and `Phase 2` governance explicitly separate `HTF block seam` from the admitted `LTF override cluster`
- therefore editing the boolean at the call boundary is the smallest exact neutralization that preserves helper semantics and avoids cluster drift

No other multi-timeframe keys may be changed as part of this slice.

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
- LTF override neutralization
- generic fib-gate-neutralization helpers
