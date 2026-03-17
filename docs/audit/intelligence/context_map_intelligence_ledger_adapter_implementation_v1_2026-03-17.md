## Context Map

### Files to Modify

| File                                                   | Purpose                                        | Changes Needed                                                                                                                                             |
| ------------------------------------------------------ | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/ledger_adapter/__init__.py`     | Public export surface for ledger adapter stage | Export deterministic adapter implementation and pure mapping helpers if added                                                                              |
| `src/core/intelligence/ledger_adapter/interface.py`    | Frozen ledger adapter contracts                | Consume existing `LedgerPersistenceRequest` / `LedgerPersistenceResult` unchanged                                                                          |
| `src/core/intelligence/ledger_adapter/processing.py`   | Runtime ledger adapter implementation          | Implement deterministic translation from validated intelligence events into Research Ledger records and append them via canonical ledger service           |
| `tests/intelligence/test_ledger_adapter_contracts.py`  | Existing contract-only coverage                | Keep as frozen contract baseline; extend only if package export compatibility needs narrow additions                                                       |
| `tests/intelligence/test_ledger_adapter_processing.py` | New ledger adapter slice tests                 | Verify request serialization integrity, tuple ordering preservation, deterministic persistence mapping, correct persistence result output, and no mutation |

### Dependencies (may need updates)

| File                                                 | Relationship                                                                                       |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `src/core/intelligence/events/models.py`             | Frozen canonical validated intelligence event shape consumed by the adapter                        |
| `src/core/research_ledger/models.py`                 | Provides `ArtifactRecord` and `IntelligenceRef` target structures for deterministic ledger mapping |
| `src/core/research_ledger/enums.py`                  | Provides `LedgerEntityType.ARTIFACT` and `ArtifactKind.INTELLIGENCE_OUTPUT`                        |
| `src/core/research_ledger/service.py`                | Provides canonical append boundary and deterministic `allocate_id` behavior                        |
| `src/core/research_ledger/storage.py`                | Provides stable file-backed ledger storage semantics used by the service                           |
| `docs/intelligence/INTELLIGENCE_PIPELINE_SPEC.md`    | Defines ledger adapter stage ownership and frozen scope boundaries                                 |
| `docs/intelligence/GOVERNANCE_INTELLIGENCE_RULES.md` | Defines no-contract-drift and no-local-workaround rules                                            |

### Test Files

| Test                                                                                                       | Coverage                                                                   |
| ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `tests/intelligence/test_ledger_adapter_contracts.py`                                                      | frozen request/result protocol contracts                                   |
| `tests/intelligence/test_ledger_adapter_processing.py`                                                     | deterministic adapter mapping, ordering, no mutation, stable result output |
| `tests/core/research_ledger/test_service.py`                                                               | canonical ledger service append semantics relied on by the adapter         |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant regression guard required by governance path            |

### Reference Patterns

| File                                                | Pattern                                                                                     |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `src/core/intelligence/collection/processing.py`    | deterministic stage implementation with frozen dataclass consumer and preserved input order |
| `src/core/intelligence/normalization/processing.py` | pure stage helper + thin runtime class wrapper                                              |
| `src/core/research_ledger/service.py`               | canonical append boundary for writing ledger records                                        |
| `tests/core/research_ledger/test_service.py`        | valid `ArtifactRecord` construction and service-backed append behavior                      |

### Risk Assessment

- [x] Breaking changes to public API: medium risk if shared contracts are modified; avoid by implementing beside frozen interface only
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Hidden behavior risk: using the wrong ledger record type or introducing orchestration/persistence semantics beyond direct adapter translation would violate scope
