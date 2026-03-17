## COMMAND PACKET

- **Mode:** `RESEARCH` — source: explicit user mode + target branch mapping (`feature/intelligence-pipeline-processing-v1`)
- **Risk:** `MED` — why: multi-file deterministic processing implementation inside new intelligence stage modules with strict frozen-contract boundaries
- **Required Path:** `Full`
- **Objective:** Implement deterministic processing stages for collection, normalization, features, and evaluation using existing canonical intelligence contracts without adding orchestration, persistence, async execution, or schema changes.
- **Candidate:** `feature/intelligence-pipeline-processing-v1`
- **Base SHA:** `26cc6128`

### Scope

- **Scope IN:**
  - `docs/audit/intelligence/context_map_intelligence_pipeline_processing_v1_2026-03-17.md`
  - `docs/audit/intelligence/command_packet_intelligence_pipeline_processing_v1_2026-03-17.md`
  - `src/core/intelligence/collection/**`
  - `src/core/intelligence/normalization/**`
  - `src/core/intelligence/features/**`
  - `src/core/intelligence/evaluation/**`
  - `tests/intelligence/**`
- **Scope OUT:**
  - `src/core/intelligence/events/**`
  - `src/core/intelligence/ledger_adapter/**`
  - `src/core/research_ledger/**`
  - research orchestrator modules
  - shared contracts defined in the preparation slice
  - async execution, schedulers, runtime automation, database logic, persistence, orchestration wiring
- **Expected changed files:** 10-14
- **Max files touched:** 14

### Gates required

- `python -m black --check src/core/intelligence tests/intelligence`
- `python -m ruff check src/core/intelligence tests/intelligence`
- `python -m pytest tests/intelligence -q`
- Required focused selectors within/alongside test run:
  - stage determinism
  - ordering preservation
  - identity / no-mutation guarantees
  - stable identical output for identical input
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Any need to modify `src/core/intelligence/events/**`
- Any need to modify `src/core/intelligence/ledger_adapter/**`
- Any need to modify `src/core/research_ledger/**`
- Any need to introduce orchestration, scheduler behavior, async execution, database logic, or persistence
- Any need to change timestamp/window semantics in shared contracts or rely on lexicographic timestamp comparison; collection window filtering must remain timezone-aware and inclusive using local stage logic only
- Any discovered contract gap that would require inventing a local schema or changing shared contracts
- Any runtime wiring outside allowed stage modules

### Output required

- **Implementation Report**
- **PR evidence template**
- **Determinism evidence:** show repeated identical outputs for identical tuple inputs across all four stages
