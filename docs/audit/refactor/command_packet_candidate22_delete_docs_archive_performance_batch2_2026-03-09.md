# Command Packet — Candidate 22 Delete deprecated performance/optimization batch2 (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `docs`
- **Risk:** `LOW` — archive-doc deletion in deprecated subtree with explicit no-external-hit refcheck for in-scope files
- **Required Path:** `Full`
- **Objective:** Increase cleanup throughput safely by deleting 8 low-risk deprecated performance/optimization snapshot docs.
- **Candidate:** `delete_docs_archive_performance_batch2_candidate22`
- **Base SHA:** `aaab92cd73f3a7bca370fd96d7801b216ff36c8f`

### Scope

- **Scope IN:**
  - Delete targets listed in `docs/audit/refactor/evidence/candidate22_performance_batch2_delete_manifest_2026-03-09.tsv` (8 files)
  - `docs/audit/refactor/command_packet_candidate22_delete_docs_archive_performance_batch2_2026-03-09.md`
  - `docs/audit/refactor/evidence/docs_archive_triage_performance_batch2_decision_2026-03-09.md`
  - `docs/audit/refactor/evidence/candidate22_performance_batch2_delete_manifest_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/candidate22_performance_batch2_path_refcheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate22_skill_invocation_2026-03-09.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate22_post_delete_scope_drift_2026-03-09.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate22_gate_transcript_2026-03-09.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate22_performance_batch2_implementation_report_2026-03-09.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate22_pr_evidence_template_2026-03-09.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - Non-candidate paths under `docs/archive/**`
- **Expected changed files:** `19` (8 deletes + up to 11 governance/evidence files)
- **Max files touched:** `20`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Only docs/audit evidence and deprecated archive docs may change.
No runtime/config/test logic files may be modified.

### Evidence for candidate safety

- Candidate decision: `docs/audit/refactor/evidence/docs_archive_triage_performance_batch2_decision_2026-03-09.md`
- Manifest: `docs/audit/refactor/evidence/candidate22_performance_batch2_delete_manifest_2026-03-09.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate22_performance_batch2_path_refcheck_2026-03-09.txt`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Scope drift proof (to generate): `docs/audit/refactor/evidence/candidate22_post_delete_scope_drift_2026-03-09.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate22_gate_transcript_2026-03-09.md`

### Skill usage (explicit)

- Repo-local skills invoked (governance evidence): `repo_clean_refactor`, `python_engineering` via `scripts/run_skill.py --dry-run`.
- Supplemental planning skills loaded: `context-map`, `refactor-plan`.
- Invocation evidence: `docs/audit/refactor/evidence/candidate22_skill_invocation_2026-03-09.txt`.
- Note: `STOP/no_steps` for SPEC-skills is recorded as governance evidence and is not a substitute for mandatory gates.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** candidate22 deletion.

### Stop Conditions

- Scope drift outside manifest-listed delete targets.
- Any active external reference found outside `docs/archive/**` and `docs/audit/**` for in-scope files.
- Behavior change without explicit exception.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template**
