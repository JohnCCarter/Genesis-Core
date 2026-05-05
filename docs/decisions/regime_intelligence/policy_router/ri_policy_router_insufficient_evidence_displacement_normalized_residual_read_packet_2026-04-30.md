# RI policy router insufficient-evidence displacement-normalized residual read packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / read-only artifact reread / no behavior change`

Relevant skills: `decision_gate_debug`, `python_engineering`

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs the bounded interpretation of the already-materialized target-vs-displacement contrasts and prevents accidental drift back into runtime speculation.
- `python_engineering` governs the minimal-diff documentation update and validation discipline even though this slice does not add new runtime or helper code.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads one already-emitted local evaluation artifact plus existing analysis notes only, emits one new analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the four-cohort displacement crosscheck is already complete, so the next honest question is whether any displacement-normalized discriminator survives on that artifact itself before any new source-mining is considered.
- **Objective:** read the already-emitted four-cohort crosscheck artifact and determine whether any candidate metric survives as a displacement-normalized discriminator after the generic target-vs-displacement pattern is accounted for.
- **Candidate:** `fixed 2021/2025 displacement-normalized residual reread`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`

## Exact allowed input surface

This slice is fail-closed to the already-emitted crosscheck artifact and its committed descriptive anchors only.

Allowed direct evidence inputs:

- `results/evaluation/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_discriminator_bundle_displacement_crosscheck_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_year_insufficient_evidence_control_2026-04-29.md`

No new reads from the upstream annual enabled-vs-absent JSON files, curated candle parquet, or fresh row payload discovery are in scope for this slice.

## Exact allowed interpretation surface

This slice may summarize only the already-emitted displacement-normalized residuals from the crosscheck artifact, with special focus on the previously surfaced candidate bundle fields:

- `bars_since_regime_change`
- `dwell_duration`
- `action_edge`
- `confidence_gate`
- `clarity_raw`
- `clarity_score`

The slice may note the observational outcome proxies only as secondary context:

- `fwd_4_close_return_pct`
- `fwd_8_close_return_pct`
- `fwd_16_close_return_pct`
- `mfe_16_pct`
- `mae_16_pct`

Allowed descriptive questions:

- do the candidate bundle fields keep the same sign in both years after target-minus-displacement normalization?
- are any residual differences only magnitude skews rather than directionally selective discriminators?
- does the artifact support an honest null conclusion that no clean displacement-normalized rule candidate remains on the current surface?

Allowed direct inputs are closed to the listed artifact and cited notes. This slice may quote
existing values and recurrence labels only; it may not derive new metrics, rebucket cohorts,
introduce thresholds, recompute normalization, weight fields, or expand to additional windows or
artifacts. If any such extension becomes necessary, stop and reopen the packet.

Not allowed:

- new thresholds
- new runtime-policy hypotheses presented as if already justified
- year-wide extrapolation
- fresh row discovery
- reopening ignored local artifacts as if they were committed evidence

## Exact output path to materialize

- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_2026-04-30.md`

Optional follow-up only if materially sharpened:

- `GENESIS_WORKING_CONTRACT.md`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_packet_2026-04-30.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_displacement_normalized_residual_read_2026-04-30.md`
  - optional refresh of `GENESIS_WORKING_CONTRACT.md` only if the null-vs-residual conclusion materially changes the next admissible step
- **Scope OUT:**
  - no new Python helpers, tests, or artifacts unless the packet is explicitly reopened
  - no runtime/config/schema/authority/default changes
  - no new backtest reruns
  - no new reads from raw source JSON/candle inputs beyond the already-emitted crosscheck artifact
  - no widening to additional years, windows, or neighboring rows
  - no promotion/readiness/champion claims
- **Expected changed files:** 2-3
- **Max files touched:** 3

## Planned method

1. read the existing four-cohort crosscheck artifact only
2. isolate the displacement-normalized residual interpretation on the candidate bundle fields
3. document whether any field remains directionally selective after normalization or whether only same-direction magnitude skews remain
4. allow the note to conclude that no clean rule candidate survives on the current repo-visible surface if that is what the artifact says

This slice is descriptive and non-authoritative. It does not authorize runtime threshold changes, router-policy changes, family/champion/promotion claims, readiness claims, or year-wide follow-up by itself.
On the current repo-visible four-cohort displacement crosscheck surface, the slice may honestly
conclude that no clean displacement-normalized sign-changing discriminator survives once the generic
target-vs-displacement pattern is accounted for. Such a null read is bounded to the allowed inputs
only: it does not imply global absence and does not authorize runtime, policy, or default-behavior
changes.

## Validation requirements

- `get_errors` on the new packet/note and any touched working-contract file
- manual number check against the already-emitted crosscheck artifact
- `pre-commit run --files` on the touched docs files
- manual diff review confirming no drift beyond this docs-only residual reread

### Docs-only trace rule

Every quoted number, recurrence label, and same-sign or magnitude-only inference in the note must
trace directly to the allowed crosscheck artifact or one of the cited committed notes. No uncited
numeric claims or fresh recomputations are allowed in this slice.

Done criteria for this slice:

- the note stays bounded to the already-emitted crosscheck artifact
- all quoted residual numbers match the artifact exactly
- the note remains descriptive/non-authoritative
- the slice may honestly conclude that no clean displacement-normalized discriminator remains on the current surface

## Stop conditions

- the note starts depending on fresh source-row mining rather than the existing artifact
- the interpretation starts implying runtime tuning or policy authority
- the slice needs new code or new artifacts to say anything honest
- scope drifts beyond the packet/note/optional working-contract trio

## Output required

- one human-readable residual-read note stating what the displacement-normalized reread does and does not justify
- exact validation outcomes
