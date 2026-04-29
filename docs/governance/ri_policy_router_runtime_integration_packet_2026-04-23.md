# RI policy router runtime integration packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code reviewed / APPROVED_WITH_NOTES / implementation may proceed inside exact scope`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice changes the runtime decision path in `src/core/strategy/decision.py` and config-authority/canonical semantics in `src/core/config/{schema,authority}.py`, but keeps behavior explicitly default-off and below family/champion authority.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: concept/replay/candidate-preservation slices already exist, and the user explicitly reopened the bounded runtime version of RI-local policy switching.
- **Objective:** introduce one bounded default-off RI policy router that selects continuation / defensive / no-trade postures from decision-time state, persists dwell/hysteresis return state, and integrates into `decision.py` without touching strict-only family-rule surfaces.
- **Candidate:** `research-only RI policy router integration`
- **Base SHA:** `c151eaafa38cc5b18497dd68b7607288de9509f0`

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/ri_policy_router.py`
  - `src/core/strategy/decision.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - replay/diagnostics already proved the non-runtime shape,
  - bounded transition-aware candidate formation already exists,
  - user intent now explicitly asks for the runtime switching model to be completed,
  - the smallest honest runtime step is a default-off RI-local router below family/champion authority.
- **Default-path stance:** `unchanged`
- **Required packet / review:**
  - Opus pre-code review completed with `APPROVED_WITH_NOTES`
  - Opus post-diff audit required after implementation

### Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- `High-sensitivity runtime/config slice`
- `No family-rule changes`
- `No champion/default/promotion/readiness semantics`
- `No backtest runner / CLI widening`
- `No decision_gates.py edits`
- `No decision_sizing.py edits`
- `No risk_state.py edits`
- `Stop if any strict-only surface becomes necessary`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: typed Python diff, small bounded module, ruff/pytest/bandit required.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: decision-path changes must remain root-cause-traceable and bounded.
- **Applied repo-local spec:** `config_authority_lifecycle_check`
  - reason: schema/authority changes must preserve canonical+alias lifecycle guarantees and deterministic reject paths.

### Scope

- **Scope IN:**
  - `docs/governance/ri_policy_router_runtime_integration_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `src/core/strategy/decision.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
- **Scope OUT:**
  - `src/core/strategy/family_registry.py`
  - `src/core/strategy/family_admission.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/intelligence/regime/risk_state.py`
  - all backtest runner / CLI surfaces
  - `config/strategy/champions/**`
  - promotion / readiness / comparison / champion / family-rule surfaces
  - prior candidate manifest / registry files
  - unrelated HTF Fibonacci test edits
- **Expected changed files:**
  - `docs/governance/ri_policy_router_runtime_integration_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `src/core/strategy/decision.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
- **Max files touched:** `10`

## Proposed runtime contract

### New config leaf

- `multi_timeframe.research_policy_router`

Exact fields:

- `enabled: bool = False`
- `switch_threshold: int = 2`
- `hysteresis: int = 1`
- `min_dwell: int = 3`
- `defensive_size_multiplier: float = 0.5`

Canonical default-off rule:

- Absent leaf and `{enabled: false}` are both canonical default-off forms and must produce identical persisted semantics and identical observable decision outputs.
- Router-specific keys, reasons, and state may appear only when `enabled: true`.

### Enabled-path semantics

When enabled only, the pure router may choose among exactly:

- `RI_continuation_policy`
- `RI_defensive_transition_policy`
- `RI_no_trade_policy`

Allowed decision-time inputs only:

- candidate action
- confidence gate after post-fib success
- `p_buy`, `p_sell`, `edge`, `max_ev`, `r_default`
- `regime`
- zone from `zone_debug`
- `bars_since_regime_change`
- prior router state from `state_in`

Integration point:

- after `apply_post_fib_gates(...)` succeeds
- before `apply_sizing(...)`

Behavior boundary:

- if router selects `RI_no_trade_policy`, return `NONE` before sizing with explicit router reason/state
- if router selects continuation or defensive, preserve existing fib/post-fib gate ownership and apply only a final posture multiplier to the size (`1.0` continuation, `defensive_size_multiplier` defensive)
- router state and debug payload may be written only to:
  - `research_policy_router_state`
  - `research_policy_router_debug`

## Gates required

### Focused source / lint gate

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check src/core/strategy/ri_policy_router.py src/core/strategy/decision.py src/core/config/schema.py src/core/config/authority.py tests/utils/test_ri_policy_router.py tests/utils/test_decision_scenario_behavior.py tests/governance/test_config_schema_backcompat.py tests/integration/test_golden_trace_runtime_semantics.py`

### Focused router/runtime tests

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_ri_policy_router.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision_scenario_behavior.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_config_schema_backcompat.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/integration/test_golden_trace_runtime_semantics.py`

### Smoke gate

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`

### Config-authority lifecycle skill selectors

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_config_ssot.py::test_regime_unified_alias_only_is_canonicalized_before_persist tests/governance/test_config_ssot.py::test_regime_unified_alias_non_dict_is_rejected tests/governance/test_config_ssot.py::test_regime_unified_alias_extra_key_is_rejected tests/integration/test_config_api_e2e.py::test_runtime_endpoints_e2e_regime_unified_alias_bridge`

### Required high-sensitivity gates

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/strategy -r src/core/config -c bandit.yaml`

## Proof obligations

- absent leaf == explicit disabled leaf canonical semantics
- untouched default path preserves observable reasons/state/debug shape for absent vs disabled leaf
- enabled path can:
  - select defensive posture in a fresh transition pocket
  - persist dwell/hysteresis state across bars
  - return to continuation when state allows and dwell/hysteresis permit
  - force no-trade when evidence floor is not met
- no family-rule, promotion, readiness, or champion semantics enter scope

## Stop Conditions

- any need to touch `family_registry.py` or `family_admission.py`
- any need to alter default/champion/promotion authority
- any need to widen beyond `decision.py` + new pure router + config-authority support
- default-off parity cannot be proven for absent vs disabled leaf
- integration requires changing backtest runner, `decision_sizing.py`, `risk_state.py`, or `decision_gates.py`

## Output required

- bounded implementation diff rooted in `ri_policy_router.py` + `decision.py` + explicit config-authority support
- exact commands run and pass/fail outcomes
- proof that absent and disabled forms are equivalent on canonical and observable default paths
- proof that router state/debug is additive and enabled-only
- proof that enabled path can switch, hold, and return without widening into family/champion surfaces
- residual-risk note if any remains
