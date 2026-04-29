# RI router replay defensive-transition candidate-carrier implementation packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `implementation contract proposed / default path unchanged intended`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this packet proposes a behavior-sensitive code slice inside `src/core/strategy/*`, which is a high-sensitivity zone. Intent is default-path preservation, but the target seam sits on runtime strategy behavior and therefore requires Full-path verification.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the backtest subject, setup surface, and carrier hypothesis are already narrowed; proving or falsifying the carrier now requires touching a durable runtime strategy surface rather than another docs-only or replay-only slice.
- **Objective:** test whether the `defensive_transition_state mandate/confidence 2` candidate can be carried by a minimal research-only code slice rooted at the transition-state propagation seam in `src/core/strategy/decision_sizing.py`, while preserving default behavior and avoiding CLI/config/family widening.
- **Candidate:** `defensive-transition mandate-2 carrier implementation`
- **Base SHA:** `2dc6df79`

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/decision_sizing.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - replay closeout already localized the blocker,
  - backtest pre-code already fixed the subject,
  - setup-only already proved baseline expressibility and candidate non-expressibility on current CLI/config surfaces,
  - carrier pre-code already narrowed the leading seam to transition-state propagation.
- **Default-path stance:** `unchanged / explicit exception required`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

### Constraints

- `DEFAULT PATH UNCHANGED`
- `High-sensitivity zone`
- `Single source file target`
- `Targeted tests allowed`
- `No CLI flag changes`
- `No config schema changes`
- `No family-rule changes`
- `Stop if second src file becomes necessary`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
- **Reason:** the slice is a Python code change in a high-sensitivity strategy seam and must stay small, typed, test-backed, and fully verified.
- **Applied repo-local spec:** `decision_gate_debug`
- **Reason:** the slice targets a decision-seam carrier hypothesis and must preserve decision-surface interpretability, gate-trace clarity, and root-cause discipline rather than introducing opaque decision drift.
- **No separate parity skill claimed:** default-off parity evidence in this slice is provided by existing targeted tests, not by claiming additional skill coverage.
- **Deferred:** `backtest_run` and `genesis_backtest_verify` remain relevant only if a later runnable backtest step is separately authorized.

### Scope

- **Scope IN:**
  - `docs/decisions/ri_router_replay_defensive_transition_candidate_carrier_implementation_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/decision_sizing.py`
  - `tests/utils/test_decision_sizing.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Scope OUT:**
  - all other `src/**`
  - all `config/**` edits
  - all `scripts/**` edits
  - all `tests/**` edits outside the two listed files
  - all CLI semantics changes
  - all config-schema changes
  - all family-rule changes
  - all `src/core/intelligence/regime/risk_state.py` edits
  - all runtime integration / paper / readiness / cutover / promotion widening
- **Expected changed files:**
  - `docs/decisions/ri_router_replay_defensive_transition_candidate_carrier_implementation_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/decision_sizing.py`
  - `tests/utils/test_decision_sizing.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

### Hypothesis under implementation

The bounded implementation hypothesis is:

- a research-only carrier can be introduced at the transition-state propagation seam in `src/core/strategy/decision_sizing.py`
- the carrier can remain explicit and default-off
- the carrier can avoid widening into CLI/config/family surfaces
- `src/core/intelligence/regime/risk_state.py` can remain unchanged as a downstream sizing consumer

This is an implementation hypothesis only.
If the slice cannot satisfy all four statements above, it must stop and re-packet rather than broaden in place.

### Gates required

#### Targeted local proof

1. lint:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check src/core/strategy/decision_sizing.py tests/utils/test_decision_sizing.py tests/utils/test_decision_scenario_behavior.py`
2. focused strategy smoke:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision.py`
3. targeted strategy seam tests:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision_sizing.py tests/utils/test_decision_scenario_behavior.py`
   - these in-scope tests must explicitly prove disabled/default-path structural parity for returned keys and state/trace payload shape on the untouched default path
4. downstream sizing preservation:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_risk_state_multiplier.py`
5. default-off runtime parity selector:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/integration/test_golden_trace_runtime_semantics.py::test_research_bull_high_persistence_override_disabled_preserves_runtime_parity`

#### Required governance gates for high-sensitivity slice

6. determinism replay:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
7. feature cache invariance:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_features_asof_cache_isolation.py::test_feature_cache_key_separates_precompute_and_runtime_modes`
8. pipeline invariant check:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
9. security hygiene for changed source surface:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/strategy -c bandit.yaml`

### Stop Conditions

- any second `src/**` file becomes necessary
- any `config/**` or `scripts/**` edit becomes necessary
- any proposed remediation requires a new CLI flag or config field
- targeted tests reveal default-path behavior drift rather than explicit default-off preservation
- disabled/default path changes returned keys, key presence, serialized payload shape, or trace/state structure from the current default path
- `risk_state.py` must be edited to make the carrier work
- any family-rule or runtime-default surface enters scope

### Output required

- one minimal code diff rooted in `src/core/strategy/decision_sizing.py`
- exact commands run and pass/fail outcomes
- proof that default behavior remains unchanged when the carrier is absent/disabled
- proof that disabled/default-path structural parity is preserved for returned keys and trace/state payload shape
- proof that the carrier stays local and does not repurpose `risk_state.py`
- explicit residual-risk note if any remains

## Why this is the smallest admissible implementation slice

This packet intentionally does **not** begin from:

- `scripts/run/run_backtest.py`
- the fixed bridge config
- runtime-config schema
- family registry / family admission
- `src/core/intelligence/regime/risk_state.py`

Those surfaces would all widen the lane before proving whether the transition-state propagation seam is sufficient.

The minimal honest first attempt is therefore:

- one source file in the already-localized seam
- targeted tests around that seam
- explicit stop if the seam proves insufficient

## Bottom line

This packet proposes one exact next implementation attempt only:

- test the candidate carrier in `src/core/strategy/decision_sizing.py`
- keep the default path unchanged
- keep `risk_state.py` unchanged
- stop immediately if the slice needs CLI/config/family widening or a second source file

No implementation is authorized by this packet alone. Opus pre-code review is required before code changes may begin.
