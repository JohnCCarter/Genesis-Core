---
goal: Normalize 6h optimizer workflow to the 3h phased protocol with a deterministic debug pre-phase
version: 1
date_created: 2026-03-16
last_updated: 2026-03-16
owner: GitHub Copilot
status: 'In progress'
tags:
	- feature
	- optimizer
	- '6h'
	- phased
	- research
---

# Introduction

![Status: In progress](https://img.shields.io/badge/status-In%20progress-yellow)

This plan defines a deterministic, traceable 6h optimizer workflow that matches the 3h phased protocol at the methodology level while allowing timeframe-specific parameter ranges. The 6h path adds an explicit debug pre-phase because current evidence indicates that 6h does not yet have a trustworthy canonical baseline.

## 1. Requirements & Constraints

- **REQ-001**: 6h must follow the same phase protocol as the 3h reference workflow at the methodology level.
- **REQ-002**: Parameter ranges may differ from 1h and 3h when justified by timeframe behavior.
- **REQ-003**: All phases must be deterministic and reproducible with fixed seeds, fixed sample windows, and tracked study/storage names.
- **REQ-004**: Each downstream phase must pin the verified winner from the prior phase.
- **REQ-005**: 6h RI experimentation must not begin until a baseline-worthy non-RI phase exists.
- **CON-001**: Default constraint is NO BEHAVIOR CHANGE outside explicitly selected research configs.
- **CON-002**: Changes must remain additive under `config/optimizer/6h/phased_v1/` and related docs/plan files.
- **CON-003**: The current validator dependency on `config/strategy/champions/tBTCUSD_6h.json` blocks canonical validation and must be worked around or explicitly documented for 6h research runs.
- **GUD-001**: Use the 3h phased flow as the methodological template, not as a requirement for identical parameter values.
- **PAT-001**: Preserve the canonical chain `best trial -> pinned config -> next phase`.

## 2. Implementation Steps

### Implementation Phase 1

- GOAL-001: Establish the normalized 6h phase taxonomy and naming.

| Task     | Description                                                                                                      | Completed | Date       |
| -------- | ---------------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-001 | Define `6h Phase A0` as a deterministic debug pre-phase under `config/optimizer/6h/phased_v1/` with RI disabled. | ✅        | 2026-03-16 |
| TASK-002 | Preserve `6h Phase A` as the first canonical non-RI baseline phase intended for later Phase B derivation.        | ✅        | 2026-03-16 |
| TASK-003 | Define `6h Phase B` as RI-only tuning that pins all non-RI values from the verified 6h Phase A winner.           |           |            |
| TASK-004 | Define `6h Phase C` as OOS validation of the 6h Phase B winner.                                                  |           |            |

### Implementation Phase 2

- GOAL-002: Produce the minimum config set required for a full 6h phased chain.

| Task     | Description                                                                                                                                                                                         | Completed | Date       |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---------- |
| TASK-005 | Keep `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_debug_baseline.yaml` as the current `Phase A0` candidate and, if needed, rename or annotate it to match the taxonomy.                      | ✅        | 2026-03-16 |
| TASK-006 | Validate whether `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseA.yaml` is good enough to remain the canonical `Phase A`; otherwise replace it with a successor derived from A0 evidence. |           |            |
| TASK-007 | Create `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseB.yaml` only after TASK-006 is satisfied.                                                                                           |           |            |
| TASK-008 | Create `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseC.yaml` from the verified Phase B winner.                                                                                           |           |            |

### Implementation Phase 3

- GOAL-003: Generate evidence to decide whether 6h is promotable to the full phased workflow.

| Task     | Description                                                                                                      | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-009 | Run isolated 6h debug experiments to test threshold, exit, hold-horizon, and risk hypotheses under A0.           |           |      |
| TASK-010 | Compare 6h trade behavior against 1h and 3h using trade count, PF, DD, win rate, hold time, and regime behavior. |           |      |
| TASK-011 | Decide whether 6h has a baseline worthy of becoming canonical Phase A.                                           |           |      |
| TASK-012 | If 6h remains structurally weak, document that Phase B/C are blocked pending deeper signal/model investigation.  |           |      |

## 3. Alternatives

- **ALT-001**: Force 6h directly into `Phase A -> Phase B -> Phase C` with no debug pre-phase. Rejected because it risks generating deterministic but analytically weak results on top of an untrusted baseline.
- **ALT-002**: Reuse 1h or 3h parameter ranges verbatim for 6h. Rejected because methodological symmetry does not require identical ranges, and 6h evidence already shows materially different behavior.
- **ALT-003**: Skip phased normalization and run ad hoc 6h experiments. Rejected because it weakens traceability and cross-timeframe comparability.

## 4. Dependencies

- **DEP-001**: `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseA.yaml` as the methodological reference.
- **DEP-002**: `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_phaseA.yaml` and `...phaseB.yaml` as current timeframe-first campaign references.
- **DEP-003**: `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseA.yaml` and `...debug_baseline.yaml` as current 6h research artifacts.
- **DEP-004**: Local 6h data artifacts and the legacy frozen path required by the runner.
- **DEP-005**: Documented validator limitation caused by missing `config/strategy/champions/tBTCUSD_6h.json`.

## 5. Files

- **FILE-001**: `config/optimizer/6h/PHASED_NORMALIZATION_PLAN.md` — implementation plan for normalized 6h phase workflow.
- **FILE-002**: `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_debug_baseline.yaml` — current A0/debug candidate.
- **FILE-003**: `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseA.yaml` — current canonical 6h baseline candidate.
- **FILE-004**: `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseB.yaml` — future RI-only phase.
- **FILE-005**: `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseC.yaml` — future OOS validation phase.

## 6. Testing

- **TEST-001**: Deterministic smoke runs for `Phase A0` and `Phase A` with fixed seeds and fixed sample windows.
- **TEST-002**: Compare 6h debug variants using consistent metrics and study naming.
- **TEST-003**: Run the existing deterministic/governance guard selectors used for optimizer/backtest changes when touching runtime-relevant config paths.
- **TEST-004**: For future 6h Phase B/C, verify that non-RI values are pinned exactly from the prior winning phase.

## 7. Risks & Assumptions

- **RISK-001**: 6h may remain structurally weak even after a normalized phased workflow, making Phase B/C low-value.
- **RISK-002**: Missing 6h champion config may continue to complicate canonical validation flows.
- **RISK-003**: Comparing timeframes without distinguishing methodology from parameter values may lead to false conclusions.
- **ASSUMPTION-001**: The 3h phased protocol is the correct methodological template for cross-timeframe comparability.
- **ASSUMPTION-002**: 6h should be allowed a debug pre-phase without violating the repository’s determinism and governance goals.

## 8. Related Specifications / Further Reading

- `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseA.yaml`
- `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_phaseA.yaml`
- `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_phaseB.yaml`
- `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_phaseA.yaml`
- `config/optimizer/6h/phased_v1/tBTCUSD_6h_phased_v1_debug_baseline.yaml`
- `archive/curated/2025-11-03/docs/THRESHOLD_OPTIMIZATION_RESULTS.md`
- `docs/optimization/optimizer.md`
