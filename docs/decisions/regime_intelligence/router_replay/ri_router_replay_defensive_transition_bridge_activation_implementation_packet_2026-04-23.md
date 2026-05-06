# RI router replay defensive-transition bridge-activation implementation packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical implementation packet / candidate bridge artifact created and absorbed / no active implementation authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This packet is not an active implementation authority on `feature/next-slice-2026-05-05`.
> - The separate bridge artifact was later created and folded into the broader bridge-activation / launch / execution chain summarized from `GENESIS_WORKING_CONTRACT.md`.
> - Preserve this file as historical config-artifact provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice would create one new research-only candidate bridge artifact under `config/strategy/candidates/**` that can materialize already-validated runtime behavior when explicitly selected, but it does not touch runtime defaults, source code, runner surfaces, or launch authority.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the runtime/config-authority carrier already exists and is validated, so the next honest step is to make that carrier expressible as one separate candidate artifact without reopening runtime implementation or launch.
- **Objective:** create one bounded candidate bridge config artifact derived from the fixed RI bridge baseline and differing only by explicit materialization of `multi_timeframe.research_defensive_transition_override`, while preserving the baseline bridge file unchanged and keeping launch separately governed.
- **Candidate:** `defensive-transition candidate artifact creation`
- **Base SHA:** `2dc6df79`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
  - `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
  - `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_candidate_gate_carrier_implementation_packet_2026-04-23.md`
  - `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_bridge_activation_precode_packet_2026-04-23.md`
  - `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- **Candidate / comparison surface:**
  - preserve the fixed bridge file as the baseline reference,
  - create one future candidate bridge artifact at a separate path,
  - keep the effective config delta confined to one explicit research leaf.
- **Vad ska förbättras:**
  - make the already-validated runtime carrier selectable via a bounded repo-visible candidate artifact,
  - preserve baseline-vs-candidate comparability,
  - keep launch/backtest execution out of scope.
- **Vad får inte brytas / drifta:**
  - baseline bridge identity,
  - untouched default/runtime-authority semantics,
  - config-authority canonical semantics,
  - runner/CLI surfaces,
  - family identity,
  - launch separation.
- **Reproducerbar evidens som måste finnas:**
  - one exact candidate config path,
  - proof that the baseline bridge file remains unchanged,
  - proof that the candidate differs only by the explicit research leaf,
  - proof that the candidate validates through current config-authority/runtime parsing surfaces,
  - explicit statement that launch remains separately governed.

### Constraints

- `BASELINE BRIDGE UNCHANGED`
- `Config-only candidate artifact creation`
- `No src/** edits`
- `No tests/** edits`
- `No scripts/** edits`
- `No launch authorization`
- `No runtime-default / family / promotion reopening`

### Skill Usage

- **Applied repo-local spec:** `config_authority_lifecycle_check`
- **Reason:** the new candidate artifact must validate through the same config-authority surface that governs canonical runtime interpretation, and the slice must preserve deterministic accept/reject behavior.
- **Slice evidence:** the lifecycle selectors listed under Gates required are part of the acceptance evidence for this slice and must remain green.
- **Consulted repo-local spec:** `python_engineering`
- **Reason:** terminal-side validation will use workspace Python directly and should remain minimal, typed in spirit, and verification-first even though no Python source file is being edited.
- **Deferred:** `backtest_run` and `genesis_backtest_verify` remain relevant only if a later launch/execution slice is separately opened.

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_bridge_activation_implementation_packet_2026-04-23.md`
  - `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
  - all other `config/**`
  - all `src/**`
  - all `tests/**`
  - all `scripts/**`
  - all `results/**` and `artifacts/**`
  - any launch packet
  - any backtest execution
  - any runner/default/family-rule change
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_bridge_activation_implementation_packet_2026-04-23.md`
  - `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `3`

### Hypothesis under implementation

The bounded implementation hypothesis is:

- one separate candidate bridge artifact is sufficient to express the already-validated runtime carrier on the fixed RI bridge subject
- the baseline bridge file can remain byte-for-byte unchanged
- the candidate artifact can differ only by:
  - `cfg.multi_timeframe.research_defensive_transition_override.enabled = true`
  - `cfg.multi_timeframe.research_defensive_transition_override.guard_bars = 3`
  - `cfg.multi_timeframe.research_defensive_transition_override.max_probability_gap = 0.05`
- no runner, launch, runtime, or family widening is necessary to complete this slice

If any of the four statements above fails, the slice must stop and re-packet rather than broaden in place.

### Gates required

1. file validation:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pre_commit run --files docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_bridge_activation_implementation_packet_2026-04-23.md config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json GENESIS_WORKING_CONTRACT.md`

2. baseline immutability proof against `HEAD`:

- `git diff --exit-code -- config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

