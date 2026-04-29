## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — why: optimizer experiment scaffolding in a high-sensitivity decision domain after slice8 established a stronger local research baseline; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Create and execute a ninth RI challenger-family Optuna slice for `tBTCUSD 3h` that freezes the slice8 local geometry as a provisional research baseline only and reopens a narrow exit/override management surface to test whether the slice8 winner depends too strongly on inherited management settings.
- **Run intent:** `research_slice` (explicit; required for `strategy_family=ri` admission in validator/preflight)
- **Candidate:** `ri challenger family slice9 management falsification`
- **Base SHA:** `9c1f9d3b76f19194217bdab629a30f3f62bf107a`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Skill Usage

- Applied repo-local skill: `optuna_run_guardrails`
- Purpose: require validator + preflight + canonical mode before any long Optuna execution
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
  - `tmp/**` smoke YAMLs / temp DBs / run-launch artifacts
  - blind-2025 execution
  - promotion/default/cutover semantics
  - canonical anchor declaration semantics
  - reopening entry/gating/selectivity breadth
  - reopening risk_state breadth
  - touching unrelated `.github/agents/Codex53.agent.md`
- **Expected changed files:** `4`
- **Max files touched:** `4`

### Evidence base frozen for this slice

Slice9 must treat the following as reviewed inputs, not as automatic canonical-anchor decisions:

- slice7 validation winner: `0.26974911658712664`
- slice8 validation winner: `0.26974911658712664`
- slice7 duplicate ratio: `0.90625`
- slice8 duplicate ratio: `0.2604166666666667`
- slice8 local geometry: `entry_conf_overall=0.27`, `regime_proba.balanced=0.36`, `hysteresis_steps=4`, `cooldown_bars=1`
- incumbent same-head control: `0.2616884080730424`
- the anchor-decision candidate packet recommends slice8 as a research anchor only, but separate governance approval remains required for any canonical anchor declaration

### Provisional research baseline discipline

- Slice9 may use the slice8 local geometry as a **provisional research baseline only**.
- Slice9 must **not** declare that geometry a canonical RI anchor.
- Slice9 must **not** promote, freeze, or rename any winner as a new canonical RI baseline.
- Slice9 exists only to falsify or strengthen the slice8 local winner under a narrowly reopened management surface.

### Hypothesis whitelist

Slice9 may **only** open these tunables:

1. Exit hold horizon
   - `exit.max_hold_bars`
2. Exit confirmation threshold
   - `exit.exit_conf_threshold`
3. LTF override threshold
   - `multi_timeframe.ltf_override_threshold`

Exact allowed search ranges:

- `exit.max_hold_bars = 7..9` with `step=1`
- `exit.exit_conf_threshold = 0.40..0.44` with `step=0.01`
- `multi_timeframe.ltf_override_threshold = 0.38..0.42` with `step=0.01`

Everything else stays fixed to the slice8-reviewed RI backbone:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`
- `authority_mode=regime_module`
- RI `version=v2`
- `clarity_score.enabled=false`
- `risk_state.enabled=true`
- fixed zone selectivity cluster from slice8
- fixed HTF exit cadence and risk-state guard family from slice8
- same train / validation windows as slice7/slice8

### Why slice9 should reopen only a narrow exit/override management surface

- Slice8 already re-ran the best local entry/gating geometry under a broader nearby search and reproduced the same governed winner with far less duplicate collapse.
- That means the next falsifiable question is no longer whether entry/gating can improve locally, but whether the slice8 local winner depends too strongly on inherited management settings.
- Reopening broad RI topology, risk-state breadth, or selectivity again would destroy interpretability and violate the packet’s bounded-falsification discipline.
- The cleanest next step is therefore to freeze the slice8 local geometry and perturb only a narrow management surface around `max_hold_bars`, `exit_conf_threshold`, and `ltf_override_threshold`.

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice9_2026-03-26.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice9_execution_2026-03-26.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Success rule for this slice

Slice9 counts as a useful bounded falsification slice only if it returns one of the following governed outcomes:

1. a validation winner that strictly exceeds the slice7/slice8 validation score `0.26974911658712664`, or
2. a validation winner at or above the incumbent same-head control `0.2616884080730424` together with a validated winner that uses at least one non-slice8 management value among `exit.max_hold_bars`, `exit.exit_conf_threshold`, or `multi_timeframe.ltf_override_threshold`.

Any result outside those thresholds is still recordable evidence, but it does **not** count as successful anchor-strengthening management falsification.

### Stop Conditions

- Stop if more than the four scoped files need to change.
- Stop if any edit is needed under `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`.
- Stop if the falsification attempt requires reopening entry/gating/selectivity breadth, risk_state breadth, or broad threshold topology.
- Stop if validator or preflight indicates that the YAML semantics require code or test changes.
- Stop if execution would require dirty-tree launch, reused DB with `resume=false`, or non-canonical mode.
- Stop if the packet drifts into canonical-anchor, promotion, freeze, or default claims.

### Output required

- **Implementation Report**
- **PR evidence template**
- committed slice9 YAML path
- committed command packet path
- committed context map path
- committed execution packet path
- exact launch command and env flags used
- run directory path
- validation winner summary
- comparison versus slice8, slice7, and incumbent control
- explicit post-run statement that canonical anchor / promotion / freeze / default decision remains deferred

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Slice9 is experiment scaffolding and management-surface falsification only; it must not alter runtime defaults, incumbent champion behavior, or production authority semantics.
- Slice9 YAML must declare `meta.runs.run_intent: research_slice` explicitly; implicit defaulting is not allowed.
- Preserve train `2023-12-21..2024-06-30` and validation `2024-07-01..2024-12-31`.
- Use fresh `study_name`, fresh `storage`, `resume=false`, `promotion.enabled=false`, and `n_jobs=1`.
- Any final canonical-anchor decision remains explicitly out of scope for this slice.
