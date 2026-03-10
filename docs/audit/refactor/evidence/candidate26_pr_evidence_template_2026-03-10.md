# PR Evidence Template — Candidate26 (2026-03-10)

## Scope and mode

- Mode: `RESEARCH`
- Category: `docs`
- Risk: `LOW`
- Constraint: `NO BEHAVIOR CHANGE`
- Candidate: `delete_docs_archive_features_semantic_batch_candidate26`

## Scope IN / OUT

- Scope IN: 8 manifest-listed archive doc deletions + Candidate26 governance/evidence files.
- Scope OUT: `src/**`, `config/**`, `tests/**` (except execution), `mcp_server/**`, `.github/workflows/**`, non-candidate archive files.

## Evidence links

- Command packet: `docs/audit/refactor/command_packet_candidate26_delete_docs_archive_features_semantic_batch_2026-03-10.md`
- Decision file: `docs/audit/refactor/evidence/docs_archive_triage_features_semantic_batch_candidate26_decision_2026-03-10.md`
- Delete manifest: `docs/audit/refactor/evidence/candidate26_features_semantic_delete_manifest_2026-03-10.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate26_features_semantic_path_refcheck_2026-03-10.txt`
- Skill invocation evidence: `docs/audit/refactor/evidence/candidate26_skill_invocation_2026-03-10.txt`
- Scope drift proof: `docs/audit/refactor/evidence/candidate26_post_delete_scope_drift_2026-03-10.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate26_gate_transcript_2026-03-10.md`
- Implementation report: `docs/audit/refactor/evidence/candidate26_features_semantic_implementation_report_2026-03-10.md`

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

- [x] Scope drift proof shows PASS_SCOPE_MATCH
- [x] Gate transcript includes pre and post PASS
- [x] No changes outside approved docs/audit/archive scope
- [x] Path refcheck confirms no external exact-path blockers

Reviewer checklist completed in post-code audit: scope drift PASS_SCOPE_MATCH, pre/post gates PASS, no out-of-scope paths detected, and path refcheck PASS_NO_EXTERNAL_HITS.
