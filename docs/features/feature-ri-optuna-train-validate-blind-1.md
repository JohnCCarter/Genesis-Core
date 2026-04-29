---
goal: Regime intelligence Optuna experiment with 2023-2024 development windows and blind 2025 evaluation
version: 1
date_created: 2026-03-18
last_updated: 2026-03-18
owner: fa06662
status: "Planned"
tags:
  - feature
  - intelligence
  - optuna
  - validation
  - blind
  - regime
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Define a deterministic experiment plan to test whether regime intelligence can improve the existing `tBTCUSD_3h` champion through Optuna-based parameter search on historical development windows, then evaluate the frozen candidate on a blind 2025 holdout. The plan preserves current champion defaults, uses canonical execution mode, and requires explicit separation between tuning data and blind evaluation data.

## 1. Requirements & Constraints

- **REQ-001**: The current `config/strategy/champions/tBTCUSD_3h.json` champion remains the control baseline and must not be modified during the experiment.
- **REQ-002**: Regime intelligence optimization must begin with the smallest search space that showed signal in prior ablation work: authority-related parameters first, then risk-state parameters.
- **REQ-002A**: Once an RI family baseline is established, default RI Optuna framing should keep the family-defining RI surface frozen and optimize adaptation/guardrail behavior first rather than reopening a broad legacy-like static parameter surface.
- **REQ-003**: The experiment must include three distinct data roles: training/tuning, validation/selection, and blind holdout.
- **REQ-004**: The blind 2025 holdout must not influence parameter ranges, candidate selection, or search-space edits.
- **REQ-005**: All runs used for comparison must use canonical mode (`GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`) and fixed seeds.
- **REQ-006**: Optuna preflight and optimizer-config validation must pass before any non-trivial trial campaign is started.
- **REQ-007**: Candidate promotion must be based on stable multi-window behavior, not single-window peak score.
- **REQ-008**: Result artifacts, best-trial JSON, and evaluation summaries must be stored under existing optimizer/result taxonomies rather than ad hoc root-level folders.
- **CON-001**: No live/default/champion behavior changes are allowed in this plan; this is an experiment design and evidence-generation slice only.
- **CON-002**: No use of blind 2025 outputs is allowed for post-hoc parameter retuning in the same campaign.
- **CON-003**: Existing Optuna storage DBs must not be reused when `resume=false`.
- **CON-004**: Existing optimizer config paths should remain stable when possible because resume signatures include repo-relative config paths.
- **CON-005**: RI campaigns should not be framed as broad mixed-surface searches that silently collapse RI into a legacy-like optimizer topology or as champion-overlay patch searches.
- **GUD-001**: Place new optimizer YAML files under `config/optimizer/3h/<campaign>/`.
- **GUD-002**: Keep search space intentionally narrow in Phase 1 to reduce overfitting and make attribution easier.
- **GUD-002A**: After the RI baseline exists, prefer bounded within-family slices in this order: adaptive policy / guardrails, regime-aware sizing, then small entry/exit cadence slices if attribution remains clear.
- **GUD-003**: Prefer deterministic walk-forward or staged validation over one-shot in-sample optimization.
- **PAT-001**: Reuse existing optimizer validation flow via `scripts/preflight/preflight_optuna_check.py` and `scripts/validate/validate_optimizer_config.py`.
- **PAT-002**: Preserve a control-vs-candidate comparison on identical windows before any blind claim is made.

### 1.1 RI optimizer framing after baseline freeze

After an RI family baseline has been demonstrated, the default research policy is:

1. keep the family-defining RI surface frozen by default (authority identity, RI threshold cluster, gating cadence, and baseline clarity stance)
2. optimize within-family adaptive behavior first (for example `risk_state`, drawdown/transition guards, or regime-aware sizing response)
3. allow broader entry/exit or cadence slices only as bounded, attribution-friendly follow-up slices after the frozen baseline exists

This framing is intended to stop RI research from drifting into a broad legacy-style parameter hunt. It does **not** claim that the repository currently enforces that distinction automatically in code; it is the governing experiment policy for RI campaign design.

