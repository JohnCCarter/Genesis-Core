# Regime Intelligence challenger family — comparison input surface decision packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `decision-prep / comparison-surface class selected / no execution or promotion approved`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet decides which class of comparison-input surface is permitted for future slice8 incumbent comparison work, but it does not approve execution, promotion, or runtime/default changes
- **Required Path:** `Quick`
- **Objective:** Decide which comparison-input surface class is valid for slice8 after the March 26 same-head runtime-materialization attempt was verified blocked by runtime semantics.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `5eadeaac`

### Scope

- **Scope IN:** decide, at governance level, whether slice8 is to be compared through runtime-config materialization, a sanctioned RI canonical materialization contract, or a different governed evidence surface entirely.
- **Scope OUT:** no source-code changes, no config changes, no champion-file changes, no runtime/default changes, no local runtime forcing, no new materialization mechanism implementation, no promotion decision.
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_challenger_family_comparison_input_surface_decision_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For any future enactment of the chosen comparison-surface class:

- explicit governed packet for the specific comparison method
- explicit evidence path and acceptance criteria
- explicit non-promotion / non-writeback / non-runtime-change boundaries unless later broadened under separate governance

### Stop Conditions

- any wording that implies a new champion, promotion approval, or runtime/default approval
- any wording that treats the verified blocker as permission for ad hoc gate-forcing
- any wording that silently approves a new RI canonical materialization mechanism
- any wording that collapses the bootstrap champion context into an execution input or second decision comparator without separate scope reopening

### Output required

- reviewable comparison-input-surface decision packet
- explicit decision among `A`, `B`, or `C`
- explicit statement of what is not approved by this packet

## Purpose

This packet answers a narrower question than execution and a much narrower question than promotion.

The question is:

> Through what class of comparison-input surface is slice8 allowed to be compared against the incumbent same-head control?

This packet does **not** approve:

- same-head comparison execution by itself
- a new materialization implementation
- promotion
- champion replacement
- writeback
- runtime/default change
- cutover

## Upstream governed context

This decision packet is downstream of the following tracked RI artifacts:

- `docs/decisions/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_incumbent_comparison_prep_packet_2026-03-26.md`
- `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_2026-03-26.md`
- `docs/analysis/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md`

Relevant already-governed interpretation:

- slice8 remains the named lead RI research candidate
- incumbent same-head control remains the only primary comparator surface
- bootstrap champion remains background context only
- the March 26 runtime-materialization attempt is verified blocked on two local input paths

## Decision options under review

### Option A — runtime-config materialization

Meaning:

- compare slice8 by materializing a runtime-config input that `scripts/run/run_backtest.py` can execute directly under current runtime semantics

Current verified status:

- **not approved** for the present attempt

Reason:

- Path A failed with `invalid_strategy_family:legacy_regime_module`
- Path B failed with `invalid_strategy_family:ri_requires_canonical_gates`
- the March 26 blocker state shows that current local runtime-materialization paths do not yield an admissible comparison surface for slice8

Governance interpretation:

- Option A is verified blocked under current runtime semantics for this attempt
- this packet does not authorize further local runtime forcing

### Option B — sanctioned RI canonical materialization contract

Meaning:

- define a special sanctioned contract that would materialize slice8 into a runtime-admissible RI canonical comparison input surface

Current verified status:

- **not approved by this packet**

Reason:

- the present blocker state does not merely show a missing launcher detail; it shows a semantic mismatch between slice8's research geometry and RI canonical runtime-admission requirements
- normalizing slice8 into canonical RI runtime semantics here would risk changing what is being compared
- doing so in response to the blocker would amount to a new explicit contract or exception, not a simple continuation of the current comparison attempt

Governance interpretation:

- Option B remains a separate future contract/exception question
- it must not be smuggled in through docs wording or local forcing
- any future B-style route would require its own separate governed packet before implementation or execution

### Option C — a different governed evidence surface entirely

Meaning:

- compare slice8 on a non-runtime evidence surface instead of trying to force it through current local runtime-config admission semantics

Current verified status:

- **approved at decision-class level by this packet**

Important limit:

- this packet approves Option C only as the comparison-surface class
- it does **not** yet approve which exact non-runtime method will be used

## Decision

### Chosen decision: Option C

This packet sets the valid slice8 comparison-input surface class to:

- **Option C — a different governed evidence surface entirely**

### Why Option C is the correct decision now

1. Option A is already verified blocked by current runtime semantics.
2. Option B would reshape the comparison surface into a newly sanctioned runtime-materialization contract and therefore cannot be normalized through this docs-only step.
3. The current blocker is about the legitimacy of the comparison-input surface, not about a missing local launch trick.
4. Further local runtime forcing has already been ruled out.
5. Ad hoc gate additions to satisfy RI canonical validation have already been ruled out.

Therefore the correct governance move is:

- stop trying to make slice8 fit the current local runtime-materialization path,
- do not bless a new canonical RI materialization contract by implication,
- move the comparison question onto a separately governed non-runtime evidence surface.

## What Option C does and does not mean

### Allowed interpretation

Option C means:

- the next legitimate slice8 comparison step must be defined on a different governed evidence surface than current local runtime-config materialization
- a future packet must identify that exact evidence surface explicitly before any comparison execution resumes

### Not allowed interpretation

Option C does **not** mean:

- that all incumbent comparison is impossible
- that slice8 is disqualified as a research candidate
- that a specific new non-runtime comparison method is already approved
- that Option B is permanently forbidden
- that promotion, writeback, or runtime/default change is closer or farther by itself

## Constraints on the next packet

Any next packet opened under Option C must stay within all of the following constraints:

- no further local runtime forcing
- no ad hoc gate additions merely to satisfy RI canonical validation
- no implicit approval of a new RI canonical materialization contract
- no reinterpretation of bootstrap champion context into an execution input
- no promotion/writeback/default/runtime scope expansion unless separately approved

## Required next step after this decision

The next governed step should be:

- a separate packet that defines the exact non-runtime evidence surface to use for slice8 incumbent comparison

That later packet must answer, explicitly and reviewably:

1. what the exact evidence surface is
2. how the candidate and incumbent are represented on that surface
3. what comparability contract applies
4. what outcome language is allowed
5. whether the step is comparison-only or promotion-preparatory only

## Bottom line

The March 26 blocker does **not** authorize more runtime experimentation.

It authorizes a narrower governance conclusion instead:

- slice8 is **not** to be compared through current local runtime-config materialization paths,
- slice8 is **not** to be normalized into a sanctioned RI canonical runtime contract by implication,
- slice8 must instead be compared on a **different governed evidence surface entirely**, to be defined in a separate later packet.
