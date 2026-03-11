# Command Packet — Candidate 20 Delete deprecated validation archive batch (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `docs`
- **Risk:** `MED` — archive deletion can hide stale dependencies if scope drifts
- **Required Path:** `Full`
- **Objective:** Execute safe, traceable deletion of deprecated validation archive docs after exact-path refcheck.
- **Candidate:** `delete_docs_archive_validation_batch_candidate20`
- **Base SHA:** `53ff07a48e24ec60812380aaca4f2a2529215417`

### Scope

- **Scope IN:**
  - Delete targets listed in `docs/audit/refactor/evidence/candidate20_validation_delete_manifest_2026-03-09.tsv` (6 files)
  - `docs/audit/refactor/command_packet_candidate20_delete_docs_archive_validation_batch_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate20_validation_delete_manifest_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/candidate20_validation_path_refcheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_validation_batch_decision_2026-03-09.md`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate20_post_delete_scope_drift_2026-03-09.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate20_gate_transcript_2026-03-09.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate20_validation_implementation_report_2026-03-09.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate20_pr_evidence_template_2026-03-09.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - Non-candidate paths under `docs/archive/**`
- **Expected changed files:** `16` (6 deletes + up to 10 governance/evidence files)
- **Max files touched:** `20`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Change is limited to docs/audit evidence updates + deletion of 6 deprecated validation archive files.
No runtime/config/test logic files may be modified.

### Evidence for candidate safety

- Manifest: `docs/audit/refactor/evidence/candidate20_validation_delete_manifest_2026-03-09.tsv`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Batch decision: `docs/audit/refactor/evidence/docs_archive_triage_validation_batch_decision_2026-03-09.md`
- Path refcheck: `docs/audit/refactor/evidence/candidate20_validation_path_refcheck_2026-03-09.txt`
- Scope-drift proof (to generate): `docs/audit/refactor/evidence/candidate20_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate20_gate_transcript_2026-03-09.md`

### Skill usage (explicit)

- Repo-local skills invoked: `repo_clean_refactor`, `python_engineering` (governance SPEC evidence).
- Supplemental planning skills loaded: `context-map`, `refactor-plan`.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** candidate20 deletion.

### Stop Conditions

- Scope drift outside manifest-listed delete targets.
- Any active external reference found outside `docs/archive/**` and `docs/audit/**` (archive-internal mentions allowed for this candidate).
- Behavior change without explicit exception.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template:** `docs/audit/refactor/evidence/candidate20_pr_evidence_template_2026-03-09.md`
