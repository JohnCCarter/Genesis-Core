# SCPE RI V1 runtime-observability slice1 implementation report

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
Status: `implemented / gated / post-diff-audit-approved`

## Scope summary

### Scope IN

- `src/core/strategy/evaluate.py`
- `tests/backtest/test_evaluate_pipeline.py`
- `tests/integration/test_ui_endpoints.py`
- this report: `docs/governance/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md`

### Scope OUT

- runtime-config authority
- champion merge semantics
- result/action/regime/confidence outputs
- `meta["observability"]["shadow_regime"]` contract shape
- paper-shadow / readiness / promotion surfaces
- backtest execution surfaces

## File-level change summary

- `src/core/strategy/evaluate.py`
  - added a bounded opt-in check for `state["observability"]["scpe_ri_v1"]`
  - added a tiny local payload builder that derives the RI runtime-observability payload only from the existing `shadow_regime` observability data
  - preserved default response shape by emitting `meta["observability"]["scpe_ri_v1"]` only when opt-in is true
- `tests/backtest/test_evaluate_pipeline.py`
  - added default-off parity coverage proving no new RI payload appears without opt-in
  - added exact allowlisted payload-shape coverage for opt-in=true
- `tests/integration/test_ui_endpoints.py`
  - tightened default endpoint assertion to prove `scpe_ri_v1` is absent by default
  - added opt-in route coverage proving the additive payload appears only when requested

## Default-parity evidence

Default-off proof for the bounded slice is established by:

- no `meta["observability"]["scpe_ri_v1"]` key without opt-in
- identical `result` payload with opt-in absent vs explicit false
- identical bounded decision/observability projection (excluding internal `state_out` echo) with opt-in absent vs explicit false
- unchanged route contract on `/strategy/evaluate` when `state` does not request the RI payload

## Gates executed and outcomes

### Test selectors

1. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_evaluate_pipeline.py`
   - PASS — `16 passed in 0.56s`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/integration/test_ui_endpoints.py::test_ui_get_and_evaluate_post tests/integration/test_ui_endpoints.py::test_ui_strategy_evaluate_emits_ri_runtime_observability_only_with_opt_in tests/integration/test_ui_endpoints.py::test_strategy_evaluate_delegates_with_current_defaults`
   - PASS — `3 passed in 0.94s`
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
   - PASS — `1 passed in 0.61s`
4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - PASS — `1 passed in 1.20s`
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
   - PASS — `1 passed in 0.68s`

### File-scoped validation

- `pre-commit run --files docs/governance/scpe_ri_v1_runtime_observability_slice1_precode_packet_2026-04-21.md docs/governance/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md src/core/strategy/evaluate.py tests/backtest/test_evaluate_pipeline.py tests/integration/test_ui_endpoints.py`
  - PASS — `black`, `ruff`, secret scan, large-file check, merge-conflict check, EOF fixer, and trailing-whitespace check all green on the final rerun

### Post-diff audit

- `Opus 4.6 Governance Reviewer`
  - APPROVED — bounded opt-in/additive implementation accepted as no-behavior-change for the reviewed slice; no code remediation requested

## Residual risks

- The new RI payload is intentionally derived from the existing `shadow_regime` observability structure; future changes to that upstream structure would need explicit review before widening or mutating the RI payload.
- The default-off contract remains the critical boundary: any future widening beyond the current allowlist or any default-on behavior would require a new packet.

## Evidence completeness for review

- mode/risk/path: `RESEARCH` / `MED` / `Full`
- scope IN/OUT: bounded to `evaluate.py`, the two test files, and this report
- gates: targeted slice tests + determinism + feature-cache invariance + pipeline invariant passed; file-level `pre-commit --files` passed
- selectors/artifacts: this report plus the governing precode packet and the updated test selectors above

No readiness, cutover, paper-shadow, or promotion claim is made here.