## 2. Implementation Steps

### Implementation Phase 1

- **GOAL-001**: Define the exact windowing, campaign taxonomy, and search-space boundaries for the first regime-intelligence Optuna campaign.

| Task     | Description                                                                                                                                                           | Completed | Date |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-001 | Create a new campaign folder under `config/optimizer/3h/` for the regime-intelligence validation campaign, keeping naming stable and timeframe-first.                 |           |      |
| TASK-002 | Define three fixed windows: training `2023-01-01..2024-06-30`, validation `2024-07-01..2024-12-31`, and blind holdout `2025-01-01..2025-12-31`.                       |           |      |
| TASK-003 | Document candidate search-space scope for Phase 1 as authority-first, with optional risk-state additions, and explicitly exclude broad clarity exploration initially. |           |      |
| TASK-004 | Define deterministic campaign metadata: seed, canonical mode flags, storage naming, run-id naming, and output destinations.                                           |           |      |

### Implementation Phase 2

- **GOAL-002**: Add optimizer configuration files that support train, validation, and blind evaluation without mutating the champion baseline.

| Task     | Description                                                                                                                                                               | Completed | Date |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-005 | Add a training Optuna YAML under `config/optimizer/3h/<campaign>/` for `2023-01-01..2024-06-30` with narrow authority-focused search space and bounded trial/time budget. |           |      |
| TASK-006 | Add a validation evaluation YAML or documented replay path for `2024-07-01..2024-12-31` using frozen top candidates from the training run.                                |           |      |
| TASK-007 | Add a blind evaluation YAML or documented replay path for `2025-01-01..2025-12-31` that consumes the frozen selected candidate without search-space edits.                |           |      |
| TASK-008 | Ensure result and best-trial artifact homes follow existing optimizer conventions, including campaign-local `best_trials/` outputs where applicable.                      |           |      |

### Implementation Phase 3

- **GOAL-003**: Define selection criteria that reward robustness and guard against overfitting.

| Task     | Description                                                                                                                                    | Completed | Date |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-009 | Define candidate ranking rules that prioritize repository score first, then drawdown control, trade-count floor, and stability across windows. |           |      |
| TASK-010 | Define hard rejection rules for candidates with too few trades, excessive drawdown, or severe train/validation degradation.                    |           |      |
| TASK-011 | Decide whether to evaluate only the top-1 candidate or a short list of top-k candidates on validation before freezing the winner.              |           |      |
| TASK-012 | Document that blind 2025 is evaluation-only and may invalidate the candidate without permitting same-campaign retuning.                        |           |      |

### Implementation Phase 4

- **GOAL-004**: Run the campaign safely and deterministically with explicit preflight and validation gates.

| Task     | Description                                                                                                                      | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-013 | Run `scripts/preflight/preflight_optuna_check.py` against the training config before any long campaign.                          |           |      |
| TASK-014 | Run `scripts/validate/validate_optimizer_config.py` for each new optimizer YAML and require exit code `0`.                       |           |      |
| TASK-015 | Execute the training Optuna run in canonical mode with fixed seed and campaign-specific storage DB.                              |           |      |
| TASK-016 | Replay the selected candidate on the validation window and compare it directly against the existing champion on the same window. |           |      |
| TASK-017 | Freeze the selected candidate and run the blind 2025 evaluation without touching parameter ranges or search logic.               |           |      |

### Implementation Phase 5

- **GOAL-005**: Produce evidence that is promotion-ready without implying automatic rollout.

| Task     | Description                                                                                                                                                    | Completed | Date |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-018 | Write an experiment summary that includes control baseline, train winner, validation outcome, and blind 2025 outcome with artifact links.                      |           |      |
| TASK-019 | Record which intelligence parameters were explored, which were frozen, and why clarity remained excluded or included.                                          |           |      |
| TASK-020 | State explicitly whether the campaign outcome is `promising`, `inconclusive`, or `rejected` based on blind 2025 evidence.                                      |           |      |
| TASK-021 | If blind 2025 is positive, open a separate follow-up plan for any candidate promotion or broader multi-symbol validation rather than expanding scope in-place. |           |      |

