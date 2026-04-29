# Feature Attribution v1 — Phase 1 feature-inventory packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase1-proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet names candidate single-seam units for future Feature Attribution v1 research and therefore carries governance-drift risk even though it remains docs-only and non-authorizing.
- **Required Path:** `Quick`
- **Objective:** Inventory candidate single-seam units that already exist in the current canonical route, define admission rules for v1 units, and freeze a fail-closed one-single-seam-unit-at-a-time ablation contract for later separate governance use.
- **Candidate:** `future Feature Attribution v1 seam inventory`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; exact single-seam-unit definition; exact admission/exclusion rules; citation matrix from current canonical route to baseline config source; non-authorizing one-unit-at-a-time contract wording; explicit exclusions for fib, POC adoption, quality-without-anchor, and execution authority.
- **Scope OUT:** no source-code changes; no tests; no results generation; no implementation authority; no execution authority; no toggle-design implementation; no champion edits; no changes under `src/**`, `tests/**`, `config/**`, `results/research/feature_attribution_v1/**`, or `config/strategy/champions/**`; no fib reopening; no adoption of `src/core/strategy/components/attribution.py`.
- **Expected changed files:** `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase1_feature_inventory_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only citation check against current canonical route modules and baseline config source
- manual wording audit that the packet remains non-authorizing
- manual wording audit that every admitted candidate has an exact canonical key anchor or is dropped
- manual wording audit that fib remains closed and that no POC route is adopted

For interpretation discipline inside this packet:

- Phase 0 remains controlling and must not be weakened
- `config/strategy/champions/tBTCUSD_3h.json` remains config-source anchor only
- all candidate units must map to current canonical route citations
- wildcard seams without exact leaves are not admissible
- any candidate without exact anchor must be excluded from v1

### Stop Conditions

- any wording that authorizes implementation, execution, runtime mutation, result generation, or promotion
- any wording that treats candidate inventory as approved toggle design
- any wording that reopens fib-derived entry seams
- any wording that adopts `src/core/strategy/components/attribution.py` as canonical route
- any wording that uses wildcard seam naming without exact cited leaf keys or explicit cluster declaration
- any wording that treats absent `quality.*` baseline config anchors as if they were present

### Output required

- one reviewable Phase 1 RESEARCH feature-inventory packet
- one fail-closed single-seam-unit definition
- one citation matrix mapping candidate unit to exact canonical key path(s) and route anchor(s)
- one non-authorizing one-unit-at-a-time ablation contract for later separate use
- one explicit admitted / citation-only / excluded classification for each candidate family

## What this packet is

This document is a **Phase 1 RESEARCH inventory and contract packet** for Feature Attribution v1.

It does the following only:

- names candidate v1 units already present in the current canonical route
- defines which candidate units are admissible, citation-only, or excluded
- freezes the wording of a future deterministic one-single-seam-unit-at-a-time contract
- preserves the fail-closed boundaries inherited from Phase 0

This packet does **not** authorize:

- implementation
- execution
- result generation
- toggle design as an introduced artifact
- code migration
- config edits
- champion replacement
- fib reopening
- promotion, readiness, or launch claims

This packet is an inventory and contract document for research and gives **no implementation, execution, configuration, result-generation, or promotion authority**.

## Inherited locks from Phase 0

This packet inherits the Phase 0 lock from:

- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`

The following remain locked and unchanged:

- research-only
- additive-only
- no-default-behavior-change
- fib non-reopen
- canonical baseline anchor = `config/strategy/champions/tBTCUSD_3h.json`
- canonical baseline observational context = `tBTCUSD`, `3h`, `2023-01-01 -> 2024-12-31`
- reserved namespace only = `results/research/feature_attribution_v1/`

Nothing in this Phase 1 packet weakens or overrides those locks.

## Terminology lock

In this packet, **Feature Attribution v1** uses the word **feature** in a constrained governance sense.

A valid v1 attribution unit is a **single-seam unit**.

A single-seam unit is either:

- exactly one already existing canonical-route seam with an exact citation anchor, or
- one pre-declared, inseparable canonical cluster with exact citation anchors for all participating keys

New toggles, shadow paths, wrappers, remaps, inferred code seams, or newly invented abstractions are not authorized here.

If a candidate cannot be anchored to:

- an exact named key path in the current baseline config source, and
- an identified current canonical route citation

then that candidate is excluded from v1.

## Canonical-route citation basis

The current canonical-route citations used by this packet are:

- `src/core/strategy/evaluate.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/confidence.py`
- `config/strategy/champions/tBTCUSD_3h.json`

Interpretation rule:

- `evaluate.py` is the current orchestrator that computes confidence and calls the decision route.
- `decision.py` is the current decision orchestrator that sequences candidate selection, fib gating, post-fib gates, and sizing.
- `decision_gates.py` is the current gate/threshold route for candidate selection and post-fib entry gating.
- `decision_sizing.py` is the current sizing route for regime, HTF, and volatility sizing multipliers.
- `confidence.py` is cited only to verify whether an exact baseline config anchor exists for confidence-quality seams.

