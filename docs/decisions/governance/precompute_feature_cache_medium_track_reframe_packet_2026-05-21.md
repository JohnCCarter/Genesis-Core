# Precompute / feature-cache medium-track reframe packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `reframe-recorded / docs-only / non-authorizing`

This packet records the bounded Wave 3 reframe of the historically grouped `#2 + #12` medium track. It grants no runtime, backtest, test, script, workflow, env/config, determinism, readiness, paper/live, launch, or promotion authority. It must not be read as approval to begin `src/**`, `tests/**`, or CI/workflow changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/*`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but it sits adjacent to backtest/cache surfaces where wording drift could be mistaken for approval to bundle `#2` and `#12` into one implementation lane
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice re-resolves the branch-visible reading of an already tracked medium seam without reopening runtime behavior
- **Objective:** determine whether Wave 3 should still carry `#2 + #12` as one combined medium track or split them into separate execution lines while preserving their shared stale-reuse family framing
- **Candidate line:** `wave3 #2/#12 stale-reuse reframe`
- **Base SHA:** `49a8070f`
- **Skill Usage:** `none required`

### Scope

- **Scope IN:** this packet; one short live-status addendum in `handoff.md`; explicit observed/inferred/unverified framing; exact current read of `#2` versus `#12`; explicit next admissible move for each line after the reframe
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `.github/**`, `config/**`, `results/**`, and `artifacts/**`; all runtime/backtest changes; all CI/workflow activation; all changes to `PRECOMPUTE_SCHEMA_VERSION`; all `GENESIS_PRECOMPUTE_CONFIG_HASH` semantics changes; all claims that `#12` is implementation-ready; all claims that `#2` already has approved implementation authority
- **Expected changed files:** `docs/decisions/governance/precompute_feature_cache_medium_track_reframe_packet_2026-05-21.md`, `handoff.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual path audit for every referenced packet, code path, and handoff pointer
- manual wording audit that `observed`, `inferred`, and `unverified` remain distinct
- manual wording audit that `#2` existing selector-policy docs are not upgraded from `föreslagen` to implemented
- manual wording audit that `#12` is not upgraded into a code-fix target without a grounded writer/schema-owner
- self-review for hidden behavior impact

### Stop Conditions

- any wording that treats this packet as approval for a bundled `#2 + #12` implementation slice
- any wording that upgrades `#12` into a runtime/backtest enforcement target on current evidence
- any wording that claims `#2` no longer needs a separate pre-code governance pass before `src/core/backtest/**` changes
- any wording that silently changes `GENESIS_PRECOMPUTE_CONFIG_HASH` or schema-bump policy
- any wording that jumps forward to `#7`, `#18`, `#15`, `#1`, or `#16` as if `#2/#12` had already been truthfully re-resolved

## Purpose

This packet answers one narrow question only:

- after the Wave 3 kickoff, should `#2` and `#12` still be carried as one combined medium track?

## What changed in this slice

- one new packet records a shared-family / split-execution reframe for the historically grouped `#2 + #12` lane
- `handoff.md` gains a short live addendum that points the next agent to the current Wave 3 reading

## What did not change

- no runtime/backtest/cache behavior changed
- no tests, scripts, workflows, or env/config semantics changed
- no new writer/schema-owner was located for `#12` in this slice
- no previously proposed `#2` selector-policy or validator carrier was implemented in this slice

## Governing basis

### Observed

1. `handoff.md` currently says the next real Wave 3 track is the previously grouped medium surface `#2 + #12`, and explicitly asks the next agent to reframe whether they still belong together.
2. `docs/decisions/governance/cache_schema_bump_enforcement_boundary_packet_2026-05-18.md` already concluded that `#2` has a real tracked code carrier while `#12` remains under-traced, and it explicitly requires split future follow-up rather than a bundled implementation move.
3. `docs/decisions/governance/cache_schema_bump_touch_triggered_selector_policy_packet_2026-05-19.md` already records a proposed first `#2` enforcement locus: a touch-triggered pytest selector policy on the existing precompute-cache contract tests.
4. `docs/decisions/governance/cache_schema_bump_selector_policy_carrier_decision_packet_2026-05-19.md` already chooses a future repo-visible carrier for that same proposed `#2` line: `scripts/validate/validate_precompute_cache_selector_policy.py`.
5. `docs/decisions/governance/feature_cache_carrier_trace_packet_2026-05-19.md` grounds `#12` only as a training-side read-side feature-artifact seam and explicitly states that no current tracked writer/schema-owner/schema-version owner has yet been grounded.
6. `docs/decisions/governance/feature_cache_architecture_claim_truthfulness_packet_2026-05-19.md` narrowed the stronger architecture wording down to read-side artifact directories and formats, rather than a live tracked feature-cache/schema-owner claim.
7. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` still groups `#2` and `#12` under the broader family theme of `silent stale-reuse` across cache/artifact carriers.
8. The current tracked code/test surface on `feature/risk-hardening-wave3` still matches the `#2` carrier described above (`src/core/backtest/engine.py`, `src/core/backtest/engine_precompute.py`, and the focused cache-contract selectors), and this slice did not uncover new tracked code grounding for `#12`.

### Inferred

- The honest remaining commonality between `#2` and `#12` is a family-level risk frame (`silent stale-reuse / cache-contract drift across distinct carriers`), not a shared implementation carrier.
- Keeping them as one combined execution queue would overstate `#12` and under-describe `#2`.
- The most truthful Wave 3 shape is therefore `shared umbrella / split execution`.
- Any code-adjacent follow-up now naturally belongs first to `#2`, not `#12`, and still requires a fresh governance pass before touching `src/core/backtest/**`.

### Unverified in this packet

- whether the next `#2` candidate should stay on the previously proposed selector-policy / validator path or later be superseded by a stronger deterministic config-subset identity candidate in the cache key
- whether `#12` can be grounded to a current tracked writer/schema-owner at all
- whether later evidence will justify keeping `#12` as an active line or narrowing it further into docs-truthfulness only

## Boundary decision

### Current standing conclusion

For `feature/risk-hardening-wave3`, the smallest honest reading is:

- keep `#2 + #12` together only as a shared `silent stale-reuse` umbrella
- split immediate execution into:
  - `#2` — implementation-bearing precompute-cache enforcement/policy seam
  - `#12` — under-grounded feature-artifact/schema trace seam

### Operational consequence for Wave 3

Wave 3 should **not** open a bundled `#2 + #12` implementation slice.

If work continues now, the next admissible move is:

1. **`#2`** — a separate pre-code packet that either confirms the already proposed selector-policy / validator path as the first bounded follow-up, or explicitly argues for a different bounded candidate such as stronger deterministic config-subset identity in the cache key
2. **`#12`** — a separate writer/schema-owner trace packet or a separate docs-truthfulness narrowing packet only

Wave 3 should also **not** jump ahead yet to `#7`, `#18`, `#15`, `#1`, or `#16` as if the `#2/#12` split had already been recorded and the first post-reframe follow-up chosen.

### What this boundary decision does not mean

This boundary decision does **not** mean:

- `#2` is already approved for runtime/backtest changes
- `#12` is fixed, stale, or implementation-ready
- the earlier `#2` selector-policy or validator-carrier packets have been implemented
- `#2` and `#12` no longer belong to the same broader stale-reuse family at all

## Bottom line

Wave 3 now has a more truthful frame: `#2 + #12` still share a family-level stale-reuse theme, but execution should split immediately. `#2` is the only current code-adjacent line on tracked evidence; `#12` remains evidence-first until a current writer/schema-owner is grounded.
