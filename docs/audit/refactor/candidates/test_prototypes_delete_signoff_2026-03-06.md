# Candidate 7 Signoff — Delete `scripts/archive/test_prototypes/**` (2026-03-06)

Mode: RESEARCH (source=branch mapping `feature/*`)
Candidate: `delete_archive_test_prototypes`

## Scope summary

- Deleted exactly 36 files under `scripts/archive/test_prototypes/**`.
- Added/updated candidate evidence/contract files:
-  - `docs/audit/refactor/candidates/command_packet_candidate7_delete_test_prototypes_2026-03-06.md`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_manifest_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_refcheck_2026-03-06.json`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_path_refcheck_2026-03-06.txt`
  - `docs/audit/refactor/evidence/candidate7_test_prototypes_exact_path_refcheck_2026-03-06.json`

## Reference safety evidence

- Manifest size: 36 targets (`candidate7_test_prototypes_manifest_2026-03-06.txt`).
- Exact per-file path refcheck (outside docs/archive):
  - `target_count = 36`
  - `paths_with_hits = 0`
  - Source: `candidate7_test_prototypes_exact_path_refcheck_2026-03-06.json`
- Strict folder path refcheck file remained empty:
  - `candidate7_test_prototypes_path_refcheck_2026-03-06.txt`
- Basename sweep had 2 metadata hits in `src/genesis_core.egg-info/SOURCES.txt` for
  test names (`tests/test_exit_fibonacci.py`, `tests/test_htf_exit_engine.py`), not archive paths.

## Gates

### Pre-change gates

- `pre-commit run --all-files` -> PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS

### Post-change gates

- `pre-commit run --all-files` -> PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS

### Final rerun before push

- `pre-commit run --all-files` -> PASS
- `pytest -q -rA` selector bundle (smoke + determinism + feature cache + pipeline invariant) -> PASS (`11 passed`).

## No-behavior-change assertion

- No runtime/config/API paths changed.
- Change is constrained to archived prototype script removals with supporting governance evidence.
