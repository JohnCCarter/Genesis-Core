## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/research-system-integration-v1`)
- **Risk:** `MED` — why: multi-file deterministic integration-verification slice spanning orchestrator, intelligence pipeline, parameter analysis, ledger adapter, and ledger readability boundaries, with explicit prohibition on core-module drift
- **Required Path:** `Full`
- **Objective:** Implement the research-system integration verification layer as deterministic end-to-end and cross-stage tests proving that already merged modules operate together correctly without adding new intelligence logic or modifying stable core modules.
- **Candidate:** `feature/research-system-integration-v1`
- **Base SHA:** `c937bdb1cf0a22dbf1db6e51bf26e3643acc9fdb`

### Scope

- **Scope IN:**
  - `docs/audit/research_system/context_map_research_system_integration_v1_2026-03-17.md`
  - `docs/audit/research_system/command_packet_research_system_integration_v1_2026-03-17.md`
  - `tests/integration/test_research_workflow_end_to_end.py`
  - `tests/integration/test_pipeline_determinism.py`
  - `tests/integration/test_parameter_intelligence_integration.py`
  - `tests/integration/test_ledger_roundtrip.py`
  - `tests/integration/test_orchestrator_flow.py`
  - `tests/helpers/__init__.py`
  - `tests/helpers/research_system.py`
- **Scope OUT:**
  - `src/core/intelligence/events/**`
  - `src/core/intelligence/collection/**`
  - `src/core/intelligence/normalization/**`
  - `src/core/intelligence/features/**`
  - `src/core/intelligence/evaluation/**`
  - `src/core/intelligence/parameter/**`
  - `src/core/intelligence/ledger_adapter/**`
  - `src/core/research_orchestrator/**`
  - `src/core/research_ledger/**`
  - new intelligence algorithms
  - new parameter models
  - new orchestrator capabilities
  - scheduler logic
  - async execution
  - database layers
- **Expected changed files:** `7-9`
- **Max files touched:** `9`

### Gates required

- `python -m black --check tests/helpers tests/integration docs/audit/research_system`
- `python -m ruff check tests/helpers tests/integration`
- `python -m bandit -r tests/helpers tests/integration -c bandit.yaml`
- `python -m pytest tests/integration/test_research_workflow_end_to_end.py -q`
- `python -m pytest tests/integration/test_pipeline_determinism.py -q`
- `python -m pytest tests/integration/test_parameter_intelligence_integration.py -q`
- `python -m pytest tests/integration/test_ledger_roundtrip.py -q`
- `python -m pytest tests/integration/test_orchestrator_flow.py -q`
- `python -m pytest tests/research_orchestrator -q`
- `python -m pytest tests/intelligence -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- `python -m pytest tests/utils/test_feature_cache.py -q`
- Required focused evidence within/alongside tests:
  - full pipeline execution through orchestrator
  - deterministic repeated execution on fresh ledger storage with identical `ResearchResult`, `persisted_event_ids`, `ledger_entity_ids`, and roundtripped ledger records across separate temporary storage roots
  - artifact persistence through the ledger adapter
  - parameter recommendation output attachment
  - readable and valid ledger artifacts
  - no mutation of upstream objects
  - stable event ordering and stage ordering

### Stop Conditions

- Any need to modify shared contracts
- Any need to modify ledger schema or ledger storage semantics
- Any need to modify orchestrator contracts or stable intelligence module APIs
- Any need to add scheduler logic, async execution, or database layers
- Any discovered integration defect that requires patching core modules instead of test-only verification

### Output required

- **Implementation Report**
- **PR evidence template**
- **Workflow description:** ResearchTask -> Research Orchestrator -> Intelligence Pipeline -> Parameter Intelligence -> Ledger Adapter -> Research Ledger
- **Boundary note:** integration slice only; no core intelligence, orchestrator, or ledger modules modified unless a blocking defect is discovered and reported
