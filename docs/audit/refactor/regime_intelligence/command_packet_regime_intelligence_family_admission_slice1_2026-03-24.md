## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `tooling`
- **Risk:** `HIGH` — why: refactor of optimizer/preflight family guardrails adjacent to high-sensitivity RI launch semantics; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Introduce a governed `run_intent`-aware family admission split so optimizer validation and preflight distinguish structural validity, family identity, and family admission policy without changing runtime defaults or backtest execution semantics.
- **Candidate:** `ri family admission slice1`
- **Base SHA:** `601efdd00552a4de9e5d6cce54a58c84725e593c`
- **Applied repo-local skills:** `python_engineering`, `repo_clean_refactor`

### Scope

- **Scope IN:**
  - `src/core/strategy/family_registry.py`
  - `src/core/strategy/run_intent.py`
  - `src/core/strategy/family_admission.py`
  - `scripts/validate/validate_optimizer_config.py`
  - `scripts/preflight/preflight_optuna_check.py`
  - `tests/core/strategy/test_families.py`
  - `tests/core/strategy/test_family_admission.py`
  - `tests/utils/test_validate_optimizer_config.py`
  - `tests/utils/test_preflight_optuna_check.py`
- **Scope OUT:**
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `config/optimizer/**` except read-only validation targets
  - `src/core/backtest/**`
  - `src/core/optimizer/runner.py`
  - `src/core/pipeline.py`
  - committed `results/**`
  - blind/promotion execution packets
  - runtime default changes
  - authority resolution semantics outside existing family validation surfaces
- **Expected changed files:** `9`
- **Max files touched:** `9`

### Problem statement frozen for this slice

Current guardrails conflate three separate concerns:

1. structural optimizer/preflight validity
2. strategy family identity (`legacy` vs `ri`)
3. stricter admission policy for a specific run purpose

This currently blocks legitimate RI research slices because `strategy_family=ri` implicitly requires the full canonical RI cluster, including exact canonical gates `3/2`, while preflight also undercounts searchable parameters by ignoring `type=int` ranges.

### Approved design target for this slice

This slice may implement only the following architectural split:

1. **Run intent contract**
   - introduce typed allowed values:
     - `research_slice`
     - `candidate`
     - `promotion_compare`
     - `champion_freeze`
2. **Family identity layer**
   - keep `family_registry.py` focused on identity + hybrid fail-fast detection
   - do not leave canonical RI freeze semantics hidden in identity validation
3. **Family admission layer**
   - new dedicated policy surface above identity
   - enforce stricter RI requirements per `run_intent`
4. **Validator/preflight integration**
   - structural checks remain structural
   - family errors remain identity-specific
   - admission errors become explicit run-intent/family-admission failures
5. **Searchability fix**
   - preflight must count `type=int` ranges as searchable parameters

### Hard boundaries

- **Default constraint:** `NO BEHAVIOR CHANGE`
- **Explicit permitted behavior change (tooling-only, scoped):** validator/preflight family-admission semantics may change only inside the scoped files so that:
  - `research_slice` can admit structurally valid, family-valid RI research configs
  - `candidate`, `promotion_compare`, and `champion_freeze` remain explicitly stricter where policy requires it
  - preflight counts `type=int` ranges as searchable
  - runtime/backtest/champion/default behavior remains unchanged
- No changes to backtest engine, runner execution semantics, champion defaults, or runtime authority resolution.
- No widening beyond validator/preflight/family guardrail surfaces.
- No silent reinterpretation of legacy configs as promotion-grade RI configs.
- Missing `run_intent` handling must be deterministic and explicit.
- Mixed/hybrid RI-vs-legacy suppressive surfaces must still fail fast.
- Slice7 must not be launched under this packet; at most it may be revalidated locally as a config target after code/test changes.

### Required gates

- pre-change and post-change lint / focused checks:
  - `python -m ruff check src/core/strategy scripts/validate scripts/preflight tests/core/strategy tests/utils`
- targeted pytest selectors:
  - `python -m pytest -q tests/core/strategy/test_families.py`
  - `python -m pytest -q tests/core/strategy/test_family_admission.py`
  - `python -m pytest -q tests/utils/test_validate_optimizer_config.py`
  - `python -m pytest -q tests/utils/test_preflight_optuna_check.py`
- explicit negative admissions proof must be present in targeted tests:
  - slice7-style RI gate-sweep accepted for `research_slice`
  - the same RI gate-sweep rejected for `champion_freeze`
- mandatory runtime-governance anchors before declaring slice complete:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`
- exact CLI validation targets after implementation:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`

### Minimum regression obligations

- Accept RI research-slice admission for a slice7-style gated RI config.
- Reject the same shape for `champion_freeze`.
- Reject mixed legacy/RI hybrid surfaces.
- Preserve explicit failure for invalid or missing strategy family declarations.
- Preserve structural failure messaging separately from admission failure messaging.
- Prove `type=int` ranges are counted as searchable in preflight.

### Stop Conditions

- Stop if `src/core/optimizer/runner.py`, `src/core/backtest/**`, or champion files must change.
- Stop if the identity/admission split cannot be implemented without changing authority resolution semantics.
- Stop if more than the nine scoped files are required.
- Stop if implementation requires adding an implicit default `run_intent` in config parsing, CLI wrappers, or validation entrypoints rather than an explicit fail-closed policy.
- Stop if new behavior outside validator/preflight/family-guardrail surfaces is needed.
- Stop if slice7 requires YAML or results-file edits beyond read-only validation.
- Stop if hidden high-sensitivity dependencies surface outside the packeted area.

### Output required

- **Implementation Report**
- **PR evidence template**
- exact file-level change summary
- exact gate commands + pass/fail outcomes
- validator/preflight result against slice7 config
- residual risks and follow-up backlog for later phases
