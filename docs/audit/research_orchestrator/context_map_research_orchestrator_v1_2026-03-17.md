## Context Map

### Files to Modify

| File                                             | Purpose                                      | Changes Needed                                                                                                                                 |
| ------------------------------------------------ | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/research_orchestrator/__init__.py`     | Public export surface for orchestrator slice | Export local orchestrator models, workflow entrypoint, and concrete orchestrator class                                                         |
| `src/core/research_orchestrator/models.py`       | Local request/result contracts               | Define frozen orchestrator request/result dataclasses without modifying shared intelligence contracts                                          |
| `src/core/research_orchestrator/workflow.py`     | Deterministic coordination flow              | Implement pure stage-by-stage orchestration across collection, normalization, features, evaluation, parameter analysis, and ledger persistence |
| `src/core/research_orchestrator/orchestrator.py` | Thin dependency-injected entrypoint          | Hold stable component dependencies and delegate execution to workflow logic                                                                    |
| `tests/research_orchestrator/test_workflow.py`   | Focused orchestrator verification            | Verify deterministic execution, stage ordering, no mutation, persistence invocation, and structured `ResearchResult` output                    |

### Dependencies (may need updates)

| File                                                 | Relationship                                                                                                                                                     |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/collection/interface.py`      | Provides canonical collection request/result contracts and collector protocol                                                                                    |
| `src/core/intelligence/normalization/interface.py`   | Provides canonical normalization request/result contracts and normalizer protocol                                                                                |
| `src/core/intelligence/features/interface.py`        | Provides canonical feature extraction request/result contracts and feature-set contracts                                                                         |
| `src/core/intelligence/evaluation/interface.py`      | Provides canonical evaluation request/result contracts consumed by parameter analysis                                                                            |
| `src/core/intelligence/parameter/interface.py`       | Provides canonical parameter analysis request/result contracts and approved-parameter-set contract                                                               |
| `src/core/intelligence/ledger_adapter/interface.py`  | Provides canonical persistence request/result contracts and adapter protocol                                                                                     |
| `src/core/research_ledger/__init__.py`               | Indirect dependency only through `core.intelligence.ledger_adapter`; the orchestrator slice must not import Research Ledger services, records, or enums directly |
| `docs/intelligence/INTELLIGENCE_ARCHITECTURE.md`     | Confirms intelligence modules are deterministic components with frozen boundaries                                                                                |
| `docs/intelligence/GOVERNANCE_INTELLIGENCE_RULES.md` | Confirms stop-on-gap behavior and no shared contract edits                                                                                                       |

### Test Files

| Test                                                                                                       | Coverage                                                                                              |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `tests/research_orchestrator/test_workflow.py`                                                             | local orchestrator determinism, stage ordering, no mutation, persistence invocation, and result shape |
| `tests/intelligence/test_pipeline_processing.py`                                                           | baseline deterministic stage behavior consumed by the orchestrator                                    |
| `tests/intelligence/test_parameter_intelligence.py`                                                        | baseline deterministic advisory parameter analysis consumed by the orchestrator                       |
| `tests/intelligence/test_ledger_adapter_processing.py`                                                     | baseline deterministic persistence mapping used by the orchestrator                                   |
| `tests/intelligence/test_stage_contracts.py`                                                               | shared contract freeze evidence across stage inputs/outputs                                           |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | narrow governance invariant selector                                                                  |

### Reference Patterns

| File                                                   | Pattern                                                                        |
| ------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `src/core/intelligence/evaluation/processing.py`       | deterministic pure processing function plus thin protocol-backed class wrapper |
| `src/core/intelligence/ledger_adapter/processing.py`   | injected dependency wrapper around explicit request/result coordination        |
| `tests/intelligence/test_pipeline_processing.py`       | repeated-run determinism and no-mutation verification style                    |
| `tests/intelligence/test_ledger_adapter_processing.py` | persistence invocation assertions with fresh ledger storage                    |

### Risk Assessment

- [x] Breaking changes to public API: medium risk if shared intelligence contracts or ledger schema are modified; avoid by keeping all contracts local to `src/core/research_orchestrator/**`
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Hidden behavior risk: orchestrator must remain a deterministic coordinator and must not become runtime execution, async scheduling, or optimization logic
