# PR Evidence Template — Candidate32 (2026-03-10)

## Scope and mode

- Mode: `RESEARCH`
- Category: `docs`
- Risk: `LOW`
- Required Path: `Full`
- Constraint: `NO BEHAVIOR CHANGE`
- Candidate: `promote_kept_archive_docs_candidate32`

## Scope IN / OUT

- Scope IN: 5 move operations from deprecated archive to active docs subfolders + Candidate32 docs/audit evidence files.
- Scope OUT: `src/**`, `config/**`, `tests/**` (except execution), `mcp_server/**`, `.github/workflows/**`, non-candidate `docs/**` paths.

## Evidence links

- Command packet: `docs/audit/refactor/command_packet_candidate32_promote_kept_archive_docs_2026-03-10.md`
- Decision file: `docs/audit/refactor/evidence/docs_archive_triage_promote_kept_batch_candidate32_decision_2026-03-10.md`
- Promote manifest: `docs/audit/refactor/evidence/candidate32_promote_manifest_2026-03-10.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate32_promote_path_refcheck_2026-03-10.txt`
- Skill invocation evidence: `docs/audit/refactor/evidence/candidate32_skill_invocation_2026-03-10.txt`
- Scope drift proof: `docs/audit/refactor/evidence/candidate32_post_move_scope_drift_2026-03-10.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate32_gate_transcript_2026-03-10.md`
- Gate raw output: `docs/audit/refactor/evidence/candidate32_gate_raw_output_2026-03-10.txt`
- Implementation report: `docs/audit/refactor/evidence/candidate32_promote_implementation_report_2026-03-10.md`

## Gates

Pre and post gates executed:

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

All gates reported PASS according to `candidate32_gate_transcript_2026-03-10.md` (pre and post, exit code 0).

## Reviewer checklist

- [x] Scope drift proof shows PASS_SCOPE_MATCH
- [x] Gate transcript includes pre and post PASS
- [x] Move coverage matches 5 manifest pairs
- [x] No changes outside approved scope
