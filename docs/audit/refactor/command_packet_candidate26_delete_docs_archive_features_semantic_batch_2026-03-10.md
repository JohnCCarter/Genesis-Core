# Command Packet — Candidate 26 Delete deprecated features semantic batch (2026-03-10)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `docs`
- **Risk:** `LOW` — deprecated archive docs-only deletion with exact-path refcheck showing no external blockers
- **Required Path:** `Full`
- **Objective:** Continue governed cleanup by deleting 8 low-risk deprecated feature docs in one concentrated subtree.
- **Candidate:** `delete_docs_archive_features_semantic_batch_candidate26`
- **Base SHA:** `b9fb042c`

### Scope

- **Scope IN:**
  - Delete targets listed in `docs/audit/refactor/evidence/candidate26_features_semantic_delete_manifest_2026-03-10.tsv` (8 files)
  - `docs/audit/refactor/command_packet_candidate26_delete_docs_archive_features_semantic_batch_2026-03-10.md`
  - `docs/audit/refactor/evidence/docs_archive_triage_features_semantic_batch_candidate26_decision_2026-03-10.md`
  - `docs/audit/refactor/evidence/candidate26_features_semantic_delete_manifest_2026-03-10.tsv`
  - `docs/audit/refactor/evidence/candidate26_features_semantic_path_refcheck_2026-03-10.txt`
  - `docs/audit/refactor/evidence/candidate26_skill_invocation_2026-03-10.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate26_post_delete_scope_drift_2026-03-10.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate26_gate_transcript_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate26_features_semantic_implementation_report_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate26_pr_evidence_template_2026-03-10.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - Non-candidate paths under `docs/archive/**`
- **Expected changed files:** `20` (8 deletes + up to 12 governance/evidence files)
- **Max files touched:** `22`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Only docs/audit evidence and deprecated archive docs may change.
No runtime/config/test logic files may be modified.

### Evidence for candidate safety

- Candidate decision: `docs/audit/refactor/evidence/docs_archive_triage_features_semantic_batch_candidate26_decision_2026-03-10.md`
- Manifest: `docs/audit/refactor/evidence/candidate26_features_semantic_delete_manifest_2026-03-10.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate26_features_semantic_path_refcheck_2026-03-10.txt`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Scope drift proof (to generate): `docs/audit/refactor/evidence/candidate26_post_delete_scope_drift_2026-03-10.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate26_gate_transcript_2026-03-10.md`

### Skill usage (explicit)

- Repo-local skills invoked (governance evidence): `repo_clean_refactor`, `python_engineering` via `scripts/run_skill.py --dry-run`.
- Executable skill evidence for this candidate is the recorded `scripts/run_skill.py --dry-run` invocations for `repo_clean_refactor` and `python_engineering`.
- Any additional planning-skill usage is treated as non-blocking context unless separately evidenced.
- Invocation evidence: `docs/audit/refactor/evidence/candidate26_skill_invocation_2026-03-10.txt`.
- Note: `STOP/no_steps` for SPEC-skills is recorded as governance evidence and is not a substitute for mandatory gates.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** candidate26 deletion.

### Stop Conditions

- Scope drift outside manifest-listed delete targets.
- Any active external reference found outside `docs/archive/**` and `docs/audit/**` for in-scope files.
- Behavior change without explicit exception.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template**
