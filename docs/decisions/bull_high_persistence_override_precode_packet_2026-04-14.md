# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `HIGH` — runtime decision-path touch in strategy gating, but intended as default-off research carveout
- **Required Path:** `Full`
- **Objective:** Add a minimal default-off research override for the observed bull/high persistence carveout so it can be validated against the locked baseline window without changing default behavior.
- **Candidate:** `bull/high persistence near-miss override`
- **Base SHA:** `feature/ri-role-map-implementation-2026-03-24 (working tree)`

## Scope

- **Scope IN:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - focused tests covering decision gating/runtime semantics/schema backcompat
- **Scope OUT:**
  - optimizer, backtest engine semantics, sizing logic behavior, fib gate logic, champion configs, runtime defaults, docs outside this packet unless strictly required for evidence
- **Expected changed files:**
  - `src/core/strategy/decision.py` (only if needed for state/debug reset/plumbing)
  - `src/core/strategy/decision_gates.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_decision_gates_contract.py`
  - `tests/utils/test_decision.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
  - `tests/governance/test_config_schema_backcompat.py`
- **Max files touched:** `8`

## Planned behavior

- Add a **default-off** config-gated research override that can admit a LONG candidate only when all are true:
  - regime is `bull`
  - signal-adaptation zone is `high`
  - probability threshold would otherwise fail
  - `buy > sell`
  - `threshold - buy <= max_probability_gap`
  - rolling same-family persistence count reaches configured minimum
- Preserve current behavior exactly when the override is disabled.
- Keep the carveout scoped to candidate admission only; do not alter post-fib gates, sizing math, fib logic, cooldown, or hysteresis semantics.

## Gates required

- `pre-commit run --all-files`
- focused pytest selectors for touched decision/schema surfaces
- determinism replay selector
- feature cache invariance selector
- pipeline hash guard selector
- locked-window disabled-path replay/smoke confirming zero decision/admission drift versus baseline
- locked-window baseline-vs-flag comparison (research efficacy evidence only; not a no-drift proof)

## Stop Conditions

- Scope drift outside listed files
- Any behavior change when override is disabled
- Determinism/hash regression
- Need for broader runtime/config redesign
- Evidence shows carveout only works via one isolated cluster and fails the focused counterfactual

## Output required

- **Implementation Report**
- **PR evidence template**

## Evidence wording discipline

- Any admitted-bar outcome from the opt-in override is research efficacy evidence only.
- No admitted-bar result may be cited as determinism, no-drift, or contract-preservation proof.
- Threshold-gap eligibility must be evaluated against the resolved active regime-probability threshold, including signal-adaptation zone ownership when present.
