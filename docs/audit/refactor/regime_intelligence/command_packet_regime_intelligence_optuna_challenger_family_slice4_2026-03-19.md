## COMMAND PACKET

- **Mode:** `STRICT` — source: `docs/governance_mode.md` via branch `master`
- **Category:** `obs`
- **Risk:** `HIGH` — why: optimizer experiment scaffolding in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Create a fourth RI challenger-family Optuna slice for `tBTCUSD 3h` that responds to slice-3 validation plateau evidence by shifting the search toward bounded risk-state and sizing robustness levers while preserving RI family identity.
- **Candidate:** `ri challenger family slice4`
- **Base SHA:** `9566e8d9017d278356bcf086ee6f16db46ff231e`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md`
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
  - broad threshold-topology reopening
- **Expected changed files:** `3`
- **Max files touched:** `3`

### Hypothesis whitelist

Slice-4 may **only** open these tunables:

1. `risk_state` guard tuning
   - `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_threshold`
   - `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.soft_mult`
   - `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_threshold`
   - `multi_timeframe.regime_intelligence.risk_state.drawdown_guard.hard_mult`
   - `multi_timeframe.regime_intelligence.risk_state.transition_guard.mult`
   - `multi_timeframe.regime_intelligence.risk_state.transition_guard.guard_bars`
2. Secondary family: regime-aware sizing
   - `risk.htf_regime_size_multipliers.bear`
   - `risk.volatility_sizing.high_vol_multiplier`

All threshold, exit, override, fib-tolerance, authority, clarity, and topology-shaping surfaces stay fixed to the canonical RI threshold cluster plus a stable RI-compatible exit/fib baseline.

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice4_2026-03-19.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice4_2024_v1.yaml`
- STRICT evidence anchors:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- Stop if more than the three scoped files need to change.
- Stop if any `tmp/**`, `results/**`, DB, smoke artifact, or run launch becomes necessary.
- Stop if any edit is needed under `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`.
- Stop if the hypothesis requires reopening legacy authority, clarity, or broad threshold-topology search.
- Stop if validator or preflight indicates that the YAML semantics require code or test changes.

### Output required

- **Implementation Report**
- **PR evidence template**
- committed slice-4 YAML path
- committed command packet path
- committed context map path

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Slice-4 is experiment scaffolding only; it must not alter runtime defaults, incumbent champion behavior, or production authority semantics.
- Preserve RI family identity: `authority_mode=regime_module`, RI `v2`, `clarity_score.enabled=false`, `risk_state.enabled=true`, `atr_period=14`, gates `3/2`.
- Preserve train `2023-12-21..2024-06-30` and validation `2024-07-01..2024-12-31`.
- Use fresh `study_name`, fresh `storage`, `resume=false`, `promotion.enabled=false`, and `n_jobs=1`.
- No long run, smoke launch, temp YAML, or temp DB creation belongs to this slice; any execution must be packeted separately.
