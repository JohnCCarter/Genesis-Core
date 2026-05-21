# Evidence-to-authority optimizer-baseline surface selection packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `decision-recorded / docs-only / non-authorizing`

This packet performs the first fresh surface-selection step required by the current `#1`
evidence-to-authority residual. It selects one exact still-misleading, frequently reused
claim-bearing surface on the current branch: the `#16` optimizer carry-forward sentence in
`docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`.

The current slice is docs-only. It does not claim that `#1` is solved, does not approve broader
optimizer work, and does not convert the premortem baseline into a current-authority source.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice selects and narrows one docs surface only; it changes no
  runtime, tests, config, or governance precedence
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice chooses one exact `#1` surface and records a
  truthfulness narrowing without authorizing broader adoption/governance work
- **Skill usage:** `none required` — bounded docs-only surface-selection slice
- **Objective:** choose one exact current-branch `#1` surface and narrow it truthfully without
  implying closure of the broader evidence-to-authority family
- **Related artifacts:**
  `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`,
  `docs/decisions/governance/evidence_to_authority_drift_residual_scope_reanchor_packet_2026-05-19.md`,
  `docs/decisions/governance/optimizer_refactor_trace_reopen_shape_packet_2026-05-19.md`,
  `docs/decisions/governance/optimizer_validation_promotion_contract_seam_packet_2026-05-21.md`,
  `handoff.md`, `src/core/optimizer/runner.py`, `src/core/optimizer/runner_trial_results.py`,
  `tests/utils/test_optimizer_runner.py`

### Scope

- **Scope IN:** this packet; one later-branch partial-reclassification note under `#16` in
  `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`; one live
  handoff note recording that this exact `#1` surface has now been consumed
- **Scope OUT:** any claim that `#1` is closed; any repo-wide claim-header retrofit; any broader
  optimizer refactor plan; any runtime/test/config/script change; any edits to other baseline rows;
  any change to governance precedence or mode rules
- **Expected changed files:**
  `docs/decisions/governance/evidence_to_authority_optimizer_baseline_surface_selection_packet_2026-05-21.md`,
  `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`,
  `handoff.md`
- **Max files touched:** `3`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the slice remains selection-only plus truthfulness narrowing
- manual wording audit that the packet does not imply `#1` closure or broader optimizer approval
- manual wording audit that the baseline remains historical/project-baseline evidence rather than a
  current-authority source

## Purpose

This packet answers one narrow question only:

- what is the first exact still-misleading, frequently reused claim-bearing surface that can be
  honestly selected for a bounded `#1` follow-up on the current branch?

## What changed in this slice

- one new docs-only packet records the first fresh `#1` surface selection
- the premortem baseline now carries a dated later-branch note narrowing the exact `#16` optimizer
  carry-forward reading for this checkout
- `handoff.md` now records that this first exact `#1` surface has been consumed, while the broader
  family-level retelling/adoption risk remains open

## What did not change

- no optimizer code changed
- no optimizer tests changed
- no claim is made that the broader `#16` family is closed
- no claim is made that the broader `#1` family is closed
- no claim-header adoption or governance rewrite was started by this slice

## Governing basis

### Observed

1. `docs/decisions/governance/evidence_to_authority_drift_residual_scope_reanchor_packet_2026-05-19.md`
   explicitly says the next honest `#1` move must first be fresh selection of a specific
   still-misleading, frequently reused claim-bearing surface.
2. `handoff.md` currently lists
   `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` in the
   recommended reading order for wave3, making it an active branch-navigation artifact rather than a
   dormant historical file.
3. A current branch search across `docs/**/*.md` plus `handoff.md` returns dozens of references to
   `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, showing
   that the baseline is repeatedly reused as a claim-bearing context anchor.
4. The optimizer section of that baseline still says:
   `mode #16 (1463 + 1113 rader orchestration) är ren komplexitets-risk. Det finns ingen audit-doc specifikt för optimizer — det är ett tomrum i tracked diagnostics som borde nämnas.`
5. Current branch evidence has moved beyond that exact carry-forward reading: the repo already
   carries `docs/decisions/governance/optimizer_refactor_trace_reopen_shape_packet_2026-05-19.md`,
   `docs/decisions/governance/optimizer_validation_promotion_contract_seam_packet_2026-05-21.md`,
   and a first code-bearing no-behavior-change helper extraction in `src/core/optimizer/runner.py`
   and `src/core/optimizer/runner_trial_results.py`, with the focused optimizer selector suite kept
   green.
6. The exact adjacent seams already consumed under the broader `#1` family are separately tracked in
   packets for citation framing, stale active-lane pointers, paused editor-worker references,
   premortem closeout scope, and premortem anchor-role competition; the selected baseline `#16`
   sentence is not one of those already-consumed surfaces.

### Inferred

- the premortem baseline is a better first fresh `#1` surface than a lower-traffic note because it
  is repeatedly reused and can therefore drift into current-authority reading if stale sentences are
  left unqualified
- the exact `#16` optimizer sentence is now too strong if repeated unchanged for the current branch
- narrowing one sentence in this widely reused baseline is smaller and truer than reopening broad
  `#1` adoption work or broad optimizer refactor planning

### Unverified

- which exact `#1` surface should come next after this one, if any
- whether the broader `#1` family should later propose wider adoption/normalization work
- whether the broader `#16` family should later reopen another optimizer boundary beyond the now
  landed first contract seam

## Surface selection conclusion

The first exact surface selected for a bounded current-branch `#1` follow-up is:

- the `#16` optimizer carry-forward sentence in
  `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

This selection does **not** close `#1`. It records that one widely reused baseline sentence had
become misleading enough on the current branch to justify a bounded truthfulness narrowing.

## Bottom line

`#1` remains a family-level risk, but it no longer needs to stay abstract in this exact spot. The
first fresh current-branch surface is now selected and narrowed: the widely reused premortem
baseline's `#16` optimizer sentence should no longer be retold as if the branch still lacked any
tracked optimizer-specific seam work.
