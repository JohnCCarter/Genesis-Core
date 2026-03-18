---
goal: Champion shadow intelligence integration for existing backtest champion
version: 1
date_created: 2026-03-18
last_updated: 2026-03-18
owner: fa06662
status: 'Planned'
tags:
	- feature
	- intelligence
	- backtest
	- shadow
	- champion
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement a minimal, deterministic, shadow-only integration that runs the new intelligence pipeline against the existing `tBTCUSD_3h` champion during backtest execution, emits research/intelligence artifacts, and proves that champion decision behavior remains unchanged.

## 1. Requirements & Constraints

- **REQ-001**: The integration must run against the existing `config/strategy/champions/tBTCUSD_3h.json` champion path without modifying champion files.
- **REQ-002**: Shadow mode must be explicitly opt-in through `scripts/run/run_backtest.py` CLI input.
- **REQ-003**: Shadow mode must execute `DeterministicResearchOrchestrator` and persist a machine-readable summary artifact.
- **REQ-004**: The slice must produce deterministic `IntelligenceEvent` inputs and a deterministic derived `ApprovedParameterSet` from the effective merged champion config.
- **REQ-005**: Shadow mode must not alter `action`, `size`, `reasons`, trades, or exit behavior.
- **CON-001**: `src/core/strategy/**`, `src/core/intelligence/**`, `src/core/research_orchestrator/**`, and `src/core/research_ledger/**` are out of scope.
- **CON-002**: No default-runtime, champion, or promotion semantics may be changed or implied.
- **CON-003**: Summary artifacts belong under `results/intelligence_shadow/<run_id>/`; shadow ledger artifacts belong under `artifacts/intelligence_shadow/<run_id>/research_ledger/`.
- **GUD-001**: Reuse `BacktestEngine.evaluation_hook` and existing run_backtest hook composition rather than introducing a new backtest seam.
- **GUD-002**: Keep the shadow adapter local to the backtest domain (`src/core/backtest/`) because the integration concern is backtest-specific, not a shared intelligence contract change.
- **PAT-001**: Follow the passive hook composition pattern already used by `_compose_decision_row_capture_hook` in `scripts/run/run_backtest.py`.
- **PAT-002**: Follow the deterministic orchestrator builder pattern used in `tests/helpers/research_system.py`.

## 2. Implementation Steps

### Implementation Phase 1

- **GOAL-001**: Define the shadow integration seam and artifact model without changing decision behavior.

| Task     | Description                                                                                                                                                                                                                                                   | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | Add opt-in CLI argument(s) to `scripts/run/run_backtest.py` for shadow summary output path and optional run id/prefix handling.                                                                                                                               |           |      |
| TASK-002 | Create `src/core/backtest/intelligence_shadow.py` with deterministic helpers to: capture per-bar shadow-safe events, derive a fingerprint-based advisory `ApprovedParameterSet`, build/run `DeterministicResearchOrchestrator`, and serialize summary output. |           |      |
| TASK-003 | Compose the new shadow hook in `scripts/run/run_backtest.py` alongside the existing decision-row hook so both can coexist without mutation or ordering drift.                                                                                                 |           |      |
| TASK-004 | Define explicit shadow failure policy in `run_backtest.py` (preferred: fail the command loudly only when shadow mode is explicitly requested; never silently mutate normal trade execution).                                                                  |           |      |

### Implementation Phase 2

- **GOAL-002**: Persist deterministic shadow artifacts with a clean separation between summary output and ledger storage.

| Task     | Description                                                                                                                                                                          | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ---- |
| TASK-005 | Persist summary JSON to `results/intelligence_shadow/<run_id>/shadow_summary.json` with counts, ids, advisory top set, run metadata, and a `decision_drift=false` attestation field. |           |      |
| TASK-006 | Persist shadow ledger records via existing service/storage under `artifacts/intelligence_shadow/<run_id>/research_ledger/` without modifying research ledger internals.              |           |      |
| TASK-007 | Ensure the derived approved parameter set is explicitly marked advisory-only in the summary payload and is based on the effective merged champion config fingerprint/checksum.       |           |      |

### Implementation Phase 3

- **GOAL-003**: Prove no decision drift and deterministic shadow output.

| Task     | Description                                                                                                                                                                                                 | Completed | Date |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-008 | Add `tests/backtest/test_run_backtest_intelligence_shadow.py` to compare control vs shadow-enabled runs and assert identical `action`, `size`, `reasons`, trades, and exit semantics.                       |           |      |
| TASK-009 | Add `tests/integration/test_backtest_champion_intelligence_shadow.py` to run the existing champion path with shadow enabled and assert deterministic summary counts, persisted ids, and artifact placement. |           |      |
| TASK-010 | Add or extend deterministic replay verification for the shadow-enabled backtest path using the same seed/window/mode configuration.                                                                         |           |      |

