# Evidence claim adoption boundary

Status: `governance runbook / complementary / no new authority`

This runbook explains **when** to use `docs/governance/templates/evidence_claim_header.md` and **when not to**.

It exists to reduce evidence-to-authority drift without turning ordinary `RESEARCH` notes into STRICT-style paperwork.

## What this runbook does not do

This runbook does **not**:

- override `.github/copilot-instructions.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md`, or `AGENTS.md`
- turn the claim header into a new SSOT
- make every scratch note carry a provenance block
- grant runtime, promotion, readiness, paper/live, or champion authority

## Core rule

Use the claim header **when the note is likely to carry decision weight outside its immediate scratch context**.

Do **not** use it as a blanket requirement for every exploratory read.

## Use the claim header when any of these are true

- the note claims a result is reproducible
- the note compares baseline versus candidate behavior
- the note cites an artifact hash, summary hash, or frozen bundle
- the note says something is unchanged / identical / divergent in a way that may influence later work
- the note is likely to be cited in a packet, signoff, review, or promotion discussion
- the note is likely to influence a runtime-adjacent, config-authority-adjacent, or paper-adjacent decision later
- the note is being written as a deliberate evidence summary rather than a local scratchpad

## A lighter scratch note is still acceptable when all of these are true

- the work is exploratory or provisional
- the note is not making a fresh reproducibility claim
- the note is not anchoring a later packet or decision by itself
- the note is not citing a new artifact hash as proof
- the note is clearly readable as a local question, hunch, or first read rather than a locked result

## Practical classification

### 1. Scratch read

Typical shape:

- quick local question
- rough comparison idea
- hypothesis list
- bounded observational jotting

Expected posture:

- no claim header required
- clearly mark the note as exploratory / provisional if ambiguity is possible

### 2. Claim-bearing evidence note

Typical shape:

- deterministic comparison summary
- exact-subject evidence summary
- artifact-backed synthesis note
- note that says a field/screen/path did or did not survive a check

Expected posture:

- use the claim header
- separate `observed`, `inferred`, and `unverified`
- record whether the evidence was rerun in the current slice

### 3. Historical note touched for housekeeping only

Typical shape:

- move, rename, normalization, wording cleanup
- adding a historical status note
- taxonomy repair without changing the substantive claim

Expected posture:

- do **not** force a new claim header just because the file was touched
- preserve historical framing instead of rewriting the note as current execution guidance

### 4. Packet- or review-adjacent evidence note

Typical shape:

- evidence likely to be quoted in a packet, signoff, or review
- note that narrows the next admissible step
- note that explains why a runtime-adjacent question is or is not ready

Expected posture:

- use the claim header
- make the non-authority boundary explicit
- remember that the header improves provenance but does **not** replace a required packet or review path

## Adoption boundary for existing notes

Do **not** try to retrofit the entire archive.

Prefer this order:

1. new claim-bearing notes
2. existing notes that are being materially updated with new claims
3. frequently cited evidence notes that currently lack enough provenance context

Low-priority cases:

- old notes touched only for formatting or relocation
- historical notes that are clearly non-active and not being reused as live anchors
- pure scratch notes that are not leaving their local exploratory context

## Minimal use ritual

1. ask: will this note carry decision weight outside the immediate scratch context?
2. if **no**: keep the note light and clearly exploratory
3. if **yes**: copy the claim header and fill only the fields that are actually known
4. if the evidence was not rerun in this slice, say so explicitly
5. if the subject approaches runtime/default/paper/live/champion surfaces, stop treating the header as enough and open the appropriate governed path

## Common failure modes to avoid

- using a scratch note as if it were a packet-grade evidence anchor
- backfilling guessed SHAs, hashes, or provenance from memory
- treating `validate` success as proof of live-write authority
- adding the header and then blurring `observed` versus `inferred`
- assuming the header itself grants readiness, promotion, or runtime authority

## Relationship to nearby helper docs

Use together with:

- `docs/governance/templates/evidence_claim_header.md` — the actual copyable header
- `docs/governance/active_lane_index.md` — short pointer to current versus parked lanes
- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md` — example of a current-state claim-bearing reference note

## Bottom line

The claim header should be **trigger-based, not universal**. Use it when a note starts becoming evidence that other work may rely on; skip it when the note is still just local exploration. That keeps `RESEARCH` fast while making decision-bearing evidence harder to overstate.
