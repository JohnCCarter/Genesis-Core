## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — why: execution-only optimizer/backtest evidence task in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Execute the already-created slice-8 RI challenger-family Optuna campaign for `tBTCUSD 3h` under canonical comparison flags and determine whether a bounded widen-search can either improve on slice7 directly or reduce duplicate collapse enough to inform a later anchor-decision packet.
- **Candidate:** `ri challenger family slice8 execution`
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
  - promotion/default/cutover semantics
  - anchor declaration semantics
  - legacy-authority reopening
  - clarity search reopening
  - blind-2025 execution
  - YAML parameter changes unless a pure typo/path fix is required before launch

### Execution provenance

- Preferred launch state: clean working tree.
- Dirty-tree launch is **not approved** for slice-8.
- Any dirty path blocks launch.
- If a clean tree cannot be obtained, stop and request fresh governance review before execution.
- Launch is **gated by post-diff audit**: do not execute until the four slice-8 files have passed post-code governance review and all required gates below are green.

### Runtime artifacts (local only, not scope-expanding)

- launch target: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- expected local outputs under `results/hparam_search/run_*`
- expected local storage DB `results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1.db`

### Baseline anchors for comparison

Slice-8 comparisons must use these governed references:

- slice7 validation winner: `0.26974911658712664`
- slice6 plateau: `0.23646934335498004`
- slice4 plateau: `0.22516209452403432`
- slice3 plateau: `0.22289051935876203`
- incumbent same-head control: `0.2616884080730424`
- slice7 duplicate ratio: `0.90625`

### Preconditions

- canonical env flags must be set exactly:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `GENESIS_RANDOM_SEED=42`
  - `PYTHONPATH=src`
- exact launch YAML must still declare `meta.runs.run_intent: research_slice`
- rerun `validate_optimizer_config.py` on the exact launch tree immediately before launch
- rerun `preflight_optuna_check.py` on the exact launch tree immediately before launch
- verify that `results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1.db` does **not** already exist while `resume=false`
- launch command must be:
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m core.optimizer.runner config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- no blind-2025 run belongs to this packet

### Evidence rules

- Compare the slice-8 validation winner directly against:
  - slice7 validation winner `0.26974911658712664`
  - slice6 plateau `0.23646934335498004`
  - slice4 plateau `0.22516209452403432`
  - slice3 plateau `0.22289051935876203`
- Treat incumbent `0.2616884080730424` as the governed current-head same-window same-canonical-mode control.
- Compare slice-8 duplicate ratio directly against slice7 duplicate ratio `0.90625`.
- Fresh launch evidence is mandatory; older pytest evidence is not sufficient by itself for execution approval.

### Success rule for this packet

Slice-8 counts as a successful widen-search only if it returns one of the following governed outcomes:

1. a validation winner that **strictly exceeds** the slice7 validation score `0.26974911658712664`, or
2. a duplicate ratio of `<= 0.70` while keeping the validation winner at or above the slice6 plateau `0.23646934335498004`.

Anything weaker may be recorded as evidence, but must be reported as **widen-search not confirmed for anchor decision**.

### Post-run decision gate

- This packet may conclude only one of the following statuses:
  - `widen-search evidence collected`
  - `widen-search blocked`
- This packet must **not** declare a new RI anchor.
- This packet must **not** promote, freeze, or default any winner.
- Any anchor, candidate, blind, promotion, or freeze decision must be packeted separately after reviewing the slice-8 outcome.

### Gates required

- file-scoped pre-launch checks:
  - `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice8_2026-03-24.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice8_execution_2026-03-24.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
  - `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
  - storage DB absence check
- mandatory runtime-governance anchors before launch:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- working tree is not clean at launch time
- storage DB already exists while `resume=false`
- validator or preflight fails on the exact launch tree
- any mandatory runtime-governance anchor fails
- launch would require editing `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`
- comparison would rely on non-canonical mode
- anyone attempts to reinterpret the run as automatic anchor/promotion/freeze authority

### Output required

- **Implementation Report**
- exact launch command and env flags used
- exact `HEAD` SHA and clean/dirty state at launch time
- storage DB path
- created run directory path
- `run_meta.json` path
- `best_trial.json` path
- validation winner summary
- comparison versus slice7, slice6 plateau, slice4 plateau, slice3 plateau, and incumbent same-head control status
- duplicate-ratio comparison versus slice7
- explicit statement that anchor/promotion/freeze/default decision remains deferred

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This packet approves only widen-search challenger evidence collection, not promotion or anchor selection.
- No edits to runtime defaults, champion files, or source/test logic are allowed as part of this execution step.
- Use fresh `study_name`, fresh sqlite path, `resume=false`, `n_jobs=1`, and `promotion.enabled=false` exactly as declared in the slice-8 YAML.
- If the run surfaces a promising winner, any anchor/candidate/blind/promotion discussion must be packeted separately.
