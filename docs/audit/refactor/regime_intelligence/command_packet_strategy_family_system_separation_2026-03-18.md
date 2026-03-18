# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit user override
- **Risk:** `HIGH` — why: config authority/validation semantics, family separation, promotion guard semantics
- **Required Path:** `Full`
- **Objective:** Implement Strategy Families as a structural separation layer so Regime Intelligence is treated as a separate strategy family rather than as an overlay/modification of the incumbent champion.
- **Candidate:** `strategy-family structural separation`
- **Base SHA:** `feature/ri-optuna-train-validate-blind-v1`

## Scope

- **Scope IN:**
  - canonical registry surface:
    - `src/core/strategy/family_registry.py`
    - `src/core/strategy/families.py` as temporary zero-logic import-compat shim only, if retained
  - runtime authority/config validation surfaces:
    - `src/core/config/schema.py`
    - `src/core/config/authority.py`
    - `config/runtime.json`
    - `config/runtime.seed.json`
  - optimizer validation surface:
    - `scripts/validate/validate_optimizer_config.py`
  - research family persistence/adoption surfaces:
    - `src/core/research_ledger/service.py`
    - `src/core/intelligence/ledger_adapter/processing.py`
    - `src/core/research_orchestrator/families.py`
    - `src/core/research_orchestrator/__init__.py`
    - `src/core/backtest/intelligence_shadow.py`
  - active authority config files that must carry explicit `strategy_family` in this slice:
    - `config/strategy/champions/tBTCUSD_1h.json`
    - `config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped.json`
    - `config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped_relaxed_size.json`
    - `config/strategy/champions/tBTCUSD_3h.json`
    - `config/strategy/champions/tTEST_1h.json`
    - `config/optimizer/1h/tBTCUSD_1h_coarse_grid.yaml`
    - `config/optimizer/1h/tBTCUSD_1h_risk_optuna_smoke.yaml`
    - `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_phaseA.yaml`
    - `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_phaseB.yaml`
    - `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_phaseB_seeded.yaml`
    - `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_phaseC_seeded_oos.yaml`
    - `config/optimizer/3h/tBTCUSD_3h_explore_validate_2024_2025.yaml`
    - `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseA.yaml`
    - `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseB.yaml`
    - `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseC.yaml`
    - `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseD.yaml`
    - `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseE_oos.yaml`
    - `config/optimizer/3h/ri_train_validate_blind_v1/tBTCUSD_3h_ri_train_validate_2023_2024_v1.yaml`
    - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml`
    - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml`
    - `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseA.yaml`
    - `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_debug_baseline.yaml`
  - focused tests directly covering registry/config/optimizer/ledger/orchestrator family behavior
- **Scope OUT:**
  - regime logic
  - probability model
  - intelligence core dataclass/protocol contracts
  - silent family merge / overlay migration behavior
  - `archive/**`
  - `config/strategy/champions/backup/**`
  - `config/tmp/**`
  - `tmp/**`
  - generated result payloads / best-trial artifacts / Optuna DBs
- **Expected changed files:**
  - `src/core/strategy/family_registry.py`
  - optional zero-logic shim `src/core/strategy/families.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `config/runtime.json`
  - `config/runtime.seed.json`
  - `scripts/validate/validate_optimizer_config.py`
  - `src/core/research_ledger/service.py`
  - `src/core/intelligence/ledger_adapter/processing.py`
  - `src/core/research_orchestrator/families.py`
  - `src/core/research_orchestrator/__init__.py`
  - `src/core/backtest/intelligence_shadow.py`
  - active config files listed above
  - exports/tests/docs directly required for the above
- **Max files touched:** `32`

## Required implementation notes

- `src/core/strategy/family_registry.py` is the only canonical SSOT for strategy-family definitions and rules.
- If `src/core/strategy/families.py` remains temporarily, it must be a zero-logic re-export shim only.
- `strategy_family` becomes mandatory on active runtime/champion/optimizer authority configs in this slice.
- No derived fallback is allowed on runtime-facing validation paths after migration.
- RI-authority + RI-cluster mismatch is a hard error, not silent legacy fallback.
- Research integration must be binary, not cosmetic:
  - either adopt actual non-test callsites into family-aware flows,
  - or prove/document/test a strict single-family invariant for any retained plain callsite.
- Ledger persistence must store `strategy_family` on the effective default persistence path, not only via an optional helper.
- No dataclass/API contract changes to:
  - `ResearchTask`
  - `ResearchResult`
  - `ParameterAnalysisRequest`
  - `ParameterRecommendation`
- Family separation must be implemented via:
  - central registry
  - config validation/classification
  - ledger metadata tagging
  - outer scheduling/default within-family orchestration behavior

## Gates required

- `pre-commit run --all-files`
- focused pytest selectors for registry/runtime/optimizer/ledger/orchestrator behavior
- runtime authority/config smoke covering validate/get/propose paths
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## Stop Conditions

- Scope drift beyond classification/system-separation
- Any regime/probability behavior change
- Contract drift in research/intelligence dataclasses or protocols
- Hidden hybrid configs being silently classified as legacy
- Mandatory-family migration breaks runtime authority bootstrap/load/validate/propose flows

## Output required

- **Implementation Report**
- **PR evidence template**
