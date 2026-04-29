# RI router replay evidence slice1 — pre-code packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code / docs-only / no execution authorization`

This document defines the first bounded research-evidence slice downstream of:

- `docs/analysis/ri_router_replay_concept_case_2026-04-23.md`

It is a planning packet only.
It does **not** authorize code changes, script execution, artifact generation, result mutation, runtime integration, paper/live coupling, or any inherited authority from older SCPE replay documents.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this is still docs-only, but the main risk is over-reading older SCPE replay lineage as inherited authority instead of freezing one fresh bounded evidence subject.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the concept has been chosen; the next need is one exact reproducible evidence subject below runtime/family/default authority.
- **Objective:** define the exact first future RI router replay evidence slice, including frozen references, future input/output envelope, prove-or-stop criteria, and explicit non-inheritance boundaries.
- **Candidate:** `RI router replay bounded evidence slice`
- **Base SHA:** `1b3f118e0407`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/analysis/ri_router_replay_concept_case_2026-04-23.md`
  - `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
  - `docs/decisions/scpe_ri_v1_research_closeout_report_2026-04-20.md` (boundary proof only)
  - frozen historical replay surfaces under `results/research/scpe_v1_ri/` (comparison-only, not inherited authority)
- **Candidate / comparison surface:**
  - one deterministic RI-local router replay over a fixed eligible RI decision population, reported separately for `2024` and `2025`, with explicit comparison against the frozen replay trace/metric contract rather than against runtime behavior.
- **Vad ska förbättras:**
  - evidence discipline around routing stability, policy separability, veto/no-trade visibility, and contradiction-year honesty.
- **Vad får inte brytas / drifta:**
  - runtime behavior
  - default path semantics
  - family/runtime authority boundaries
  - cross-family separation
  - leakage boundary between decision-time fields and realized outcomes
  - the frozen historical SCPE replay root
- **Reproducerbar evidens som måste finnas:**
  - fixed input manifest and hashes
  - deterministic `routing_trace.ndjson`
  - deterministic `replay_metrics.json`
  - approved output manifest and hashes
  - explicit `2024` / `2025` comparison
  - explicit PASS / FAIL / inconclusive framing

### Scope

- **Scope IN:**
  - this one docs-only pre-code packet
  - exact definition of the future bounded evidence subject
  - exact future output envelope
  - exact prove-or-stop conditions for a later runnable slice
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `scripts/**`
  - `results/**`
  - `artifacts/**`
  - any runtime integration
  - any runtime-default or champion authority work
  - any claim that the old SCPE replay lineage grants inherited approval
  - any new strategy family semantics
- **Expected changed files:**
  - `docs/decisions/ri_router_replay_evidence_slice_precode_packet_2026-04-23.md`
- **Max files touched:** `1`

### Gates required

- `pre-commit run --files docs/decisions/ri_router_replay_evidence_slice_precode_packet_2026-04-23.md`

### Stop Conditions

- any wording that treats older SCPE replay or closeout artifacts as inherited runtime or implementation authority
- any widening into code execution, result generation, or runtime surfaces
- inability to define one exact future RI-only replay subject from already cited frozen surfaces
- inability to keep realized outcome fields out of future routing/state logic
- any wording that collapses `2024` and `2025` into one blended story without explicit contradiction handling

### Output required

- one docs-only pre-code packet
- one exact future evidence-slice subject boundary
- one exact future output envelope
- one explicit statement of what remains out of scope

## Decision question

After the concept case chose RI router replay as the first non-runtime container for RI role-map ideas, what is the **exact first research-evidence slice** that should follow?

## Short answer

The first research-evidence slice should be:

- **one bounded RI-local router replay evidence slice with a föreslagen fresh research output root, frozen decision-time inputs, deterministic trace outputs, and explicit `2024` vs `2025` contradiction reporting**

This slice remains:

- RI-only
- research-only
- default unchanged
- non-authoritative
- below runtime integration

It is still smaller than any runtime, family, or paper-shadow lane.

## Why a fresh evidence slice is needed instead of reusing old authority

The repository already contains a historical SCPE replay lineage, including planning, implementation, reports, and a frozen replay root under:

- `results/research/scpe_v1_ri/`

Those surfaces are useful as:

- frozen comparison references,
- shape examples,
- boundary proofs,
- evidence that replay work can exist below runtime.

