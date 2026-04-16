# RI advisory environment-fit Phase 2 label taxonomy packet

Date: 2026-04-16
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / label-definition / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only label/taxonomy definition using already generated current-ATR evidence and already tracked RI observability surfaces; no runtime/config/test changes and no artifact regeneration.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** define the admissible label families and failure taxonomy for the RI advisory environment-fit lane so that a later deterministic baseline can be evaluated without circular logic or hidden 2024-only pattern memory.
- **Candidate:** `RI advisory environment-fit Phase 2 label taxonomy`
- **Base SHA:** `45fecbeb`

### Scope

- **Scope IN:**
  - `docs/governance/ri_advisory_environment_fit_phase2_label_taxonomy_packet_2026-04-16.md`
  - `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - any score implementation
  - any threshold tuning
  - any runtime/shadow integration
  - any ML/model work
- **Expected changed files:**
  - `docs/governance/ri_advisory_environment_fit_phase2_label_taxonomy_packet_2026-04-16.md`
  - `docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/governance/ri_advisory_environment_fit_phase2_label_taxonomy_packet_2026-04-16.md docs/analysis/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`

### Stop Conditions

- any wording that turns this slice into scoring implementation authority
- any wording that lets post-entry fields leak into scoring-time inputs
- any wording that rebrands 2024 discovery seeds as universal labels
- any silent extension outside the `ri` family
- any attempt to open ML comparison before the deterministic baseline exists

### Output required

- one docs-only packet
- one label-definition / failure-taxonomy memo
- explicit separation between outcome labels and state tags
- explicit allowed-vs-forbidden feature boundary for label construction and later scoring

## Purpose

This slice answers one narrow question only:

> what labels and state tags may the RI advisory environment-fit lane use later without collapsing into circular 2024 pattern memory or leaking post-entry information into scoring-time inputs?

This packet does **not** authorize:

- score implementation
- runtime/shadow integration
- ML comparison
- config changes

## Allowed evidence inputs

This slice may cite only the already tracked surfaces below:

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase1_observability_inventory_2026-04-16.md`
- `docs/governance/current_atr_900_multi_year_env_robustness_packet_2026-04-16.md`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/robustness_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/closeout.md`
- already tracked RI observability sources cited in the Phase 1 memo

## Required distinctions

The memo must keep the following boundaries explicit:

1. **outcome labels** built from post-entry evidence
2. **state tags** built from entry-time RI observability
3. **scoring-time features** allowed for a later deterministic baseline
4. **forbidden leakage** from post-entry evidence into score inputs

## Required questions

The memo must answer at minimum:

1. what counts as a `supportive` context label?
2. what counts as a `hostile` context label?
3. how should `transition` and `ambiguity` be represented without creating circular labels?
4. which years are evaluable, contradiction-heavy, or no-evidence surfaces?
5. what failure modes must a later deterministic baseline report explicitly?

## Exact next admissible step

If the label memo remains non-circular and operationally usable, the next admissible step is:

- a separate bounded Phase 3 deterministic advisory-baseline slice

If the label memo cannot define a usable non-circular label surface, the lane must stop or be reframed before any score implementation opens.

## Bottom line

This packet authorizes one docs-only label/taxonomy memo and nothing more.
Its job is to make the next deterministic baseline slice admissible — or to stop the lane honestly if that cannot be done without circularity.
