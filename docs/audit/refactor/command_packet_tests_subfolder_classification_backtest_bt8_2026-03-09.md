# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `MED` — why: selector-ankrad testfil-relokering med aktiva docs/contracts-referenser, men ingen runtime behavior change.
- **Required Path:** `Full`
- **Objective:** Relocate `test_backtest_determinism_smoke.py` to `tests/backtest/` and update only active operational/governance references.
- **Candidate:** `tests/test_backtest_determinism_smoke.py -> tests/backtest/test_backtest_determinism_smoke.py`
- **Base SHA:** `07b1c7ed`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (endast path-relokering av testfil + docs path updates; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

### Scope

- **Scope IN:**
  - `tests/test_backtest_determinism_smoke.py` (move source)
  - `tests/backtest/test_backtest_determinism_smoke.py` (move target)
  - `handoff.md` (active operational reference update)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (selector guardrail update)
  - `docs/ideas/REGIME_INTELLIGENCE_DOD_P1_P2_2026-02-27.md` (active DoD reference update)
  - `docs/ideas/REGIME_INTELLIGENCE_T9_CONTRACT_2026-03-04.md` (active contract selector update)
  - `docs/ideas/REGIME_INTELLIGENCE_T9A_COMMAND_PACKET_2026-03-04.md` (active packet selector update)
  - `docs/ideas/REGIME_INTELLIGENCE_T9A_IMPLEMENTATION_REPORT_2026-03-04.md` (active report selector update)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_backtest_bt8_2026-03-09.md`
- **Scope OUT:**
  - All runtime/source paths: `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - CI workflow changes: `.github/workflows/**`
  - Historical/harmonization updates in `docs/ideas/REGIME_INTELLIGENCE_T0_*` .. `T8_*` (deferred batch)
  - Historical/archive refs in `docs/archive/**` and legacy `docs/audit/**` command packet history
  - Generated/non-authoritative references: `src/genesis_core.egg-info/SOURCES.txt`, `.pytest_cache/**`
  - Additional test-file moves beyond the single candidate
- **Expected changed files:** 8-9
- **Max files touched:** 9

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q`
- Selectors (exact commands):
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
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

- Explore subagent reference mapping: **completed** (active vs historical reference segmentation)
- QA subagent risk review: **GO_WITH_SPLIT** (minimal active reference scope)
- Opus pre-code review: **APPROVED**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pre_commit run --all-files`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check .`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q`: **PASS**
- `runTests` (moved file): **PASS** (`3 passed, 0 failed`)
- Skill dry-runs (`repo_clean_refactor`, `python_engineering`): **STOP/no_steps** (expected), process exit code `1`
