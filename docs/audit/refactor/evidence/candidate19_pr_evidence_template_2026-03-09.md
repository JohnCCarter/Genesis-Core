# PR Evidence Template — Candidate19 (2026-03-09)

## Mode and governance

- Mode: `RESEARCH` (source: branch mapping `feature/docs-archive-review-2026-03-09`)
- Risk: `MED`
- Path: `Full`
- Constraint: **NO BEHAVIOR CHANGE**

## Scope

### IN

- 4 manifest-listed deletes:
  - `docs/archive/phase6/DOCUMENTATION_ANALYSIS.md`
  - `docs/archive/phase6/ORIGINAL_REPO_MENTIONS.md`
  - `docs/archive/phase6/TODO.md`
  - `docs/archive/STRATEGY_SPEC_phase3.md`
- Candidate19 packet/evidence files under `docs/audit/refactor/**`

### OUT

- `src/**`, `config/**`, `mcp_server/**`, `.github/workflows/**`
- Non-candidate paths under `docs/archive/**`

## Evidence artifacts

- Packet (current retained path): `docs/audit/refactor/candidates/command_packet_candidate19_delete_docs_archive_phase6_legacy_core_2026-03-09.md`
- Manifest: `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_delete_manifest_2026-03-09.tsv`
- Refcheck: `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_path_refcheck_2026-03-09.txt`
- Scope drift: `docs/audit/refactor/evidence/candidate19_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript: `docs/audit/refactor/evidence/candidate19_gate_transcript_2026-03-09.md`
- Implementation report: `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_implementation_report_2026-03-09.md`

## Gate outcomes (pre + post)

- `pre_commit --all-files` → PASS
- `tests/test_backtest_determinism_smoke.py` → PASS
- `tests/test_feature_cache.py` → PASS
- `tests/test_pipeline_fast_hash_guard.py` → PASS (with targeted invariant node-id reruns documented)
- `scripts/run/run_backtest.py --help` → PASS

## Residual risk

- Low: potential informal/manual references to deleted archive docs outside tracked code paths.
- Mitigation: explicit no-hit refcheck outside `docs/archive` and `docs/audit`.
