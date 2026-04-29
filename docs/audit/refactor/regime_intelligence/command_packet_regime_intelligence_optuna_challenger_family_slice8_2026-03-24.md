## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — why: optimizer experiment scaffolding in a high-sensitivity decision domain after a successful but duplicate-heavy RI slice; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Create and execute an eighth RI challenger-family Optuna slice for `tBTCUSD 3h` that performs a bounded widen-search around the successful slice7 neighborhood to reduce duplicate collapse and test whether the slice7 gain survives a broader nearby RI search surface before any new family anchor is declared.
- **Run intent:** `research_slice` (explicit; required for `strategy_family=ri` admission in validator/preflight)
- **Candidate:** `ri challenger family slice8 widen search`
- **Base SHA:** `3be2a497ab8c9e6b87fbb9c8c8344d958701fb9e`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_execution_2026-03-24.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - committed `results/**`
  - `tmp/**` smoke YAMLs / temp DBs / run-launch artifacts
  - blind-2025 execution
  - promotion/default/cutover semantics
  - legacy-authority reopening
  - clarity search reopening
  - renewed risk_state breadth
  - renewed exit/override cadence
  - renewed zone-selectivity breadth
  - broad threshold-topology reopening
- **Expected changed files:** `4`
- **Max files touched:** `4`

### Evidence base frozen for this slice

Slice8 must treat the following as reviewed inputs, not as automatic new-anchor decisions:

- slice6 plateau: `0.23646934335498004`
- slice7 validation winner: `0.26974911658712664`
- slice7 winning gates: `4 / 1`
- incumbent same-head control: `0.2616884080730424`
- slice7 duplicate ratio: `0.90625` (`87/96`)
- validator/preflight admission for `strategy_family=ri` with `run_intent=research_slice` and integer gate sweeps is already covered by current repo tests (`tests/utils/test_validate_optimizer_config.py::test_validate_optimizer_strategy_family_accepts_ri_research_slice_gate_sweep` and `tests/utils/test_preflight_optuna_check.py::test_check_parameters_valid_accepts_ri_research_slice_with_int_gate_ranges`); slice8 must stop rather than widen scope if the concrete YAML contradicts that verified admission surface.

### Anchor discipline

- Slice8 must **not** claim that `4 / 1` is the new RI family anchor.
- Slice8 must **not** promote, freeze, or rename any winner as a new canonical RI baseline.
- Slice8 exists only to widen the local search surface enough to decide later whether the slice7 gain is robust or merely a narrow-surface artifact.
- Slice8 execution/reporting must end in one of two statuses only: `widen-search evidence collected` or `widen-search blocked`; any anchor/promote/freeze/default recommendation is explicitly out of scope for this slice.

### Validator / preflight compatibility rule

- Slice8 may proceed only if the exact scoped YAML passes both optimizer validator and Optuna preflight unchanged under the current repo code.
- If validator or preflight rejects the widened search surface for semantic reasons, treat that as a governed blocker for this slice rather than as permission to edit `src/**`, `tests/**`, or relax the RI contract.
- No compatibility shim, runtime patch, or test rewrite is allowed inside slice8 scope.

### Hypothesis whitelist

Slice8 may **only** open these tunables:

1. Gating cadence
   - `gates.hysteresis_steps`
   - `gates.cooldown_bars`
2. Core selectivity
   - `thresholds.entry_conf_overall`
   - `thresholds.regime_proba.balanced`

Exact allowed search ranges:

- `gates.hysteresis_steps = 3..5` with `step=1`
- `gates.cooldown_bars = 1..3` with `step=1`
- `thresholds.entry_conf_overall = 0.26..0.30` with `step=0.01`
- `thresholds.regime_proba.balanced = 0.34..0.38` with `step=0.01`

These ranges are chosen to:

- retain the slice6 canonical values `3 / 2`, `0.28`, and `0.36`
- retain the slice7 validation winner neighborhood `4 / 1`
- increase unique combinations enough to reduce duplicate collapse without reopening broad RI topology

Everything else stays fixed to the slice7-reviewed RI backbone:

- `authority_mode=regime_module`
- RI `version=v2`
- `clarity_score.enabled=false`
- `risk_state.enabled=true`
- `atr_period=14`
- fixed zone selectivity cluster from slice6/slice7
- fixed exit / override / HTF / risk-state / sizing surfaces from slice6/slice7

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_execution_2026-03-24.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Success rule for this slice

Slice8 counts as a useful widen-search only if it returns one of the following governed outcomes:

1. a validation winner that strictly exceeds the slice7 validation score `0.26974911658712664`, or
2. a no-better winner together with a duplicate ratio of `<= 0.70` while also keeping the validation winner at or above the slice6 plateau `0.23646934335498004`.

Any result outside those thresholds is still recordable evidence, but it does **not** count as a successful widen-search for anchor-decision purposes.

### Stop Conditions

- Stop if more than the four scoped files need to change.
- Stop if any edit is needed under `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`.
- Stop if the widen-search requires reopening zone selectivity, risk-state tuning, exit/override cadence, clarity, or broad topology search.
- Stop if validator or preflight indicates that the YAML semantics require code or test changes.
- Stop if validator or preflight fails on the exact scoped YAML; report the failure as a slice8 blocker and do not launch.
- Stop if execution would require dirty-tree launch, reused DB with `resume=false`, or non-canonical mode.
- Stop if the packet drifts into promotion, freeze, or anchor-declaration claims.

### Output required

- **Implementation Report**
- **PR evidence template**
- committed slice8 YAML path
- committed command packet path
- committed context map path
- committed execution packet path
- exact launch command and env flags used
- run directory path
- validation winner summary
- comparison versus slice7, slice6, and incumbent control
- duplicate-ratio comparison versus slice7
- explicit post-run statement that anchor/promotion/freeze/default decision remains deferred

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Slice8 is experiment scaffolding and challenger evidence collection only; it must not alter runtime defaults, incumbent champion behavior, or production authority semantics.
- Slice8 YAML must declare `meta.runs.run_intent: research_slice` explicitly; implicit defaulting is not allowed.
- Preserve train `2023-12-21..2024-06-30` and validation `2024-07-01..2024-12-31`.
- Use fresh `study_name`, fresh `storage`, `resume=false`, `promotion.enabled=false`, and `n_jobs=1`.
- Any final anchor decision remains explicitly out of scope for this slice and must be made only after the widen-search outcome is reviewed.
