# Regime Intelligence challenger family — slice8 follow-up setup-only packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical setup snapshot / consumed by later follow-up launch chain / no active setup authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This file records an earlier slice8 follow-up setup stage on `feature/ri-role-map-implementation-2026-03-24`, not an active setup authority on `feature/next-slice-2026-05-05`.
> - Its active setup role was later consumed by `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_followup_launch_authorization_packet_2026-03-26.md` and the downstream follow-up packet chain.
> - Preserve this file as historical setup provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet specializes the already-open slice8-first follow-up research lane into a bounded setup-only surface, but must remain docs-only and must not imply launch approval, comparison, readiness, promotion, or runtime/default change.
- **Required Path:** `Quick`
- **Objective:** Define one bounded setup-only packet for a possible later slice8-first follow-up RI research run, including admissible inputs, preconditions for any later separate launch packet, storage/resume discipline, and non-authoritative reproducibility notes.
- **Candidate:** `slice8-first follow-up setup only`
- **Base SHA:** `018066f5`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup-only / non-authorizing`
- `No comparison/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Supporting repo reference:** `docs/templates/skills/optuna_run_guardrails.md`
- **Supporting repo reference:** `docs/optuna/OPTUNA_BEST_PRACTICES.md`
- **Not applied:** any launch-authorization or comparison skill surface; this packet defines no launch approval and no comparison interpretation

### Scope