This packet adopts none of these modules as implementation targets.
They are cited only as current-route anchors.

## Admission rule for v1 units

A candidate unit is admissible in v1 only if all of the following are true:

1. it already exists in the current canonical route
2. it has an exact cited baseline config key path or explicit exact cluster membership
3. it can be described without wildcard expansion ambiguity
4. it does not reopen fib-derived entry research
5. it does not require adoption of `src/core/strategy/components/attribution.py`
6. it does not imply redesign, interaction testing, or retuning

If any one of these conditions is false, the candidate is either:

- `citation-only`, or
- `excluded`

## Candidate inventory matrix

| Candidate unit                       | Exact baseline config key path(s)                                                                                                                                                                                                                                                                                                                                                                                                   | Canonical route anchor(s)                                                            | Status             | Initial wave note                                                          |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------ | -------------------------------------------------------------------------- |
| Base entry confidence seam           | `cfg.thresholds.entry_conf_overall`                                                                                                                                                                                                                                                                                                                                                                                                 | `src/core/strategy/decision_gates.py::select_candidate`                              | `admitted`         | admissible as one exact seam                                               |
| Regime probability threshold cluster | `cfg.thresholds.regime_proba.balanced`; `cfg.thresholds.regime_proba.bull`; `cfg.thresholds.regime_proba.bear`; `cfg.thresholds.regime_proba.ranging`                                                                                                                                                                                                                                                                               | `src/core/strategy/decision_gates.py::select_candidate`                              | `admitted-cluster` | treat as one pre-declared inseparable threshold cluster                    |
| Signal-adaptation threshold cluster  | `cfg.thresholds.signal_adaptation.atr_period`; `cfg.thresholds.signal_adaptation.zones.low.entry_conf_overall`; `cfg.thresholds.signal_adaptation.zones.low.regime_proba`; `cfg.thresholds.signal_adaptation.zones.mid.entry_conf_overall`; `cfg.thresholds.signal_adaptation.zones.mid.regime_proba`; `cfg.thresholds.signal_adaptation.zones.high.entry_conf_overall`; `cfg.thresholds.signal_adaptation.zones.high.regime_proba` | `src/core/strategy/decision_gates.py::select_candidate`                              | `admitted-cluster` | exact leaves declared; no wildcard authority beyond listed keys            |
| Minimum-edge gate seam               | `cfg.thresholds.min_edge`                                                                                                                                                                                                                                                                                                                                                                                                           | `src/core/strategy/decision_gates.py::apply_post_fib_gates`                          | `admitted`         | admissible as one exact seam                                               |
| Hysteresis gate seam                 | `cfg.gates.hysteresis_steps`                                                                                                                                                                                                                                                                                                                                                                                                        | `src/core/strategy/decision_gates.py::apply_post_fib_gates`                          | `admitted`         | admissible as one exact seam                                               |
| Cooldown gate seam                   | `cfg.gates.cooldown_bars`                                                                                                                                                                                                                                                                                                                                                                                                           | `src/core/strategy/decision.py::decide`                                              | `admitted`         | admissible as one exact seam                                               |
| Risk-map sizing cluster              | `cfg.risk.risk_map`                                                                                                                                                                                                                                                                                                                                                                                                                 | `src/core/strategy/decision_sizing.py::_compute_size_base`                           | `citation-only`    | cluster boundary remains unresolved for v1 wave 1                          |
| Regime sizing multiplier cluster     | `cfg.risk.regime_size_multipliers.bull`; `cfg.risk.regime_size_multipliers.bear`; `cfg.risk.regime_size_multipliers.ranging`; `cfg.risk.regime_size_multipliers.balanced`                                                                                                                                                                                                                                                           | `src/core/strategy/decision_sizing.py::_compute_size_multipliers`                    | `admitted-cluster` | treat as one inseparable regime-sizing cluster                             |
| HTF regime sizing multiplier cluster | `cfg.risk.htf_regime_size_multipliers.bull`; `cfg.risk.htf_regime_size_multipliers.bear`; `cfg.risk.htf_regime_size_multipliers.ranging`; `cfg.risk.htf_regime_size_multipliers.unknown`                                                                                                                                                                                                                                            | `src/core/strategy/decision_sizing.py::_compute_size_multipliers`                    | `admitted-cluster` | treat as one inseparable HTF-sizing cluster                                |
| Volatility sizing cluster            | `cfg.risk.volatility_sizing.enabled`; `cfg.risk.volatility_sizing.high_vol_threshold`; `cfg.risk.volatility_sizing.high_vol_multiplier`; `cfg.risk.volatility_sizing.atr_period`                                                                                                                                                                                                                                                    | `src/core/strategy/decision_sizing.py::_compute_size_multipliers`                    | `admitted-cluster` | exact leaves declared; no leaf-by-leaf authority created here              |
| HTF block seam                       | `cfg.multi_timeframe.use_htf_block`                                                                                                                                                                                                                                                                                                                                                                                                 | `src/core/strategy/decision.py::decide`                                              | `admitted`         | separate from override logic                                               |
| LTF override cluster                 | `cfg.multi_timeframe.allow_ltf_override`; `cfg.multi_timeframe.ltf_override_threshold`                                                                                                                                                                                                                                                                                                                                              | `src/core/strategy/decision.py::decide`                                              | `admitted-cluster` | separate from HTF block seam                                               |
| Exit parameter surface               | `cfg.exit.enabled`; `cfg.exit.max_hold_bars`; `cfg.exit.stop_loss_pct`; `cfg.exit.take_profit_pct`; `cfg.exit.exit_conf_threshold`; `cfg.exit.regime_aware_exits`; `cfg.exit.trailing_stop_enabled`; `cfg.exit.trailing_stop_pct`                                                                                                                                                                                                   | `src/core/strategy/evaluate.py`; downstream exit route cited by config presence only | `citation-only`    | existing contributor, but excluded from initial execution wave             |
| HTF exit configuration surface       | `cfg.htf_exit_config.enable_partials`; `cfg.htf_exit_config.enable_trailing`; `cfg.htf_exit_config.enable_structure_breaks`; `cfg.htf_exit_config.partial_1_pct`; `cfg.htf_exit_config.partial_2_pct`; `cfg.htf_exit_config.fib_threshold_atr`; `cfg.htf_exit_config.trail_atr_multiplier`; `cfg.htf_exit_config.swing_update_strategy`                                                                                             | `config/strategy/champions/tBTCUSD_3h.json`                                          | `citation-only`    | existing config surface, but excluded from initial execution wave          |
| Confidence-quality surface           | no exact `cfg.quality.*` keys present in `config/strategy/champions/tBTCUSD_3h.json`                                                                                                                                                                                                                                                                                                                                                | `src/core/strategy/evaluate.py`; `src/core/strategy/confidence.py`                   | `excluded`         | supported in code path, but not anchored in current baseline config source |
| Fib entry surfaces                   | `cfg.htf_fib.entry.enabled`; `cfg.htf_fib.entry.missing_policy`; `cfg.htf_fib.entry.tolerance_atr`; `cfg.htf_fib.entry.long_max_level`; `cfg.htf_fib.entry.short_min_level`; `cfg.ltf_fib.entry.enabled`; `cfg.ltf_fib.entry.missing_policy`; `cfg.ltf_fib.entry.tolerance_atr`; `cfg.ltf_fib.entry.long_max_level`; `cfg.ltf_fib.entry.short_min_level`                                                                            | `src/core/strategy/decision.py::decide`; fib gating route                            | `excluded`         | explicit fib non-reopen boundary controls                                  |
| Composable attribution POC surface   | `src/core/strategy/components/attribution.py`                                                                                                                                                                                                                                                                                                                                                                                       | `src/core/strategy/components/attribution.py`                                        | `excluded`         | POC citation only; not canonical route                                     |

