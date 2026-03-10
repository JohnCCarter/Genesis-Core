# Command Packet — Candidate 32 Promote kept archive docs to active doc subfolders (2026-03-10)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Category:** `docs`
- **Risk:** `LOW` — docs file moves + audit metadata updates only
- **Required Path:** `Full`
- **Objective:** Move the 5 retained files from `docs/archive/deprecated_2026-02-24/docs/**` into active corresponding `docs/**` subfolders.
- **Candidate:** `promote_kept_archive_docs_candidate32`
- **Base SHA:** `711cd68a`

### Scope

- **Scope IN:**
  - Move operations listed in `docs/audit/refactor/evidence/candidate32_promote_manifest_2026-03-10.tsv` (5 files)
  - `docs/audit/refactor/command_packet_candidate32_promote_kept_archive_docs_2026-03-10.md`
  - `docs/audit/refactor/evidence/docs_archive_triage_promote_kept_batch_candidate32_decision_2026-03-10.md`
  - `docs/audit/refactor/evidence/candidate32_promote_manifest_2026-03-10.tsv`
  - `docs/audit/refactor/evidence/candidate32_promote_path_refcheck_2026-03-10.txt`
  - `docs/audit/refactor/evidence/candidate32_skill_invocation_2026-03-10.txt`
  - `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate32_post_move_scope_drift_2026-03-10.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate32_gate_transcript_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate32_gate_raw_output_2026-03-10.txt` (to be generated)
  - `docs/audit/refactor/evidence/candidate32_promote_implementation_report_2026-03-10.md` (to be generated)
  - `docs/audit/refactor/evidence/candidate32_pr_evidence_template_2026-03-10.md` (to be generated)
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` (except executing tests)
  - `mcp_server/**`
  - `.github/workflows/**`
  - Any non-candidate file under `docs/**`
- **Expected changed files:** `22` (5 source removals + 5 destination adds + 12 governance/evidence files)
- **Max files touched:** `22`

### Constraints

Constraint: **NO BEHAVIOR CHANGE**.
Primary change scope is moving retained documentation files from deprecated archive to active docs locations.
Additional generated governance artifacts are allowed only under `docs/audit/refactor/evidence/` and must not alter runtime/config/test behavior.
No code/runtime/config/test logic files may be modified.

### Evidence for candidate safety

- Candidate decision: `docs/audit/refactor/evidence/docs_archive_triage_promote_kept_batch_candidate32_decision_2026-03-10.md`
- Promote manifest: `docs/audit/refactor/evidence/candidate32_promote_manifest_2026-03-10.tsv`
- Path refcheck: `docs/audit/refactor/evidence/candidate32_promote_path_refcheck_2026-03-10.txt`
- Triage matrix: `docs/audit/refactor/evidence/docs_archive_triage_matrix_2026-03-09.tsv`
- Triage summary: `docs/audit/refactor/evidence/docs_archive_triage_summary_2026-03-09.txt`
- Scope drift proof (to generate): `docs/audit/refactor/evidence/candidate32_post_move_scope_drift_2026-03-10.txt`
- Gate transcript (to generate): `docs/audit/refactor/evidence/candidate32_gate_transcript_2026-03-10.md`
- Gate raw output (to generate): `docs/audit/refactor/evidence/candidate32_gate_raw_output_2026-03-10.txt`

### Skill usage (explicit)

- Repo-local skills invoked (governance evidence): `repo_clean_refactor`, `python_engineering` via `scripts/run_skill.py --manifest dev --dry-run`.
- Invocation evidence: `docs/audit/refactor/evidence/candidate32_skill_invocation_2026-03-10.txt`.
- Note: `STOP/no_steps` for SPEC-skills is recorded as governance evidence and is not a substitute for mandatory gates.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_fast_hash_guard`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** Candidate32 move/update.

### Stop Conditions

- Scope drift outside approved paths.
- Any file overwrite/collision on destination paths.
- Determinism/cache/pipeline invariant regression.
- Forbidden paths touched.

### Output required

- **Implementation Report**
- **PR evidence template**