They are **not** valid as inherited approval for this new lane framing.

This packet therefore fixes the following rule:

- **older SCPE replay lineage may inform the new slice, but it may not substitute for a fresh bounded subject definition under the lane model now in force.**

## Exact future subject boundary

The future runnable slice, if later opened separately, must do exactly this and no more:

1. freeze one RI-only decision-time input manifest from already tracked frozen surfaces,
2. define one deterministic eligible RI decision population,
3. replay one RI-local deterministic router over that population only,
4. emit canonical routing / state / policy / veto traces,
5. summarize routing behavior separately for `2024` and `2025`,
6. stop if the replay requires forbidden fields, hidden runtime assumptions, or cross-family logic.

It must **not** at this stage:

- open runtime integration,
- change defaults,
- claim family authority,
- reopen full RI role-map baseline claims,
- or smuggle trade-level realized outcomes into routing logic.

## Fixed frozen references for the future slice

The future runnable slice may use only already tracked/frozen references unless a later packet explicitly widens scope.

### Boundary and framing references

- `docs/analysis/ri_router_replay_concept_case_2026-04-23.md`
- `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/ri_advisory_environment_fit_trade_level_deterministic_baseline_admissibility_2026-04-17.md`
- `docs/decisions/scpe_ri_v1_research_closeout_report_2026-04-20.md`

### Frozen data/evidence references

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`
- frozen historical comparison surfaces under `results/research/scpe_v1_ri/`

If the future slice needs additional sources beyond these, it must stop and request a separate scope decision.

## Proposed future output root

To avoid conflating the new lane-model subject with older SCPE lineage, the future runnable slice should write to one föreslagen fresh output root if a later runnable packet is separately approved:

- `results/research/ri_router_replay_v1/`

This packet does **not** authorize creating that path now.
It only freezes the intended output envelope for a later separately governed runnable slice.

Approved future files under that root, if that later slice is opened, should be exactly:

- `input_manifest.json`
- `routing_trace.ndjson`
- `state_trace.json`
- `policy_trace.json`
- `veto_trace.json`
- `replay_metrics.json`
- `summary.md`
- `manifest.json`

The old `results/research/scpe_v1_ri/` root remains frozen comparison context only.

## Exact evidence questions the future slice must answer

The future runnable slice must answer only these bounded research questions:

1. Can an RI-local deterministic router be materialized from fixed decision-time state only?
2. Are continuation / defensive / no-trade policies materially distinct in routed posture?
3. Does veto or no-trade dominate so strongly that router-selected policy becomes mostly decorative?
4. Does `2025` materially contradict the apparent `2024` story?
5. Does the replay remain useful as a non-runtime container, or does it collapse without runtime/family semantics?

These are evidence questions only.
They are not runtime, promotion, or integration questions.

## Required future validation envelope

If a later runnable slice is opened, it must prove at minimum:

- deterministic rerun stability
- frozen input hashing
- no forbidden-field leakage into routing/state logic
- no cross-family routing
- no runtime/default mutation
- explicit `2024` / `2025` comparison
- explicit failure reporting if policy separation is weak or veto dominance is high

## PASS / FAIL / inconclusive framing for the future slice

### PASS means only

- the replay stayed deterministic,
- the route/policy/veto traces were structurally interpretable,
- the lane remained below runtime authority,
- and the results were honest enough to justify later consideration of a further bounded deterministic baseline slice.

PASS does **not** mean:

- runtime readiness,
- family promotion,
- backtest superiority,
- or paper/live authorization.

### FAIL means

- hidden runtime assumptions were required,
- the replay required forbidden fields,
- policy separation collapsed,
- veto/no-trade dominated the subject,
- or contradiction-year behavior made the container too weak to carry forward honestly.

### Inconclusive means

- the slice stayed bounded and clean, but the evidence remained too thin or too weakly separated to support the next baseline lane.

## What remains explicitly out of scope after this packet

Even if this packet remains green, the following still remain out of scope until separately reopened:

- runtime integration
- family semantics
- authority surfaces
- champion/default changes
- paper/live coupling
- ML comparison
- full role-map baseline claims

## Bottom line

The exact next research-evidence move is now frozen at pre-code level:

- **one fresh bounded RI router replay evidence slice on research surfaces only**

That gives the lane model a real downstream subject without yet paying runtime cost or inheriting authority from the older SCPE replay lineage.