## Interpretation notes on the matrix

The matrix above is intentionally conservative.

It means:

- `admitted` = exact seam named and citation-anchored
- `admitted-cluster` = a pre-declared inseparable unit with exact cluster membership frozen in this packet
- `citation-only` = current-route contributor acknowledged, but not admitted as an initial v1 execution unit
- `excluded` = not part of v1 under the current Phase 0 / Phase 1 lock

No row in the matrix creates runtime authority.
No row in the matrix creates toggle-design authority.
No row in the matrix creates result-generation authority.

## Non-authorizing ablation contract

If a later separate governance packet ever opens execution, the only admissible v1 contract inherited from this packet is:

- compare one admitted single-seam unit or one admitted exact cluster against the locked baseline
- change exactly one admitted unit at a time
- keep all non-target units identical to the locked baseline
- do not retune adjacent thresholds, multipliers, exits, or route order to compensate
- do not substitute an alternative route, shadow route, or POC route
- do not introduce new features, bundles, interaction units, or redesign abstractions
- do not reinterpret citation-only units as implicitly admitted
- do not reinterpret excluded units as reopened by adjacency

This contract is wording only.
It is not an execution approval.

## Explicit exclusions preserved in Phase 1

The following remain explicitly out of scope after this packet:

- any code change
- any config change
- any experiment run
- any artifact creation under `results/research/feature_attribution_v1/`
- any Optuna/search/tuning work
- any interaction or pairwise ablation
- any default behavior change
- any POC adoption from `src/core/strategy/components/attribution.py`
- any fib-derived entry seam reopening
- any quality-surface admission without exact baseline config anchor

Fib-related entry seams remain explicitly excluded; mention of adjacent canonical contributors must not be interpreted as reopening the fib path.

## Exact future approval boundary

Every future implementation step, toggle-design step, execution step, or result-generation step requires a separate later packet and separate approval.

No such approval is granted here.

## Bottom line

Feature Attribution v1 now has a Phase 1 inventory packet that:

- keeps Phase 0 fully intact
- replaces vague feature language with fail-closed single-seam-unit language
- splits broad candidate families into exact seams or exact declared clusters
- excludes confidence-quality surfaces that lack exact baseline config anchors
- keeps exits citation-only for now
- keeps fib explicitly closed
- preserves the current canonical route without adopting the composable attribution POC

This packet names the candidate units.
It does not authorize acting on them.
