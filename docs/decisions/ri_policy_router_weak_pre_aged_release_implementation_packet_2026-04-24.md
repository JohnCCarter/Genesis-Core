# RI policy router weak pre-aged release implementation packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code reviewed / APPROVED_WITH_NOTES / implementation may proceed inside exact scope`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice changes enabled-only continuation-routing behavior inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, while keeping default-path semantics unchanged and leaving strong continuation semantics out of scope.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the split seam has already been verified, the seam-A candidate is preserved, and Opus has now confirmed that one bounded continuation-local runtime slice is admissible if it stays confined to the weak-release seam.
- **Objective:** implement one enabled-only weak pre-aged continuation release guard that blocks release from prior router-local no-trade into weak continuation before sufficient regime maturity, without changing strong continuation, defensive routing, generic switch controls, sizing, exits, or authority surfaces.
- **Candidate:** `weak pre-aged continuation release guard`
- **Base SHA:** `HEAD`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- review scope: one bounded seam-A runtime slice local to `src/core/strategy/ri_policy_router.py`
- review lock: implementation remains admissible only if it stays on the weak continuation release seam and does not alter strong continuation semantics, shared switch-control behavior, or the meaning/value of `stable_bars_strong`

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - the seam split is already documented and the cheapest seam-A candidate is now frozen in repo-visible form,
  - the next unknown is whether one bounded weak-release guard can remove the `2023-12-22 15:00` row without widening into seam B / strong continuation,
  - that unknown cannot be resolved honestly without one explicit runtime experiment on the named router-local branch.
- **Default-path stance:** `unchanged`
- **Required packet / review:**
  - Opus pre-code review already recorded for this exact seam-A direction
  - Opus post-diff audit required after any implementation

### Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- `Affect only seam A: weak continuation release from prior router-local no-trade`
- `Use only router-local signals already present in ri_policy_router.py`
- `Do not change the value or meaning of stable_bars_strong`
- `Do not alter stable_continuation_state`
- `Do not alter strong continuation branch logic`
- `Do not alter generic switch controls`
- `Do not alter defensive routing`
- `Do not alter sizing`
- `Do not alter exits`
- `Do not alter cooldown semantics`
- `No config/env/schema/authority changes`
- `Stop if any new authority surface or seam-B logic becomes necessary`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: small typed Python diff with bounded focused tests and full gates.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: this slice changes one verified continuation-release seam and must remain root-cause traceable through replay/timestamp evidence.
- **Conditional repo-local spec:** `feature_parity_check`
  - reason: only if validation drifts into feature computation parity; not expected for the current seam.

### Scope

- **Scope IN:**
  - `docs/decisions/ri_policy_router_weak_pre_aged_release_implementation_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/strategy/family_registry.py`
  - `src/core/strategy/family_admission.py`
  - `src/core/config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - `config/**`
  - `results/**`
  - seam B / the `2023-12-24 21:00` strong continuation case
  - strong continuation behavior
  - defensive routing behavior
  - route ordering
  - exits
  - sizing
  - cooldown behavior
  - env/config/schema/cache semantics
  - champion/promotion/family-rule surfaces
- **Expected changed files:**
  - `docs/decisions/ri_policy_router_weak_pre_aged_release_implementation_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- keep all changes inside `src/core/strategy/ri_policy_router.py`
- add at most one private helper if needed for readability
- pin the exact target as the release path where:
  - previous router-local policy is `RI_no_trade_policy`
  - the new raw decision would otherwise be weak continuation (`raw_switch_reason = "continuation_state_supported"`, `mandate_level = 2`)
  - `bars_since_regime_change` is still below the existing stronger stability boundary (`stable_bars_strong = 8`)
- evaluate that guard only on the seam-A release path; do not reuse it as a generic continuation veto
- retain router-local no-trade on that path with a dedicated router-local reason
- leave the strong continuation branch and generic switch-control semantics untouched

## Gates required

### Pre-change and post-change source checks

- `pre-commit run --all-files`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check .`

### Focused router/runtime tests

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_ri_policy_router.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision_scenario_behavior.py`

### Required high-sensitivity gates

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`

## Proof obligations

- default path unchanged when router leaf is absent/disabled
- direct code deltas confined to one weak continuation release seam in `ri_policy_router.py`
- `2023-12-22 15:00` is the intended target seam and is covered by replay/timestamp proof
- `2023-12-24 21:00` remains governed by the existing strong continuation semantics and is not reclassified by the seam-A change
- rows previously hit by the old `AGED_WEAK_CONTINUATION_GUARD` on `2023-12-28 06:00` and `2023-12-30 18:00` are included in replay proof so any new cascade is disclosed honestly
- no change to the meaning/value of `stable_bars_strong`, mandate semantics, or shared switch-control ordering

## Stop Conditions

- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics
- any need to alter strong continuation or generic switch controls as the primary mechanism
- inability to express the guard using only router-local seam-A signals already present in `ri_policy_router.py`
- seam-A proof requires claiming that the candidate also solves seam B

## Output required

- bounded implementation diff in the seam-A router release path plus focused tests
- exact commands run and pass/fail outcomes
- residual-risk note about why seam B remains a separate question even if seam A improves
