# RI router replay defensive-transition candidate-gate carrier implementation packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `implementation contract proposed / default path unchanged intended`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this packet proposes a behavior-sensitive code slice inside `src/core/strategy/*` plus bounded config-authority support inside `src/core/config/*`. Intent is default-path preservation, but the slice still touches runtime decision behavior and canonical config interpretation, so Full-path verification is required.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the prior sizing seam has already been falsified, the nearest honest runtime seam is now upstream candidate formation, and any explicit default-off activation path must be admitted through bounded config-authority support rather than a silent config convention.
- **Objective:** test whether `defensive_transition_state mandate/confidence 2` can be carried by a minimal research-only runtime slice rooted at `src/core/strategy/decision_gates.py::select_candidate(...)`, with explicit default-off config-authority support only if needed, while preserving untouched default behavior and avoiding CLI/backtest/family widening.
- **Candidate:** `defensive-transition candidate-gate carrier implementation`
- **Base SHA:** `2dc6df79`

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/decision_gates.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - replay closeout already localized the blocker,
  - the bounded `decision_sizing.py` attempt has already been honestly falsified,
  - `decision_gates.py::select_candidate(...)` is now the nearest repo-visible runtime seam for candidate formation,
  - current config authority already enforces whitelist/canonical-dump semantics for research leaves, so an explicit activation path cannot be treated as a docs-only or config-file-only convention.
- **Default-path stance:** `unchanged / explicit exception required`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

### Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when one new research leaf is explicitly enabled`
- `High-sensitivity zone`
- `Bounded multi-surface slice only`
- `Targeted tests allowed`
- `No CLI flag changes`
- `No backtest launch authorization`
- `No family-rule changes`
- `No bridge-config activation in this slice`
- `Stop if additional strategy/config surfaces become necessary`

### Skill Usage

- **Applied repo-local spec:** `python_engineering`
- **Reason:** the slice is a Python code change across bounded runtime and config-authority surfaces and must stay typed, minimal, test-backed, and fully verified.
- **Applied repo-local spec:** `decision_gate_debug`
- **Reason:** the slice targets candidate formation and threshold-pass behavior, so gate-trace clarity and root-cause discipline are mandatory.
- **No separate parity skill claimed:** default-off parity evidence in this slice is provided by explicit targeted and integration tests, not by claiming additional skill coverage.
- **Deferred:** `backtest_run` and `genesis_backtest_verify` remain relevant only if a later runnable backtest step is separately authorized.

### Scope

