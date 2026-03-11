# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `MED` — why: test-file relocation is path-sensitive (docs/tooling references), even without runtime behavior change.
- **Required Path:** `Full`
- **Objective:** Execute first incremental move in Phase 2A by relocating one clearly marked PoC test file to `tests/experiments/` with minimal reversible diff.
- **Candidate:** `tests/test_components_poc.py -> tests/experiments/test_components_poc.py`
- **Base SHA:** `942d79d0`

### Scope

- **Scope IN:**
  - `tests/test_components_poc.py` (move source)
  - `tests/experiments/test_components_poc.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (status/reference update)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_phase2a_batch1_2026-03-09.md`
- **Scope OUT:**
  - All runtime/source paths: `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - CI workflow changes: `.github/workflows/**`
  - Historical archives: `docs/archive/**` (including `docs/archive/deprecated_2026-02-24/**`)
  - Additional test-file moves beyond the single candidate
- **Expected changed files:** 3-4
- **Max files touched:** 4

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/experiments/test_components_poc.py`
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

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** (notes applied in this packet)
- Opus post-diff audit: **APPROVED**
- `python -m pre_commit run --all-files` (venv Python): **PASS**
- `python -m ruff check .` (venv Python): **PASS**
- `python -m pytest -q tests/experiments/test_components_poc.py`: **PASS** (`20 passed`)
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- full suite (`runTests`): **PASS** (`1016 passed, 0 failed`)
