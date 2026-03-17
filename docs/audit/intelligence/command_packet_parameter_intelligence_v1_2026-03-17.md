## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping (`feature/parameter-intelligence-v1`)
- **Risk:** `MED` — why: new deterministic intelligence analysis module with advisory ranking logic and narrow contract surface, but strict prohibition on orchestrator/runtime drift
- **Required Path:** `Full`
- **Objective:** Implement Parameter Intelligence v1 as a local intelligence module that consumes existing evaluation outputs plus approved parameter-set snapshots and produces deterministic, serializable, advisory-only analysis results without modifying shared contracts or runtime behavior.
- **Candidate:** `feature/parameter-intelligence-v1`
- **Base SHA:** `0d0036d8136d1c69c101fb5ecf12a0ed9815c79a`

### Skill Usage

- **Repo-local skill:** `.github/skills/python_engineering.json`
  - Why applied: Python 3.11+ typed feature slice with new deterministic logic, focused tests, and required `ruff` / `pytest` / `bandit` gates.
- **Planning/context skills used for working method:**
  - `context-map`
  - `refactor-plan`
  - `create-implementation-plan`

### Scope

- **Scope IN:**
  - `docs/audit/intelligence/context_map_parameter_intelligence_v1_2026-03-17.md`
  - `docs/audit/intelligence/command_packet_parameter_intelligence_v1_2026-03-17.md`
  - `src/core/intelligence/parameter/**`
  - `tests/intelligence/test_parameter_intelligence.py`
- **Scope OUT:**
  - `src/core/intelligence/events/**`
  - `src/core/intelligence/collection/**`
  - `src/core/intelligence/normalization/**`
  - `src/core/intelligence/features/**`
  - `src/core/intelligence/evaluation/**`
  - `src/core/intelligence/ledger_adapter/**`
  - `src/core/research_ledger/**`
  - research orchestrator modules
  - shared prep/contracts files outside the new parameter module
  - runtime strategy mutation, scheduler logic, async execution, database additions, config-authority writes
- **Expected changed files:** `4-6`
- **Max files touched:** `6`

### Gates required

- `python -m black --check src/core/intelligence/parameter tests/intelligence docs/audit/intelligence`
- `python -m ruff check src/core/intelligence/parameter tests/intelligence`
- `python -m bandit -r src/core/intelligence/parameter -c bandit.yaml`
- `python -m pytest tests/intelligence/test_parameter_intelligence.py -q`
- `python -m pytest tests/intelligence/test_stage_contracts.py -q`
- `python -m pytest tests/intelligence -q`
- `python -m pytest tests/utils/test_feature_cache.py -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- Required focused evidence within/alongside tests:
  - deterministic output for identical inputs
  - stable ranking/order under ties
  - no mutation of input tuples or payloads
  - advisory-only outputs
  - JSON-serializable structured result shape
  - rejection of incomplete or invalid parameter-set inputs

### Stop Conditions

- Any need to modify shared intelligence contracts outside `src/core/intelligence/parameter/**`
- Any need to modify `src/core/intelligence/events/**`
- Any need to modify `src/core/intelligence/collection/**`
- Any need to modify `src/core/intelligence/normalization/**`
- Any need to modify `src/core/intelligence/features/**`
- Any need to modify `src/core/intelligence/evaluation/**`
- Any need to modify `src/core/intelligence/ledger_adapter/**`
- Any need to modify `src/core/research_ledger/**`
- Any need to modify `src/core/intelligence/__init__.py`
- Any need to add orchestrator behavior, execution control, scheduling, async execution, or runtime strategy mutation
- Any need to auto-create or auto-apply parameter changes beyond advisory outputs
- Any need to depend on non-finite numerics, implicit dict ordering, time/random/uuid/env-derived behavior, or file/network IO
- Any discovered contract gap that would require a silent local workaround

### Output required

- **Implementation Report**
- **PR evidence template**
- **Advisory note:** outputs must remain research/advisory only and must not directly mutate runtime strategy or configuration
- **Determinism evidence:** repeated identical advisory results and stable tie-breaking for identical inputs
