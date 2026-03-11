# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification-bt34`)
- **Risk:** `LOW` — why: single-candidate utility-test relocation utan runtime- eller configpåverkan.
- **Required Path:** `Full`
- **Objective:** Relocate `test_regime_filter.py` till `tests/utils/` med no-behavior-change.
- **Candidate:** `tests/test_regime_filter.py -> tests/utils/test_regime_filter.py`
- **Base SHA:** `7877ce46`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE` (endast path-flytt av testfil + planrad + packet-evidence).
- **Done criteria:** Samtliga gates gröna + Opus pre/post godkännande + commit/push.

## COMMAND PACKET (template alignment v1.1)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Risk:** `LOW` — why: isolated regime-filter utility-test utan path/cwd/IO-känslighet
- **Required Path:** `Full`
- **Objective:** Continue utils-category migration med låg-risk-kandidat.
- **Candidate:** `test_regime_filter.py`
- **Base SHA:** `7877ce46`

### Scope

- **Scope IN:**
  - `tests/test_regime_filter.py` (move source)
  - `tests/utils/test_regime_filter.py` (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` (BT34-rad)
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt34_2026-03-10.md`
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
- `python -m pytest -q tests/utils/test_regime_filter.py`
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

- `repo_clean_refactor` (repo-lokal SPEC-skill; tillämpad för scope/no-behavior-change-guardrails i pre-code review)

### Branch/mode evidence (pre-coding)

- `git rev-parse --short HEAD` -> `7877ce46`

### Pre-coding verification evidence

- Candidate file inspected (`tests/test_regime_filter.py`): inga `__file__`-referenser, ingen relativ fil-I/O eller cwd-beroende.
- `python -m pytest --collect-only -q tests/test_regime_filter.py` -> `12` tests collected.
- Repo-wide path-reference check: inga externa träffar utanför BT34-packetet för `tests/test_regime_filter.py`.
- `tests/utils/test_regime_filter.py` saknas före flytt (ingen target-kollision).

### Review + verification evidence

- Opus pre-code review: **APPROVED_WITH_NOTES** (Opus 4.6 Governance Reviewer, 2026-03-10; inga blockerare, noter införda i packet)
- Gates: **PASS**
  - `python -m pre_commit run --all-files` -> PASS
  - `python -m ruff check .` -> PASS
  - `python -m pytest -q tests/utils/test_regime_filter.py` -> PASS (`12 passed`)
  - `python -m pytest -q tests/test_import_smoke_backtest_optuna.py` -> PASS (`1 passed`)
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` -> PASS (`3 passed`)
  - `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py` -> PASS (`4 passed`)
  - `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> PASS (`4 passed`)
- Opus post-diff audit: **APPROVED_WITH_NOTES** (Opus 4.6 Governance Reviewer, 2026-03-10; note-fixar införda, commit/push tillåten)

### Implementation Report (BT34)

- **Scope summary (IN):**
  - Relokerade `tests/test_regime_filter.py` -> `tests/utils/test_regime_filter.py` (path-only, oförändrat testinnehåll).
  - Uppdaterade `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` med BT34-rad.
  - Dokumenterade kontrakt + pre/post audit + gate evidence i denna packet-fil.
- **Scope summary (OUT):**
  - Inga ändringar i `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`.
  - Ingen ytterligare testflytt utöver BT34-kandidaten.
- **File-level changes:**
  - `tests/test_regime_filter.py` -> deleted (move source)
  - `tests/utils/test_regime_filter.py` -> added (move target)
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` -> BT34-rad tillagd
  - `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt34_2026-03-10.md` -> packet + evidence uppdaterad
- **Gate outcomes:** samtliga gates PASS (se ovan)
- **Residual risk:** låg; kvarvarande risk begränsad till path-referenser, hanterad via repo-wide reference-check + selectors.
- **READY_FOR_REVIEW evidence completeness:** komplett (mode/risk/path, scope IN/OUT, gates + selectors, Opus pre/post, artifacts)

### PR evidence template (BT34)

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
- **Artifacts:** BT34 packet + flyttdiff + planuppdatering + gate logs
