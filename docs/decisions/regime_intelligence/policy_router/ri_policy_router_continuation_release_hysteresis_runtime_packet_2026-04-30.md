# RI policy router continuation-release hysteresis runtime packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `implemented / validated / Opus post-diff APPROVED`

This packet is the first bounded runtime follow-up after the RI payoff-state translation packet.
It does **not** widen routing inputs, does **not** reopen Legacy, and does **not** introduce
payoff/outcome fields into runtime.

The slice extracts one explicit continuation-biased release dial from the existing RI router:

- `continuation_release_hysteresis`

The goal is to make the router's defensive-release asymmetry explicit and configurable on the
enabled path only, while preserving:

- default-off parity
- absent-vs-disabled parity
- existing enabled-path behavior when the new field is not materially used
- size-first defensive posture
- unchanged raw router classification logic

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice changes a high-sensitivity runtime strategy surface in `src/core/strategy/ri_policy_router.py` and adds one config-authority/schema field under `multi_timeframe.research_policy_router`, but keeps the default path unchanged and avoids widening into family, exit, or outcome-driven routing.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is now the cheapest admissible lane: the RI-vs-Legacy decision is frozen, the payoff-state note has already been translated into Genesis terms, and the smallest honest runtime step is one explicit enabled-only continuation-biased release control inside the existing RI-local router.
- **Objective:** add one enabled-only release-side hysteresis override so that `RI_defensive_transition_policy -> RI_continuation_policy` reversion can be made easier than defensive activation, without changing raw classifier inputs, no-trade floors, or any default/off behavior.
- **Candidate:** `continuation-biased defensive release hysteresis`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`
- **Opus post-diff audit:** `APPROVED`

## Why this is the smallest honest runtime slice

The current router already carries a meaningful continuation bias implicitly:

- defensive raw mandates top out at `2`
- continuation raw mandates can reach `3`
- the shared hysteresis check compares the incoming mandate against `previous_state.mandate_level + hysteresis`

That means defensive activation is already structurally harder than continuation retention on many
rows.

So the cheapest asymmetry that is both real and bounded is **not** to widen activation logic first.
It is to extract the **release side** into one explicit enabled-only dial:

- continuation release may use a separate hysteresis value from the shared switch hysteresis

This keeps the raw policy classifier unchanged and only changes the stability-control seam for one
specific transition direction:

- `RI_defensive_transition_policy -> RI_continuation_policy`

## Exact proposed config contract

Inside `multi_timeframe.research_policy_router`, add one optional enabled-path field:

- `continuation_release_hysteresis: int`

### Canonical behavior target

- when the router leaf is absent: no router leaf materializes
- when the router leaf is disabled: canonical dump remains equivalent to absent
- when the router leaf is enabled and `continuation_release_hysteresis` is omitted or equal to the shared `hysteresis`, canonical dump should preserve prior enabled-leaf semantics rather than forcing a materially different canonical shape
- when the router leaf is enabled and `continuation_release_hysteresis` differs from `hysteresis`, the canonical dump should retain that explicit difference

### Effective runtime semantics target

- shared `switch_threshold` remains unchanged in this slice
- shared `hysteresis` remains the activation/stability control for all transitions except one explicit release seam
- only when:
  - `previous_policy == RI_defensive_transition_policy`, and
  - `raw_target_policy == RI_continuation_policy`
    should the router use `continuation_release_hysteresis`
- all other transitions keep the current shared hysteresis path
- `RI_no_trade_policy` immediate handling remains unchanged
- raw classifier reason codes and policy labels remain unchanged

## Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- `Behavior may change only when continuation_release_hysteresis materially differs from shared hysteresis`
- `No change to raw router classification inputs`
- `No change to continuation / defensive / no-trade raw mandate construction`
- `No change to no-trade immediate path`
- `No change to aged-weak continuation guard`
- `No change to weak-pre-aged single-veto latch semantics`
- `No change to decision.py integration point`
- `No change to sizing ownership except existing size-first defensive multiplier path`
- `No exit-side rewrite`
- `No cross-family routing`
- `No payoff/outcome-derived runtime inputs`
- `No backtest runner / CLI widening`

## Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: typed bounded Python diff, focused tests, and required lint/security discipline.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: router behavior change must remain reason-code traceable and fail-closed on exact transition semantics.
- **Applied repo-local spec:** `config_authority_lifecycle_check`
  - reason: config-authority/schema widening must preserve canonical dump discipline and deterministic reject paths.

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_runtime_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/governance/test_config_ssot.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/strategy/family_registry.py`
  - `src/core/strategy/family_admission.py`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - `config/strategy/**`
  - `results/**`
  - `artifacts/**`
  - `tmp/**`
  - any new candidate bridge config
  - any Legacy implementation surface
  - any family/champion/promotion/readiness semantics
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_runtime_packet_2026-04-30.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/governance/test_config_ssot.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
- **Max files touched:** `10`

## Implemented shape

### Router

Inside `src/core/strategy/ri_policy_router.py`:

- extended router config normalization to accept one optional `continuation_release_hysteresis`
- kept the existing shared `switch_threshold`, `hysteresis`, and `min_dwell` semantics unchanged by default
- added one small internal control-resolution branch inside `_apply_stability_controls(...)` so that:
  - `POLICY_DEFENSIVE -> POLICY_CONTINUATION` uses `continuation_release_hysteresis`
  - all other transitions keep current shared hysteresis
