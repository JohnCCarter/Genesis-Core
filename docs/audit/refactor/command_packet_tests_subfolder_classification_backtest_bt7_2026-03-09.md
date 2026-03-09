# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `MED` — why: selector-ankrad testfil-relokering är path-sensitiv i docs/contracts, men ingen runtime behavior change.
- **Required Path:** `Full`
- **Objective:** Start dedicated selector-anchored batch by relocating `test_backtest_hook_invariants.py` with explicit plan guardrail update.
- **Candidate:** `tests/test_backtest_hook_invariants.py -> tests/backtest/test_backtest_hook_invariants.py`
- **Base SHA:** `42dfbfc8`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (endast path-relokering av testfil; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

### Scope

- **Scope IN:**
  - `tests/test_backtest_hook_invariants.py` (move source)
  - `tests/backtest/test_backtest_hook_invariants.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (classification + selector guardrail update)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_backtest_bt7_2026-03-09.md`
- **Scope OUT:**
  - All runtime/source paths: `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - CI workflow changes: `.github/workflows/**`
  - Historical references cleanup in `docs/ideas/**`, `docs/audit/**`, `docs/archive/**` beyond planfile
  - Generated/non-authoritative references: `src/genesis_core.egg-info/SOURCES.txt`, `.pytest_cache/**`
  - Additional test-file moves beyond the single candidate
- **Expected changed files:** 3-4
- **Max files touched:** 4

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/backtest/test_backtest_hook_invariants.py`
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
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pre_commit run --all-files`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check .`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_hook_invariants.py`: **PASS** (`7 skipped` in current environment)
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_backtest_determinism_smoke.py`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q`: **PASS**
- `runTests` (moved file): **PASS** (`0 passed, 0 failed`; skipped in current environment)
- Skill dry-runs (`repo_clean_refactor`, `python_engineering`): **STOP/no_steps** (expected), process exit code `1`
