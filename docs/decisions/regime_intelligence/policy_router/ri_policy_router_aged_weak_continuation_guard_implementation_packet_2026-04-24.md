# RI policy router aged weak continuation guard implementation packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical implementation packet / later aged-weak closeout chain parked / no active implementation authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This packet is not an active implementation authority on `feature/next-slice-2026-05-05`.
> - The later aged-weak closeout chain was re-anchored to a parked state in `docs/decisions/regime_intelligence/policy_router/ri_policy_router_reanchor_post_aged_weak_closeouts_2026-04-27.md`.
> - Preserve this file as historical packet context only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice changes enabled-only runtime route-admission behavior inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, while keeping default-path semantics unchanged and staying below family/champion authority.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the first candidate has already been preserved and pre-reviewed in docs, and the next honest step is one bounded runtime experiment on the exact weak-continuation admission seam.
- **Objective:** implement one enabled-only weak-continuation suppression guard that reduces aged late-entry continuation substitution without altering strong continuation, defensive routing, sizing, exits, cooldown semantics, switch controls, or authority surfaces.
- **Candidate:** `aged weak continuation guard`
- **Base SHA:** `HEAD`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- review scope: one bounded high-sensitivity runtime slice on the enabled-only weak-continuation admission seam
- review lock: implementation may proceed only if the packet keeps an explicit aged threshold, explicit existing strong predicate ordering, and no new authority surface

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - the candidate mechanism is already localized and preserved in repo-visible form,
  - the user explicitly asked to begin,
  - the next unknown is whether one exact enabled-only guard on weak continuation admission can improve the late-December substitution seam without collateral drift.
- **Default-path stance:** `unchanged`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

### Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- `One negative admission guard only`
- `Use existing age signal only: bars_since_regime_change`
- `Exact aged threshold: bars_since_regime_change >= 16.0`
- `Affect only weak continuation: raw_switch_reason="continuation_state_supported" / mandate_level=2`
- `Run only after existing strong continuation predicate continuation_points >= 6 has already failed`
- `Do not alter strong continuation`
- `Do not alter defensive routing`
- `Do not alter sizing`
- `Do not alter exits`
- `Do not alter cooldown semantics`
- `Do not alter switch controls`
- `No config/env/schema/authority changes`
- `Stop if any new authority surface becomes necessary`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: small typed Python diff with tests and full gates.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: this slice changes one decision-path admission seam and must remain root-cause traceable.
- **Conditional repo-local spec:** `feature_parity_check`
  - reason: only if validation drifts into feature-computation parity; not expected for the current seam.

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_continuation_guard_implementation_packet_2026-04-24.md`
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
  - strong continuation behavior
  - defensive routing behavior
  - route ordering
  - exits
  - sizing
  - cooldown behavior
  - env/config/schema/cache semantics
  - champion/promotion/family-rule surfaces
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_continuation_guard_implementation_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- introduce one local helper in `src/core/strategy/ri_policy_router.py` only if needed for readability
- evaluate the new guard only inside the weak continuation branch of `_raw_router_decision(...)`
- derive the age condition only from existing router semantics using `bars_since_regime_change >= 16.0`
- evaluate the guard only after the existing strong continuation predicate (`continuation_points >= 6`) has not been met and the weak branch (`raw_switch_reason = "continuation_state_supported"`, `mandate_level = 2`) is otherwise eligible
- reject aged weak continuation by returning `POLICY_NO_TRADE` with router-local reason `AGED_WEAK_CONTINUATION_GUARD`
- leave the strong continuation branch and all downstream stability/sizing semantics unchanged

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
- direct code deltas confined to one weak-continuation admission seam
- strong continuation remains allowed when stronger evidence is present
- aged weak continuation is suppressed on the enabled path
- enabled-path decision scenario shows router-local no-trade before sizing for the guarded weak-continuation case

## Stop Conditions

- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics
- any need to alter strong continuation or defensive routing
- inability to express the guard using only `bars_since_regime_change` plus the existing weak-continuation selector
- keep-set protection cannot be reasoned about from the resulting decision-row/test evidence

## Output required

- bounded implementation diff in the single router runtime seam plus focused tests
- exact commands run and pass/fail outcomes
- residual-risk note about why broader fail/keep/stress replay evidence still remains a separate follow-up
