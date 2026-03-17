## Context Map

### Files to Modify

| File                                                | Purpose                                       | Changes Needed                                                                  |
| --------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------- |
| `src/core/intelligence/collection/__init__.py`      | Public export surface for collection stage    | Export deterministic collection implementation if added                         |
| `src/core/intelligence/collection/interface.py`     | Collection request/result contracts           | Consume existing `CollectionRequest` and `CollectionResult` unchanged           |
| `src/core/intelligence/collection/processing.py`    | Deterministic collection stage                | Implement pure event collection ordering / tuple output from stage input        |
| `src/core/intelligence/normalization/__init__.py`   | Public export surface for normalization stage | Export deterministic normalizer implementation if added                         |
| `src/core/intelligence/normalization/interface.py`  | Normalization request/result contracts        | Consume existing `NormalizationRequest` and `NormalizationResult` unchanged     |
| `src/core/intelligence/normalization/processing.py` | Deterministic normalization stage             | Implement validation + canonical structure without mutating inputs              |
| `src/core/intelligence/features/__init__.py`        | Public export surface for feature stage       | Export deterministic feature extractor implementation if added                  |
| `src/core/intelligence/features/interface.py`       | Feature extraction contracts                  | Consume existing `IntelligenceFeatureSet` / request/result contracts unchanged  |
| `src/core/intelligence/features/processing.py`      | Deterministic feature stage                   | Derive stable feature sets from validated events                                |
| `src/core/intelligence/evaluation/__init__.py`      | Public export surface for evaluation stage    | Export deterministic evaluator implementation if added                          |
| `src/core/intelligence/evaluation/interface.py`     | Evaluation contracts                          | Consume existing evaluation request/result contracts unchanged                  |
| `src/core/intelligence/evaluation/processing.py`    | Deterministic evaluation stage                | Produce structured evaluation output with no persistence                        |
| `tests/intelligence/test_stage_contracts.py`        | Existing stage compatibility coverage         | Extend/adjust for implementation compatibility without breaking contract intent |
| `tests/intelligence/test_pipeline_processing.py`    | New processing slice tests                    | Verify determinism, ordering, stable output, and no-mutation guarantees         |

### Dependencies (may need updates)

| File                                                           | Relationship                                                                |
| -------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `src/core/intelligence/events/models.py`                       | Frozen canonical event schema consumed by collection/normalization/features |
| `src/core/intelligence/events/validators.py`                   | Canonical validation entrypoint for normalization stage                     |
| `docs/intelligence/INTELLIGENCE_PIPELINE_SPEC.md`              | Defines stage IO and determinism constraints                                |
| `docs/intelligence/GOVERNANCE_INTELLIGENCE_RULES.md`           | Defines forbidden areas and no-local-schema rule                            |
| `docs/intelligence/INTELLIGENCE_PARALLEL_DEVELOPMENT_RULES.md` | Parallel ownership and merge sequencing                                     |

### Test Files

| Test                                                                                                       | Coverage                                                                                    |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `tests/intelligence/test_stage_contracts.py`                                                               | tuple boundaries, frozen requests, ordering assumptions                                     |
| `tests/intelligence/test_event_schema.py`                                                                  | frozen event schema / validation behavior                                                   |
| `tests/intelligence/test_pipeline_processing.py`                                                           | deterministic stage implementations, ordering, identity/no-mutation, stable repeated output |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant regression guard                                                         |

### Reference Patterns

| File                                                        | Pattern                                                               |
| ----------------------------------------------------------- | --------------------------------------------------------------------- |
| `src/core/intelligence/events/models.py`                    | frozen dataclass contracts + deterministic serialization              |
| `src/core/intelligence/events/validators.py`                | pure validation wrapper returning validated event without mutation    |
| `tests/intelligence/test_stage_contracts.py`                | tuple-preserving stage boundary expectations                          |
| `docs/intelligence/INTELLIGENCE_PIPELINE_BRANCH_HANDOFF.md` | explicit handoff from prep/contracts branch to this processing branch |

### Risk Assessment

- [x] Breaking changes to public API: medium risk if interfaces are modified; avoid by implementing beside frozen contracts
- [ ] Database migrations needed
- [ ] Configuration changes required
- [x] Hidden behavior risk: adding orchestration/persistence would violate scope and must be avoided
