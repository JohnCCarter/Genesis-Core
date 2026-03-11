# Command Packet — Candidate 19 Delete phase6/legacy-core archive subset (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `docs`
- **Risk:** `MED` — archive deletion can hide stale path dependencies if scope drifts
- **Required Path:** `Full`
- **Objective:** Execute safe, traceable deletion of phase6/legacy-core archive files marked `DELETE_CANDIDATE` after exact-path reference verification.
- **Candidate:** `delete_docs_archive_phase6_legacy_core_candidate19`
- **Base SHA:** `916f33baad116402af5e0fee5b3c686aec8c26ff`

### Scope

- **Scope IN:**
  - delete targets listed in `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_delete_manifest_2026-03-09.tsv` (4 files)
  - `docs/audit/refactor/command_packet_candidate19_delete_docs_archive_phase6_legacy_core_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_delete_manifest_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_path_refcheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_phase6_legacy_core_decision_2026-03-09.md`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate19_post_delete_scope_drift_2026-03-09.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate19_gate_transcript_2026-03-09.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_implementation_report_2026-03-09.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate19_pr_evidence_template_2026-03-09.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - non-candidate paths under `docs/archive/**`
- **Expected changed files:** `14` (4 deletes + up to 10 governance/evidence files)
- **Max files touched:** `16`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Change is limited to docs/audit evidence updates + deletion of 4 deprecated archive files.
No runtime/config/test logic files may be modified.

### Evidence for candidate safety

- Manifest: `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_delete_manifest_2026-03-09.tsv`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Batch decision: `docs/audit/refactor/evidence/docs_archive_triage_phase6_legacy_core_decision_2026-03-09.md`
- Path refcheck: `docs/audit/refactor/evidence/candidate19_phase6_legacy_core_path_refcheck_2026-03-09.txt`
- Scope-drift proof (to generate): `docs/audit/refactor/evidence/candidate19_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate19_gate_transcript_2026-03-09.md`

### Skill usage (explicit)

- Repo-local skills invoked: `repo_clean_refactor`, `python_engineering` (governance SPEC evidence).
- Supplemental planning skills loaded: `context-map`, `refactor-plan`.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** candidate19 deletion.

### Stop Conditions

- Scope drift outside manifest-listed delete targets.
- Any active external reference found outside `docs/archive/**` and `docs/audit/**`.
- Behavior change without explicit exception.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template:** `docs/audit/refactor/evidence/candidate19_pr_evidence_template_2026-03-09.md`
