# Regime Intelligence challenger family — slice8 cross-regime setup-only packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `setup-only / docs-only / no config materialization / no launch authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet narrows the cross-regime question into one admissible setup surface for a possible later falsification replay of the reproduced slice8 tuple, but must remain docs-only and must not drift into config creation, launch authorization, comparison, readiness, promotion, or runtime/default change.
- **Required Path:** `Quick`
- **Objective:** Define one bounded setup-only surface for a possible later cross-regime falsification replay of the reproduced slice8 full tuple by naming one admissible fixed non-2024 OOS candidate window and the authoritative repo guardrails that any later separate launch packet would have to satisfy.
- **Candidate:** `slice8 cross-regime setup only`
- **Base SHA:** `0d6004db`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Setup-only / non-authorizing`
- `No config materialization`
- `No launch authorization`
- `No comparison/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Supporting repo reference:** `docs/templates/skills/optuna_run_guardrails.md`
- **Supporting repo reference:** `.github/skills/optuna_run_guardrails.json`
- **Not applied:** any launch-authorization, comparison, readiness, or promotion skill surface; this packet remains setup-only and authorizes nothing operational

### Scope

- **Scope IN:**
  - exactly one docs-only setup-only packet under `docs/governance/`
  - explicit subordination to the already committed cross-regime research-question packet
  - explicit active subject locked to the reproduced slice8 full tuple from `results/hparam_search/ri_slice8_followup_launch_20260326/best_trial.json` together with its anchor YAML
  - explicit naming of one admissible fixed non-2024 OOS candidate setup subject: `2025-01-01..2025-12-31`
  - explicit references to repo-authoritative validation/preflight/guardrail surfaces
  - explicit preconditions for any later separate launch packet
  - explicit statement that no config file is created here and no replay is authorized here
- **Scope OUT:**
  - no source-code changes
  - no `tests/**`, `config/**`, or `results/**` changes
  - no config creation or config path reservation
  - no launch authorization
  - no actual replay execution
  - no replay outputs, pass/fail criteria, or result interpretation
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/env/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_setup_only_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain setup-only
- no sentence may authorize launch, execution, or replay-window selection beyond the named candidate setup subject
- no sentence may create or reserve a config file, output path, or result artifact contract
- no sentence may define pass/fail thresholds, score gates, or later decision logic
- no sentence may reopen incumbent comparison, readiness, promotion, or writeback
- no sentence may restore slice9 or slice7 as active setup subjects
- no sentence may generalize this setup surface beyond the reproduced slice8 tuple

### Stop Conditions

- any wording that turns the named `2025-01-01..2025-12-31` window into an approved replay window rather than a named candidate setup subject
- any wording that materializes a config path, config file, or output location as if approved now
- any wording that authorizes launch or actual replay execution
- any wording that defines pass/fail criteria, score thresholds, artifact requirements, or later decision standards
- any wording that reopens incumbent comparison, readiness, promotion, or writeback
- any wording that makes slice9 a backup or co-primary setup subject
- any wording that restores slice7 as an active setup subject
- any need to modify files outside this one scoped packet

### Output required

- reviewable cross-regime setup-only packet
- explicit active subject and named candidate OOS setup subject
- explicit validator/preflight/guardrail references
- explicit preconditions for any later separate launch packet
- explicit statement that no config is created and no launch is authorized here

## Purpose

This document narrows the already-open cross-regime research question into one **setup-only** surface.

It does so by naming a single admissible candidate OOS setup subject for a possible later falsification replay of the already reproduced slice8 full tuple.

This packet does **not**:

- create a config
- choose an operational replay contract
- authorize launch
- execute a replay
- reopen comparison, readiness, promotion, or writeback

Fail-closed interpretation:

> This packet defines only an admissible setup surface for a possible later separate launch
> assessment. The active subject remains the reproduced slice8 full tuple. The named OOS
> window `2025-01-01..2025-12-31` is recorded here only as the candidate setup subject for a
> possible later cross-regime falsification replay. No config is created here, no replay is
> authorized here, and no result criteria are defined here.

## Upstream governed basis

This packet is downstream of the following already tracked documents:

- `docs/decisions/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_followup_research_lane_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_followup_setup_only_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_followup_launch_authorization_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_research_question_packet_2026-03-26.md`

Carried-forward meaning from those packets:

1. the active lane remains RI-family-internal research only
2. slice8 remains the sole primary continuation surface
3. slice9 remains secondary robustness context only
4. slice7 remains historical context only
5. the reproduced slice8 full tuple remains a research-only subject, not a runtime/default candidate
6. the cross-regime packet opened only the question of whether one fixed non-2024 OOS falsification surface should be prepared later

## Active subject and candidate setup subject

### Active subject

The only active subject in this packet is the reproduced slice8 full tuple evidenced by:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `results/hparam_search/ri_slice8_followup_launch_20260326/best_trial.json`
- `results/hparam_search/ri_slice8_followup_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_followup_launch_20260326/validation/trial_001.json`

Allowed use:

- identify the exact reproduced tuple that would be the subject of any later separate launch assessment
- preserve that the subject is frozen and already evidenced rather than a new search-space proposal
- preserve that the current continuation question is now bounded falsification rather than additional local search

Disallowed use:

- treating the subject as comparison-ready
- treating the subject as readiness-ready or promotion-ready
- generalizing from this subject to the RI family as a whole

### Named candidate OOS setup subject

The only named candidate OOS setup subject in this packet is:

- `2025-01-01..2025-12-31`

That named window may be used here only to:

- define the single candidate non-2024 OOS setup surface for a possible later separate launch assessment
- preserve a narrow, fixed falsification subject rather than widening immediately to multiple windows or structural search changes
- align with already existing repository blind/OOS patterns without creating any operational authority here

That named window may **not** be used here to claim:

- that the replay window has been approved
- that launch should occur now
- that this is the only acceptable future candidate surface in all circumstances
- that any result on that window would by itself reopen comparison, readiness, or promotion

## Admissible input surface

Only the following inputs are admissible inside this packet.

### 1. Cross-regime question authority

- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_research_question_packet_2026-03-26.md`

Allowed use:

- preserve that this packet is subordinate to the already-open research question
- preserve that the named OOS window remains a setup subject only and not an authorized replay

### 2. Slice8 reproduced tuple evidence

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `results/hparam_search/ri_slice8_followup_launch_20260326/best_trial.json`
- `results/hparam_search/ri_slice8_followup_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_followup_launch_20260326/validation/trial_001.json`

Allowed use:

- lock the exact subject for any later separate launch assessment
- preserve provenance for the tuple whose falsification surface is being prepared conceptually

### 3. Existing repository OOS pattern references

- `docs/features/feature-ri-optuna-train-validate-blind-1.md`
- `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseE_oos.yaml`

Allowed use:

- confirm that the repository already contains fixed-window OOS evaluation patterns
- confirm that `2025`-era OOS sits inside an existing repository taxonomy rather than being invented ad hoc here

Disallowed use:

- copying those patterns into a new config here
- inferring that the phased-v3 OOS config already authorizes this replay subject

### 4. Repo-authoritative guardrail surfaces

- `scripts/validate/validate_optimizer_config.py`
- `scripts/preflight/preflight_optuna_check.py`
- `.github/skills/optuna_run_guardrails.json`
- `docs/templates/skills/optuna_run_guardrails.md`
- `docs/optuna/OPTUNA_BEST_PRACTICES.md`

Allowed use:

- define the authoritative validator/preflight/guardrail surfaces that any later separate launch packet would need to cite and satisfy
- preserve canonical-mode and `resume=false` guardrails as future preconditions only

Disallowed use:

- treating these references as immediate launch approval
- inventing new validator/preflight semantics in this packet

### 5. Secondary and historical context only

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`
- the already tracked ranked-summary discussion of slice7

Allowed use:

- preserve slice9 as secondary robustness context only
- preserve slice7 as historical context only
- explain why the setup subject remains centered on the reproduced slice8 tuple

Disallowed use:

- making slice9 a backup setup subject
- restoring slice7 as an active setup subject

## Preconditions for any later separate launch packet

Any later separate launch packet that seeks assessment of this setup surface remains blocked unless all of the following are true:

1. the active subject remains the same reproduced slice8 full tuple cited above
2. the named OOS setup subject remains the same fixed window `2025-01-01..2025-12-31`, unless a later separate governance step changes it explicitly
3. a later separate step materializes any needed replay config or replay surface outside this packet
4. the repo-authoritative validator is run against that later materialized replay surface and returns exit code `0`
5. the repo-authoritative preflight surface is run against that later materialized replay surface and returns exit code `0`
6. canonical comparability guardrails remain satisfied for any later replay attempt
7. `resume=false` storage safety is explicitly handled in that later launch assessment rather than assumed here
8. the later step remains RI-family research only and does not reopen comparison, readiness, promotion, or writeback

These are later-launch preconditions only.
They are not launch approval in this packet.

## What this packet still does not decide

This packet does **not** decide:

- the replay config path
- whether a replay config will be created
- the storage path
- the run id
- the exact launch command
- the output location
- any pass/fail threshold
- any result interpretation standard
- any comparison/readiness/promotion consequence

If any later step needs those details, that later step must be handled by a **separate future governance packet**.

## Explicit exclusions / not in scope

The following remain explicitly outside this packet:

- config creation
- launch authorization
- actual replay execution
- replay-result interpretation
- incumbent comparison reopening
- readiness reopening
- promotion reopening
- writeback
- any new evidence class

## Bottom line

This packet creates only a **cross-regime setup-only surface** for the reproduced slice8 full tuple.

Within this packet:

- the active subject is the reproduced slice8 full tuple
- the named candidate OOS setup subject is `2025-01-01..2025-12-31`
- validator, preflight, and Optuna guardrails are cited only as future preconditions
- no config is created
- no launch is authorized
- no replay is executed

Any operational step beyond this would require a **separate future governance packet** and is not authorized here.