3. focused candidate-artifact validation via current authority surface:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -c "import json; from copy import deepcopy; from pathlib import Path; from core.config.authority import ConfigAuthority; root = Path(r'C:/Users/fa06662/Projects/Genesis-Core'); base = json.loads((root / 'config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json').read_text(encoding='utf-8')); candidate = json.loads((root / 'config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json').read_text(encoding='utf-8')); expected = deepcopy(base); expected['cfg'].setdefault('multi_timeframe', {})['research_defensive_transition_override'] = {'enabled': True, 'guard_bars': 3, 'max_probability_gap': 0.05}; assert candidate == expected; base_dump = ConfigAuthority().validate(base['cfg']).model_dump_canonical(); cand_dump = ConfigAuthority().validate(candidate['cfg']).model_dump_canonical(); assert 'research_defensive_transition_override' not in base_dump['multi_timeframe']; assert cand_dump['multi_timeframe']['research_defensive_transition_override'] == {'enabled': True, 'guard_bars': 3, 'max_probability_gap': 0.05}; print('bridge_candidate_validation:ok')"`

4. explicit candidate-load smoke through the current `run_backtest.py` config-file merge path:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -c "import json; from pathlib import Path; from core.config.authority import ConfigAuthority; from core.config.merge_policy import resolve_runtime_merge_decision; root = Path(r'C:/Users/fa06662/Projects/Genesis-Core'); payload = json.loads((root / 'config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json').read_text(encoding='utf-8')); override_cfg = payload.get('cfg') or payload.get('parameters'); assert isinstance(override_cfg, dict); merged_config_from_file = payload.get('merged_config'); resolution = resolve_runtime_merge_decision(has_merged_config=merged_config_from_file is not None); assert resolution.use_runtime_merge is True; authority = ConfigAuthority(); runtime_cfg, _, _ = authority.get();
def deep_merge(base, override):
   merged = dict(base)
   for key, value in (override or {}).items():
      if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
        merged[key] = deep_merge(merged[key], value)
      else:
        merged[key] = value
   return merged
merged_cfg = deep_merge(runtime_cfg.model_dump(), override_cfg); validated = authority.validate(merged_cfg).model_dump_canonical(); assert validated['multi_timeframe']['research_defensive_transition_override'] == {'enabled': True, 'guard_bars': 3, 'max_probability_gap': 0.05}; print('bridge_candidate_load_smoke:ok')"`

5. config backcompat proof for the enabled leaf:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_config_schema_backcompat.py`

6. config authority lifecycle attestation selectors:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_config_ssot.py::test_regime_unified_alias_only_is_canonicalized_before_persist tests/governance/test_config_ssot.py::test_regime_unified_alias_non_dict_is_rejected tests/governance/test_config_ssot.py::test_regime_unified_alias_extra_key_is_rejected tests/integration/test_config_api_e2e.py::test_runtime_endpoints_e2e_regime_unified_alias_bridge`

7. determinism replay selector:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`

8. feature cache invariance selector:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_features_asof_cache_isolation.py::test_feature_cache_key_separates_precompute_and_runtime_modes`

9. pipeline invariant selector:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- any need to edit the existing baseline bridge file in place
- any need to edit `src/**`, `tests/**`, or `scripts/**`
- any need to widen the candidate delta beyond the exact research leaf listed above
- candidate validation fails through `ConfigAuthority`
- any sentence or artifact starts implying launch authorization rather than candidate artifact creation only

### Output required

- one reviewable implementation packet
- one separate candidate bridge config artifact
- exact commands run and pass/fail outcomes
- proof that baseline remained unchanged
- proof that candidate differs only by the explicit research leaf
- explicit residual-risk note if any remains

## Why this is the smallest admissible implementation slice

This packet intentionally does **not** begin from:

- `scripts/run/run_backtest.py`
- a launch packet
- any backtest execution command
- any runtime/config-authority code change
- any baseline bridge mutation

Those surfaces would widen the lane beyond what the current evidence requires.

The smallest honest next step is therefore:

- one separate candidate bridge file
- one bounded config delta
- current authority-surface validation only
- launch still separately blocked

## Bottom line

This packet proposes one exact next implementation attempt only:

- create `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`
- keep `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json` unchanged
- add only the already-validated `research_defensive_transition_override` leaf
- stop immediately if the slice spills into code, tests, runner, or launch surfaces

This slice creates only a separate research candidate artifact. It does **not** authorize selecting that artifact for backtest/runtime use, and it does **not** authorize launch or execution. Opus pre-code review is required before the candidate artifact is created.
