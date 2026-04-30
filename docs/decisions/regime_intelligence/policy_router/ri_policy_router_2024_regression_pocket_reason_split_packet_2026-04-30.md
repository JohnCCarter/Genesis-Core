# RI policy router 2024 regression pocket reason split packet

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `proposed / docs-only fixed-pocket reason-split reread / no behavior change`

Relevant skills: `decision_gate_debug`

Skill coverage for this slice is explicit and bounded:

- `decision_gate_debug` governs the separation between the two blocker reasons inside the already-fixed 2024 pocket and prevents accidental drift back into year-wide or runtime-oriented claims.
- no additional repository skill-coverage claim is made for code work in this slice because it is docs-only and introduces no new helper or test surface.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice rereads one already-emitted local 2024 evaluation artifact plus committed notes only, emits one new analysis note, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: one exact 2024 pocket has already been materialized, so the next honest move is to split its fixed blocked target cluster by the two already-present blocker reasons before proposing any broader comparison or new helper.
- **Objective:** determine whether the exact 2024 fixed blocked target cluster separates descriptively into a cleaner `insufficient_evidence` sub-pocket versus `AGED_WEAK_CONTINUATION_GUARD` sub-pocket, or whether the reason split still behaves as a mixed local surface.
- **Candidate:** `fixed 2024 regression pocket blocker-reason split`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Skill Usage:** `decision_gate_debug`

## Exact allowed input surface

This slice is fail-closed to the already-emitted 2024 pocket artifact and its committed descriptive anchors only.

Allowed direct evidence inputs:

- `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`

No fresh reads from upstream annual enabled-vs-absent JSON files, curated candles, or new row discovery are in scope for this slice.

## Exact reason-subset surface

This slice may summarize only the already-materialized `regression_target` cohort from the 2024 pocket artifact, split by its two fixed blocker reasons.
Authoritative row membership for this slice is the fixed nine-row timestamp set already materialized in `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`. Reason labels are descriptive only and may not be used to widen selection.

### Exact `AGED_WEAK_CONTINUATION_GUARD` target subset (`4` rows)

- `2024-11-28T15:00:00+00:00`
- `2024-11-29T00:00:00+00:00`
- `2024-11-30T12:00:00+00:00`
- `2024-11-30T21:00:00+00:00`

### Exact `insufficient_evidence` target subset (`5` rows)

- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

The slice may reference the already-fixed nearby rows only as context already established by the previous note:

- true displacement row: `2024-12-01T00:00:00+00:00`
- stable blocked context row: `2024-12-01T06:00:00+00:00`

The nearby `2024-12-01T00:00:00+00:00` and `2024-12-01T06:00:00+00:00` rows may be cited only as previously established context. They are not a new comparison cohort, denominator, or extension of the fixed 2024 pocket.

## Exact allowed interpretation surface

Allowed descriptive questions:

- do the `AGED_WEAK_CONTINUATION_GUARD` and `insufficient_evidence` subsets differ directionally on the already-emitted local observational proxy surface?
- does one blocker reason account for most of the weak local profile inside the exact 2024 pocket?
- or do both reasons remain part of the same mixed local suppression surface?

Allowed fields are limited to values already present in the emitted 2024 artifact, especially:

- `switch_reason`
- `timestamp`
- `bars_since_regime_change`
- `action_edge`
- `confidence_gate`
- `clarity_score`
- `fwd_4_close_return_pct`
- `fwd_8_close_return_pct`
- `fwd_16_close_return_pct`
- `mfe_16_pct`
- `mae_16_pct`

Not allowed:

- new thresholds
- new runtime-policy hypotheses presented as if already justified
- year-wide extrapolation
- fresh row discovery
- recomputing the 2024 pocket from raw sources instead of rereading the emitted artifact
- turning the nearby stable rows into a new primary comparison surface
- joins, new metrics, new helper code, new test code, and new artifacts

## Exact output path to materialize

- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`

Optional follow-up only if materially sharpened:

- `GENESIS_WORKING_CONTRACT.md`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_packet_2026-04-30.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`
  - optional refresh of `GENESIS_WORKING_CONTRACT.md` only if the reason-split conclusion materially changes the next admissible step
- **Scope OUT:**
  - no new Python helpers, tests, or artifacts unless the packet is explicitly reopened
  - no runtime/config/schema/authority/default changes
  - no new backtest reruns
  - no new reads from raw source JSON/candle inputs beyond the already-emitted 2024 pocket artifact
  - no widening to additional 2024 pockets, years, or neighboring rows
  - no promotion/readiness/champion claims
- **Expected changed files:** 2-3
- **Max files touched:** 3

## Planned method

1. reread the existing 2024 pocket artifact only
2. isolate the fixed target rows by blocker reason using the already-emitted per-row payload
3. document whether the local weak profile concentrates inside one reason subset or remains mixed across both blocker reasons
4. allow the note to conclude boundedly that the 2024 pocket reason split is still mixed if that is what the existing artifact says

This slice is descriptive and non-authoritative. It does not authorize runtime threshold changes, router-policy changes, family/champion/promotion claims, readiness claims, or broader year-level follow-up by itself.
This note is observational and local to one fixed 2024 regression pocket. It carries no runtime, promotion, or cross-year authority and makes no causal router-rule claim.

## Validation requirements

- `get_errors` on the new packet/note and any touched working-contract file
- manual number check against the already-emitted 2024 pocket artifact
- `pre-commit run --files` on the touched docs files
- manual diff review confirming no drift beyond this docs-only reason-split reread

### Docs-only trace rule

Every quoted number, subgroup count, timestamp membership claim, and mixed-vs-clean inference in the note must trace directly to the allowed 2024 pocket artifact or one of the cited committed notes. No uncited numeric claims or fresh recomputations from raw annual files are allowed in this slice.

Done criteria for this slice:

- the note stays bounded to the already-emitted 2024 pocket artifact
- all quoted subgroup timestamps and summary numbers match the artifact exactly
- the note remains descriptive/non-authoritative
- the slice may honestly conclude that no clean single-reason local seam emerges inside this exact 2024 pocket if that is what the artifact says

## Stop conditions

- the note starts depending on fresh source-row mining rather than the existing 2024 pocket artifact
- the interpretation starts implying runtime tuning or year-level authority
- the slice needs new code or new artifacts to say anything honest
- scope drifts beyond the packet/note/optional working-contract trio

## Output required

- one human-readable reason-split note stating what the exact 2024 blocker split does and does not justify
- exact validation outcomes
