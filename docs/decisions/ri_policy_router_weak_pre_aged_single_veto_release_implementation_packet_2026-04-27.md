# RI policy router weak pre-aged single-veto release implementation packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `pre-code reviewed / APPROVED_WITH_NOTES / implementation may proceed inside exact scope`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice changes enabled-only continuation-routing behavior inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, while keeping the default path unchanged and leaving seam-B / strong continuation semantics out of scope.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the split seam, negative fail-set result, cooldown-displacement diagnosis, and preserved single-veto candidate already exist, so the next unknown is whether one bounded enabled-only runtime change can remove repeated same-guard re-blocking without widening into broader continuation semantics.
- **Objective:** implement one enabled-only seam-A single-veto release guard in `src/core/strategy/ri_policy_router.py` that allows the weak pre-aged release guard to fire at most once per contiguous weak-continuation-below-strong pocket, preventing repeated same-guard no-trade chaining while leaving seam-B / strong continuation, cooldown semantics, generic switch controls, defensive routing, sizing, exits, config/env/schema/authority, and the default path unchanged.
- **Candidate:** `weak pre-aged single-veto release guard`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- review scope: one bounded seam-A runtime slice local to `src/core/strategy/ri_policy_router.py`
- review lock: implementation remains admissible only if it stays on the guard-specific, pocket-scoped latch contract below and does not widen into generic router-history semantics
- post-diff audit: `APPROVED_WITH_NOTES` — bounded enabled-only seam-A exception honored on the supplied diff/gates; same-pocket single-veto and raw-pocket-exit reset are focused-test-covered, while disabled/absent leaf reset remains out of scope for this slice

## Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: small typed Python diff with focused tests, linting, security scan, and full gates.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: this slice changes one verified continuation-release seam and must remain root-cause traceable through state/switch reasoning rather than blind threshold retuning.
- **Conditional repo-local spec:** `feature_parity_check`
  - reason: use only if validation unexpectedly drifts into feature-computation parity; not expected for the current seam.

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - the candidate is already preserved in repo-visible form,
  - the current blocker is no longer conceptual discovery but enabled-path runtime behavior inside the router-local seam,
  - that unknown cannot be resolved honestly without one explicit runtime experiment on the named seam-A path.
- **Default-path stance:** `unchanged`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

## Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- approved enabled-only exception: the seam-A weak pre-aged single-veto release guard may suppress at most one release within a contiguous weak-continuation-below-strong pocket; absent/disabled leaf path remains unchanged
- add at most one enabled-only, guard-specific pocket latch inside `src/core/strategy/ri_policy_router.py`
- that latch may record only whether this same seam-A weak pre-aged release guard has already fired within the current contiguous raw-decision pocket where the raw decision remains weak continuation below `stable_bars_strong`
- reset the latch whenever the raw decision exits that pocket or the path reaches strong continuation / stable continuation semantics
- disabled/absent router-leaf state propagation is not changed by this slice and is not part of the behavior-change exception here
- do not reinterpret generic router history or `previous_policy = RI_no_trade_policy`
- do not alter `stable_continuation_state`
- do not alter strong continuation branch ordering or semantics
- do not alter cooldown timing, cooldown expiry, or cooldown meaning
- do not alter generic switch controls
- do not alter defensive routing
- do not alter sizing
- do not alter exits
- no config/env/schema/authority changes
- stop if any new authority surface or seam-B logic becomes necessary

## Scope

- **Scope IN:**
  - `docs/decisions/ri_policy_router_weak_pre_aged_single_veto_release_implementation_packet_2026-04-27.md`
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
  - seam B / the `2023-12-24 21:00` strong continuation case as a change target
  - strong continuation behavior
  - cooldown behavior
  - defensive routing
  - sizing
  - exits
  - env/config/schema/cache semantics
  - champion/promotion/family-rule surfaces
- **Expected changed files:**
  - `docs/decisions/ri_policy_router_weak_pre_aged_single_veto_release_implementation_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- keep the direct runtime diff inside `src/core/strategy/ri_policy_router.py`
- extend the enabled-only router state with one private seam-A pocket latch only if needed for the single-veto contract
- define the latch as guard-specific and pocket-scoped, not as a general no-trade origin tracker
- allow `_should_block_weak_pre_aged_release(...)` to block only when:
  - previous selected policy is `RI_no_trade_policy`
  - the raw decision remains seam-A weak continuation (`raw_switch_reason = "continuation_state_supported"`, `mandate_level = 2`)
  - `bars_since_regime_change < stable_bars_strong`
  - the same seam-A guard has not already fired in the current contiguous pocket
- when the guard fires, persist the pocket latch as enabled-only router-local state
- when the immediately following weak-continuation bar remains in the same pocket, do not reapply the same guard; fall back to the existing weak-continuation path plus unchanged switch controls
- clear the latch when the raw decision exits the local pocket or reaches strong continuation / stable continuation semantics
- leave the aged weak continuation guard for `bars_since_regime_change >= 16` unchanged

## Proof obligations

- default path unchanged when router leaf is absent/disabled
- direct code deltas confined to one seam-A release de-chaining path in `ri_policy_router.py`
- the first weak pre-aged release from no-trade can still be blocked on the enabled path
- the same seam-A guard cannot recursively re-block the immediately following weak-continuation bar in the same local pocket
- strong continuation / seam-B remains governed by existing semantics, including the preserved `2023-12-24 21:00` strong-continuation anchor
- the aged weak continuation guard on `bars_since_regime_change >= 16` remains unchanged

## Tests required

- `tests/utils/test_ri_policy_router.py`
  - first block allowed on seam-A weak pre-aged release from no-trade
  - second same-pocket weak bar is not re-blocked by the same guard
  - aged weak continuation guard at `bars_since_regime_change >= 16` remains unchanged
- `tests/utils/test_decision_scenario_behavior.py`
  - enabled-path scenario proves first block + second same-pocket release behavior
  - preserved strong continuation scenario remains unchanged on the seam-B-like path corresponding to the `2023-12-24 21:00` anchor

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
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/strategy -c bandit.yaml`

## Stop Conditions

- any need to interpret generic router history instead of a guard-specific pocket latch
- any need to alter strong continuation or seam-B semantics as the primary mechanism
- any need to alter cooldown semantics or generic switch controls as the primary mechanism
- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics
- inability to express the contract using only the router-local seam-A signals plus one enabled-only, guard-specific pocket latch

## Output required

- bounded implementation diff in the single seam-A router runtime seam plus focused tests
- exact commands run and pass/fail outcomes
- residual-risk note about whether removing repeated re-blocking also bounds the displacement loop without reopening seam-B or cooldown semantics
