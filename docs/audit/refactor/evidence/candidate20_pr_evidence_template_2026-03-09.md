# PR Evidence Template — Candidate20 (2026-03-09)

## Mode and governance

- Mode: `RESEARCH` (source: branch mapping `feature/docs-archive-review-2026-03-09`)
- Risk: `MED`
- Path: `Full`
- Constraint: **NO BEHAVIOR CHANGE**

## Scope

### IN

- 6 manifest-listed deletes:
  - `docs/archive/deprecated_2026-02-24/docs/validation/AB_QUALITY_V2_PHASE7E.md`
  - `docs/archive/deprecated_2026-02-24/docs/validation/ADVANCED_VALIDATION_PRODUCTION.md`
  - `docs/archive/deprecated_2026-02-24/docs/validation/CONFIG_LOADING_VERIFICATION_20251114.md`
  - `docs/archive/deprecated_2026-02-24/docs/validation/PARITY_TEST_20251125.md`
  - `docs/archive/deprecated_2026-02-24/docs/validation/VALIDATION_CHECKLIST.md`
  - `docs/archive/deprecated_2026-02-24/docs/validation/VALIDATION_VS_BACKTEST_EXPLAINED.md`
- Candidate20 packet/evidence files under `docs/audit/refactor/**`

### OUT

- `src/**`, `config/**`, `mcp_server/**`, `.github/workflows/**`
- Non-candidate paths under `docs/archive/**`

## Evidence artifacts

- Packet (current retained path): `docs/audit/refactor/candidates/command_packet_candidate20_delete_docs_archive_validation_batch_2026-03-09.md`
- Manifest: `docs/audit/refactor/evidence/candidate20_validation_delete_manifest_2026-03-09.tsv`
- Refcheck: `docs/audit/refactor/evidence/candidate20_validation_path_refcheck_2026-03-09.txt`
- Scope drift: `docs/audit/refactor/evidence/candidate20_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate20_gate_transcript_2026-03-09.md`
- Implementation report: `docs/audit/refactor/evidence/candidate20_validation_implementation_report_2026-03-09.md`

## Gate outcomes (pre + post)

- `pre_commit --all-files` → PASS
- `tests/test_backtest_determinism_smoke.py` → PASS
- `tests/test_feature_cache.py` → PASS
- `tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard` → PASS
- `tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → PASS
- `scripts/run/run_backtest.py --help` → PASS

## Residual risk

- Low: potential informal/manual references to deleted archive docs outside tracked code paths.
- Mitigation: explicit no-hit refcheck outside `docs/archive` and `docs/audit`.
