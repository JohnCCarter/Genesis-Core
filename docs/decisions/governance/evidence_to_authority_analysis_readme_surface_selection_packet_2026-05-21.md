# Evidence-to-authority analysis README surface selection packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `decision-recorded / docs-only / non-authorizing`

This packet records the next fresh current-branch `#1` surface after the already-landed premortem
baseline `#16` narrowing. It selects `docs/analysis/README.md` as the next still-misleading,
frequently reused claim-bearing surface on the current branch.

The current slice is docs-only. It does not claim that the broader `#1` family is closed, does not
turn `docs/analysis/README.md` into a new authority surface, and does not authorize runtime or
governance changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice narrows one docs surface only and changes no runtime, tests,
  governance precedence, or workflow gates
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice selects and narrows one claim-bearing docs surface
  without widening into repo-wide claim-header adoption or broader governance work
- **Skill usage:** `none required` — bounded docs-only surface-selection slice
- **Objective:** select and narrow the next fresh current-branch `#1` surface after the first
  premortem-baseline narrowing already landed
- **Related artifacts:**
  `docs/analysis/README.md`, `handoff.md`,
  `docs/decisions/governance/evidence_to_authority_drift_residual_scope_reanchor_packet_2026-05-19.md`,
  `docs/decisions/governance/evidence_to_authority_optimizer_baseline_surface_selection_packet_2026-05-21.md`

### Scope

- **Scope IN:** this packet; one later-branch truthfulness note in `docs/analysis/README.md`; one
  live note refresh in `handoff.md`
- **Scope OUT:** any claim that the broader `#1` family is closed; any repo-wide claim-header
  retrofit; any edits to other README/index surfaces; any runtime/test/config changes; any change to
  governance precedence
- **Expected changed files:**
  `docs/decisions/governance/evidence_to_authority_analysis_readme_surface_selection_packet_2026-05-21.md`,
  `docs/analysis/README.md`, `handoff.md`
- **Max files touched:** `3`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the slice remains surface-selection only and non-authorizing
- manual wording audit that the root analysis README is narrowed as historical branch context rather
  than rewritten as a new authority source
- manual wording audit that the broader `#1` family is not claimed closed

## Purpose

This packet answers one narrow question only:

- what is the next fresh current-branch `#1` claim-bearing surface after the first premortem
  baseline narrowing already landed?

## What changed in this slice

- one new packet selects `docs/analysis/README.md` as the next fresh `#1` surface
- the root analysis README now explicitly reads as a zone guide plus retained historical RI/R1
  overview rather than current wave3 kickoff/work-order guidance
- `handoff.md` is refreshed so wave3 records this second consumed `#1` surface

## What did not change

- no analysis conclusions changed
- no runtime code changed
- no tests changed
- no new authority surface was created
- no repo-wide claim-header rollout was started

## Governing basis

### Observed

1. `docs/analysis/README.md` sits at the root of the analysis zone and is therefore a likely
   first-read navigation surface for later workers.
2. That README currently mixes a general zone guide with a retained historical RI/R1 series
   overview, including:
   - a recommended reading order that begins with `handoff.md`
   - a “master-diff review” summary
   - a “next prioritized analysis surface” for RI/legacy follow-up
3. On `feature/risk-hardening-wave3`, `handoff.md` is no longer a single-purpose RI kickoff note;
   it is a multi-era branch handoff file whose live truth sits in the top current note, while older
   sections remain historical background.
4. The already-landed `docs/decisions/governance/evidence_to_authority_optimizer_baseline_surface_selection_packet_2026-05-21.md`
   explicitly said the next honest `#1` move would require selecting another still-misleading,
   frequently reused claim-bearing surface rather than reusing already-consumed seams.
5. The root analysis README currently lacks an explicit later-branch note telling current wave3
   readers not to treat the retained RI/R1 reading order and follow-up language as branch-current
   execution guidance.

### Inferred

- `docs/analysis/README.md` is a better next `#1` surface than a lower-traffic note because it is a
  root index and can therefore be over-read as current guidance if its retained historical series
  framing is left implicit
- a small later-branch note is enough to narrow this surface truthfully without rewriting the whole
  historical RI/R1 overview
- this slice narrows one concrete over-reading risk without claiming broader `#1` closure

### Unverified

- which exact `#1` surface should come next after this one, if any
- whether broader adoption work is still needed later
- whether other root index surfaces should receive similar treatment in a future bounded slice

## Surface selection conclusion

The next fresh current-branch `#1` surface is:

- the root `docs/analysis/README.md` reading-order / kickoff framing

This selection does **not** close `#1`. It records that one more frequently reused surface has now
been narrowed away from current wave3 execution guidance.

## Bottom line

On wave3, `#1` is no longer abstract only in the premortem baseline. The root analysis README is now
the next bounded surface consumed: it should be read as a zone guide plus retained historical
RI/R1 framing, not as branch-current kickoff/work-order authority.
