# Command Packet — Candidate 24 Delete deprecated optuna/phase batch (2026-03-10)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `docs`
- **Risk:** `LOW` — deprecated archive docs-only deletion with exact-path refcheck showing no external blockers
- **Required Path:** `Full`
- **Objective:** Continue safe high-throughput cleanup by deleting 8 low-risk deprecated archive docs across optimization/features/performance phase reports.
- **Candidate:** `delete_docs_archive_optuna_phase_batch_candidate24`
- **Base SHA:** `c657303b`

### Scope

- **Scope IN:**
  - Delete targets listed in `docs/audit/refactor/evidence/candidate24_optuna_phase_delete_manifest_2026-03-10.tsv` (8 files)
  - `docs/audit/refactor/command_packet_candidate24_delete_docs_archive_optuna_phase_batch_2026-03-10.md`
  - `docs/audit/refactor/evidence/docs_archive_triage_optuna_phase_batch_candidate24_decision_2026-03-10.md`
  - `docs/audit/refactor/evidence/candidate24_optuna_phase_delete_manifest_2026-03-10.tsv`
  - `docs/audit/refactor/evidence/candidate24_optuna_phase_path_refcheck_2026-03-10.txt`
  - `docs/audit/refactor/evidence/candidate24_skill_invocation_2026-03-10.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate24_post_delete_scope_drift_2026-03-10.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate24_gate_transcript_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate24_optuna_phase_implementation_report_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate24_pr_evidence_template_2026-03-10.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - Non-candidate paths under `docs/archive/**`
- **Expected changed files:** `19` (8 deletes + up to 11 governance/evidence files)
- **Max files touched:** `21`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Only docs/audit evidence and deprecated archive docs may change.
No runtime/config/test logic files may be modified.

### Evidence for candidate safety

- Candidate decision: `docs/audit/refactor/evidence/docs_archive_triage_optuna_phase_batch_candidate24_decision_2026-03-10.md`
- Manifest: `docs/audit/refactor/evidence/candidate24_optuna_phase_delete_manifest_2026-03-10.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate24_optuna_phase_path_refcheck_2026-03-10.txt`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Scope drift proof (to generate): `docs/audit/refactor/evidence/candidate24_post_delete_scope_drift_2026-03-10.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate24_gate_transcript_2026-03-10.md`

### Skill usage (explicit)

- Repo-local skills invoked (governance evidence): `repo_clean_refactor`, `python_engineering` via `scripts/run_skill.py --dry-run`.
- Supplemental planning skills loaded: `context-map`, `refactor-plan`.
- Invocation evidence: `docs/audit/refactor/evidence/candidate24_skill_invocation_2026-03-10.txt`.
- Note: `STOP/no_steps` for SPEC-skills is recorded as governance evidence and is not a substitute for mandatory gates.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** candidate24 deletion.

### Stop Conditions

- Scope drift outside manifest-listed delete targets.
- Any active external reference found outside `docs/archive/**` and `docs/audit/**` for in-scope files.
- Behavior change without explicit exception.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template**
