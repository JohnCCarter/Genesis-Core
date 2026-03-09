# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `MED` — why: test-file relocation is path-sensitive (docs/tooling references), without runtime behavior change.
- **Required Path:** `Full`
- **Objective:** Start `tests/backtest/` classification by relocating one active backtest test with low non-archive reference surface.
- **Candidate:** `tests/test_backtest_trade_logger.py -> tests/backtest/test_backtest_trade_logger.py`
- **Base SHA:** `ceceaf47`

### Scope

- **Scope IN:**
  - `tests/test_backtest_trade_logger.py` (move source)
  - `tests/backtest/test_backtest_trade_logger.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (classification/reference update)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_backtest_bt1_2026-03-09.md`
- **Scope OUT:**
  - All runtime/source paths: `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - CI workflow changes: `.github/workflows/**`
  - Historical archives: `docs/archive/**` (including `docs/archive/deprecated_2026-02-24/**`)
  - Generated/non-authoritative references: `src/genesis_core.egg-info/SOURCES.txt`, `.pytest_cache/**`
  - Additional test-file moves beyond the single candidate
- **Expected changed files:** 3-4
- **Max files touched:** 4

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/backtest/test_backtest_trade_logger.py`
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

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> `STOP/no_steps` (expected)
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> `STOP/no_steps` (expected)

### Review + verification evidence

- Opus pre-code review: **APPROVED**
- Opus post-diff audit: **APPROVED_WITH_NOTES**
- `python -m pre_commit run --all-files` (venv Python): **PASS**
- `python -m ruff check .` (venv Python): **PASS**
- `python -m pytest -q tests/backtest/test_backtest_trade_logger.py`: **PASS**
- `python -m pytest -q tests/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- `python -m pytest -q` (full suite): **PASS**
- full suite (`runTests`): **PASS** (`1016 passed, 0 failed`)
