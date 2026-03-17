## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/intelligence-ledger-adapter-implementation-v1`)
- **Risk:** `MED` — why: runtime ledger adapter implementation touches ledger persistence boundaries but must preserve frozen intelligence contracts and avoid orchestration drift
- **Required Path:** `Full`
- **Objective:** Implement a deterministic `IntelligenceLedgerAdapter` that translates validated intelligence events into canonical Research Ledger records and returns `LedgerPersistenceResult` without changing shared contracts, orchestration, or database backends.
- **Candidate:** `feature/intelligence-ledger-adapter-implementation-v1`
- **Base SHA:** `26cc612858fc8aae33fc961bb7b8f17e7ce00981`

### Skill Usage

- **Repo-local skill:** `.github/skills/python_engineering.json`
  - Why applied: Python 3.11+ typed implementation slice with new deterministic runtime logic, focused tests, and required `ruff`/`pytest`/`bandit` gates.
- **Planning/context skills used for working method:**
  - `context-map`
  - `refactor-plan`

### Scope

- **Scope IN:**
  - `docs/audit/intelligence/context_map_intelligence_ledger_adapter_implementation_v1_2026-03-17.md`
  - `docs/audit/intelligence/command_packet_intelligence_ledger_adapter_implementation_v1_2026-03-17.md`
  - `src/core/intelligence/ledger_adapter/**`
  - `tests/intelligence/test_ledger_adapter_contracts.py`
  - `tests/intelligence/test_ledger_adapter_processing.py`
- **Scope OUT:**
  - `src/core/intelligence/events/**`
  - `src/core/intelligence/collection/**`
  - `src/core/intelligence/normalization/**`
  - `src/core/intelligence/features/**`
  - `src/core/intelligence/evaluation/**`
  - `src/core/research_ledger/**`
  - research orchestrator modules
  - shared contracts created in the preparation slice
  - scheduler logic, async execution, runtime automation, backend additions, or database model changes
- **Expected changed files:** `4-6`
- **Max files touched:** `6`

### Gates required

- `python -m black --check src/core/intelligence/ledger_adapter tests/intelligence docs/audit/intelligence`
- `python -m ruff check src/core/intelligence/ledger_adapter tests/intelligence`
- `python -m pytest tests/intelligence/test_ledger_adapter_contracts.py tests/intelligence/test_ledger_adapter_processing.py -q`
- `python -m pytest tests/core/research_ledger/test_service.py -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- Required focused evidence within/alongside tests:
  - request serialization integrity
  - tuple ordering preservation
  - deterministic persistence mapping on repeated runs
  - correct `LedgerPersistenceResult` output
  - no mutation of input objects

### Stop Conditions

- Any need to modify `src/core/intelligence/events/**`
- Any need to modify `src/core/intelligence/collection/**`
- Any need to modify `src/core/intelligence/normalization/**`
- Any need to modify `src/core/intelligence/features/**`
- Any need to modify `src/core/intelligence/evaluation/**`
- Any need to modify `src/core/research_ledger/**`
- Any need to change `LedgerPersistenceRequest` or `LedgerPersistenceResult`
- Any need to set `experiment_id` or other lineage references not present in the frozen adapter request contract
- Any need to add orchestration logic, scheduler behavior, async execution, hidden state, or new storage/backend semantics
- Any discovered contract gap that would require a local workaround instead of canonical imports

### Output required

- **Implementation Report**
- **PR evidence template**
- **Determinism evidence:** repeated identical mapping for identical validated event tuples with stable persisted event ordering and ledger entity ordering
- **Lineage note:** artifact persistence in this slice is intentionally `experiment_id=None`; experiment/hypothesis lineage linkage is deferred to a later approved contract or wiring slice
