# Status: `föreslagen / execution conditionally gated / not approved or performed by this document`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — why: local backtest-comparison evidence task in a high-sensitivity champion/promotion decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Execute one governed same-head comparison for `tBTCUSD 3h` between the named slice8 RI lead research candidate surface and the incumbent same-head control artifact under canonical comparison mode, while keeping promotion/writeback/default semantics explicitly out of scope.
- **Candidate:** `ri challenger family incumbent comparison execution`
- **Base SHA:** `e339e026460639a8946e3744f0314cac819df674`
- **Applied repo-local skill:** `genesis_backtest_verify`

### Skill Usage

- Applied repo-local skill: `genesis_backtest_verify`
- Purpose: keep the backtest comparison deterministic and artifact-focused
- No `optuna_run_guardrails` coverage is claimed here because this packet is a backtest-comparison task, not a long Optuna run

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_2026-03-26.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `config/strategy/champions/**` as changed files
  - committed `results/**`
  - runtime/default/cutover semantics
  - promotion/writeback/champion-declaration semantics
  - any widening from one primary incumbent comparator to broader multi-comparator logic
- **Expected changed files:** `1`
- **Max files touched:** `1`

### Upstream governed basis

This packet is downstream of the following already tracked RI research decisions:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_anchor_decision_governance_review_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_incumbent_comparison_prep_packet_2026-03-26.md`

These upstream artifacts establish only the following:

- the slice8-backed backbone is approved as **research anchor only**
- the slice8 full tuple is the named **lead RI research candidate**
- slice9 is **supporting robustness evidence only**
- no promotion, champion replacement, writeback, default/runtime change, or cutover is approved

### Comparison surfaces

#### RI candidate surface

The RI side of this comparison is the named slice8 full tuple:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`
- `exit.max_hold_bars=8`
- `exit.exit_conf_threshold=0.42`
- `multi_timeframe.ltf_override_threshold=0.40`

This packet treats that surface as a **research comparison candidate only**.

It does **not** treat it as:

- a promoted candidate
- a new champion
- a runtime-approved configuration
- a writeback-ready artifact

#### Primary comparator surface

The only primary comparator surface in this packet is the incumbent same-head control artifact:

- `results/backtests/tBTCUSD_3h_20260324_170603.json`

Observed comparator context from that artifact:

- total return: `0.42059270143001415%`
- profit factor: `1.8721119891064304`
- max drawdown: `1.4705034784627329%`
- trades: `37`

#### Background context only

The current bootstrap champion file is background context only:

- `config/strategy/champions/tBTCUSD_3h.json`

It is not an execution input and not a second decision comparator in this packet.

### Candidate materialization rule

This packet does **not** approve direct execution from raw `results/hparam_search/run_20260324_174006/validation/trial_001.json` as an unconditional canonical config input.

Reason:

- that artifact still carries the known metadata quirk `merged_config.strategy_family=legacy`
- the RI line must remain semantically separated from legacy-family interpretation

Therefore the approved local execution path is narrower:

1. materialize a **local, untracked** candidate input JSON under:
   - `tmp/ri_candidate_materializations/tBTCUSD_3h_slice8_trial_001_runtime_override.json`
2. copy only the `parameters` payload from:
   - `results/hparam_search/run_20260324_174006/validation/trial_001.json`
3. do **not** carry forward `merged_config`
4. let `scripts/run/run_backtest.py` resolve the effective config by runtime-merge from the materialized `parameters` surface

This path is valid only if a separate local resolution-proof step confirms that the effective candidate surface still resolves to the intended RI comparison shape.

Required local proof artifact before launch:

- `tmp/ri_candidate_materializations/tBTCUSD_3h_slice8_trial_001_resolution_proof.json`

This materialization step is containment, not scope expansion.

Local temporary material under `tmp/**` remains out of tracked commit scope.

### Execution provenance and mode discipline

- Preferred launch state: clean working tree.
- Dirty-tree launch is not approved.
- Any dirty path blocks launch until re-reviewed.
- Canonical env flags must be set exactly:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `GENESIS_RANDOM_SEED=42`
  - `PYTHONPATH=src`
- Comparison window must remain the same-head validation window:
  - start: `2024-07-01`
  - end: `2024-12-31`
- Symbol/timeframe must remain:
  - symbol: `tBTCUSD`
  - timeframe: `3h`
- Economics must remain explicit to match the incumbent artifact framing:
  - capital: `10000`
  - commission: `0.002`
  - slippage: `0.0005`
  - warmup: `120`