- exposed the effective release-control choice in router debug so the enabled-path decision remains audit-friendly

### Schema / authority

Inside `src/core/config/schema.py`:

- added the field to `ResearchPolicyRouterConfig`
- preserved enabled-leaf backcompat by avoiding unnecessary canonical materialization when the new field does not materially differ from shared `hysteresis`

Inside `src/core/config/authority.py`:

- whitelisted the new field under `multi_timeframe.research_policy_router`
- kept all other whitelist semantics unchanged

### Tests

Added/updated focused tests for:

- raw router default behavior unchanged when the new field is omitted
- explicit enabled-path release behavior when `continuation_release_hysteresis=0`
- schema canonical dump backcompat when the field is absent/equal-to-shared
- authority whitelist persistence when the field is explicitly set
- absent vs disabled parity still holding with the widened leaf surface

## Implementation outcome

- `src/core/strategy/ri_policy_router.py` now normalizes `continuation_release_hysteresis`, resolves effective switch controls through `_resolve_switch_controls(...)`, and confines the override to the exact `POLICY_DEFENSIVE -> POLICY_CONTINUATION` release seam.
- enabled-path router debug now exposes `effective_switch_threshold`, `effective_hysteresis`, `switch_control_mode`, and the explicit `router_params.continuation_release_hysteresis` value for traceability.
- `src/core/config/schema.py` now adds the field while eliding canonical materialization when it is absent or equal to shared `hysteresis`.
- `src/core/config/authority.py` now admits the field without widening the rest of the router leaf.
- the targeted test surface now proves the blocked-default seam, explicit release override behavior, locality of the override, canonical backcompat, config persistence, and absent-vs-disabled parity.

## Proof obligations

- absent leaf == explicit disabled leaf canonical semantics still hold
- enabled leaf without explicit release override preserves prior canonical shape
- enabled router behavior is unchanged when `continuation_release_hysteresis` is absent or equal to shared `hysteresis`
- enabled router can release `POLICY_DEFENSIVE -> POLICY_CONTINUATION` on a mandate-2 continuation row after dwell when `continuation_release_hysteresis=0`
- same row remains blocked by hysteresis under the current shared value path
- no raw no-trade floor drift
- no aged-weak continuation drift
- no weak-pre-aged single-veto drift
- no default/off path drift

## Focused tests required

### Router + decision-path selectors

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_ri_policy_router.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision_scenario_behavior.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/integration/test_golden_trace_runtime_semantics.py`

### Config canonical / authority selectors

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_config_schema_backcompat.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_config_ssot.py::test_multi_timeframe_research_policy_router_whitelisted`

### Focused source gate

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check src/core/strategy/ri_policy_router.py src/core/config/schema.py src/core/config/authority.py tests/utils/test_ri_policy_router.py tests/utils/test_decision_scenario_behavior.py tests/governance/test_config_schema_backcompat.py tests/governance/test_config_ssot.py tests/integration/test_golden_trace_runtime_semantics.py`

### Required high-sensitivity gates

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/strategy -r src/core/config -c bandit.yaml`

## Verification outcome

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check src/core/strategy/ri_policy_router.py src/core/config/schema.py src/core/config/authority.py tests/utils/test_ri_policy_router.py tests/utils/test_decision_scenario_behavior.py tests/governance/test_config_schema_backcompat.py tests/governance/test_config_ssot.py tests/integration/test_golden_trace_runtime_semantics.py` -> `PASS`
- focused pytest cluster on the touched router / decision / config / golden files -> `PASS` (`89 passed`)
- required high-sensitivity selectors (`import smoke`, `backtest determinism smoke`, `feature cache`, `pipeline fast hash`) -> `PASS` (`17 passed`)
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/integration/test_config_api_e2e.py::test_runtime_endpoints_e2e_regime_unified_alias_bridge` -> `PASS` (`1 passed`)
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -c bandit.yaml -r src/core/strategy src/core/config` -> `PASS` (`No issues identified`)
- focused file diagnostics on the touched runtime/config/test files -> `PASS`

## Residual risk

- behavior change remains intentionally bounded to the enabled-only defensive-release seam; any further widening of activation-side semantics, no-trade handling, or decision integration requires a new packet
- Opus post-diff audit reported default-off / absent-vs-disabled parity preserved and no hidden behavior drift outside the intended enabled-path seam

## Stop Conditions

- any need to touch `decision.py`, `decision_gates.py`, or `decision_sizing.py`
- any need to widen activation-side classifier semantics in the same slice
- any need to alter no-trade immediate behavior
- any need to alter aged-weak continuation or weak-pre-aged single-veto semantics
- any need to add bridge configs, backtests, or candidate artifacts
- inability to preserve canonical backcompat when the new field is absent or equal to shared hysteresis
- inability to prove default/off parity after the config-authority widening

## Output required

- one bounded implementation diff rooted in `ri_policy_router.py` plus schema/authority support
- exact commands run and pass/fail outcomes
- proof that the new field is additive and enabled-only
- proof that release-side asymmetry is explicit without widening the router into payoff/outcome or cross-family surfaces
- residual-risk note if any remains
