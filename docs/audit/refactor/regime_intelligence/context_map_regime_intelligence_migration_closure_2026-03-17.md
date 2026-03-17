## Context Map

### Files to Modify

| File                                                                                                         | Purpose                                  | Changes Needed                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/strategy/evaluate.py`                                                                              | Runtime pipeline orchestrator            | Remove dependency on `core.strategy.regime_intelligence` and import canonical RI/config helpers directly while preserving local monkeypatch seams and runtime behavior |
| `src/core/strategy/decision_sizing.py`                                                                       | Runtime sizing path                      | Replace shim-based RI helper calls with direct canonical imports and preserve sizing/state semantics                                                                   |
| `src/core/intelligence/regime/__init__.py`                                                                   | Canonical RI export surface              | Export any newly canonical RI helper needed after shim retirement                                                                                                      |
| `src/core/intelligence/regime/risk_state.py`                                                                 | Canonical RI risk-state helper           | Host `compute_risk_state_multiplier` as a first-class intelligence-regime component instead of leaving it in the strategy compatibility shim                           |
| `src/core/strategy/regime_intelligence.py`                                                                   | Legacy compatibility shim                | Retire the shim after all production and test imports are redirected                                                                                                   |
| `tests/backtest/test_evaluate_pipeline.py`                                                                   | Runtime parity/invariant coverage        | Redirect monkeypatch/import usage away from the retired shim and preserve authority/shadow/no-drift assertions                                                         |
| `tests/backtest/test_evaluate_regime_precomputed_index.py`                                                   | Evaluate precomputed-index regression    | Redirect regime-module monkeypatch usage away from the retired shim                                                                                                    |
| `tests/core/intelligence/regime/test_clarity.py`                                                             | Clarity canonical contract               | Remove legacy-shim comparison and assert canonical payload contract directly                                                                                           |
| `tests/core/intelligence/regime/test_htf.py`                                                                 | HTF canonical contract                   | Remove legacy-shim comparison and assert canonical outcomes directly                                                                                                   |
| `tests/governance/test_authority_mode_resolver.py`                                                           | Authority precedence governance contract | Point parity checks at canonical resolver module instead of strategy shim                                                                                              |
| `tests/governance/test_phase2_merge_authority_bypass_contracts.py`                                           | Merge/authority governance contract      | Point authority-mode checks at canonical resolver module                                                                                                               |
| `tests/utils/test_risk_state_multiplier.py`                                                                  | Risk-state helper contract               | Move imports from strategy shim to canonical intelligence helper                                                                                                       |
| `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_migration_closure_2026-03-17.md`    | Scope map                                | Record exact closure scope                                                                                                                                             |
| `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_migration_closure_2026-03-17.md` | Commit contract                          | Record scope, gates, constraints, and stop conditions                                                                                                                  |

### Dependencies (may need updates)

| File                                                | Relationship                                                                                                             |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `src/core/config/authority_mode_resolver.py`        | Canonical authority-mode source already used indirectly by the shim and should become the direct runtime/test dependency |
| `src/core/intelligence/regime/authority.py`         | Canonical authority helpers already used by the shim and should remain the regime detection source of truth              |
| `src/core/intelligence/regime/clarity.py`           | Canonical clarity helper already used by the shim and should remain the clarity source of truth                          |
| `src/core/intelligence/regime/htf.py`               | Canonical HTF helper already used by the shim and should remain the HTF source of truth                                  |
| `src/core/strategy/regime.py`                       | Shadow observer source still used for observability-only regime sampling                                                 |
| `tests/backtest/test_backtest_determinism_smoke.py` | Determinism invariant must remain green after runtime import cutover                                                     |
| `tests/governance/test_pipeline_fast_hash_guard.py` | Pipeline order contract must remain unchanged                                                                            |

### Test Files

| Test                                                                                                       | Coverage                                                                        |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `tests/backtest/test_evaluate_pipeline.py`                                                                 | authority-mode parity, shadow observer invariants, clarity sizing-only behavior |
| `tests/backtest/test_evaluate_regime_precomputed_index.py`                                                 | precomputed EMA50 indexing and regime-module authority bypass regression        |
| `tests/core/intelligence/regime/test_clarity.py`                                                           | clarity deterministic contract and legacy-payload shape                         |
| `tests/core/intelligence/regime/test_htf.py`                                                               | HTF regime deterministic outcomes                                               |
| `tests/governance/test_authority_mode_resolver.py`                                                         | canonical/alias precedence and strict/permissive asymmetry                      |
| `tests/governance/test_phase2_merge_authority_bypass_contracts.py`                                         | authority precedence contract and merge bypass invariants                       |
| `tests/utils/test_risk_state_multiplier.py`                                                                | risk-state helper determinism and debug payload contract                        |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | runtime determinism replay invariant                                            |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant hash                                                         |

### Reference Patterns

| File                                         | Pattern                                                                                                              |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/regime/clarity.py`    | Canonical domain helper returning typed contract + `to_legacy_payload()` when needed                                 |
| `src/core/intelligence/regime/authority.py`  | Canonical no-IO regime authority helper boundary                                                                     |
| `src/core/config/authority_mode_resolver.py` | Canonical strict/permissive config resolution with exact precedence                                                  |
| `src/core/strategy/evaluate.py`              | Existing local wrapper seams used for monkeypatch-safe tests; should be preserved while switching underlying imports |

### Risk Assessment

- [x] Breaking changes to public API: medium risk because runtime imports and test imports still point at a soon-to-be-retired shim
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Hidden behavior risk: evaluate/decision sizing are runtime-sensitive and must preserve default legacy authority behavior while changing import ownership only
