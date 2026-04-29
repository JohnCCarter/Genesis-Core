# Regime Intelligence challenger family — next admissible lane decision

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `decision-only / next lane selected / no readiness or promotion scope`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet selects the next admissible lane after runtime bridge classification, but does not reopen readiness, promotion, or the closed raw-slice8 comparison lane
- **Required Path:** `Quick`
- **Objective:** Decide exactly one next admissible lane after the bridge artifact was classified as execution-proof only.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `b34ffd0e`

### Scope

- **Scope IN:** docs-only decision of the next admissible lane; explicit selection between `Comparison lane` and `Research lane`; explicit non-selection rationale for the rejected option; explicit allowed use of the bridge result inside the chosen lane.
- **Scope OUT:** no source-code changes, no config changes, no runtime/default changes, no readiness opening, no promotion opening, no writeback authority, no new evidence class, no expansion of bridge governance, no new comparison execution contract.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_challenger_family_next_admissible_lane_decision_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- exactly one lane must be selected
- execution-proof must not be treated as comparison-proof
- no sentence may reopen readiness or promotion
- no sentence may treat the bridge artifact as automatically comparison-eligible
- non-selection of the comparison lane must remain present-state and non-permanent

### Stop Conditions

- any wording that opens readiness reconsideration
- any wording that opens promotion or writeback
- any wording that silently upgrades the bridge artifact into comparison-proof
- any wording that creates a new derived-runtime comparison lane by implication
- any wording that permanently forbids all future separately governed comparison lanes

### Output required

- reviewable next-lane decision packet
- explicit chosen lane label
- explicit rejected-lane label
- explicit bridge-result allowed-use statement
- explicit next allowed step inside the chosen lane

## Purpose

This packet answers one narrow question only:

- what is the next admissible lane after the bridge artifact was classified as execution-proof only?

This packet does **not**:

- reopen the closed raw-slice8 comparison lane
- reopen readiness
- reopen promotion
- create a new general comparison standard
- create a new bridge-governance branch

## Governing basis

This packet is downstream of the following already tracked decisions:

- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_terminal_closeout_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_runtime_bridge_classification_2026-03-26.md`

Carried-forward meaning from those packets:

1. the original raw-slice8 comparison/readiness lane is closed in current tracked state
2. the runtime bridge artifact is a derived runtime representation of raw slice8
3. the runtime bridge artifact is execution-proof only
4. the runtime bridge artifact is not comparison-eligible in the existing raw-slice8 lane
5. the runtime bridge artifact is not readiness-eligible
6. the runtime bridge artifact is not promotion-eligible

## Lane options under decision

### Option 1 — Comparison lane

Meaning:

- open a new governed lane to decide whether a derived runtime representation could become comparison-eligible under separately defined constraints

Current suitability:

- **not selected by this packet**

Why it is not selected now:

- the bridge artifact has already been classified as not comparison-eligible in the existing raw-slice8 lane
- selecting a comparison lane now would require a new comparison subject and new comparability constraints
- that would be a wider governance opening than is needed for the immediate next legitimate step
- the user explicitly asked not to treat execution-proof as comparison-proof

Important boundary:

- non-selection here does **not** permanently forbid a future separately governed derived-runtime comparison lane
- it means only that such a lane is **not** the next admissible lane chosen by this packet

### Option 2 — Research lane

Meaning:

- continue work as a separate RI research / Optuna track outside the closed raw-slice8 comparison/readiness lane

Current suitability:

- **selected by this packet**

Why it is selected now:

- the terminal closeout already allows a separate research-run / Optuna opening outside the closed lane
- the bridge result already proves one narrow fact that is useful for research continuity:
  - `RI is runnable`
- choosing Research lane avoids smuggling bridge execution into comparison merit
- choosing Research lane avoids reopening readiness or promotion
- choosing Research lane is the narrowest legitimate continuation after execution-proof-only classification

## Decision

### Chosen lane label

- `CHOSEN — Research lane`

### Rejected lane label

- `NOT CHOSEN NOW — Comparison lane`

## Meaning of the decision

This packet selects exactly one next admissible lane:

- **Research lane**

This means the next legitimate continuation is:

- a separate RI research / Optuna track
- outside the closed raw-slice8 comparison/readiness lane
- using the bridge result only as execution-proof that RI is runnable under a runtime-valid RI surface

This decision does **not** mean:

- the bridge artifact is comparison-proof
- the bridge artifact is readiness input
- the bridge artifact is promotion input
- a derived-runtime comparison lane is now open
- a future separately governed comparison lane is permanently forbidden

## Allowed use of the bridge result in the chosen lane

Inside the chosen Research lane, the bridge result may support only the following bounded claim:

- `RI is runnable under current runtime-valid RI semantics`

That bridge result may be used only to justify:

- continued RI research / Optuna work
- continued runtime-valid RI experimentation
- continued investigation of RI candidate behavior on a research track

## Disallowed use of the bridge result in the chosen lane

Even inside the chosen Research lane, the bridge result may **not** be used to claim:

- `raw slice8 is directly runnable unchanged`
- `the bridge artifact is comparison-eligible`
- `the bridge artifact is readiness-eligible`
- `the bridge artifact is promotion-ready`
- `the bridge run establishes incumbent comparison merit`

## Why Comparison lane is not the next lane

Comparison lane is not selected now because the bridge artifact is a derived runtime representation rather than the already governed raw slice8 subject.

A comparison lane built on the bridge artifact would therefore need to answer a new class of subject-validity and comparability questions.

Those questions are broader than what is required to choose the immediate next admissible lane.

Therefore the narrower and cleaner next step is:

- continue as Research lane
- do not silently convert execution-proof into comparison-proof

## Next allowed step inside the chosen lane

The next allowed step after this packet is:

- a separate research-run / Optuna packet for RI work that remains outside readiness and promotion

That later research packet may cite the bridge result only for runtime-runnability.

It may not cite the bridge result as comparison merit, readiness support, or promotion support.

## Bottom line

After execution-proof-only bridge classification, the next admissible lane is now explicitly decided as:

- **Research lane**

The Comparison lane is **not** selected now.

The bridge result may support only the bounded research claim:

- `RI is runnable`

It may not be upgraded by this packet into comparison-proof, readiness input, or promotion support.