### Implementation Phase 4

- **GOAL-004**: Validate the slice under STRICT gates and document evidence.

| Task     | Description                                                                                                                                                                          | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ---- |
| TASK-011 | Run formatting/lint gates over touched backtest/tests/docs files.                                                                                                                    |           |      |
| TASK-012 | Run focused shadow tests plus existing `tests/research_orchestrator`, `tests/intelligence`, pipeline hash guard, feature-cache invariance, and backtest determinism smoke selectors. |           |      |
| TASK-013 | Produce an implementation report summarizing scope, artifact paths, parity proof, determinism proof, and residual risks.                                                             |           |      |

## 3. Alternatives

- **ALT-001**: Wire the new intelligence modules directly into `src/core/strategy/**` decision logic. Rejected because the user explicitly wants a shadow-only first step and this would exceed scope/risk on `master`.
- **ALT-002**: Modify shared intelligence/orchestrator contracts to accept backtest-native inputs directly. Rejected because the minimal slice can adapt to existing contracts locally in backtest space.
- **ALT-003**: Create a new top-level `plan/` folder for planning documents. Rejected because the repository layout policy discourages new root buckets when existing docs taxonomies are available.

## 4. Dependencies

- **DEP-001**: Existing `BacktestEngine.evaluation_hook` seam in `src/core/backtest/engine.py`
- **DEP-002**: Existing hook composition pattern in `scripts/run/run_backtest.py`
- **DEP-003**: Existing deterministic orchestrator stack from `core.research_orchestrator`
- **DEP-004**: Existing deterministic intelligence stage modules and contracts under `core.intelligence.*`
- **DEP-005**: Existing research ledger service/storage implementation for artifact persistence

## 5. Files

- **FILE-001**: `scripts/run/run_backtest.py` — CLI opt-in flag(s), hook composition, shadow artifact write path, failure policy
- **FILE-002**: `src/core/backtest/intelligence_shadow.py` — new local adapter module for shadow event capture and orchestrator execution
- **FILE-003**: `tests/backtest/test_run_backtest_intelligence_shadow.py` — control-vs-shadow parity proof
- **FILE-004**: `tests/integration/test_backtest_champion_intelligence_shadow.py` — champion shadow artifact integration proof
- **FILE-005**: `docs/audit/research_system/command_packet_backtest_champion_shadow_intelligence_v1_2026-03-18.md` — governance packet
- **FILE-006**: `docs/audit/research_system/context_map_backtest_champion_shadow_intelligence_v1_2026-03-18.md` — context map
- **FILE-007**: `docs/features/feature-champion-shadow-intelligence-1.md` — this plan

## 6. Testing

- **TEST-001**: `python -m pytest tests/backtest/test_run_backtest_intelligence_shadow.py -q`
- **TEST-002**: `python -m pytest tests/integration/test_backtest_champion_intelligence_shadow.py -q`
- **TEST-003**: `python -m pytest tests/research_orchestrator -q`
- **TEST-004**: `python -m pytest tests/intelligence -q`
- **TEST-005**: `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`
- **TEST-006**: `python -m pytest tests/utils/test_feature_cache.py -q`
- **TEST-007**: `python -m pytest tests/backtest/test_backtest_determinism_smoke.py -q`
- **TEST-008**: Determinism replay of the shadow-enabled backtest run on the fixed `tBTCUSD 3h 2024-01-02..2024-12-31` window with fixed seed and canonical mode flags

## 7. Risks & Assumptions

- **RISK-001**: The shadow hook could accidentally mutate `result`/`meta` and drift trade behavior. Mitigation: enforce parity tests and keep event capture write-only.
- **RISK-002**: The orchestrator may fail when collection is empty or persistence returns no ids. Mitigation: define explicit shadow failure policy and test both success and empty/failure paths.
- **RISK-003**: Derived approved parameter semantics could be misread as champion recommendation logic. Mitigation: mark it clearly as advisory-only and fingerprint-derived in the summary artifact.
- **ASSUMPTION-001**: Existing deterministic intelligence/orchestrator tests remain green and do not require core module changes.
- **ASSUMPTION-002**: A single derived approved parameter set is sufficient for the first shadow-only integration slice because recommendation ranking is observational only.

## 8. Related Specifications / Further Reading

- `docs/audit/research_system/context_map_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
- `docs/audit/research_system/command_packet_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
- `docs/intelligence/INTELLIGENCE_ARCHITECTURE.md`
- `tests/helpers/research_system.py`
- `tests/integration/test_orchestrator_flow.py`
