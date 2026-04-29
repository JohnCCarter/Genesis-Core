# Regime Intelligence challenger family — first admissible SIGNAL slice pre-code command packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / research-only / config-only SIGNAL slice`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet authorizes one minimal research-only SIGNAL slice under already defined admissibility rules, but does not modify runtime code, family rules, comparison authority, readiness authority, promotion authority, or writeback authority
- **Required Path:** `Quick`
- **Objective:** Authorize exactly one minimal, testable, research-only SIGNAL slice that varies only already implemented zone-entry signal thresholds and keeps all non-SIGNAL surfaces fixed.
- **Candidate:** `RI SIGNAL slice1 zone-entry-threshold research lane`
- **Base SHA:** `d227be7e`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Usage mode in this packet:** guardrail/reference only at pre-code stage; this packet itself performs no validator run, preflight run, smoke run, optimizer run, comparison, readiness, promotion, or writeback

### Scope

- **Scope IN:** one docs-only pre-code packet that selects exactly one minimal SIGNAL hypothesis, defines the exact future implementation surface, defines what remains fixed, defines exact future artifacts, defines the falsification condition, and defines expected research-only outputs for the first admissible SIGNAL slice.
- **Scope OUT:** no source-code changes, no config changes, no YAML creation in this packet, no changes under `src/core/**`, no changes under `scripts/**`, no changes under `config/runtime/**`, no changes under `config/strategy/champions/**`, no `family_registry.py` change, no `family_admission.py` change, no validator/preflight execution, no smoke run, no Optuna run, no comparison opening, no readiness opening, no promotion opening, no champion/default writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_first_admissible_slice_precode_command_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- manual wording audit that the future slice remains research-only and config-only

For interpretation discipline inside this packet:

- exactly one SIGNAL hypothesis must be selected
- the future slice must remain within already implemented runtime/config signal surfaces
- no sentence may reinterpret `research_slice` as runtime-valid RI conformity
- no sentence may change or soften `family_registry.py` or `family_admission.py`
- no sentence may open comparison, readiness, promotion, runtime materialization, or writeback

### Stop Conditions

- any wording that permits changes outside the exact future slice surface defined below
- any wording that makes research-only outputs count as runtime-valid RI family conformity
- any wording that changes or reinterprets family rules by implication
- any wording that opens comparison, readiness, promotion, runtime materialization, or writeback

### Output required

- reviewable pre-code command packet
- exact SIGNAL hypothesis
- exact future file/module surface
- exact fixed backdrop
- exact future artifacts
- exact falsification condition
- exact research-only output boundary

## Purpose

This packet answers one narrow question only:

- what is the first admissible, minimal, testable SIGNAL slice that may be opened under the current research-level launch admissibility framework?

This packet authorizes only a **research-only** slice under `run_intent=research_slice` for tuning already implemented signal thresholds.
The intended execution semantics for this first slice are exact grid enumeration inside the existing optimizer pipeline, not Optuna-sampler behavior.
The packet filename retains historical `optuna` naming for traceability only and does not change the governing grid-based execution semantics.

This packet does **not**:

- establish runtime-valid RI family conformity
- change the canonical RI cluster in `src/core/strategy/family_registry.py`
- change family admission rules in `src/core/strategy/family_admission.py`
- open comparison, readiness, promotion, runtime materialization, or champion/default writeback
- authorize DECISION or OBJECTIVE surfaces

Any YAML or run artifact produced by the future slice remains research-only and must not be treated as family-rule precedent, runtime authority, or promotion authority.

## Governing basis

This packet is downstream of the following current tracked artifacts and code surfaces:

- `docs/analysis/regime_intelligence/core/regime_intelligence_plateau_evidence_slice7_slice10_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_exit_override_plateau_closeout_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_lane_launch_admissibility_packet_2026-03-27.md`
- `.github/skills/optuna_run_guardrails.json`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice10_2024_v1.yaml`

Carried-forward meaning from those artifacts:

1. the exit/override-only lane is closed
2. the next chosen hypothesis class is exactly `SIGNAL`
3. research-level launch admissibility is already defined and remains distinct from runtime-level or promotion-level authority
4. `decision_gates.py` already consumes `thresholds.signal_adaptation.zones.<zone>.entry_conf_overall`
5. RI research slices under `run_intent=research_slice` may vary non-canonical RI threshold surfaces without changing runtime family authority

Nothing in this packet changes, reinterprets, or creates exceptions to existing family rules.
`research_slice` admission remains separate from runtime-valid RI conformity.

## 1) Exact SIGNAL hypothesis

The exact first SIGNAL hypothesis is:

- **A bounded change to already implemented zone-specific entry thresholds may break the slice7–slice10 plateau without changing ATR period, regime-probability thresholds, decision logic, exit logic, objective/scoring, or family authority.**

### Exact tunable dimensions for the future slice

Only the following three already implemented SIGNAL dimensions may vary:

- `thresholds.signal_adaptation.zones.low.entry_conf_overall`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall`

The exact bounded future search grid is:

- `thresholds.signal_adaptation.zones.low.entry_conf_overall ∈ {0.12, 0.14, 0.16}`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall ∈ {0.40, 0.42, 0.44}`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall ∈ {0.32, 0.34, 0.36}`

Total bounded future grid cardinality:

- `3 × 3 × 3 = 27`

### Exact non-tunable SIGNAL fields for the future slice

The following SIGNAL-adjacent fields remain fixed in the future slice:

- `thresholds.signal_adaptation.atr_period = 14`
- `thresholds.signal_adaptation.zones.low.regime_proba = 0.32`
- `thresholds.signal_adaptation.zones.mid.regime_proba = 0.52`
- `thresholds.signal_adaptation.zones.high.regime_proba = 0.58`

## 2) Exact files/modules allowed to change

The future first SIGNAL slice is intentionally **config-only**.

### Allowed tracked file changes

Exactly the following future tracked files may be created or changed:

1. `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`
2. `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_slice1_execution_outcome_signoff_summary_2026-03-27.md`

### Allowed temporary / generated artifacts

The following future temporary or generated artifacts are permitted:

1. `tmp/tBTCUSD_3h_ri_signal_slice1_smoke_20260327.yaml`
2. `results/hparam_search/ri_signal_slice1_smoke_20260327/`
3. `results/hparam_search/ri_signal_slice1_launch_20260327/`
4. `results/hparam_search/storage/ri_signal_slice1_3h_2024_v1.db`

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

No Python module changes are allowed in this first SIGNAL slice.

## 3) What remains fixed

The future slice must preserve the slice10 research backdrop except for the exact three tunable fields named above.

### Fixed family / authority backdrop

The following remain fixed:

- `strategy_family = ri`
- `meta.runs.run_intent = research_slice`
- `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- `thresholds.signal_adaptation.atr_period = 14`

### Fixed threshold / gating backdrop

The following remain fixed:

- `thresholds.entry_conf_overall = 0.27`
- `thresholds.regime_proba.balanced = 0.36`
- `gates.hysteresis_steps = 4`
- `gates.cooldown_bars = 1`
- `thresholds.min_edge = 0.01`

### Fixed non-SIGNAL behavior backdrop

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

The future first SIGNAL slice must produce exactly the following artifact set.

### A. Exact launch-subject YAML

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`

This YAML must:

- declare `strategy_family: ri`
- declare `strategy: grid`
- declare `run_intent: research_slice`
- keep the fixed backdrop above unchanged
- expose only the exact three tunable dimensions defined in this packet
- enumerate the exact bounded `3 × 3 × 3 = 27` search grid
- use `resume=false`
- keep promotion disabled

### B. Exact pre-launch validation proofs

The future slice must produce green evidence for:

1. optimizer config validation on the exact launch subject
2. preflight validation on the exact launch subject under canonical flags
3. bounded smoke success on the exact launch subject or its bounded smoke derivative

These proofs may be cited inside the future signoff summary rather than committed as standalone tracked logs.

### C. Exact research-run artifacts

The future slice must produce:

1. bounded smoke artifacts under `results/hparam_search/ri_signal_slice1_smoke_20260327/`
2. bounded research-only optimizer artifacts under `results/hparam_search/ri_signal_slice1_launch_20260327/`

### D. Exact research-only signoff summary

The future slice must produce:

- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_slice1_execution_outcome_signoff_summary_2026-03-27.md`

That summary must remain research-only and must not frame outcomes as runtime-validity, comparison authority, readiness authority, promotion authority, or writeback authority.

## 5) Golden plateau reference and falsification condition

The golden plateau reference for this slice is the already tracked plateau evidence and closeout chain, with the following exact signature tuple:

- validation score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`
- sharpe: `0.20047738907046656`

Golden reference citations:

- `docs/analysis/regime_intelligence/core/regime_intelligence_plateau_evidence_slice7_slice10_2026-03-27.md`
- `docs/decisions/regime_intelligence/optuna/decision/regime_intelligence_optuna_exit_override_plateau_closeout_2026-03-27.md`

The future first SIGNAL slice is falsified if either of the following is true:

1. no validated artifact from the bounded 27-trial slice exceeds validation score `0.26974911658712664`, or
2. the best validated artifact reproduces the exact plateau signature tuple above without verified improvement geometry

For this slice, simple reproduction of the plateau is not success.
It counts as non-breaking confirmation of the existing plateau.

## 6) Expected research-only outputs

The future first SIGNAL slice is expected to emit only the following research-only outputs:

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

The first admissible SIGNAL slice is now defined as a **config-only, research-only, bounded 27-trial zone-entry-threshold slice** that:

- tunes only `thresholds.signal_adaptation.zones.<low|mid|high>.entry_conf_overall`,
- executes as exact grid enumeration inside the existing optimizer pipeline,
- keeps `atr_period`, zone `regime_proba`, and all non-SIGNAL surfaces fixed,
- changes no Python modules,
- produces only research-only YAML/run/signoff artifacts, and
- is falsified unless it beats the tracked plateau signature.

That is the narrowest admissible first SIGNAL slice under the current framework.
It authorizes a minimal, testable SIGNAL implementation surface without opening runtime conformity, comparison, readiness, promotion, or writeback.
