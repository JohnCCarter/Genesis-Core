# PR Evidence Template — Candidate25 (2026-03-10)

## Scope and mode

- Mode: `RESEARCH`
- Category: `docs`
- Risk: `LOW`
- Constraint: `NO BEHAVIOR CHANGE`
- Candidate: `delete_docs_archive_phase3_features_batch_candidate25`

## Scope IN / OUT

- Scope IN: 10 manifest-listed archive doc deletions + Candidate25 governance/evidence files.
- Scope OUT: `src/**`, `config/**`, `tests/**` (except execution), `mcp_server/**`, `.github/workflows/**`, non-candidate archive files.

## Evidence links

- Command packet (current retained path): `docs/audit/refactor/candidates/command_packet_candidate25_delete_docs_archive_phase3_features_batch_2026-03-10.md`
- Decision file: `docs/audit/refactor/evidence/docs_archive_triage_phase3_features_batch_candidate25_decision_2026-03-10.md`
- Delete manifest: `docs/audit/refactor/evidence/candidate25_phase3_features_delete_manifest_2026-03-10.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate25_phase3_features_path_refcheck_2026-03-10.txt`
- Skill invocation evidence: `docs/audit/refactor/evidence/candidate25_skill_invocation_2026-03-10.txt`
- Scope drift proof: `docs/audit/refactor/evidence/candidate25_post_delete_scope_drift_2026-03-10.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate25_gate_transcript_2026-03-10.md`
- Implementation report: `docs/audit/refactor/evidence/candidate25_phase3_features_implementation_report_2026-03-10.md`

## Gates

Pre and post gates executed:

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

All gates: PASS.

## Reviewer checklist

- [ ] Scope drift proof shows PASS_SCOPE_MATCH
- [ ] Gate transcript includes pre and post PASS
- [ ] No changes outside approved docs/audit/archive scope
- [ ] Path refcheck confirms no external exact-path blockers
