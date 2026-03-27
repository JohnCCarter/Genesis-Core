# Regime Intelligence challenger family — SIGNAL regime-definition slice1 pre-code command packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / research-only / enablement-backed`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `HIGH` — why: this packet opens the first research slice on a newly enabled regime-definition surface inside the authoritative `regime_module` path, but must remain research-only and must not reopen runtime validity, comparison, readiness, promotion, or writeback.
- **Required Path:** `Full gated docs-only`
- **Objective:** Define exactly one minimal first regime-definition research slice that varies only the newly enabled ADX-band thresholds in the `regime_module` regime-definition surface while keeping all downstream signal, decision, exit, and family surfaces fixed.
- **Candidate:** `RI SIGNAL regime-definition slice1 ADX-band research lane`
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

### Skill Usage

- **Applied repo-local skill/spec:** `.github/skills/optuna_run_guardrails.json`
- **Usage mode in this packet:** guardrail/reference only at pre-code stage; this packet itself performs no validator run, preflight run, smoke run, optimizer run, comparison, readiness, promotion, or writeback.
- **No dedicated repo skill found for:** regime-definition slice construction on the newly enabled `regime_module` config surface.

### Scope

- **Scope IN:** one docs-only pre-code packet that selects exactly one regime-definition hypothesis, defines the exact future YAML surface, defines what remains fixed, defines the exact future artifacts, and defines the falsification condition for the first enabled regime-definition lane.
- **Scope OUT:** no source-code changes, no further changes under `src/core/**`, no `family_registry.py` change, no `family_admission.py` change, no validator/preflight execution in this packet, no smoke run, no full optimizer run, no comparison opening, no readiness opening, no promotion opening, no writeback.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_signal_regime_definition_slice1_precode_command_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the future slice remains research-only and bounded to the enabled regime-definition surface

For interpretation discipline inside this packet:

- exactly one regime-definition hypothesis must be selected
- the future slice must remain inside the enabled `multi_timeframe.regime_intelligence.regime_definition` surface
- no sentence may reinterpret `research_slice` as runtime-valid RI conformity
- no sentence may change or soften `family_registry.py` or `family_admission.py`
- no sentence may open comparison, readiness, promotion, runtime materialization, or writeback

### Stop Conditions

- any wording that widens beyond the enabled ADX-band surface
- any wording that makes research-only outputs count as runtime-valid RI conformity
- any wording that changes or reinterprets family rules by implication
- any wording that opens comparison, readiness, promotion, runtime materialization, or writeback

### Output required

- reviewable pre-code command packet
- exact regime-definition hypothesis
- exact future YAML/search surface
- exact fixed backdrop
- exact future artifacts
- exact falsification condition
- exact research-only output boundary

## Purpose

This packet answers one narrow question only:

- what is the first admissible, minimal, testable regime-definition slice after the threshold-only SIGNAL surface closed as plateau and the canonical regime-definition config surface was enabled?

This packet authorizes only a **research-only** slice under `run_intent=research_slice` for tuning the newly enabled ADX-band regime-definition surface.

This packet does **not**:

- establish runtime-valid RI family conformity
- change the canonical RI cluster in `src/core/strategy/family_registry.py`
- change family admission rules in `src/core/strategy/family_admission.py`
- open comparison, readiness, promotion, runtime materialization, or champion/default writeback
- authorize feature-surface or DECISION surfaces

Any YAML or run artifact produced by the future slice remains research-only and must not be treated as family-rule precedent, runtime authority, or promotion authority.

## Governing basis

This packet is downstream of the following tracked artifacts and verified code state:

- `docs/governance/regime_intelligence_optuna_signal_regime_definition_direction_packet_2026-03-27.md`
- `docs/governance/regime_intelligence_optuna_signal_regime_definition_enablement_command_packet_2026-03-27.md`
- `src/core/strategy/regime.py`
- `src/core/strategy/evaluate.py`
- `src/core/config/schema.py`
- `src/core/config/authority.py`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`

Carried-forward meaning from those artifacts:

1. the broader `SIGNAL` class remains open, but the threshold-only surface is closed as `PLATEAU`
2. the next chosen direction is `SIGNAL / regime-definition surface`
3. the canonical runtime/config path now supports the bounded `multi_timeframe.regime_intelligence.regime_definition` surface with default-parity preserved when absent
4. RI research slices under `run_intent=research_slice` may vary this enabled surface without changing runtime family authority
5. no further `src/core/**` changes are required for the first runnable slice

Nothing in this packet changes, reinterprets, or creates exceptions to existing family rules.
`research_slice` admission remains separate from runtime-valid RI conformity.

## 1) Exact regime-definition hypothesis

The exact first regime-definition hypothesis is:

- **A bounded change to the authoritative `regime_module` ADX-band thresholds may break the tracked plateau without changing downstream threshold, decision, exit, objective, or family surfaces.**

### Exact tunable dimensions for the future slice

Only the following two enabled regime-definition dimensions may vary:

- `multi_timeframe.regime_intelligence.regime_definition.adx_trend_threshold`
- `multi_timeframe.regime_intelligence.regime_definition.adx_range_threshold`

The exact bounded future search grid is:

- `multi_timeframe.regime_intelligence.regime_definition.adx_trend_threshold ∈ {23.0, 25.0, 27.0}`
- `multi_timeframe.regime_intelligence.regime_definition.adx_range_threshold ∈ {18.0, 20.0, 22.0}`

Total bounded future grid cardinality:

- `3 × 3 = 9`

The selected values preserve ordering for every combination:

- `adx_range_threshold < adx_trend_threshold`

### Exact tuple set for the future slice

The only admissible tuples are:

1. `(adx_trend_threshold=23.0, adx_range_threshold=18.0)`
2. `(adx_trend_threshold=23.0, adx_range_threshold=20.0)`
3. `(adx_trend_threshold=23.0, adx_range_threshold=22.0)`
4. `(adx_trend_threshold=25.0, adx_range_threshold=18.0)`
5. `(adx_trend_threshold=25.0, adx_range_threshold=20.0)`
6. `(adx_trend_threshold=25.0, adx_range_threshold=22.0)`
7. `(adx_trend_threshold=27.0, adx_range_threshold=18.0)`
8. `(adx_trend_threshold=27.0, adx_range_threshold=20.0)`
9. `(adx_trend_threshold=27.0, adx_range_threshold=22.0)`

No other tuple is admissible in this slice.

### Exact non-tunable regime-definition fields for the future slice

The following enabled regime-definition fields remain fixed in the future slice:

- `multi_timeframe.regime_intelligence.regime_definition.slope_threshold = 0.001`
- `multi_timeframe.regime_intelligence.regime_definition.volatility_threshold = 0.05`

These two fields are canonical fixed backdrops for this slice and must not be left implicit, widened, or tuned.

## 2) Exact files/modules allowed to change

The future first regime-definition slice is intentionally **config-only** on top of the already merged enablement.

### Allowed tracked file changes

Exactly the following future tracked files may be created or changed:

1. `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`
2. `docs/governance/regime_intelligence_optuna_signal_regime_definition_slice1_launch_authorization_packet_2026-03-27.md`
3. `docs/governance/regime_intelligence_optuna_signal_regime_definition_slice1_execution_outcome_signoff_summary_2026-03-27.md`

### Allowed temporary / generated artifacts

The following future temporary or generated artifacts are permitted:

1. `tmp/tBTCUSD_3h_ri_signal_regime_definition_slice1_smoke_20260327.yaml`
2. `results/hparam_search/ri_signal_regime_definition_slice1_smoke/`
3. `results/hparam_search/ri_signal_regime_definition_slice1_launch_20260327/`
4. `results/hparam_search/storage/ri_signal_regime_definition_slice1_3h_2024_v1.db`

Temporary YAMLs and generated run artifacts are non-authoritative research outputs only.
They must not be treated as runtime defaults, canonical RI artifacts, or promotion candidates.

### Forbidden file/module changes

No future slice changes are allowed in:

- `src/core/**`
- `scripts/**`
- `config/runtime/**`
- `config/strategy/champions/**`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`

No Python module changes are allowed in this first regime-definition slice.

## 3) What remains fixed

The future slice must preserve the threshold-slice research backdrop except for the exact two tunable ADX-band fields named above.

### Fixed family / authority backdrop

The following remain fixed:

- `strategy_family = ri`
- `meta.runs.run_intent = research_slice`
- `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- `thresholds.signal_adaptation.atr_period = 14`

### Fixed downstream threshold / gating backdrop

The following remain fixed:

- `thresholds.entry_conf_overall = 0.27`
- `thresholds.regime_proba.balanced = 0.36`
- `thresholds.signal_adaptation.zones.low.entry_conf_overall = 0.14`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall = 0.42`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall = 0.34`
- `thresholds.signal_adaptation.zones.low.regime_proba = 0.32`
- `thresholds.signal_adaptation.zones.mid.regime_proba = 0.52`
- `thresholds.signal_adaptation.zones.high.regime_proba = 0.58`
- `gates.hysteresis_steps = 4`
- `gates.cooldown_bars = 1`
- `thresholds.min_edge = 0.01`
- `multi_timeframe.ltf_override_threshold = 0.38`

### Fixed non-regime-definition behavior backdrop

The following remain fixed:

- decision / EV / confidence logic
- gating semantics
- exit / management surface
- objective / scoring surface
- risk-state and sizing surface
- HTF/LTF fib surface
- family-registry and family-admission rules
- champion/runtime/default state
- comparison closed
- readiness closed
- promotion closed

## 4) Exact artifacts to produce

The future first regime-definition slice must produce exactly the following artifact set.

### A. Exact launch-subject YAML

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_regime_definition_slice1_2024_v1.yaml`

This YAML must:

- declare `strategy_family: ri`
- declare `strategy: grid`
- declare `run_intent: research_slice`
- keep the fixed backdrop above unchanged
- expose only the exact two tunable dimensions defined in this packet
- explicitly set the two fixed regime-definition fields (`slope_threshold`, `volatility_threshold`)
- enumerate the exact bounded `3 × 3 = 9` search grid
- use `resume=false`
- keep promotion disabled

### B. Exact pre-launch validation proofs

The future slice must produce green evidence for:

1. optimizer config validation on the exact launch subject
2. preflight validation on the exact launch subject under canonical flags
3. bounded smoke success on the exact launch subject or its bounded smoke derivative
4. carry-forward HIGH/STRICT invariants on the verified enablement base:
   - determinism smoke
   - pipeline component order hash
   - feature-cache invariance

These proofs may be cited inside the future signoff summary rather than committed as standalone tracked logs.

### C. Exact research-run artifacts

The future slice must produce:

1. bounded smoke artifacts under `results/hparam_search/ri_signal_regime_definition_slice1_smoke/`
2. bounded research-only optimizer artifacts under `results/hparam_search/ri_signal_regime_definition_slice1_launch_20260327/`

### D. Exact research-only signoff summary

The future slice must produce:

- `docs/governance/regime_intelligence_optuna_signal_regime_definition_slice1_execution_outcome_signoff_summary_2026-03-27.md`

That summary must remain research-only and must not frame outcomes as runtime-validity, comparison authority, readiness authority, promotion authority, or writeback authority.

## 5) Golden plateau reference and falsification condition

The golden plateau reference for this slice remains the already tracked plateau evidence, with the following exact signature tuple:

- validation score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`

The future first regime-definition slice is falsified if either of the following is true:

1. no validated artifact from the bounded 9-trial slice exceeds validation score `0.26974911658712664`, or
2. the best validated artifact reproduces the exact plateau signature tuple above without verified improvement geometry

For this slice, simple reproduction of the plateau is not success.
It counts as non-breaking confirmation of the existing plateau.

## 6) Expected research-only outputs

The future first regime-definition slice is expected to emit only the following research-only outputs:

- one research-only launch-subject YAML
- validator/preflight/smoke proof citations
- bounded research-only grid-run artifacts
- one research-only governance signoff summary

These outputs are sufficient only for:

- research execution
- research validation
- research analysis

These outputs are **not** sufficient for:

- runtime-valid RI family conformity claims
- comparison opening
- readiness opening
- promotion opening
- runtime materialization
- champion/default writeback
- family-rule reinterpretation

## Authority boundary

This slice is research-only under `run_intent=research_slice` and does not establish runtime-valid RI family conformity.

This packet does not change RI family rules, runtime authority, or the canonical RI cluster in `src/core/strategy/family_registry.py`.

This packet opens neither comparison, readiness, promotion, runtime materialization, champion/default writeback, nor any new canonical comparison surface.

## Bottom line

The first admissible regime-definition slice is now defined as a **config-only, research-only, bounded 9-trial ADX-band slice** that:

- tunes only `multi_timeframe.regime_intelligence.regime_definition.{adx_trend_threshold,adx_range_threshold}`,
- fixes `slope_threshold` and `volatility_threshold` at canonical defaults,
- keeps downstream threshold, decision, exit, objective, and family surfaces fixed,
- changes no Python modules,
- produces only research-only YAML/run/signoff artifacts, and
- is falsified unless it beats the tracked plateau signature.

That is the narrowest admissible first regime-definition slice after the enablement packet.
