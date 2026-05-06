# PR Evidence Template — Candidate22 (2026-03-09)

## Scope and mode

- Mode: `RESEARCH`
- Category: `docs`
- Risk: `LOW`
- Constraint: `NO BEHAVIOR CHANGE`
- Candidate: `delete_docs_archive_performance_batch2_candidate22`

## Scope IN / OUT

- Scope IN: 8 manifest-listed archive doc deletions + Candidate22 governance/evidence files.
- Scope OUT: `src/**`, `config/**`, `tests/**` (except execution), `mcp_server/**`, `.github/workflows/**`, non-candidate archive files.

## Evidence links

- Command packet (current retained path): `docs/audit/refactor/candidates/command_packet_candidate22_delete_docs_archive_performance_batch2_2026-03-09.md`
- Decision file: `docs/audit/refactor/evidence/docs_archive_triage_performance_batch2_decision_2026-03-09.md`
- Delete manifest: `docs/audit/refactor/evidence/candidate22_performance_batch2_delete_manifest_2026-03-09.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate22_performance_batch2_path_refcheck_2026-03-09.txt`
- Skill invocation evidence: `docs/audit/refactor/evidence/candidate22_skill_invocation_2026-03-09.txt`
- Scope drift proof: `docs/audit/refactor/evidence/candidate22_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate22_gate_transcript_2026-03-09.md`
- Implementation report: `docs/audit/refactor/evidence/candidate22_performance_batch2_implementation_report_2026-03-09.md`

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
- [ ] No changes outside approved docs/audit scope
- [ ] External-reference blocker file remained excluded
