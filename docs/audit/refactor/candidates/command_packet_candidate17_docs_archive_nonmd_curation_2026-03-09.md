# Command Packet — Candidate 17 Docs Archive Non-MD Curation (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/docs-archive-review-2026-03-09`)
- **Risk:** `MED` — archive scope includes executable text (`.py`) and notebooks (`.ipynb`)
- **Required Path:** `Full`
- **Objective:** Curate 4 historical non-markdown analysis files under `docs/archive/deprecated_2026-02-24/docs/analysis/` into explicit non-markdown quarantine paths using rename-only operations, with no runtime behavior change.
- **Candidate:** `docs_archive_nonmd_curation_candidate17`
- **Base SHA:** `e1947604`

### Scope

- **Scope IN:**
  - `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_analysis.ipynb`
  - `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_analysis.py`
  - `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_v4_analysis.ipynb`
  - `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_v4_analysis.py`
  - `docs/archive/quarantine/non_markdown/deprecated_2026-02-24/analysis/optimization_analysis.ipynb`
  - `docs/archive/quarantine/non_markdown/deprecated_2026-02-24/analysis/optimization_analysis.py`
  - `docs/archive/quarantine/non_markdown/deprecated_2026-02-24/analysis/optimization_v4_analysis.ipynb`
  - `docs/archive/quarantine/non_markdown/deprecated_2026-02-24/analysis/optimization_v4_analysis.py`
  - `docs/audit/refactor/command_packet_candidate17_docs_archive_nonmd_curation_2026-03-09.md`
  - `docs/audit/refactor/evidence/docs_archive_review_kickoff_2026-03-09.md`
  - `docs/audit/refactor/evidence/docs_archive_nonmd_proposed_manifest_2026-03-09.tsv`
  - `docs/audit/refactor/evidence/candidate17_docs_archive_nonmd_precheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate17_docs_archive_nonmd_postcheck_2026-03-09.txt`
  - `docs/audit/refactor/evidence/candidate17_docs_archive_nonmd_gate_transcript_2026-03-09.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `scripts/**` (except running approved smoke command)
  - `.github/workflows/**`
  - `tests/**` (read/execute only)
- **Expected changed files:** `4 archive files (rename only) + up to 6 governance/evidence docs`
- **Max files touched:** `10`

### Constraints

- **NO BEHAVIOR CHANGE** by default.
- Rename/move operations only for scoped 4 non-md files.
- No content edits inside moved `.py`/`.ipynb` files.
- No execution of archive scripts/notebooks.

### Evidence requirements (before move)

- External reference scan for the 4 basenames outside `docs/archive/**` and `docs/audit/**`.
- Exact old->new mapping manifest (already prepared) must match executed paths.

### Skill Usage

- Pre-review: invoke relevant repo skill(s) for archive/refactor governance; record outcome in `docs/audit/refactor/evidence/candidate17_docs_archive_nonmd_precheck_2026-03-09.txt`.
- Post-audit: repeat skill invocation and record outcome in `docs/audit/refactor/evidence/candidate17_docs_archive_nonmd_postcheck_2026-03-09.txt`.

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** curation execution.

### Stop Conditions

- Scope drift outside files listed under Scope IN.
- Any content edit detected in moved `.py`/`.ipynb` (must be pure rename/move).
- Any reference check indicates active dependency outside archive/audit.
- Any touched path in freeze escalation set (`config/strategy/champions/**`, `.github/workflows/champion-freeze-guard.yml`).
- Any gate failure in pre or post phase.

### Output required

- **Implementation Report**
- **PR evidence template (precheck + mapping + postcheck + gate outcomes)**
