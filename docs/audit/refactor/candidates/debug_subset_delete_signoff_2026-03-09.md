# Candidate 11 Signoff — Delete `scripts/archive/debug` subset (2026-03-09)

Mode: RESEARCH (source=branch mapping `feature/*`)
Candidate: `delete_archive_debug_subset_except_diagnose_zero_trades`

## Scope summary

- Deleted exactly 37 files listed in:
  - `docs/audit/refactor/evidence/candidate11_debug_subset_manifest_2026-03-09.txt`
- Explicitly preserved:
  - `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py`
- Added candidate artifacts:
  - `docs/audit/refactor/command_packet_candidate11_delete_archive_debug_subset_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate11_debug_subset_manifest_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate11_debug_subset_path_refcheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate11_debug_subset_exact_path_refcheck_2026-03-09.json`
  - `docs/audit/refactor/evidence/candidate11_final_rerun_transcript_2026-03-09.txt`
  - `docs/audit/refactor/debug_subset_delete_signoff_2026-03-09.md`

## Reference safety evidence

- Exact delete manifest: `candidate11_debug_subset_manifest_2026-03-09.txt`
- Exact-path refcheck summary:
  - `target_count = 37`
  - `paths_with_hits = 0`
  - `total_hits = 0`
  - source: `candidate11_debug_subset_exact_path_refcheck_2026-03-09.json`
- Excluded path safety reason:
  - `.github/skills/decision_gate_debug.json` references `scripts/archive/debug/2026-02-14/diagnose_zero_trades.py` (r. 35, 57)

## Skill evidence (supplemental)

- `repo_clean_refactor` (`--manifest dev --dry-run`) -> Triggered `OK`, Verified/Result `STOP` (`no executable steps`)
- `python_engineering` (`--manifest dev --dry-run`) -> Triggered `OK`, Verified/Result `STOP` (`no executable steps`)

## Gates (post-delete)

- `pre-commit run --all-files` -> PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` -> PASS
- `pytest -q tests/test_feature_cache.py tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` -> PASS
- Transcript: `docs/audit/refactor/evidence/candidate11_final_rerun_transcript_2026-03-09.txt`

## Parity check

- `manifest_targets=37`
- `existing_after_delete=0`
- `excluded_exists=True`

## No-behavior-change assertion

- No runtime/config/API paths changed.
- No env/config interpretation changes.
- Change is constrained to archive cleanup + governance evidence artifacts.
