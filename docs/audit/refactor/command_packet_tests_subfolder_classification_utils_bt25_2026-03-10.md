# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: single-candidate test relocation av liten indikator-smoke-test utan aktiva docs-referenser.
- **Required Path:** `Full`
- **Objective:** Relocate `test_indicators_min.py` to `tests/utils/` with no behavior change.
- **Candidate:** `tests/test_indicators_min.py -> tests/utils/test_indicators_min.py`
- **Base SHA:** `266bfa03`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (enbart testflytt + planrad/paket; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: single-candidate utility move, kandidat saknar path-känslighet och saknar aktiva docs-referenser
- **Required Path:** `Full`
- **Objective:** Continue utils-category migration with low-friction candidate.
- **Candidate:** `test_indicators_min.py`
- **Base SHA:** `266bfa03`

### Scope

- **Scope IN:**
  - `tests/test_indicators_min.py` (move source)
  - `tests/utils/test_indicators_min.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (batch progress row)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt25_2026-03-10.md`
- **Scope OUT:**
  - `src/**`, `mcp_server/**`, `scripts/**`, `config/**`
  - `.github/workflows/**`
  - All docs outside plan/paket-filen ovan
  - Any additional test-file moves
  - Generated metadata/cache paths (`.pytest_cache/**`, `**/*.egg-info/**`)
- **Expected changed files:** 3-4
- **Max files touched:** 4

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/utils/test_indicators_min.py`
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
- Selectors:
  - determinism replay: `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - feature cache invariance: `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
  - pipeline invariant: `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`

### Stop Conditions

- Scope drift outside Scope IN
- Behavior change utan explicit undantag
- Determinism/cache/pipeline selector regression
- Forbidden runtime/high-sensitivity paths touched

### Output required

- **Implementation Report**
- **PR evidence template**

### Skill Usage

- `repo_clean_refactor` (SPEC reference)
- `python_engineering` (SPEC reference)

### Skill invocation evidence

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` (run from cwd `.../Genesis-Core-refactor-b`) -> **STOP/no_steps** (expected), non-zero exit.
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` (run from cwd `.../Genesis-Core-refactor-b`) -> **STOP/no_steps** (expected), non-zero exit.

### Branch/mode evidence (pre-coding)

- `git status -sb` -> `## feature/tests-subfolder-classification...`
- `git rev-parse --short HEAD` -> `266bfa03`

### Pre-coding verification evidence

- Candidate file inspected (`tests/test_indicators_min.py`): inga `__file__`-referenser, ingen relativ fil-I/O eller cwd-beroende.
- `python -m pytest --collect-only -q tests/test_indicators_min.py` -> `2` tests collected.
- `rg -n "tests/test_indicators_min.py" docs --glob "!docs/archive/**" --glob "!docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt25_2026-03-10.md"` -> inga träffar (exit code `1`, expected for no matches).
- `tests/utils/test_indicators_min.py` saknas före flytt (ingen target-kollision).

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** (`Opus 4.6 Governance Reviewer`, BT25 pre-code review).
  - Scope/constraints/gates accepted som governance-kompatibla.
  - Required note: add explicit post-move discovery evidence (`pytest --collect-only` på target path).
- Post-move discovery evidence:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest --collect-only -q tests/utils/test_indicators_min.py` -> `2` tests collected.
- Gates: **PASS**
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pre_commit run --all-files` -> PASS
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check .` -> PASS
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_indicators_min.py` -> PASS (`2 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS (`1 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` -> PASS (`3 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS (`4 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> PASS (`4 passed`)
- Opus post-diff audit: **APPROVED** (`Opus 4.6 Governance Reviewer`, BT25 post-diff audit).
  - No mandatory remediation.
  - Note observed: attach gate terminal outputs as commit/PR evidence.

### Implementation Report (BT25)

- **Scope summary (IN):**
  - Relokerade `tests/test_indicators_min.py` -> `tests/utils/test_indicators_min.py` (path-only; testkod oförändrad).
  - Uppdaterade planrad i `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` med BT25.
  - Dokumenterade kontrakt + gate evidence i denna packet-fil.
- **Scope summary (OUT):**
  - Ingen ändring i `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`.
  - Ingen ytterligare testfil flyttad i BT25.
- **File-level changes:**
  - `tests/test_indicators_min.py` -> deleted (move source)
  - `tests/utils/test_indicators_min.py` -> added (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` -> BT25-rad tillagd
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt25_2026-03-10.md` -> packet + gate evidence
- **Gate outcomes:** samtliga listade gates PASS (se ovan).
- **Residual risk:** låg; begränsad till path-referensrisk, redan verifierad via docs-sökning + selectors.
- **READY_FOR_REVIEW evidence completeness:** komplett (mode/risk/path, scope IN/OUT, gates + selectors, Opus pre/post audit, artifacts).

### PR evidence template (BT25)

- **Mode/risk/path:** `RESEARCH` / `LOW` / `Full`
- **Scope IN/OUT:** Enligt packet (Scope-sektion)
- **Selectors + outcomes:**
  - determinism replay -> PASS (`tests/backtest/test_backtest_determinism_smoke.py`)
  - feature cache invariance -> PASS (`tests/test_features_asof_cache.py`, `tests/test_features_asof_cache_key_deterministic.py`)
  - pipeline invariant -> PASS (`tests/test_pipeline_fast_hash_guard.py`)
- **Smoke + lint outcomes:**
  - pre-commit -> PASS
  - ruff -> PASS
  - smoke import (`tests/test_import_smoke_backtest_optuna.py`) -> PASS
- **Artifacts:** BT25 packet + flyttdiff + planuppdatering + gate logs (terminal output)
