## Context Map

### Files to Modify

| File                                                | Purpose                                          | Changes Needed                                                                                                                       |
| --------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `src/core/intelligence/parameter/__init__.py`       | Public export surface for parameter intelligence | Export local parameter contracts and deterministic analyzer implementation                                                           |
| `src/core/intelligence/parameter/interface.py`      | Parameter-intelligence-local contracts           | Define frozen advisory request/result dataclasses and protocol without changing shared intelligence contracts                        |
| `src/core/intelligence/parameter/processing.py`     | Deterministic parameter analysis                 | Implement advisory-only ranking, stability/sensitivity/consistency synthesis, weighting suggestions, and risk-multiplier suggestions |
| `tests/intelligence/test_parameter_intelligence.py` | Focused parameter-intelligence verification      | Verify deterministic output, stable ranking, no mutation, advisory-only semantics, serialization shape, and invalid-input rejection  |

### Dependencies (may need updates)

| File                                                 | Relationship                                                                                                           |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/evaluation/interface.py`      | Provides canonical `IntelligenceEvaluation` inputs consumed by parameter intelligence                                  |
| `src/core/intelligence/__init__.py`                  | Describes intelligence as deterministic, thin-adapter friendly domain package                                          |
| `src/core/intelligence/events/models.py`             | Provides canonical JSON-friendly `JsonObject` alias reused for advisory parameter payloads and audit-friendly metadata |
| `src/core/ml/decision_matrix.py`                     | Reference pattern for deterministic weighted ranking and stable ordering semantics                                     |
| `docs/intelligence/INTELLIGENCE_ARCHITECTURE.md`     | Confirms existing intelligence module layout and no-orchestrator constraints                                           |
| `docs/intelligence/GOVERNANCE_INTELLIGENCE_RULES.md` | Governs contract boundaries, determinism, and stop-on-gap behavior                                                     |

### Test Files

| Test                                                                                                       | Coverage                                                                                                      |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `tests/intelligence/test_parameter_intelligence.py`                                                        | local parameter-intelligence outputs, advisory boundaries, determinism, serialization, and rejection behavior |
| `tests/intelligence/test_stage_contracts.py`                                                               | baseline frozen upstream contract expectations that parameter intelligence must consume without modification  |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | narrow governance invariant requested by branch workflow                                                      |

### Reference Patterns

| File                                                 | Pattern                                                                                            |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/evaluation/processing.py`     | deterministic scoring helper + thin protocol implementation wrapper                                |
| `src/core/intelligence/ledger_adapter/processing.py` | local deterministic intelligence runtime module with injected, explicit inputs and no hidden state |
| `src/core/ml/decision_matrix.py`                     | deterministic weighted ranking and stable sorted output                                            |
| `tests/intelligence/test_pipeline_processing.py`     | no-mutation and repeated-run determinism test style for intelligence modules                       |

### Risk Assessment

- [x] Breaking changes to public API: medium risk if shared intelligence contracts are altered; avoid by defining local parameter contracts only under `src/core/intelligence/parameter/**`
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Hidden behavior risk: crossing from advisory analysis into runtime mutation/orchestration would violate scope and must be blocked
