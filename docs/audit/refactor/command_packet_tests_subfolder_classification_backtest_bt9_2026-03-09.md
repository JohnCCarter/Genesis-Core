# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: docs-only harmonisering av historiska testvägar; ingen runtime-kod, ingen testlogik, ingen config/API-semantik.
- **Required Path:** `Full`
- **Objective:** Harmonize remaining historical RI T0–T8 contract references from `tests/test_backtest_determinism_smoke.py` to `tests/backtest/test_backtest_determinism_smoke.py`.
- **Candidate:** `docs-only historical path harmonization (T0..T8 contracts)`
- **Base SHA:** `6389f61e`
- **Category:** `docs`
- **Constraints:** `NO BEHAVIOR CHANGE` (endast docs-path-harmonisering + planstatus-uppdatering).
- **Done criteria:** Samtliga listade gates gröna + Implementation Report + PR evidence template.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: historical docs harmonization only
- **Required Path:** `Full`
- **Objective:** Update remaining T0–T8 RI contract references to the canonical backtest test path.
- **Candidate:** `T0..T8 docs references`
- **Base SHA:** `6389f61e`

### Scope

- **Scope IN:**
  - `docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T1_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T2_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T3_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T4_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T5_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T6_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T7_CONTRACT_2026-02-26.md`
  - `docs/ideas/REGIME_INTELLIGENCE_T8_CONTRACT_2026-02-26.md`
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_backtest_bt9_2026-03-09.md`
- **Scope OUT:**
  - `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `tests/**`
  - `.github/workflows/**`
  - Historical evidence transcripts outside listed T0–T8 contracts
  - Any additional test-file moves
- **Expected changed files:** 10-11
- **Max files touched:** 11

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
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

### Skill invocation evidence (planned)

- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run` -> expected `STOP/no_steps`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run` -> expected `STOP/no_steps`

### Review + verification evidence

- Branch/mode evidence: `git status -sb` -> `## feature/tests-subfolder-classification...`
- Opus pre-code review: **APPROVED_WITH_NOTES** (noter införda innan implementation)
- `python scripts/run_skill.py --skill repo_clean_refactor --manifest dev --dry-run`: **STOP/no_steps** (expected), exit code `1`
- `python scripts/run_skill.py --skill python_engineering --manifest dev --dry-run`: **STOP/no_steps** (expected), exit code `1`
- `python -m pre_commit run --all-files`: **PASS**
- `python -m ruff check .`: **PASS**
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`: **PASS**
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`: **PASS**
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`: **PASS**
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`: **PASS**

### Implementation Report (BT9)

- **Scope summary (IN):** T0..T8 RI contract docs, BT9 packet, och klassificeringsplanens harmoniseringsstatus.
- **Scope summary (OUT):** Inga ändringar i `src/**`, `tests/**`, `config/**`, `scripts/**` eller workflows.
- **File-level change summary:** 16 path-harmoniseringar i T0..T8 (`tests/test_backtest_determinism_smoke.py` -> `tests/backtest/test_backtest_determinism_smoke.py`) + 1 planstatus-uppdatering + 1 ny command packet.
- **Gates:** pre-commit, ruff, smoke, determinism, cache invariance, pipeline invariant: alla **PASS**.
- **Skill evidence:** `repo_clean_refactor` + `python_engineering` dry-run -> **STOP/no_steps** (förväntat policyutfall).
- **Residual risks:** Låg; begränsat till docs-spårbarhet (ingen runtime-beteendepåverkan).

### PR evidence template (BT9)

- **Mode/risk/path:** `RESEARCH` / `LOW` / `Full`
- **Scope IN/OUT:** Enligt packet (se Scope-sektion ovan)
- **Selectors + outcomes:** determinism/cache/pipeline -> **PASS**
- **Smoke + lint outcomes:** pre-commit/ruff/smoke -> **PASS**
- **Artifacts:** detta packet + diff i T0..T8 + planrad i `tests_subfolder_classification_plan_2026-03-09.md`