## 3. Alternatives

- **ALT-001**: Optimize across all 2023-2024 data and select the single best result before running 2025 blind. Rejected as the primary plan because it lacks an internal validation layer and increases overfitting risk.
- **ALT-002**: Include clarity parameters from the first Optuna campaign. Rejected initially because earlier ablation did not show a clear positive contribution from clarity and would widen the search space prematurely.
- **ALT-003**: Skip Optuna and hand-tune the intelligence parameters. Rejected because it weakens reproducibility and makes attribution less rigorous.
- **ALT-004**: Use blind 2025 observations to immediately adjust ranges and rerun the same campaign. Rejected because it destroys the purpose of the blind holdout.

## 4. Dependencies

- **DEP-001**: Existing champion baseline at `config/strategy/champions/tBTCUSD_3h.json`
- **DEP-002**: Existing optimizer config taxonomy under `config/optimizer/3h/`
- **DEP-003**: Preflight script `scripts/preflight/preflight_optuna_check.py`
- **DEP-004**: Optimizer config validator `scripts/validate/validate_optimizer_config.py`
- **DEP-005**: Existing backtest/score path used by the optimizer and `scripts/run/run_backtest.py`
- **DEP-006**: Existing Optuna storage and best-trial artifact conventions described in `config/optimizer/README.md`

## 5. Files

- **FILE-001**: `docs/features/feature-ri-optuna-train-validate-blind-1.md` — this experiment plan
- **FILE-002**: `config/optimizer/3h/<campaign>/...` — planned train/validation/blind optimizer YAML files for the regime-intelligence campaign
- **FILE-003**: `config/optimizer/3h/<campaign>/best_trials/...` — planned best-trial JSON outputs
- **FILE-004**: `results/hparam_search/...` — planned run outputs and evaluation evidence
- **FILE-005**: `docs/analysis/...` or `docs/audit/...` — planned evidence summary after execution

## 6. Testing

- **TEST-001**: Preflight passes for the training config via `scripts/preflight/preflight_optuna_check.py`
- **TEST-002**: Validator passes for every new optimizer YAML via `scripts/validate/validate_optimizer_config.py`
- **TEST-003**: Training Optuna run completes in canonical mode with deterministic storage/config naming
- **TEST-004**: Selected candidate is replayed on validation and compared against the unchanged champion on the same window
- **TEST-005**: Blind 2025 replay is run only after candidate freeze and produces machine-readable summary artifacts
- **TEST-006**: Result comparisons confirm that all control/candidate evaluations used the same execution mode, symbol, timeframe, and score path

## 7. Risks & Assumptions

- **RISK-001**: Even a narrow authority/risk-state search space may overfit to `tBTCUSD_3h` if candidate selection overweights train score. Mitigation: require validation stability before freeze.
- **RISK-002**: A candidate may look strong on validation and fail on blind 2025. Mitigation: treat blind failure as a valid negative result, not a reason to relax the rules.
- **RISK-003**: Search-space sprawl will make attribution difficult and reduce confidence in any apparent improvement. Mitigation: keep clarity excluded in the first campaign unless prior evidence changes.
- **RISK-004**: Reusing optimizer DBs or changing config paths mid-campaign can corrupt resume assumptions or comparability. Mitigation: stable campaign naming and fresh storage when not resuming.
- **ASSUMPTION-001**: The current champion remains the correct control baseline for all comparison windows in this campaign.
- **ASSUMPTION-002**: Prior ablation evidence remains directionally valid: authority is the main candidate driver, with risk-state as a secondary candidate dimension.

## 8. Related Specifications / Further Reading

- `docs/features/feature-champion-shadow-intelligence-1.md`
- `docs/templates/skills/optuna_run_guardrails.md`
- `config/optimizer/README.md`
- `docs/optuna/optuna_performance_improvements.md`
- `config/strategy/champions/tBTCUSD_3h.json`
- `results/intelligence_shadow/tBTCUSD_3h_shadow_validation_20260318/shadow_summary.json`