### Preconditions

Before local execution, all of the following must be true:

1. the tracked docs packet in Scope IN has passed docs validation
2. the working tree is clean
3. the source candidate artifact exists:
   - `results/hparam_search/run_20260324_174006/validation/trial_001.json`
4. the incumbent comparator artifact exists:
   - `results/backtests/tBTCUSD_3h_20260324_170603.json`
5. the local materialized candidate file exists under `tmp/**`
6. the local materialized candidate file contains only a `parameters` object and no `merged_config`
7. a local resolution-proof artifact exists under `tmp/**` and records the resolved effective candidate surface prior to launch
8. the local resolution proof shows all of the following:

- `multi_timeframe.regime_intelligence.enabled=true`
- `multi_timeframe.regime_intelligence.authority_mode=regime_module`
- the named slice8 tuple values for the seven comparison axes listed above
- no silent fallback to bootstrap champion comparison semantics

9. if the resolved proof does not report top-level `strategy_family=ri` exactly — including missing, null, inherited, or legacy-valued resolution — the parameters-only execution path is blocked and must not launch under this packet
10. the materialized candidate still contains the named slice8 tuple values for the seven comparison axes listed above
11. execution uses canonical mode only; no mixed-mode or debug-mode comparison is allowed
12. `--compare-warn-only` is **not** allowed for this packet

### Launch command

The governed launch command for the RI candidate side must be:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-07-01 --end 2024-12-31 --capital 10000 --commission 0.002 --slippage 0.0005 --warmup 120 --config-file tmp/ri_candidate_materializations/tBTCUSD_3h_slice8_trial_001_runtime_override.json --compare results/backtests/tBTCUSD_3h_20260324_170603.json`

The launch may save local outputs under `results/backtests/**`, but those outputs remain outside commit scope unless a later governed packet explicitly reopens that scope.

The launch is valid only if the pre-launch resolution proof remains consistent with the executed candidate surface.

### Evidence rules

A valid run under this packet must report all of the following:

- whether the candidate backtest completed successfully
- whether the candidate artifact was comparable to the incumbent same-head control under `run_backtest --compare`
- the path to the local resolution-proof artifact and its resolved RI-surface summary
- the candidate score and core metrics
- the printed metric delta versus the incumbent artifact
- whether the result reads as:
  - `candidate stronger`
  - `candidate weaker`
  - `inconclusive`

The packet must also keep these disclosures explicit:

- this is a local governed research comparison only
- the bootstrap champion file remains background context only
- the legacy/RI metadata quirk remains disclosed and is partially contained here by materializing from `parameters` only

### Success rule for this packet

This packet counts as successful only if it produces one of these bounded outputs:

1. `comparison evidence collected / candidate stronger`
2. `comparison evidence collected / candidate weaker`
3. `comparison evidence collected / inconclusive`

This packet does **not** require the RI candidate to win.

Its job is to produce a governed comparison outcome, not to force a promotion conclusion.

### Post-run decision boundary

This packet may conclude only comparison-status language.

It must **not** conclude:

- promotion approved
- champion replaced
- writeback approved
- default/runtime change approved
- RI family canonically promoted over legacy

Required safe framing:

- this packet describes only a local, governed research comparison between one artifact-derived RI candidate surface and one explicit incumbent artifact
- this packet does not constitute promotion, writeback, champion decision, runtime approval, default change, or family reclassification

### Gates required before launch

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_2026-03-26.md`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/governance/test_authority_mode_resolver.py`

### Stop Conditions

- Stop if more than the one scoped packet file needs to change.
- Stop if any tracked file under `src/**`, `tests/**`, or `config/**` must change.
- Stop if the candidate materialization requires carrying forward `merged_config` to stay runnable.
- Stop if the local resolution-proof step cannot demonstrate the intended RI authority/backbone before launch.
- Stop if the materialized candidate no longer cleanly represents the named slice8 tuple.
- Stop if `run_backtest --compare` raises a comparability failure.
- Stop if local execution would require `--compare-warn-only`.
- Stop if the packet drifts into promotion/writeback/default/champion claims.

### Output required

- **Implementation Report**
- **PR evidence template**
- materialized local candidate path under `tmp/**`
- local resolution-proof path under `tmp/**`
- exact launch command and env flags used
- local result path under `results/backtests/**` if generated
- comparison classification: `candidate stronger`, `candidate weaker`, or `inconclusive`
- explicit reminder that promotion/writeback/default/runtime change remains out of scope
