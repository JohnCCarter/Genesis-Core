# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: single-candidate test relocation av liten endpoint-smoke-test utan aktiva docs-referenser.
- **Required Path:** `Full`
- **Objective:** Relocate `test_health.py` to `tests/utils/` with no behavior change.
- **Candidate:** `tests/test_health.py -> tests/utils/test_health.py`
- **Base SHA:** `71e9036d`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (enbart testflytt + planrad/paket; ingen runtime/API/env/config-semantik ändras).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: single-candidate utility move, 0 non-archive docs refs for old path
- **Required Path:** `Full`
- **Objective:** Continue utils-category migration with low-friction candidate.
- **Candidate:** `test_health.py`
- **Base SHA:** `71e9036d`

### Scope

- **Scope IN:**
  - `tests/test_health.py` (move source)
  - `tests/utils/test_health.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (batch progress row)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt22_2026-03-10.md`
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
- `python -m pytest -q tests/utils/test_health.py`
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

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> **STOP/no_steps** (expected), non-zero exit (current implementation returns `3` for `no_steps`).
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> **STOP/no_steps** (expected), non-zero exit (current implementation returns `3` for `no_steps`).

### Branch/mode evidence (pre-coding)

- `git status -sb` -> `## feature/tests-subfolder-classification...`

### Pre-coding verification evidence

- Branch/mode verified via `git status -sb` on `feature/tests-subfolder-classification`.
- Path-reference check i `docs/**` gav inga träffar utanför denna packet-fil; inga ytterligare icke-arkiv-referenser kräver uppdatering i BT22.
- `rg -n "tests/test_health.py" docs --glob "!docs/archive/**" --glob "!docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt22_2026-03-10.md"` -> inga träffar (exit code `1`, expected for no matches).

### Review + verification evidence

- Opus pre-code review: **APPROVED** (`Opus 4.6 Governance Reviewer`, BT22 pre-code review).
  - Candidate validated as low-risk endpoint smoke test (`tests/test_health.py`).
  - Scope and RESEARCH selector-set accepted as compliant.
  - Note to complete all `_PENDING_` sections efter gates innan `READY_FOR_REVIEW`.
- Gates: **PASS**
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pre_commit run --all-files` -> PASS
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check .` -> PASS
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_health.py` -> PASS (`1 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS (`1 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` -> PASS (`3 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS (`4 passed`)
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> PASS (`4 passed`)
- Opus post-diff audit: **APPROVED_WITH_NOTES** (`Opus 4.6 Governance Reviewer`, BT22 post-diff audit).
  - Note addressed: gate evidence was run on pre-commit HEAD `71e9036d`; no HEAD change occurred before commit step.
  - No additional code remediation required.

### Implementation Report (BT22)

- **Scope summary (IN):**
  - Relokerade `tests/test_health.py` -> `tests/utils/test_health.py` (path-only; testkod oförändrad).
  - Uppdaterade planrad i `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` med BT22.
  - Dokumenterade kontrakt + gate evidence i denna packet-fil.
- **Scope summary (OUT):**
  - Ingen ändring i `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`.
  - Ingen ytterligare testfil flyttad i BT22.
- **File-level changes:**
  - `tests/test_health.py` -> deleted (move source)
  - `tests/utils/test_health.py` -> added (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` -> BT22-rad tillagd
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt22_2026-03-10.md` -> packet + gate evidence
- **Gate outcomes:** samtliga listade gates PASS (se ovan).
- **Residual risk:** låg; begränsad till path-referensrisk, redan verifierad via docs-sökning + selectors.
- **READY_FOR_REVIEW evidence completeness:** komplett (mode/risk/path, scope IN/OUT, gates + selectors, Opus pre/post audit, artifacts).

### PR evidence template (BT22)

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
- **Artifacts:** BT22 packet + flyttdiff + planuppdatering + gate logs (terminal output)
