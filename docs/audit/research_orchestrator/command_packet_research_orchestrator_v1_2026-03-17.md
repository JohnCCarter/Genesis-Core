## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/research-orchestrator-v1`)
- **Risk:** `MED` — why: new deterministic coordination slice spanning several stable intelligence components and ledger persistence boundaries, with strict prohibition on runtime/orchestration drift beyond explicit workflow coordination
- **Required Path:** `Full`
- **Objective:** Implement Research Orchestrator v1 as a deterministic coordination layer that accepts a research task, runs the merged intelligence pipeline, invokes Parameter Intelligence, persists validated intelligence artifacts through the ledger adapter, and returns a structured research result without modifying existing intelligence modules or ledger schema.
- **Candidate:** `feature/research-orchestrator-v1`
- **Base SHA:** `6520b85a7342a7b597fcf95ebf45300be66e7571`

### Scope

- **Scope IN:**
  - `docs/audit/research_orchestrator/context_map_research_orchestrator_v1_2026-03-17.md`
  - `docs/audit/research_orchestrator/command_packet_research_orchestrator_v1_2026-03-17.md`
  - `src/core/research_orchestrator/**`
  - `tests/research_orchestrator/**`
- **Scope OUT:**
  - `src/core/intelligence/events/**`
  - `src/core/intelligence/collection/**`
  - `src/core/intelligence/normalization/**`
  - `src/core/intelligence/features/**`
  - `src/core/intelligence/evaluation/**`
  - `src/core/intelligence/parameter/**`
  - `src/core/intelligence/ledger_adapter/**`
  - `src/core/research_ledger/**`
  - trading execution logic
  - strategy runtime/config-authority mutation
  - async schedulers, cron/job runners
  - database layers or schema changes
  - optimization logic and intelligence algorithms
- **Expected changed files:** `5-8`
- **Max files touched:** `8`

### Gates required

- `python -m black --check src/core/research_orchestrator tests/research_orchestrator docs/audit/research_orchestrator`
- `python -m ruff check src/core/research_orchestrator tests/research_orchestrator`
- `python -m bandit -r src/core/research_orchestrator -c bandit.yaml`
- `python -m pytest tests/research_orchestrator -q`
- `python -m pytest tests/intelligence -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- `python -m pytest tests/utils/test_feature_cache.py -q`
- Required focused evidence within/alongside tests:
  - deterministic orchestration for identical inputs
  - correct stage ordering
  - no mutation of upstream intelligence objects
  - correct persistence invocation
  - structured `ResearchResult` output

### Stop Conditions

- Any need to modify shared intelligence contracts
- Any need to modify Research Ledger schema or storage semantics
- Any need for direct `core.research_ledger` imports in `src/core/research_orchestrator/**`
- Any need to add runtime trading integration or config-authority writes
- Any need to add async execution, scheduling, cron, or job-runner behavior
- Any need to implement new intelligence algorithms, optimization logic, or database layers
- Any discovered contract gap that would require a silent local workaround

### Output required

- **Implementation Report**
- **PR evidence template**
- **Workflow summary:** collection -> normalization -> features -> evaluation -> parameter -> ledger adapter -> structured result
- **Boundary note:** no shared contracts modified; Research Ledger interaction is permitted only through the injected `IntelligenceLedgerAdapter` contract; no orchestrator/runtime/config-authority behavior beyond explicit deterministic coordination
- **Fail-fast note:** if upstream stage outputs violate canonical downstream contract requirements (for example empty evaluations for parameter analysis), the orchestrator must fail deterministically and surface the contract violation explicitly; it must not synthesize empty advisory or persistence success outputs