- **Scope IN:**
  - `docs/decisions/ri_router_replay_defensive_transition_candidate_gate_carrier_implementation_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/decision_gates.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_decision_gates_contract.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
- **Scope OUT:**
  - all other `src/**`
  - all `config/strategy/**` edits
  - all `scripts/**` edits
  - all `tests/**` edits outside the four listed files
  - all CLI semantics changes
  - all backtest-runner changes
  - all family-rule changes
  - all `src/core/strategy/decision.py` edits
  - all `src/core/strategy/decision_sizing.py` edits
  - all `src/core/intelligence/regime/risk_state.py` edits
  - all runtime integration / paper / readiness / cutover / promotion widening
- **Expected changed files:**
  - `docs/decisions/ri_router_replay_defensive_transition_candidate_gate_carrier_implementation_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/decision_gates.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_decision_gates_contract.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
- **Max files touched:** `9`

### Hypothesis under implementation

The bounded implementation hypothesis is:

- a research-only carrier can be introduced at candidate-formation time inside `src/core/strategy/decision_gates.py::select_candidate(...)`
- if explicit activation is required, it can remain default-off through one bounded research leaf under `multi_timeframe`
- that leaf can be admitted explicitly through `src/core/config/schema.py` and `src/core/config/authority.py` without widening into runtime defaults, CLI, launch surfaces, or bridge-config activation
- `decision_sizing.py` and `risk_state.py` can remain unchanged as downstream consumers rather than being repurposed into mandate-ranking surfaces

Bounded exception rule for this slice:

- behavior may differ **only** when the new research leaf is explicitly enabled
- absent leaf and explicit disabled leaf must remain canonically identical
- untouched authority/default outputs must not materialize the new leaf on the default path

This is an implementation hypothesis only.
If the slice cannot satisfy all four statements above, it must stop and re-packet rather than broaden in place.

### Gates required

#### Targeted local proof

1. lint:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check src/core/strategy/decision_gates.py src/core/config/schema.py src/core/config/authority.py tests/utils/test_decision_gates_contract.py tests/utils/test_decision_scenario_behavior.py tests/governance/test_config_schema_backcompat.py tests/integration/test_golden_trace_runtime_semantics.py`
2. focused decision smoke:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision.py`
3. candidate-gate contract tests:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision_gates_contract.py tests/utils/test_decision_scenario_behavior.py`
   - these in-scope tests must explicitly prove disabled/default-path structural parity for returned reasons, key presence, and state/debug payload shape on the untouched default path
4. config-authority backcompat proof:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_config_schema_backcompat.py`
   - this test surface must explicitly prove absent leaf == explicit disabled leaf canonical semantics if a new research leaf is introduced
   - this test surface must also prove that untouched authority/default outputs do not materialize the new leaf on the default path
5. default-off runtime parity selector:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/integration/test_golden_trace_runtime_semantics.py`
   - the in-scope integration edits must include and pass a targeted disabled/default parity selector for the new carrier
   - that selector must prove identical golden-trace/runtime semantics for absent leaf versus explicit disabled leaf before any enabled-path behavior claim is accepted

#### Required governance gates for high-sensitivity slice

6. determinism replay:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
7. feature cache invariance:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_features_asof_cache_isolation.py::test_feature_cache_key_separates_precompute_and_runtime_modes`
8. pipeline invariant check:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
9. security hygiene for changed source surfaces:
   - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/strategy -r src/core/config -c bandit.yaml`

### Stop Conditions

- any additional `src/core/strategy/**` file beyond `decision_gates.py` becomes necessary
- any additional `src/core/config/**` file beyond `schema.py` and `authority.py` becomes necessary
- any `config/strategy/**` or `scripts/**` edit becomes necessary
- any proposed remediation requires a new CLI flag, runner change, or launch-surface widening
- disabled/default path changes returned reasons, key presence, serialized payload shape, or state/debug structure from the current default path
- absent leaf == explicit disabled leaf semantics cannot be proven canonically
- `decision.py`, `decision_sizing.py`, or `risk_state.py` must be edited to make the carrier work
- any family-rule or runtime-default surface enters scope

### Output required

- one bounded code diff rooted in `decision_gates.py` plus explicit config-authority support only if required
- exact commands run and pass/fail outcomes
- proof that default behavior remains unchanged when the carrier leaf is absent or disabled
- proof that disabled/default-path structural parity is preserved for returned reasons and state/debug payload shape
- proof that absent leaf == explicit disabled leaf semantics hold in canonical config authority output
- proof that untouched authority/default outputs do not materialize the new leaf on the default path
- proof that the carrier stays local to candidate formation and does not repurpose downstream sizing/risk-state surfaces
- explicit residual-risk note if any remains

## Why this is the smallest admissible widened implementation slice

This packet intentionally does **not** begin from:

- `scripts/run/run_backtest.py`
- the fixed bridge config
- a candidate bridge-config file
- `decision.py`
- `decision_sizing.py`
- `risk_state.py`
- family registry or family admission surfaces

Those surfaces would widen the lane beyond what the current evidence requires.

The minimal honest next attempt is therefore:

- one upstream strategy seam where candidate formation already exists
- bounded config-authority support only if a documented default-off leaf is truly required
- targeted tests plus explicit parity/backcompat proof
- explicit stop if the slice spills into activation, launch, or downstream reinterpretation

## Bottom line

This packet proposes one exact next implementation attempt only:

- test the candidate carrier in `src/core/strategy/decision_gates.py::select_candidate(...)`
- admit a new explicit default-off research leaf only through bounded `schema.py` / `authority.py` support if activation truly needs it
- keep `decision.py`, `decision_sizing.py`, `risk_state.py`, runner surfaces, and bridge-config activation unchanged
- stop immediately if the slice needs broader runtime or launch widening

No implementation is authorized by this packet alone. Opus pre-code review is required before code changes may begin.
