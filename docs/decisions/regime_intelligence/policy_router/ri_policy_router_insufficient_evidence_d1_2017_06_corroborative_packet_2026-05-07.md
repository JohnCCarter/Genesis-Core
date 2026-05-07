# RI policy router insufficient-evidence D1 2017-06 corroborative packet

Date: 2026-05-07
Branch: `copilot/agent-b-research-prep`
Mode: `RESEARCH`
Status: `föreslagen / corroborative packet / packet-first bounded prep only / docs-only / non-authoritative / no behavior change`

This packet stays inside the Agent B dispatch tuple only:

- `window = 2017-06`
- `question class = corroborative packet framing`
- `output class = packet-first bounded prep`
- `activation state = secondary`

It does **not** duplicate Agent A's `2023-06` implementation-prepared falsifier lane.
It does **not** activate Agent C's dormant `2023-04` fallback lane.
It does **not** widen into March, July `2024`, late-2024, annual-wide rescans, or implementation work.
It does **not** authorize runtime/default/config/policy/promotion/shared-truth updates.

Instead it asks one bounded packet-first question only:

> should control / integration lane consider opening one later exact `2017-06` low-zone suppression subject as corroborative prep, precisely because `2017` shares the June-led suppression shape with `2023` while diverging on the combined and continuation tops?

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: workforce dispatch on base branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — why: this slice creates one docs-only packet and touches no runtime, analysis, helper, test, artifact, or shared-truth surface.
- **Required Path:** `Quick`
- **Lane:** `packet-first bounded prep` — why this is the cheapest admissible lane now: the current repo-visible comparison already says the overlap with `2023` sits on June suppression, so the only honest next move for Agent B is to frame one later exact `2017-06` corroborative subject rather than reopen annual scans or imitate Agent A's implementation lane.
- **Objective:** define one later exact `2017-06` corroborative subject boundary without claiming that the later subject is already validated.
- **Candidate:** `2017-06 low-zone suppression corroborative subject`
- **Base branch:** `feature/next-slice-2026-05-06`
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08`
- **Question fingerprint:** `qfp_d1_2017_06_corroborative_packet_v1`
- **Skill Usage:** no suitable repository skill identified for this bounded docs-only corroborative slice.

## Allowed inputs for this packet

- `docs/decisions/governance/workforce/workforce_v1_wave1_cloud_batch_dispatch_2026-05-07.md`
- `docs/decisions/governance/workforce/workforce_v1_wave1_agent_b_d1_2017_06_cloud_dispatch_2026-05-07.md`
- `docs/governance/worker_governance_envelope.md`
- `workforce_roadmap.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`

No new helper, test, analysis note, or result JSON is opened by this packet.

## Observed bounded basis

From the completed mixed-year comparison note only:

1. `2017` and `2023` share the same top suppression month: `June`.
2. `2017` does **not** share `2023`'s top combined month:
   - `2017` top combined month = `July`
   - `2023` top combined month = `December`
3. `2017` does **not** share `2023`'s top continuation month:
   - `2017` top continuation month = `March`
   - `2023` top continuation month = `December`
4. The note's smallest honest cross-year read is therefore split:
   - overlap exists on June-led suppression
   - divergence remains on combined and continuation structure

That is enough for one narrow corroborative framing claim:

> if Agent B does anything later, it should stay on the June-suppression overlap only, because the rest of the `2023` mixed-year shape is explicitly not shared with `2017`.

## Exact later subject this packet frames

If control / integration lane chooses to open a later bounded follow-up, the only subject framed by this packet is:

- instrument/timeframe: the same exact subject family already implied by the named mixed-year annual comparison inputs
- window: `2017-06-01` through `2017-06-30`
- phenomenon: low-zone suppression rows only
- comparison role: corroborative external subject for June suppression overlap only
- selector boundary:
  - absent action = `LONG`
  - enabled action = `NONE`
  - zone = `low`
  - switch reason in `{insufficient_evidence, AGED_WEAK_CONTINUATION_GUARD}`

Fail-closed constraints for any later step:

- the later step must stay exact to `2017-06`
- the later step must not reopen March as a rescue loop
- the later step must not use July `2024`, late-2024, or annual-wide rescans as justification
- the later step must not widen into a second implementation lane
- if the exact `2017-06` subject cannot be isolated honestly from already named evidence anchors, the later step should park rather than widen

## Explicit non-overlap with Agent A and Agent C

### Agent A non-overlap

Agent A owns:

- `2023-06`
- `D1 external falsifier`
- `implementation-prepared deep-dive`
- the primary activation state

This packet therefore does **not** do any of the following:

- claim `2017-06` is a falsifier replacement for `2023-06`
- reuse Agent A's output class
- define helper/test/artifact work that would become an implementation-prepared lane
- imply that `2023-06` should be paused, superseded, or reinterpreted

The honest boundary is narrower:

> Agent B is only framing whether one later exact `2017-06` June-suppression subject might be worth a bounded corroborative packet, precisely because that is the shared component and not the distinctive `2023` shape Agent A owns.

### Agent C non-activation

Agent C remains dormant on `2023-04`.
Nothing in this packet opens, references, or backfills that fallback lane.

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_2017_06_corroborative_packet_2026-05-07.md`
- **Scope OUT:**
  - all `2023-06` files owned by Agent A
  - all `2023-04` files owned by Agent C
  - `docs/analysis/**`
  - `results/**`
  - `scripts/**`
  - `tests/**`
  - `src/**`
  - `config/**`
  - `GENESIS_WORKING_CONTRACT.md`
  - March, July `2024`, late-2024, and annual-wide rescans

## Optional bounded planning appendix

If control / integration lane wants to continue later, the bounded follow-up should be sized as:

1. one exact `2017-06` subject-opening step only
2. packet-first or packet-plus-bounded-evidence only if non-overlap with Agent A remains explicit
3. fail closed immediately if the step starts to require helper creation, test creation, result JSON creation, or widened annual rereads merely to justify its existence

Anything larger than that would leave Agent B's dispatch envelope.

## What this packet does **not** prove

This packet does **not** prove:

- that `2017-06` is already a valid external falsifier
- that the exact `2017-06` row set is already isolated and verified
- that June suppression alone can carry transport-clean or runtime-ready authority
- that Agent A's `2023-06` lane should be replaced, paused, or merged into this lane
- that Agent C's dormant fallback should be activated
- that any runtime/default/config/policy/promotion change is admissible

## Recommended next step for control / integration lane

Either:

1. open one later exact `2017-06` corroborative subject step that stays packet-first and June-suppression-only, or
2. park this packet if that exact subject cannot be opened without widening beyond the dispatch envelope.

The recommended integration class for this packet is therefore `deep-dive` only in the narrow sense of a later exact `2017-06` corroborative follow-up, not an implementation lane and not a shared-truth promotion.
