# SCPE RI V1 paper-shadow slice1 implementation report

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
Status: `implemented / gates-green / post-diff-audited`

## Scope summary

### Scope IN

- `docs/governance/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md`
- `scripts/paper_trading_runner.py`
- `tests/integration/test_paper_trading_runner.py`
- this report: `docs/governance/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md`

### Scope OUT

- all edits under `src/**`, `config/**`, `results/**`, and `artifacts/**`
- `tests/backtest/**` edits
- `tests/integration/test_ui_endpoints.py` edits
- `docs/paper_trading/runner_deployment.md`
- `docs/paper_trading/phase3_runbook.md`
- `scripts/paper_trading_runner.py` live-paper order-submission logic
- runtime-config/default-authority surfaces
- paper approval, live-paper approval, readiness, cutover, launch, deployment, or promotion semantics

## File-level change summary

- `scripts/paper_trading_runner.py`
  - added one explicit default-OFF CLI flag: `--ri-paper-shadow`
  - added fail-fast guardrails so `--ri-paper-shadow` is rejected together with `--live-paper`
  - added one bounded outbound state helper that preserves default behavior when opt-in is absent, injects only `state["observability"]["scpe_ri_v1"] = true` when opt-in is present, and fail-fast stops if `state_in` already contains `observability`
  - added one bounded allowlist extractor so RI paper-shadow data remains local to runner-side dry-run observability only via `DECISION_CONTEXT`
- `tests/integration/test_paper_trading_runner.py`
  - added CLI parsing coverage for the new flag and the hard conflict with `--live-paper`
  - added evaluate payload coverage for default-OFF unchanged behavior and opt-in state injection
  - added fail-fast coverage for conflicting live-paper mode and pre-existing `state_in["observability"]`
  - added bounded runner decision-context coverage proving only allowlisted RI fields are surfaced and absent-path remains silent

## Default-off and dry-run-only evidence

The bounded slice preserves no drift on the default path while confining the new behavior to one limited additive opt-in CLI path:

- without `--ri-paper-shadow`, outbound `/strategy/evaluate` payload state remains unchanged
- `--ri-paper-shadow` may only inject `state["observability"]["scpe_ri_v1"] = true`
- `--ri-paper-shadow` hard-fails when combined with `--live-paper`
- if runner state already contains `observability`, the slice stops rather than merge ambiguous authority
- RI paper-shadow output remains local to runner-side `DECISION_CONTEXT` observability only and does not widen `/paper/submit`, persisted runner state, or any external surface

## Gates executed and outcomes

1. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/integration/test_paper_trading_runner.py tests/integration/test_paper_trading_runner_candles_window_ordering.py`
   - PASS — `37 passed in 0.39s`
2. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_runtime_observability_default_off_parity tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_runtime_observability_payload_opt_in_shape`
   - PASS — `2 passed in 0.50s`
3. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/backtest/test_backtest_determinism_smoke.py::test_backtest_engine_is_deterministic_across_two_runs`
   - PASS — `1 passed in 0.73s`
4. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
   - PASS — `1 passed in 1.27s`
5. `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
   - PASS — `1 passed in 0.58s`
6. `pre-commit run --files docs/governance/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md scripts/paper_trading_runner.py tests/integration/test_paper_trading_runner.py`
   - PASS — `black`, `ruff`, secret scan, large-file check, merge-conflict check, EOF fixer, and trailing-whitespace check all green on the final rerun

### Remaining packet validation after report creation

- `pre-commit run --files docs/governance/scpe_ri_v1_paper_shadow_slice1_precode_packet_2026-04-21.md docs/governance/scpe_ri_v1_paper_shadow_slice1_implementation_report_2026-04-21.md scripts/paper_trading_runner.py tests/integration/test_paper_trading_runner.py`
  - PASS — `black`, `ruff`, secret scan, large-file check, merge-conflict check, EOF fixer, and trailing-whitespace check all green

### Post-diff audit

- `Opus 4.6 Governance Reviewer`
  - APPROVED_WITH_NOTES — accepted as a dry-run-only, default-OFF, local-observability-only paper-shadow slice; report wording tightened to describe this as no default-path drift plus a limited additive opt-in CLI path

## Residual risks

- This slice remains intentionally below live-paper semantics; any future attempt to let the RI opt-in survive into live-paper mode would require a new packet.
- The hard fail on pre-existing `state_in["observability"]` is deliberate risk containment; if the runner later needs additional local observability composition, that composition must be separately reviewed.
- A separate out-of-scope whitespace diff may still exist in `docs/governance/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md`; it was not touched in this slice.

## Evidence completeness for review

- mode/risk/path: `RESEARCH` / `HIGH` / `Full`
- scope IN/OUT: bounded to the paper runner, one integration test file, the precode packet, and this report
- gates: exact gate stack above passed on the implementation diff; file-scoped validation including this report is pending
- selectors/artifacts: this report plus the governing precode packet and the updated runner integration tests

No paper approval, live-paper approval, readiness, cutover, launch, deployment, or promotion claim is made here.
