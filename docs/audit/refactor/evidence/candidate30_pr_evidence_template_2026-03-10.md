# PR Evidence Template — Candidate30 (2026-03-10)

## Scope and mode

- Mode: `RESEARCH`
- Category: `docs`
- Risk: `LOW`
- Constraint: `NO BEHAVIOR CHANGE`
- Candidate: `delete_docs_archive_opt_strategy_batch_candidate30`

## Scope IN / OUT

- Scope IN: 2 manifest-listed archive doc deletions + Candidate30 governance/evidence files.
- Scope OUT: `src/**`, `config/**`, `tests/**` (except execution), `mcp_server/**`, `.github/workflows/**`, non-candidate archive files.

## Evidence links

- Command packet: `docs/audit/refactor/command_packet_candidate30_delete_docs_archive_opt_strategy_batch_2026-03-10.md`
- Decision file: `docs/audit/refactor/evidence/docs_archive_triage_opt_strategy_batch_candidate30_decision_2026-03-10.md`
- Delete manifest: `docs/audit/refactor/evidence/candidate30_opt_strategy_delete_manifest_2026-03-10.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate30_opt_strategy_path_refcheck_2026-03-10.txt`
- Skill invocation evidence: `docs/audit/refactor/evidence/candidate30_skill_invocation_2026-03-10.txt`
- Scope drift proof: `docs/audit/refactor/evidence/candidate30_post_delete_scope_drift_2026-03-10.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate30_gate_transcript_2026-03-10.md`
- Gate raw output: `docs/audit/refactor/evidence/candidate30_gate_raw_output_2026-03-10.txt`
- Implementation report: `docs/audit/refactor/evidence/candidate30_opt_strategy_implementation_report_2026-03-10.md`

## Gates

Pre and post gates executed:

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

All gates reported PASS according to `candidate30_gate_transcript_2026-03-10.md` (pre and post, exit code 0).
Gate PASS is verified via attached local transcripts/raw output for Candidate30. Independent CI rerun is recommended before merge.

## Reviewer checklist

- [x] Scope drift proof shows PASS_SCOPE_MATCH
- [x] Gate transcript includes pre and post PASS
- [x] No changes outside approved docs/audit/archive scope
- [x] Path refcheck confirms no external exact-path blockers