- **Scope IN:**
  - create one docs-only setup-only packet inside the already-open `slice8-first` follow-up research lane
  - anchor the setup to `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
  - record the admissible input surface, later-launch preconditions, storage/resume discipline, smoke/baseline guardrails, and non-authoritative reproducibility notes
  - explicitly preserve that `slice9` is secondary robustness context only and `slice7` is historical context only
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `results/**` changes
  - no launch authorization
  - no actual Optuna launch
  - no execution command authorization
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_followup_setup_only_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain subordinate to the already-open slice8-first follow-up research lane
- no sentence may authorize or imply an actual launch
- no sentence may define new env/config semantics
- no sentence may reopen comparison, readiness, or promotion
- no sentence may restore slice7 or slice9 as active setup subjects
- no sentence may convert reproducibility notes into authority or approval

### Stop Conditions

- any wording that sounds like launch preparation approval instead of setup-only framing
- any wording that treats slice9 as a co-equal or backup setup subject
- any wording that reopens slice7 as an active continuation surface
- any wording that defines new env/config/default authority rather than citing existing repo surfaces
- any wording that broadens the lane beyond RI-family-internal research
- any need to modify files outside this one scoped packet

### Output required

- reviewable slice8-first follow-up setup-only packet
- explicit anchor config and admissible input surface
- explicit preconditions for any later separate launch packet
- explicit storage/resume discipline
- explicit reproducibility notes framed as non-authority
- explicit exclusions and disallowed claims

## Purpose

This document is a **setup-only packet** for the already-open slice8-first follow-up research lane.

It specializes the existing lane into a narrow setup-underlag for a possible later RI-only follow-up run.
It does **not** authorize launch, run execution, readiness, promotion, writeback, or any new evidence class.

Fail-closed interpretation:

> This packet defines only a bounded setup surface for a possible later slice8-first follow-up
> RI research run. The packet itself does not authorize launch, perform any run, reopen
> comparison/readiness/promotion, or create any new config/env/runtime authority.

## Upstream governed basis

This packet is downstream of the following already tracked documents:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_followup_research_lane_packet_2026-03-26.md`

This packet does not replace or widen those packets.
It only specializes them into a fail-closed setup surface.

Carried-forward meaning from those packets:

1. the active lane remains RI-family-internal research only
2. slice8 is the sole preferred continuation surface
3. slice9 is secondary robustness context only
4. slice7 is historical context only
5. incumbent comparison, readiness, promotion, and writeback remain outside the active lane

## Setup subject and anchor

The only active setup subject in this packet is the slice8-first follow-up surface anchored to:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

This anchor may be used only to:

- preserve the already-selected slice8-first continuation surface
- define a possible later follow-up setup framing inside the RI-family research lane
- reference the exact surface that already delivered the cleanest tracked duplicate ratio among the tied RI contenders

This anchor may **not** be used by this packet to claim:

- incumbent superiority or inferiority
- launch approval
- readiness eligibility
- promotion eligibility
- champion replacement suitability

## Admissible input surface

Only the following inputs are admissible inside this setup-only packet.

### 1. Lane-governance anchors

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_followup_research_lane_packet_2026-03-26.md`

Allowed use:

- preserve the already-open research-lane boundary
- preserve the ranked-summary and follow-up-lane conclusions
- keep this packet subordinate to existing lane authority rather than creating new authority

### 2. Slice8 tracked run artifacts

- `results/hparam_search/ri_slice8_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_launch_20260326/validation/trial_001.json`

Allowed use:

- preserve the tracked process-cleanliness reason for keeping slice8 as the only active setup subject
- preserve the already-recorded validation context of the slice8 surface

### 3. Existing repo-authoritative validation and preflight entrypoints

- `scripts/validate/validate_optimizer_config.py`
- `scripts/preflight/preflight_optuna_check.py`

Allowed use:

- reference the existing repo-authoritative validation and preflight surfaces that must remain the source of truth before any later separately proposed launch packet

This packet does not define new script semantics.
It only references existing repo entrypoints.

### 4. Optuna run guardrails

- `.github/skills/optuna_run_guardrails.json`
- `docs/templates/skills/optuna_run_guardrails.md`
- `docs/optuna/OPTUNA_BEST_PRACTICES.md`

Allowed use:

- carry forward the already-established guardrails that long Optuna runs require validation, preflight, smoke/baseline discipline, and storage safety

### 5. Non-active supporting context only

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`

Allowed use:

- retain slice9 only as secondary robustness context for why the lane remains RI-only and why slice8 remains the only active setup subject

Disallowed use:

- making slice9 an active setup subject
- creating a parallel or backup setup surface
- widening the continuation surface beyond slice8-first

## Preconditions for any later separate launch packet

Any later launch packet that wishes to use this setup surface remains blocked unless all of the following are true.

1. this packet remains unchanged in meaning and still subordinate to the already-open slice8-first follow-up lane
2. the slice8 anchor YAML still exists at the path named above
3. the relevant repo-authoritative config validation entrypoint passes with exit code `0`
4. the relevant repo-authoritative preflight entrypoint passes with exit code `0`
5. the `optuna_run_guardrails` smoke/baseline discipline is satisfied and recorded before any long run is considered
6. the later step remains RI-family-internal research only and does not reopen comparison, readiness, promotion, or writeback
7. any future launch proposal records the effective run metadata actually used rather than relying on this packet as execution authority

These are preconditions for a later separate launch packet only.
They are not launch approval in this packet.

## Storage and resume discipline

Because the slice8 anchor YAML is tracked with `resume: false`, this setup packet preserves the following storage discipline:

- no later launch packet may silently reuse an existing storage DB for the same setup surface
- any existing storage target must be treated as blocking until a later separately tracked step explicitly resolves it
- this packet does not resolve, delete, rename, or authorize any storage action itself

This section exists only to preserve the already-established storage guardrail.
It does not authorize any operator action now.

## Reproducibility notes (non-authority)

Any environment variables, flags, script surfaces, or command components mentioned in relation to this setup are recorded here only as **reproducibility notes** tied to already-existing repo scripts and prior slice8 research provenance.

They do **not** create new authority, do **not** change config/env interpretation, and do **not** imply launch approval.

If a later separate launch packet is ever approved, only the effectively used values should be logged as run metadata.
This packet defines no new mandatory env values, defaults, or fallback rules.

Previously logged slice8 research provenance included items such as:

- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_HASH=0`
- `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
- `PYTHONPATH=src`
- `PYTHONIOENCODING=utf-8`
- `TQDM_DISABLE=1`
- `OPTUNA_MAX_DUPLICATE_STREAK=2000`

These items are descriptive provenance only.
They are not instructions to run now.

## Explicit exclusions / not in scope

This packet is exclusively scoped to slice8-first follow-up as a possible later research setup surface.

The following are explicitly **not in scope**:

- slice9 as an active setup subject
- slice7 as an active setup subject
- incumbent comparison reopening
- readiness reopening
- promotion reopening
- launch authorization
- actual execution
- writeback
- any new evidence class

## Disallowed claims

This packet must not be read as permitting any of the following claims:

- `launch is approved`
- `setup is approved for immediate execution`
- `slice8 has beaten the incumbent`
- `slice9 is now a parallel follow-up candidate`
- `slice7 has been reopened`
- `this packet defines new env/config/default semantics`
- `this packet creates promotion or readiness evidence`

## Bottom line

This packet creates only a **slice8-first follow-up setup-only surface** inside the already-open RI-family research lane.

It records the active setup subject, admissible inputs, later-launch preconditions, storage discipline, and non-authoritative reproducibility notes.

It does **not** authorize launch, execution, comparison, readiness, promotion, writeback, or any new evidence class.
