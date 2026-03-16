## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/research-ledger-v1`)
- **Risk:** `MED` — why: multi-file additive ledger substrate plus one test-only stabilization and merge-readiness validation
- **Required Path:** `Full`
- **Objective:** Make `feature/research-ledger-v1` merge-assessable by committing the canonical local Research Ledger substrate, applying the already-validated flaky trial-key test stabilization, and rerunning full verification.
- **Candidate:** `feature/research-ledger-v1`
- **Base SHA:** `2a214b6e`

### Scope

- **Scope IN:**
  - `docs/audit/research_ledger/context_map_research_ledger_v1_merge_readiness_2026-03-16.md`
  - `docs/audit/research_ledger/command_packet_research_ledger_v1_merge_readiness_2026-03-16.md`
  - `src/core/research_ledger/**`
  - `tests/core/research_ledger/**`
  - `tests/utils/test_optimizer_performance.py`
  - `handoff.md` (readiness note only, if verification outcome changes)
- **Scope OUT:**
  - `src/core/optimizer/**` runtime code
  - strategy/backtest/optimizer behavior
  - config authority paths including `config/strategy/champions/**`
  - registry/CI/governance enforcement logic
  - `.worktrees/**`
- **Expected changed files:** 14 without `handoff.md`, 15 if readiness note is updated
- **Max files touched:** 15

### Gates required

- `pre-commit run --all-files`
- `python scripts/validate/validate_registry.py`
- `bandit -r src -c bandit.yaml -f txt -o bandit-report.txt`
- `pytest -q`
- Required focused evidence within/alongside pytest results:
  - `tests/core/research_ledger/test_storage.py`
  - `tests/core/research_ledger/test_validators.py`
  - `tests/core/research_ledger/test_service.py`
  - `tests/utils/test_optimizer_performance.py`
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift outside files listed above
- Cherry-pick or manual transfer of `d3b9a099` changes anything outside `tests/utils/test_optimizer_performance.py`
- Any generated/output files are pulled in, including `artifacts/research_ledger/**`, `results/**`, `logs/**`, or anything under `.worktrees/**`
- Any new runtime import/wiring to `core.research_ledger` appears outside scoped files
- Any optimizer/runtime behavior change outside test stabilization
- Full verification not green
- Forbidden paths touched

### Output required

- **Implementation Report**
- **PR evidence template**
- **Root evidence block:** show that `tests/utils/test_optimizer_performance.py::TestTrialKeyPerformance.test_trial_key_caching` in the root repo changed from the old single-sample timing assertion to the verified repeated-sample median comparison
