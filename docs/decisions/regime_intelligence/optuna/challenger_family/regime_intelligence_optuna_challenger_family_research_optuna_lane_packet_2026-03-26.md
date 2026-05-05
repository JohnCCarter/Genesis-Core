# Regime Intelligence challenger family — research / Optuna lane packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical lane-opening snapshot / narrowed by later RI follow-up chain / no active lane authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This file records the initial RI research-lane opening on `feature/ri-role-map-implementation-2026-03-24`, not an active lane authority on `feature/next-slice-2026-05-05`.
> - Its broad lane-opening role was later specialized by the execution-setup / launch packet chain and then narrowed by the slice8 follow-up, cross-regime, and structural-search-space question chain.
> - Preserve this file as historical lane-opening provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet opens a narrow RI research / Optuna lane and defines its input/output boundaries, but does not reopen comparison, readiness, promotion, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Open a separate RI research / Optuna lane that continues RI-family work using the bridge result only for the bounded claim that RI is runnable.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `7035ab13`

### Scope

- **Scope IN:** docs-only definition of the next RI research objective; admissible artifact/input surface for the research lane; exact constraints that keep the lane outside comparison/readiness/promotion; expected research outputs and their bounded future use.
- **Scope OUT:** no source-code changes, no config changes, no runtime/default changes, no incumbent comparison reopening, no readiness opening, no promotion opening, no writeback authority, no new evidence class unless separately governed later, no use of bridge execution as comparison merit.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the lane must remain RI-family-internal research only
- the bridge result may support only the bounded claim `RI is runnable`
- no sentence may turn research outputs into incumbent-comparison evidence
- no sentence may open readiness or promotion by implication
- no sentence may normalize the bridge artifact into comparison-proof, parity-proof, ranking-proof, or calibration target against the incumbent

### Stop Conditions

- any wording that reopens incumbent comparison
- any wording that reopens readiness or promotion
- any wording that uses the bridge artifact as comparison merit or parity proof
- any wording that treats research outputs as directly promotion-eligible
- any wording that creates a new evidence class by implication

### Output required

- reviewable RI research / Optuna lane packet
- explicit research objective
- explicit admissible input surface
- explicit lane-separation constraints
- explicit expected outputs and bounded use rules

## Purpose

This packet opens only a **separate RI-family-internal research / Optuna lane**.

Its purpose is to allow RI work to continue after bridge classification without reopening any of the following:

- the closed raw-slice8 comparison lane
- readiness
- promotion

This packet does **not** authorize:

- incumbent comparison
- comparison-ready interpretation
- readiness-ready interpretation
- promotion-ready interpretation
- champion replacement
- writeback

## Governing basis

This packet is downstream of the following already tracked decisions:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_terminal_closeout_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_runtime_bridge_classification_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_next_admissible_lane_decision_2026-03-26.md`

Carried-forward meaning from those packets:

1. the original raw-slice8 comparison/readiness lane is closed
2. the runtime bridge artifact is a derived runtime representation of raw slice8
3. the bridge artifact is execution-proof only
4. the next admissible lane has already been decided as **Research lane**
5. execution-proof must not be upgraded into comparison-proof, readiness input, or promotion support

## Research objective for the next run

The RI research objective for the next run is:

- continue RI as a separate family research / Optuna track
- investigate RI candidate behavior and bounded RI-family search surfaces
- generate new RI-family-internal research artifacts under runtime-valid RI semantics where needed

This objective is intentionally narrower than any comparison or promotion question.

It does **not** ask:

- whether RI is stronger than the incumbent
- whether a bridge artifact should be comparison-eligible
- whether slice8 is readiness-ready
- whether promotion should open

## Admissible artifact / input surface

Only the following inputs are admissible inside this research lane.

### 1. RI family research anchors

The lane may use existing RI-family research anchors, including where relevant:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `results/hparam_search/run_20260324_174006/validation/trial_001.json`
- existing March 26 slice8 governance chain as boundary context only

Allowed use:

- define the RI-family research starting point
- define the bounded search neighborhood or follow-up hypotheses
- preserve RI-family identity and continuity within research

### 2. Runtime bridge artifact

The lane may use:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Allowed use is strictly limited to:

- proof that `RI is runnable`
- proof that a runtime-valid RI representation can be executed under current runtime semantics
- runtime-valid reference surface for RI-family experimentation only

The bridge artifact may **not** be used as:

- incumbent-comparison merit
- parity proof
- ranking proof against incumbent
- readiness support
- promotion support
- calibration target against the incumbent

### 3. RI runtime / family validator rules

The lane may cite and use the following as runtime/family guardrails:

- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`

