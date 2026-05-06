# PR Evidence Template — Candidate31 (2026-03-10)

## Scope and mode

- Mode: `RESEARCH`
- Category: `docs`
- Risk: `LOW`
- Required Path: `Full`
- Constraint: `NO BEHAVIOR CHANGE`
- Candidate: `resolve_docs_archive_uncertain_keep_batch_candidate31`

## Scope IN / OUT

- Scope IN: triage metadata/evidence updates under `docs/audit/refactor/**` only.
- Scope OUT: `src/**`, `config/**`, `tests/**` (except execution), `mcp_server/**`, `.github/workflows/**`, any `docs/archive/**` deletions.

## Evidence links

- Command packet (current retained path): `docs/audit/refactor/candidates/command_packet_candidate31_resolve_docs_archive_uncertain_keep_batch_2026-03-10.md`
- Decision file: `docs/audit/refactor/evidence/docs_archive_triage_uncertain_keep_batch_candidate31_decision_2026-03-10.md`
- KEEP manifest: `docs/audit/refactor/evidence/candidate31_uncertain_keep_manifest_2026-03-10.tsv`
- Retention refcheck: `docs/audit/refactor/evidence/candidate31_uncertain_retention_refcheck_2026-03-10.txt`
- Skill invocation evidence: `docs/audit/refactor/evidence/candidate31_skill_invocation_2026-03-10.txt`
- Scope drift proof: `docs/audit/refactor/evidence/candidate31_post_resolution_scope_drift_2026-03-10.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate31_gate_transcript_2026-03-10.md`
- Gate raw output: `docs/audit/refactor/evidence/candidate31_gate_raw_output_2026-03-10.txt`
- Implementation report: `docs/audit/refactor/evidence/candidate31_uncertain_keep_implementation_report_2026-03-10.md`

## Gates

Pre and post gates executed:

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

All gates reported PASS according to `candidate31_gate_transcript_2026-03-10.md` (pre and post, exit code 0).
Gate PASS is verified via attached local transcripts/raw output for Candidate31. Independent CI rerun is recommended before merge.

## Reviewer checklist

- [x] Scope drift proof shows PASS_SCOPE_MATCH
- [x] Gate transcript includes pre and post PASS
- [x] No changes outside approved docs/audit scope
- [x] No archive deletions performed
