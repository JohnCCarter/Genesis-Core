# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `MED` — why: test-file relocation is path-sensitive (docs/tooling references), without runtime behavior change.
- **Required Path:** `Full`
- **Objective:** Execute Phase 2A micro-batch 3A by relocating one e2e-stub candidate to `tests/experiments/` with minimal reversible diff.
- **Candidate:** `tests/test_e2e_pipeline.py -> tests/experiments/test_e2e_pipeline.py`
- **Base SHA:** `ad546104`

### Scope

- **Scope IN:**
  - `tests/test_e2e_pipeline.py` (move source)
  - `tests/experiments/test_e2e_pipeline.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (status/reference update)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_phase2a_batch3a_2026-03-09.md`
- **Scope OUT:**
  - All runtime/source paths: `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - CI workflow changes: `.github/workflows/**`
  - Historical archives: `docs/archive/**` (including `docs/archive/deprecated_2026-02-24/**`)
  - Generated/non-authoritative references: `src/genesis_core.egg-info/SOURCES.txt`, `.pytest_cache/**`
  - Archive reference updates are intentionally deferred to a later cleanup batch.
  - Additional test-file moves beyond the single candidate
- **Expected changed files:** 3-4
- **Max files touched:** 4

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/experiments/test_e2e_pipeline.py`
- `python -m pytest -q`
- Selectors (exact commands):
  - `python -m pytest -q tests/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`

### Stop Conditions

- Any scope drift outside Scope IN
- Any behavior change beyond path relocation
- Selector regression (determinism/cache/pipeline)
- Forbidden/high-sensitivity runtime paths touched

### Output required

- **Implementation Report**
- **PR evidence template**

### Skill Usage

- `repo_clean_refactor` (SPEC reference)
- `python_engineering` (SPEC reference)

### Skill invocation evidence

- `scripts/run_skill.py` invocation evidence is recorded below.
- `STOP/no_steps` is expected for SPEC-only skills and does **not** replace required gates.
- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> `STOP/no_steps` (expected)
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> `STOP/no_steps` (expected)

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** (notes applied in this packet)
- Opus post-diff audit: **APPROVED_WITH_NOTES** (no code changes required)
- `python -m pre_commit run --all-files` (venv Python): **PASS**
- `python -m ruff check .` (venv Python): **PASS**
- `python -m pytest -q tests/experiments/test_e2e_pipeline.py`: **PASS** (`2 passed`)
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- `python -m pytest -q` (full suite): **PASS**
- full suite (`runTests`): **PASS** (`1016 passed, 0 failed`)
