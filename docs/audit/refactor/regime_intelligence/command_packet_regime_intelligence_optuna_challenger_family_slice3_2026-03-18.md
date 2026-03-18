## COMMAND PACKET

- **Mode:** `STRICT` — source: explicit task override; branch `feature/*` would otherwise resolve to `RESEARCH`
- **Category:** `obs`
- **Risk:** `HIGH` — why: execution-only optimizer/backtest evidence task in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Create and execute a third RI challenger-family Optuna slice for `tBTCUSD 3h` that changes the hypothesis away from slice-2 threshold-only refinement and instead targets generalization-sensitive surfaces while preserving the RI family identity.
- **Candidate:** `ri challenger family slice3`
- **Base SHA:** `eb005af4`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md`
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml`
  - uncommitted `tmp/*` smoke YAML + tmp smoke DB
  - background execution of the committed slice-3 YAML after gates pass
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - committed `results/**`
  - blind-2025 execution
  - promotion/default/cutover semantics
  - legacy-authority reopening
  - clarity search reopening
- **Expected changed files:** `3`
- **Max files touched:** `4`

### Execution Preconditions

- working tree must be clean before launch
- canonical execution flags must be set:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `GENESIS_RANDOM_SEED=42`
  - `PYTHONPATH=src`
- committed slice-3 storage DB must not already exist while `resume=false`
- repo-local skill `optuna_run_guardrails` governs validator + preflight + canonical mode for this run
- baseline proof may reuse `tmp/champion_validation_eb005af4.log` (score `0.2617`) because slice-3 changes only docs plus isolated optimizer config on base SHA `eb005af4`; a fresh incumbent rerun becomes mandatory if the SHA changes or if any file under `src/**`, `config/runtime.json`, or `config/strategy/champions/**` changes

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml`
- Temporary smoke-step before background launch:
  - derive an uncommitted smoke YAML under `tmp/`
  - use unique temporary `study_name` + `storage`
  - run a reduced-budget optimizer start to prove the config boots cleanly without storage reuse ambiguity
- STRICT evidence anchors before background launch:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- Any need to touch `src/**`, `tests/**`, `config/runtime.json`, or champion files
- Any attempt to widen the slice into legacy-authority or clarity exploration
- Any reuse of an existing storage DB while `resume=false`
- Any implication that slice-3 execution grants automatic promotion authority
- Any need to commit `results/**` or temporary smoke artifacts as part of this slice
- Any evidence that the new YAML cannot be validated, preflighted, and smoke-started cleanly

### Output required

- **Implementation Report**
- **PR evidence template**
- **Config artifact:** `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice3_2024_v1.yaml`
- **Launch evidence:** exact HEAD, canonical env flags, smoke artifact paths, background terminal id, and expected committed result paths

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Slice-3 is experiment scaffolding plus background execution only; it must not alter runtime defaults or incumbent champion behavior.
- Preserve RI family identity: `authority_mode=regime_module`, RI `v2`, `clarity_score.enabled=false`, `risk_state.enabled=true`, `atr_period=14`, gates `3/2`.
- Preserve train `2023-12-21..2024-06-30` and validation `2024-07-01..2024-12-31`.
- Use fresh `study_name`, fresh `storage`, `resume=false`, `promotion.enabled=false`, and `n_jobs=1`.
- Hypothesis shift for slice-3: keep threshold family narrower than slice-2 while opening exit, LTF-override, and Fib-tolerance surfaces that are more likely to affect generalization.
- Blind 2025 remains a separate follow-up after candidate freeze.
