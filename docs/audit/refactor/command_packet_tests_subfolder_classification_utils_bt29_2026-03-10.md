# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification`)
- **Risk:** `LOW` — why: single-candidate utility-test relocation utan runtime- eller configpåverkan.
- **Required Path:** `Full`
- **Objective:** Relocate `test_indicators_rsi_adx.py` till `tests/utils/` med no-behavior-change.
- **Candidate:** `tests/test_indicators_rsi_adx.py -> tests/utils/test_indicators_rsi_adx.py`
- **Base SHA:** `ce4dea27`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (endast path-flytt av testfil + planrad + packet-evidence).
- **Done criteria:** Samtliga gates gröna + Opus pre/post godkännande + commit/push.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: isolated indikator-enhetstest utan path/cwd/IO-känslighet
- **Required Path:** `Full`
- **Objective:** Continue utils-category migration med låg-risk-kandidat.
- **Candidate:** `test_indicators_rsi_adx.py`
- **Base SHA:** `ce4dea27`

### Scope

- **Scope IN:**
  - `tests/test_indicators_rsi_adx.py` (move source)
  - `tests/utils/test_indicators_rsi_adx.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (BT29-rad)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt29_2026-03-10.md`
- **Scope OUT:**
  - `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`
  - övriga docs-filer utanför plan + denna packet
  - alla andra testflyttar
  - genererade cache/metadatafiler
- **Expected changed files:** 3-4
- **Max files touched:** 4

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/utils/test_indicators_rsi_adx.py`
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
- Selectors:
  - determinism replay: `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - feature cache invariance: `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
  - pipeline invariant: `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`

### Stop Conditions

- Scope drift utanför Scope IN
- Behavior change utan explicit undantag
- Determinism/cache/pipeline selector regression
- Forbidden/runtime-känsliga paths touched

### Output required

- **Implementation Report**
- **PR evidence template**

### Skill Usage

- `repo_clean_refactor` (repo-lokal SPEC-skill; invocation evidence i `logs/skill_runs.jsonl` med run_id `d7c98a85d7ba`, status `STOP/no_steps` som förväntat)

### Branch/mode evidence (pre-coding)

- `git rev-parse --short HEAD` -> `ce4dea27`

### Pre-coding verification evidence

- Candidate file inspected (`tests/test_indicators_rsi_adx.py`): inga `__file__`-referenser, ingen relativ fil-I/O eller cwd-beroende.
- `python -m pytest --collect-only -q tests/test_indicators_rsi_adx.py` -> `2` tests collected.
- Workspace path-reference check: inga externa träffar utanför BT29-packetet för `tests/test_indicators_rsi_adx.py`.
- `tests/utils/test_indicators_rsi_adx.py` saknas före flytt (ingen target-kollision).

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** (Opus 4.6 Governance Reviewer, 2026-03-10; inga blockerare, noter införda i packet)
- Gates: **PASS**
  - `python -m pre_commit run --all-files` -> PASS
  - `python -m ruff check .` -> PASS
  - `python -m pytest -q tests/utils/test_indicators_rsi_adx.py` -> PASS (`2 passed`)
  - `python -m pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS (`1 passed`)
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` -> PASS (`3 passed`)
  - `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS (`4 passed`)
  - `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> PASS (`4 passed`)
- Opus post-diff audit: **APPROVED_WITH_NOTES** (Opus 4.6 Governance Reviewer, 2026-03-10; notes införda, commit/push explicit tillåten)

### Implementation Report (BT29)

- **Scope summary (IN):**
  - Relokerade `tests/test_indicators_rsi_adx.py` -> `tests/utils/test_indicators_rsi_adx.py` (path-only, oförändrat testinnehåll).
  - Uppdaterade `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` med BT29-rad.
  - Dokumenterade kontrakt + pre/post audit + gate evidence i denna packet-fil.
- **Scope summary (OUT):**
  - Inga ändringar i `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`.
  - Ingen ytterligare testflytt utöver BT29-kandidaten.
- **File-level changes:**
  - `tests/test_indicators_rsi_adx.py` -> deleted (move source)
  - `tests/utils/test_indicators_rsi_adx.py` -> added (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` -> BT29-rad tillagd
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt29_2026-03-10.md` -> packet + evidence uppdaterad
- **Gate outcomes:** samtliga gates PASS (se ovan)
- **Residual risk:** låg; kvarvarande risk begränsad till path-referenser, hanterad via reference-check + selectors.
- **READY_FOR_REVIEW evidence completeness:** komplett (mode/risk/path, scope IN/OUT, gates + selectors, Opus pre/post, artifacts)

### PR evidence template (BT29)

- **Mode/risk/path:** `RESEARCH` / `LOW` / `Full`
- **Scope IN/OUT:** enligt packet Scope-sektion
- **Selectors + outcomes:**
  - determinism replay -> PASS (`tests/backtest/test_backtest_determinism_smoke.py`)
  - feature cache invariance -> PASS (`tests/test_features_asof_cache.py`, `tests/test_features_asof_cache_key_deterministic.py`)
  - pipeline invariant -> PASS (`tests/test_pipeline_fast_hash_guard.py`)
- **Smoke + lint outcomes:**
  - pre-commit -> PASS
  - ruff -> PASS
  - smoke import (`tests/test_import_smoke_backtest_optuna.py`) -> PASS
- **Artifacts:** BT29 packet + flyttdiff + planuppdatering + gate logs
