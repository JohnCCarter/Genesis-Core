## COMMAND PACKET

- **Mode:** `STRICT` — source: explicit governance/task override; branch `feature/*` would otherwise resolve to `RESEARCH`
- **Risk:** `HIGH` — why: closure slice touches runtime strategy entrypoints and retires a legacy RI compatibility shim while preserving behavior in a high-sensitivity decision path
- **Required Path:** `Full`
- **Objective:** Complete the remaining no-behavior-change Regime Intelligence migration closure by redirecting runtime and tests from `core.strategy.regime_intelligence` to canonical intelligence/config helpers, moving the remaining RI risk-state helper into the intelligence layer, and retiring the strategy shim without changing default authority semantics.
- **Candidate:** `regime intelligence migration closure`
- **Base SHA:** `d58fe2f067996d91c05ca0fa17ab8bc170d31067`

### Scope

- **Scope IN:**
  - `src/core/strategy/evaluate.py`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/intelligence/regime/__init__.py`
  - `src/core/intelligence/regime/risk_state.py`
  - `src/core/strategy/regime_intelligence.py`
  - `tests/backtest/test_evaluate_pipeline.py`
  - `tests/backtest/test_evaluate_regime_precomputed_index.py`
  - `tests/core/intelligence/regime/test_clarity.py`
  - `tests/core/intelligence/regime/test_htf.py`
  - `tests/governance/test_authority_mode_resolver.py`
  - `tests/governance/test_phase2_merge_authority_bypass_contracts.py`
  - `tests/utils/test_risk_state_multiplier.py`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_migration_closure_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_migration_closure_2026-03-17.md`
- **Scope OUT:**
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - `src/core/research_ledger/**`
  - `src/core/research_orchestrator/**`
  - changes to `multi_timeframe.regime_intelligence.authority_mode` default value
  - changes to authority precedence/fallback semantics
  - changes to sizing math, clarity math, HTF regime math, or shadow-regime decision semantics
  - new wrapper/compat indirection beyond the minimum local test seams in `evaluate.py`
- **Expected changed files:** `10-14`
- **Max files touched:** `14`

### Gates required

- `pre-commit run --all-files`
- `python -m black --check src/core/strategy/evaluate.py src/core/strategy/decision_sizing.py src/core/intelligence/regime tests/backtest/test_evaluate_pipeline.py tests/backtest/test_evaluate_regime_precomputed_index.py tests/core/intelligence/regime tests/governance/test_authority_mode_resolver.py tests/governance/test_phase2_merge_authority_bypass_contracts.py tests/utils/test_risk_state_multiplier.py docs/audit/refactor/regime_intelligence`
- `python -m ruff check src/core/strategy/evaluate.py src/core/strategy/decision_sizing.py src/core/intelligence/regime tests/backtest/test_evaluate_pipeline.py tests/backtest/test_evaluate_regime_precomputed_index.py tests/core/intelligence/regime tests/governance/test_authority_mode_resolver.py tests/governance/test_phase2_merge_authority_bypass_contracts.py tests/utils/test_risk_state_multiplier.py`
- `python -m bandit -r src/core/intelligence/regime src/core/strategy -c bandit.yaml`
- `python -m pytest tests/core/intelligence/regime/test_clarity.py -q`
- `python -m pytest tests/core/intelligence/regime/test_htf.py -q`
- `python -m pytest tests/utils/test_risk_state_multiplier.py -q`
- `python -m pytest tests/governance/test_authority_mode_resolver.py -q`
- `python -m pytest tests/governance/test_phase2_merge_authority_bypass_contracts.py -q`
- `python -m pytest tests/backtest/test_evaluate_pipeline.py -q`
- `python -m pytest tests/backtest/test_evaluate_regime_precomputed_index.py -q`
- `python -m pytest tests/backtest/test_regime_shadow_artifacts.py -q`
- `python -m pytest tests/utils/test_decision.py -q`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py -q`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py -q`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q`

### Stop Conditions

- Any requirement to change default `authority_mode` semantics or fallback precedence
- Any change in runtime outputs for legacy/default path beyond import ownership
- Any need to touch unrelated high-sensitivity files outside Scope IN
- Any sign that shim retirement requires external/public compatibility guarantees not covered by repository tests
- Any drift in `meta.observability.shadow_regime` shape or `decision_sizing.py` `state_out` RI keys/semantics
- Any implementation path that requires removing or renaming `evaluate.py` local seam `_detect_shadow_regime_from_regime_module`
- Any determinism or pipeline hash regression

### Output required

- **Implementation Report**
- **PR evidence template**

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Preserve default `authority_mode="legacy"`
- Preserve canonical-vs-alias precedence and invalid-value fallback behavior exactly
- Preserve evaluate.py local monkeypatch seams where tests rely on them
- Prefer direct imports from canonical intelligence/config modules over creating new wrapper layers
- If a small new helper module is needed, it must be a real domain component with stable responsibility; `risk_state.py` is the only anticipated new module in this slice