Allowed use:

- constrain RI-family runtime-valid experimentation
- explain why certain RI search shapes are runtime-valid or runtime-invalid
- keep new RI artifacts family-consistent inside research

### 4. New RI research outputs generated under this lane

The lane may generate and use new RI-family-internal outputs, including:

- Optuna study artifacts under `results/hparam_search/...`
- validation artifacts under `results/hparam_search/.../validation/...`
- research candidate configs under `config/strategy/candidates/3h/...`
- research summaries or notes tied to this research lane

Allowed use:

- RI-family-internal research interpretation only
- future separately governed RI research continuation

## Exact constraints separating this lane from comparison / readiness / promotion

### Constraint 1 — no comparison reopening

No artifact in this lane may be used to claim:

- incumbent comparison merit
- comparison eligibility in the closed raw-slice8 lane
- same-head superiority or inferiority versus incumbent

### Constraint 2 — no readiness reopening

No artifact in this lane may be used to claim:

- readiness sufficiency
- readiness reopening
- readiness-eligible input

### Constraint 3 — no promotion reopening

No artifact in this lane may be used to claim:

- promotion eligibility
- promotion readiness
- promotion recommendation
- writeback suitability

### Constraint 4 — bridge result remains bounded

The bridge result remains admissible only for the bounded claim:

- `RI is runnable`

That claim may justify continued RI research execution.

It may **not** justify:

- comparison interpretation
- promotion interpretation
- incumbent ranking interpretation

### Constraint 5 — outputs remain RI-family-internal research artifacts

All outputs produced under this packet remain:

- **RI-family-internal research artifacts only**

They may not be used as incumbent-comparison, readiness, or promotion evidence unless a separate governance lane is explicitly opened later.

## Expected research outputs

The expected outputs from this lane are limited to research outputs such as:

1. new RI Optuna run artifacts
2. new RI validation summaries
3. new RI candidate config artifacts
4. new RI research notes or bounded hypotheses about RI-family behavior

These outputs are expected to answer only research questions such as:

- which RI-family surfaces remain tradable
- which RI-family parameter neighborhoods are runtime-valid
- which RI-family candidates merit further internal RI research follow-up

## How expected research outputs may be used afterward

The outputs from this lane may be used afterward only in the following bounded ways:

- to support future separately governed **RI research** interpretation
- to support future separately governed **RI research / Optuna** follow-up runs
- to support future internal narrowing of RI-family hypotheses

The outputs from this lane may **not** by themselves support:

- incumbent comparison claims
- readiness claims
- promotion claims
- champion replacement claims

## Claim surface inside this lane

### Allowed claims

- `RI is runnable`
- `RI-family research may continue under a separate Optuna lane`
- `This run/output is an RI-family-internal research artifact`

### Disallowed claims

- `RI has beaten the incumbent`
- `This RI artifact is comparison-ready`
- `This RI artifact is readiness-ready`
- `This RI artifact is promotion-ready`
- `Execution-proof has become comparison-proof`

## Next allowed step inside this lane

The next allowed step after this packet is:

- a separate RI research / Optuna execution packet or run setup that remains fully inside this lane's constraints

That later step must preserve all boundaries above.

## Bottom line

This packet opens a narrow **RI research / Optuna lane** outside comparison, readiness, and promotion.

Inside this lane:

- the bridge result may support only the bounded claim that `RI is runnable`
- all outputs remain RI-family-internal research artifacts only
- no artifact produced here may be upgraded into comparison, readiness, or promotion support without a separate governance opening
