# Command Packet — Candidate 16 Archive Mixed Assets Curation (2026-03-09)

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/archive-mixed-assets-curation`)
- **Risk:** `MED` — mixed archive content includes executable legacy scripts and temporary configs
- **Required Path:** `Full`
- **Objective:** Curate and normalize historical assets in `archive/2025-11-03/**` and `archive/model_optimization/**` with full traceability and no runtime behavior change.
- **Candidate:** `archive_mixed_assets_curation_candidate16`
- **Base SHA:** `b7940890`

### Scope

- **Scope IN:**
  - `archive/2025-11-03/**`
  - `archive/model_optimization/**`
  - `docs/audit/refactor/command_packet_candidate16_archive_mixed_assets_curation_2026-03-09.md`
  - `docs/audit/refactor/evidence/*candidate16*`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `mcp_server/**`
  - `tests/**` (read/search only)
  - `.github/workflows/**`
  - active runtime paths under `scripts/**`
- **Expected changed files:** `72 archive files (move/rename only) + up to 6 governance/evidence docs`
- **Max files touched:** `78`

### Constraints

- **NO BEHAVIOR CHANGE** by default.
- Archive curation only (move/group/manifest/documentation).
- No executable logic edits in active runtime paths.

### Evidence requirements (before move/delete)

- Complete file inventory of scope IN.
- Exact old->new path mapping manifest.
- External reference scan proving no non-archive path dependency.

### Skill usage evidence

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`

### Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_feature_cache.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`
- `python scripts/run/run_backtest.py --help`

Execution rule:

- Run full gate set **pre** and **post** each curation batch (A/B/C).

### Stop Conditions

- Scope drift outside archive curation intent.
- Missing old->new mapping evidence.
- Any touched active runtime file under `scripts/**`.
- Any freeze-escalation trigger paths touched (`config/strategy/champions/**` or `.github/workflows/champion-freeze-guard.yml`).
- Any content edit to `archive/**/*.py` (only rename/move allowed).
- Any execution of archive python scripts during curation workflow.

### Output required

- **Implementation Report**
- **PR evidence template (inventory + mapping + refscan + gate outcomes)**
