# Command Packet — Candidate 31 Resolve remaining UNCERTAIN docs to KEEP (2026-03-10)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `docs`
- **Risk:** `LOW` — docs/audit-only triage reclassification with no runtime/config file edits
- **Required Path:** `Full`
- **Objective:** Resolve remaining 5 `UNCERTAIN` archive docs into `KEEP` based on semantic-retention evidence.
- **Candidate:** `resolve_docs_archive_uncertain_keep_batch_candidate31`
- **Base SHA:** `246b4232`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/command_packet_candidate31_resolve_docs_archive_uncertain_keep_batch_2026-03-10.md`
  - `docs/audit/refactor/evidence/docs_archive_triage_uncertain_keep_batch_candidate31_decision_2026-03-10.md`
  - `docs/audit/refactor/evidence/candidate31_uncertain_keep_manifest_2026-03-10.tsv`
  - `docs/audit/refactor/evidence/candidate31_uncertain_retention_refcheck_2026-03-10.txt`
  - `docs/audit/refactor/evidence/candidate31_skill_invocation_2026-03-10.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate31_post_resolution_scope_drift_2026-03-10.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate31_gate_transcript_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate31_gate_raw_output_2026-03-10.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate31_uncertain_keep_implementation_report_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate31_pr_evidence_template_2026-03-10.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - Any delete operation under `docs/archive/**`
- **Expected changed files:** `12` (docs/audit triage + governance/evidence artifacts only)
- **Max files touched:** `14`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Primary change scope is triage reclassification in audit metadata only (no archive content changes).
Additional generated governance artifacts are allowed only under `docs/audit/refactor/evidence/` and must not alter runtime/config/test behavior.
No deletions are permitted in Candidate31.
No runtime/config/test logic files may be modified.

### Evidence for candidate safety

- Candidate decision: `docs/audit/refactor/evidence/docs_archive_triage_uncertain_keep_batch_candidate31_decision_2026-03-10.md`
- KEEP manifest: `docs/audit/refactor/evidence/candidate31_uncertain_keep_manifest_2026-03-10.tsv`
- Retention refcheck: `docs/audit/refactor/evidence/candidate31_uncertain_retention_refcheck_2026-03-10.txt`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Scope drift proof (to generate): `docs/audit/refactor/evidence/candidate31_post_resolution_scope_drift_2026-03-10.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate31_gate_transcript_2026-03-10.md`
- Gate raw output (to generate): `docs/audit/refactor/evidence/candidate31_gate_raw_output_2026-03-10.txt`

### Skill usage (explicit)

- Repo-local skills invoked (governance evidence): `repo_clean_refactor`, `python_engineering` via `scripts/run_skill.py --manifest dev --dry-run`.
- Invocation evidence: `docs/audit/refactor/evidence/candidate31_skill_invocation_2026-03-10.txt`.
- Note: `STOP/no_steps` for SPEC-skills is recorded as governance evidence and is not a substitute for mandatory gates.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** Candidate31 metadata update.

### Stop Conditions

- Scope drift outside `docs/audit/refactor/**`.
- Any direct/indirect runtime/config behavior changes.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template**
