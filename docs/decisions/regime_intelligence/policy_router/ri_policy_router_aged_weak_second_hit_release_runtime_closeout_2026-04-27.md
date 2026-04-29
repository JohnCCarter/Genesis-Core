# RI policy router aged-weak second-hit release runtime closeout

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / negative runtime closeout / implementation reverted / no retained runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice records the bounded negative verdict for the aged-weak second-hit runtime packet on a high-sensitivity router seam without widening into a new behavior-changing packet.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the runtime attempt has already been falsified by focused feasibility checks, so the honest next step is to record the failure mechanism, retain no code, and hand off only if a new packet explicitly reopens stability semantics.
- **Objective:** close the aged-weak second-hit release runtime slice honestly after feasibility failure under unchanged stability controls.
- **Candidate:** `aged-weak second-hit release`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_second_hit_release_runtime_packet_2026-04-27.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_second_hit_release_candidate_packet_2026-04-27.md`
- `results/backtests/ri_policy_router_aged_weak_residual_probe_20260427/aged_weak_residual_rows.json`
- `src/core/strategy/ri_policy_router.py`
- `tests/utils/test_ri_policy_router.py`
- `tests/utils/test_decision_scenario_behavior.py`

## Skill Usage

Skills applied in this slice and its closeout handling:

- `decision_gate_debug` — used for the row-set lock, focused feasibility framing, and falsification reasoning
- `python_engineering` — used for the bounded prototype/revert cycle plus focused tests and final gate handling

## Verdict

The aged-weak second-hit runtime slice is **negative** on feasibility.

The packet locked this behavior-change exception:

- first aged-weak guard hit in a bounded pocket still blocks
- only the repeated second-hit row in that same pocket may fall through to the existing continuation classifier plus existing stability controls unchanged
- direct helper-hit target rows were limited to:
  - `2023-12-28T09:00:00+00:00`
  - `2023-12-30T21:00:00+00:00`

Focused router and scenario tests falsified that shape.

## Failure mechanism

The failure is not that the prototype could not identify the aged-weak second-hit pocket. The failure is that, on the exact locked residual rows, the unchanged downstream stability path still keeps the router in `RI_no_trade_policy`.

Mechanism:

- the first same-pocket aged-weak row leaves the router in `previous_policy = RI_no_trade_policy`
- on the attempted second-hit release row, the raw router decision can be made to fall through from `AGED_WEAK_CONTINUATION_GUARD` into the continuation classifier
- but the unchanged `_apply_stability_controls(...)` logic still sees a switch away from `RI_no_trade_policy` while `previous_state.dwell_duration = 1`
- so the router resolves `switch_blocked_by_min_dwell` and retains `RI_no_trade_policy`

Therefore the packet's exact target rows cannot become direct release rows without widening the governed surface from "router-local aged-weak reconsideration" into explicit stability/min-dwell semantics.

## Retained runtime proof

The reverted final tree keeps **no** aged-weak second-hit runtime mechanism in active code.

Repo-visible proof on the final tree:

- `src/core/strategy/ri_policy_router.py` contains no `aged_weak_second_hit_release_latch` symbol
- `src/core/strategy/ri_policy_router.py` contains no `aged_weak_second_hit_release_applied` symbol
- retained router-local enabled-path additions in that file are limited to the already-validated seam-A single-veto latch and the bars-7 continuation-persistence reconsideration path

## Consequence

The experimental aged-weak code and tests were reverted.

Nothing from this slice remains in active runtime code.

This closeout does **not** authorize reopening:

- generic aged-threshold retuning
- low-zone families
- seam-A single-veto semantics
- strong-continuation / seam-B semantics
- generic stability-control weakening

## Gate summary

- focused router tests on the first implementation attempt: **failed**
- focused decision-scenario tests on the first implementation attempt: **failed**
- retained runtime code after revert: **none**
- post-revert `get_errors` on router/tests/docs/working contract: **passed**
- post-revert focused router tests (`tests/utils/test_ri_policy_router.py`): **passed**
- post-revert focused decision scenario tests (`tests/utils/test_decision_scenario_behavior.py`): **passed**
- post-revert required selectors:
  - `tests/governance/test_import_smoke_backtest_optuna.py`: **passed**
  - `tests/backtest/test_backtest_determinism_smoke.py`: **passed**
  - `tests/utils/test_feature_cache.py`: **passed**
  - `tests/utils/diffing/test_feature_cache.py`: **passed**
  - `tests/governance/test_pipeline_fast_hash_guard.py`: **passed**
- `pre-commit run --all-files`: **passed**
- `ruff check .`: **passed**
- `bandit -r src/core/strategy -c bandit.yaml`: **passed**

## Next admissible move

If this seam is reopened at all, it must be under a fresh packet that says so explicitly:

- either prove a still-cheaper router-local shape that does **not** rely on changing stability/min-dwell semantics,
- or reopen governance review for a separate aged-weak-plus-stability interaction question.

Until then, the aged-weak second-hit runtime slice remains closed negative and the bars-7 implementation remains the last retained positive slice in this chain.
