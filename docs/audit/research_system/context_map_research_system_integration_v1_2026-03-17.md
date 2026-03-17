## Context Map

### Files to Modify

| File                                                           | Purpose                                   | Changes Needed                                                                                                                   |
| -------------------------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `tests/helpers/__init__.py`                                    | Test helper package marker                | Keep helper imports explicit for a single narrow deterministic research-system helper module                                     |
| `tests/helpers/research_system.py`                             | Shared deterministic integration fixtures | Provide only reusable event/task/orchestrator builders and stable temporary ledger setup for end-to-end verification             |
| `tests/integration/test_research_workflow_end_to_end.py`       | Full-stack workflow verification          | Verify a `ResearchTask` runs through orchestrator, intelligence pipeline, parameter analysis, ledger adapter, and ledger storage |
| `tests/integration/test_pipeline_determinism.py`               | Repeated-run determinism proof            | Verify identical task inputs produce identical stage outputs and persistence mappings on fresh storage                           |
| `tests/integration/test_parameter_intelligence_integration.py` | Parameter-analysis attachment proof       | Verify parameter recommendations are produced and attached correctly to `ResearchResult`                                         |
| `tests/integration/test_ledger_roundtrip.py`                   | Ledger readability and validation proof   | Verify persisted artifacts are readable through ledger storage/service and satisfy ledger validation rules                       |
| `tests/integration/test_orchestrator_flow.py`                  | Ordering and no-mutation proof            | Verify stable stage ordering, stable event ordering, and no mutation of upstream objects through full orchestration              |

### Dependencies (may need updates)

| File                                                   | Relationship                                                                                                            |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `src/core/research_orchestrator/__init__.py`           | Provides the canonical orchestrator entrypoint and result contracts to exercise end-to-end                              |
| `src/core/intelligence/collection/__init__.py`         | Provides deterministic collector request and implementation used in integration setup                                   |
| `src/core/intelligence/normalization/__init__.py`      | Provides deterministic normalizer used in integration setup                                                             |
| `src/core/intelligence/features/__init__.py`           | Provides deterministic feature extractor used in integration setup                                                      |
| `src/core/intelligence/evaluation/__init__.py`         | Provides deterministic evaluator used in integration setup                                                              |
| `src/core/intelligence/parameter/__init__.py`          | Provides deterministic parameter analyzer and approved-parameter-set contract                                           |
| `src/core/intelligence/ledger_adapter/__init__.py`     | Provides deterministic ledger adapter used for persistence verification                                                 |
| `src/core/research_ledger/storage.py`                  | Provides local file-backed test ledger storage for roundtrip verification                                               |
| `src/core/research_ledger/validators.py`               | Provides canonical ledger record validation used to prove persisted artifacts are valid                                 |
| `tests/research_orchestrator/test_workflow.py`         | Existing orchestrator slice tests provide reference patterns for deterministic orchestration and temporary ledger setup |
| `tests/intelligence/test_ledger_adapter_processing.py` | Existing persistence tests provide roundtrip and deterministic mapping reference patterns                               |

### Test Files

| Test                                                           | Coverage                                                   |
| -------------------------------------------------------------- | ---------------------------------------------------------- |
| `tests/integration/test_research_workflow_end_to_end.py`       | full pipeline execution and structured result output       |
| `tests/integration/test_pipeline_determinism.py`               | deterministic repeated execution with fresh storage        |
| `tests/integration/test_parameter_intelligence_integration.py` | parameter recommendation attachment and advisory ordering  |
| `tests/integration/test_ledger_roundtrip.py`                   | readable persisted artifact records and validation         |
| `tests/integration/test_orchestrator_flow.py`                  | stage ordering, event ordering, and no-mutation guarantees |
| `tests/research_orchestrator/test_workflow.py`                 | existing local orchestrator baseline                       |
| `tests/intelligence/test_pipeline_processing.py`               | existing stage-level deterministic baseline                |
| `tests/intelligence/test_parameter_intelligence.py`            | existing parameter-intelligence deterministic baseline     |
| `tests/intelligence/test_ledger_adapter_processing.py`         | existing ledger-adapter deterministic baseline             |

### Reference Patterns

| File                                                   | Pattern                                                                                      |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `tests/research_orchestrator/test_workflow.py`         | orchestrator fixture assembly, local recording wrappers, and temporary ledger service setup  |
| `tests/intelligence/test_ledger_adapter_processing.py` | roundtrip verification against temporary ledger storage                                      |
| `tests/intelligence/test_pipeline_processing.py`       | repeated-run determinism and no-mutation assertions across sequential stages                 |
| `src/core/research_orchestrator/workflow.py`           | canonical stage ordering that integration tests must verify without modifying implementation |

### Risk Assessment

- [x] Breaking changes to public API: medium risk only if a discovered integration defect tempts edits to stable core modules; avoid by keeping this slice test-only
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Hidden behavior risk: integration tests must verify coordination and persistence without adding new orchestrator capabilities, schedulers, or intelligence logic
