# Feature Attribution v1 — Phase 4 runner-boundary packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase4-proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet freezes the future single-unit ablation runner boundary for Feature Attribution v1 and therefore carries cumulative authority-drift risk even though it remains docs-only and non-authorizing.
- **Required Path:** `Quick`
- **Objective:** Define the future single-unit execution-plan boundary for Feature Attribution v1 without authorizing commands, execution, artifact generation, schema authority, or runtime change.
- **Candidate:** `future Feature Attribution v1 runner boundary`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; inherited-lock confirmation from Phase 0 through Phase 3; future single-unit run-shape boundary; baseline provenance classification rule; future run metadata minimum; reserved future output path placeholders only; explicit non-adoption of execution-plan semantics by reference.
- **Scope OUT:** no source-code changes; no tests; no execution; no commands; no CLI definition; no env-var policy; no concurrency, retry, scheduler, cache, or batch semantics; no artifact generation authority; no runtime/config/result changes; no changes under `src/**`, `tests/**`, `config/**`, or `results/**`; no fib reopening.
- **Expected changed files:** `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase4_runner_boundary_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only consistency check against controlling Phase 0, Phase 1, Phase 2, and Phase 3 packets
- manual wording audit that the packet remains runner-outline only
- manual wording audit that reserved paths remain placeholders only

For interpretation discipline inside this packet:

- neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes execution, artifact generation, or runtime change
- only one admitted Phase 1 row may appear in a future run request
- the locked baseline context from Phase 0 and Phase 3 remains controlling
- reserved paths are placeholders only and confer no generation authority

### Stop Conditions

- any wording that defines commands, CLI flags, env vars, concurrency, retries, scheduler behavior, cache policy, or artifact-emission semantics
- any wording that authorizes batch or multi-unit execution
- any wording that treats reserved paths as approved output locations rather than placeholders
- any wording that reopens fib-derived units or citation-only / excluded Phase 1 rows
- any wording that imports execution authority by analogy from another packet or skill

### Output required

- one reviewable Phase 4 RESEARCH runner-boundary packet
- one future single-unit run-shape boundary
- one future metadata minimum set
- one reserved-path placeholder discipline statement

## What this packet is

This packet is docs-only, research-only, and non-authorizing.
Neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes running a runner, generating artifacts, executing tests, changing runtime behavior, or opening implementation authority.

This packet describes only the future admissibility boundary for what a later single-unit attribution execution request would have to look like if a separate later packet ever sought approval.

## Inherited controlling packets

This packet inherits and does not weaken:

- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase1_feature_inventory_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase2_toggle_boundary_packet_2026-03-31.md`
- `docs/decisions/feature_attribution/v1/feature_attribution_v1_phase3_baseline_metrics_packet_2026-03-31.md`

The following remain locked and unchanged:

- research-only
- additive-only
- no-default-behavior-change
- fib non-reopen
- one admitted Phase 1 row at a time only
- candidate-vs-locked-baseline only

## Future single-unit run shape

Any future execution request under this lane must remain all of the following:

- one selected admitted Phase 1 row only
- one locked baseline context only
- one symbol/timeframe/window only
- one future run identifier only
- one effective-config diff surface only, as constrained by Phase 2
- one baseline metrics surface only, as constrained by Phase 3

The following are forbidden in the future run shape unless separately reopened later:

- multi-unit batches
- stacked selectors
- repeated auto-retry loops
- concurrent candidate execution
- leaderboard generation
- family replacement analysis

## Future baseline provenance rule

Any later execution request must classify its baseline provenance exactly as:

- `locked historical attribution baseline under explicit Phase 3 anchor`

If a later request cannot maintain that classification, it must stop and return for a separate governance review.

This packet does not authorize baseline materialization or baseline mutation.

## Future metadata minimum

If a later execution request is ever opened, its future execution packet must record at minimum:

- `run_id`
- `git_sha`
- `branch`
- `executed_at_utc`
- selected exact Phase 1 row label
- symbol
- timeframe
- start date / end date
- baseline source anchor
- baseline metrics source anchor
- effective-config diff reference
- controlling packet paths for Phase 0 through Phase 4

These are future metadata minima only.
They do not authorize creating any execution packet now.

## Reserved future path placeholders

If a later packet ever opens execution, the following placeholder families may be used as future naming anchors only:

- `results/research/feature_attribution_v1/runs/<run_id>/`
- `results/research/feature_attribution_v1/reports/<run_id>/`
- `results/research/feature_attribution_v1/manifests/<run_id>.json`

These are naming placeholders only.
They confer no generation authority, no schema authority, and no requirement that any file be created there now.

## Non-adoption-by-reference boundary

Structural analogies to governed execution-plan documents elsewhere in the repository are analogy-only anchors.
They do not import commands, CLI shapes, env-var settings, artifact contracts, or approval semantics into Feature Attribution v1 by reference.

In particular:

- `docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_rerun_execution_plan_2026-03-17.md` is a structural analogy only
- `.github/skills/backtest_run.json` is a discipline/spec anchor only and is not adopted by reference here

## Bottom line

Phase 4 freezes only the future runner boundary for Feature Attribution v1 by stating that:

- any future execution request must be single-unit and single-baseline
- only admitted Phase 1 rows may appear
- baseline provenance must remain locked to the Phase 3 anchor
- metadata minima are future-only requirements
- reserved paths are placeholders only
- no command, env, concurrency, batch, or artifact-emission semantics are authorized

This packet outlines a future run shape.
It does not approve a run.
