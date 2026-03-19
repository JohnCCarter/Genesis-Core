## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-challenger-slice4-eval-2026-03-19`
- **Category:** `obs`
- **Risk:** `HIGH` — why: optimizer experiment scaffolding in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Create a sixth RI challenger-family Optuna slice for `tBTCUSD 3h` that preserves RI family identity, freezes the explicit slice-4 anchor baseline, and reopens only bounded entry-selectivity levers to test whether the RI family can reduce overtrading / drawdown without reopening exit cadence, authority, clarity, or broad threshold topology.
- **Candidate:** `ri challenger family slice6`
- **Base SHA:** `9566e8d9017d278356bcf086ee6f16db46ff231e`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice6_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice6_2026-03-19.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - committed `results/**`
  - `tmp/**` smoke YAMLs / temp DBs / run-launch artifacts
  - any execution packet or live run
  - promotion/default/cutover semantics
  - blind-2025 execution
  - legacy-authority reopening
  - clarity search reopening
  - renewed risk_state/sizing breadth
  - exit/hold/override cadence reopening beyond the explicit slice-4 anchor baseline
- **Expected changed files:** `3`
- **Max files touched:** `3`

### Baseline anchor

Slice-6 must freeze a single explicit slice-4 anchor:

- source run: `results/hparam_search/run_20260319_111953`
- source validation plateau: `0.22516209452403432`
- deterministic tie-break rule: among the tied validation winners, choose the member with highest train score
- selected anchor: `trial_002`

The slice-6 YAML must freeze exactly these anchor-derived values:

- `htf_exit_config.partial_1_pct = 0.5`
- `htf_exit_config.partial_2_pct = 0.45`
- `htf_exit_config.fib_threshold_atr = 0.9`
- `htf_exit_config.trail_atr_multiplier = 2.5`
- `gates.hysteresis_steps = 3`
- `gates.cooldown_bars = 2`
- `thresholds.entry_conf_overall = 0.25` must remain included exactly inside the reopened range
- `thresholds.regime_proba.balanced = 0.36` must remain included exactly inside the reopened range
- canonical zone thresholds / zone regime_proba values must remain included exactly inside their reopened ranges
- `exit.max_hold_bars = 8`
- `exit.trailing_stop_pct = 0.022`
- `exit.stop_loss_pct = 0.016`
- `exit.exit_conf_threshold = 0.42`
- `multi_timeframe.ltf_override_threshold = 0.4`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold = 0.04`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult = 1.0`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold = 0.06`
- `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult = 0.65`
- `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars = 2`
- `risk.htf_regime_size_multipliers.bear = 0.65`
- `risk.volatility_sizing.high_vol_multiplier = 0.70`

### Hypothesis whitelist

Slice-6 may **only** open these tunables:

1. Core selectivity
   - `thresholds.entry_conf_overall`
   - `thresholds.regime_proba.balanced`
2. Zone selectivity
   - `thresholds.signal_adaptation.zones.low.entry_conf_overall`
   - `thresholds.signal_adaptation.zones.mid.entry_conf_overall`
   - `thresholds.signal_adaptation.zones.high.entry_conf_overall`
   - `thresholds.signal_adaptation.zones.low.regime_proba`
   - `thresholds.signal_adaptation.zones.mid.regime_proba`
   - `thresholds.signal_adaptation.zones.high.regime_proba`

Everything else stays fixed to the canonical RI threshold cluster, RI identity, and the explicit slice-4 anchor baseline.

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice6_2026-03-19.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice6_2026-03-19.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice6_2024_v1.yaml`
- reuse-eligible STRICT anchors only if HEAD and runtime-affecting files remain unchanged:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- Stop if more than the three scoped files need to change.
- Stop if any `tmp/**`, `results/**`, DB, smoke artifact, or run launch becomes necessary.
- Stop if any edit is needed under `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`.
- Stop if the slice-4 anchor cannot be represented exactly in the YAML.
- Stop if any reopened selectivity range excludes the canonical RI value it is supposed to preserve.
- Stop if the hypothesis requires reopening exit/override cadence, legacy authority, clarity, broad threshold topology, or renewed risk_state/sizing breadth.
- Stop if validator or preflight indicates that the YAML semantics require code or test changes.

### Output required

- **Implementation Report**
- **PR evidence template**
- committed slice-6 YAML path
- committed command packet path
- committed context map path

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Slice-6 is experiment scaffolding only; it must not alter runtime defaults, incumbent champion behavior, or production authority semantics.
- Preserve RI family identity: `authority_mode=regime_module`, RI `v2`, `clarity_score.enabled=false`, `risk_state.enabled=true`, `atr_period=14`, gates `3/2`.
- Preserve train `2023-12-21..2024-06-30` and validation `2024-07-01..2024-12-31`.
- Use fresh `study_name`, fresh `storage`, `resume=false`, `promotion.enabled=false`, and `n_jobs=1`.
- No long run, smoke launch, temp YAML, or temp DB creation belongs to this slice; any execution must be packeted separately.
