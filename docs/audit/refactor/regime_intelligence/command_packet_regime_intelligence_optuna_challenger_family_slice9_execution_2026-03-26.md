# Status: `föreslagen / execution not approved or performed by this document`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — why: execution-only optimizer/backtest evidence task in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Execute the already-created slice9 RI challenger-family Optuna campaign for `tBTCUSD 3h` under canonical comparison flags and determine whether the slice8-backed provisional research baseline survives a narrow exit/override management reopen.
- **Candidate:** `ri challenger family slice9 execution`
- **Base SHA:** `9c1f9d3b76f19194217bdab629a30f3f62bf107a`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Skill Usage

- Applied repo-local skill: `optuna_run_guardrails`
- Purpose: require validator + preflight + canonical comparison mode before any long Optuna execution
- No additional skill coverage is claimed by this packet

### Scope

- **Scope IN:**
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_execution_2026-03-26.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - committed `results/**`
  - promotion/default/cutover semantics
  - canonical anchor declaration semantics
  - touching unrelated `.github/agents/Codex53.agent.md`
  - any YAML parameter changes beyond the approved slice9 management surface unless a pure typo/path fix is required before launch

### Execution provenance

- Preferred launch state: clean working tree.
- Dirty-tree launch is **not approved** for slice9.
- Any dirty path blocks launch.
- If a clean tree cannot be obtained, stop and request fresh governance review before execution.
- Launch is **gated by post-diff audit**: do not execute until the four slice9 files have passed post-code governance review and all required gates below are green.

### Runtime artifacts (local only, not scope-expanding)

- launch target: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- expected local outputs under `results/hparam_search/run_*`
- expected local storage DB `results/hparam_search/storage/ri_challenger_family_slice9_3h_2024_v1.db`

### Baseline anchors for comparison

Slice9 comparisons must use these governed references:

- slice7 validation winner: `0.26974911658712664`
- slice8 validation winner: `0.26974911658712664`
- slice8 duplicate ratio: `0.2604166666666667`
- incumbent same-head control: `0.2616884080730424`
- provisional slice8 management tuple: `exit.max_hold_bars=8`, `exit.exit_conf_threshold=0.42`, `multi_timeframe.ltf_override_threshold=0.40`

### Preconditions

- canonical env flags must be set exactly:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `GENESIS_RANDOM_SEED=42`
  - `PYTHONPATH=src`
- exact launch YAML must still declare `meta.runs.run_intent: research_slice`
- exact launch YAML must explicitly state that slice8 geometry is used as a provisional research baseline only
- rerun `validate_optimizer_config.py` on the exact launch tree immediately before launch
- rerun `preflight_optuna_check.py` on the exact launch tree immediately before launch
- verify that `results/hparam_search/storage/ri_challenger_family_slice9_3h_2024_v1.db` does **not** already exist while `resume=false`
- launch command must be:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- no blind-2025 run belongs to this packet

### Evidence rules

- Compare the slice9 validation winner directly against:
  - slice7 validation winner `0.26974911658712664`
  - slice8 validation winner `0.26974911658712664`
  - incumbent same-head control `0.2616884080730424`
- Compare the slice9 validated winner’s management tuple directly against the provisional slice8 tuple `8 / 0.42 / 0.40`.
- A validated winner that exactly reproduces the slice8 management tuple may be recorded, but does **not** by itself count as management-surface robustness evidence.
- Fresh launch evidence is mandatory; older pytest evidence is not sufficient by itself for execution approval.

### Success rule for this packet

Slice9 counts as successful bounded management falsification only if it returns one of the following governed outcomes:

1. a validation winner that **strictly exceeds** the slice7/slice8 validation score `0.26974911658712664`, or
2. a validation winner at or above the incumbent same-head control `0.2616884080730424` while using at least one non-slice8 management value among `exit.max_hold_bars`, `exit.exit_conf_threshold`, or `multi_timeframe.ltf_override_threshold`.

Anything weaker may be recorded as evidence, but must be reported as **management-surface evidence not confirmed for canonical-anchor decision**.

### Post-run decision gate

- This packet may conclude only one of the following statuses:
  - `management-surface evidence collected`
  - `management-surface blocked`
- This packet must **not** declare a canonical RI anchor.
- This packet must **not** promote, freeze, or default any winner.

### Gates required before launch

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_execution_2026-03-26.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/governance/test_authority_mode_resolver.py`
