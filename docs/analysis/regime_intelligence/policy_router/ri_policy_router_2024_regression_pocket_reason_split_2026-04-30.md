# RI policy router 2024 regression pocket reason split

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / docs-only fixed-pocket reason reread / observational only`

This slice is a bounded reread of the already-materialized 2024 regression pocket.
It does **not** reopen raw annual JSONs, curated candles, helper code, tests, or new artifacts.
It does **not** authorize runtime tuning, policy changes, promotion claims, or cross-year generalization.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** reread the exact fixed 2024 blocked target cluster by blocker reason only, using the already-emitted pocket artifact.
- **Candidate:** `fixed 2024 regression pocket blocker-reason split`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Skill Usage:** `decision_gate_debug`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

Allowed direct inputs were restricted to:

- `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`

Artifact packaging note:

- the source JSON artifact remains reproducible local evidence and is still ignored under current repo policy unless explicitly staged

No fresh reads from raw annual enabled-vs-absent JSONs, curated candle parquet, or new helper outputs were used in this slice.

## Fixed row-membership surface

Authoritative row membership for this slice is the fixed nine-row timestamp set already materialized in `results/evaluation/ri_policy_router_2024_regression_pocket_isolation_2026-04-30.json`.
Reason labels are descriptive only and are not used to widen selection.

### `AGED_WEAK_CONTINUATION_GUARD` subset (`4` rows)

- `2024-11-28T15:00:00+00:00`
- `2024-11-29T00:00:00+00:00`
- `2024-11-30T12:00:00+00:00`
- `2024-11-30T21:00:00+00:00`

### `insufficient_evidence` subset (`5` rows)

- `2024-11-29T09:00:00+00:00`
- `2024-11-29T18:00:00+00:00`
- `2024-11-30T03:00:00+00:00`
- `2024-12-01T15:00:00+00:00`
- `2024-12-02T00:00:00+00:00`

The nearby `2024-12-01T00:00:00+00:00` and `2024-12-01T06:00:00+00:00` rows are cited only as previously established context from the completed 2024 pocket note.
They are **not** a new comparison cohort, denominator, or extension of the fixed 2024 pocket in this slice.

## Main result

The exact 2024 blocked target cluster becomes **sharper** when split by blocker reason, but it still does not collapse into a fully clean single-reason seam.

The clearest bounded reading is:

1. the `insufficient_evidence` subset carries the stronger local weakness
2. the `AGED_WEAK_CONTINUATION_GUARD` subset is more mixed than uniformly weak
3. the total pocket still remains a mixed local suppression surface rather than a clean one-reason answer

So this reread tightens the local interpretation, but it does **not** convert the 2024 pocket into a runtime-authoritative `insufficient_evidence` verdict by itself.

## Evidence summary

### 1. `insufficient_evidence` is the weaker subset on the local outcome surface

For the exact `insufficient_evidence` subset (`5` rows):

- `fwd_4` mean: `-0.556048%`
- `fwd_8` mean: `-1.305251%`
- `fwd_16` mean: `-0.855705%`
- `fwd_16` median: `-0.744680%`
- `fwd_16 > 0` share: `0%`
- `mfe_16` mean: `+0.724505%`
- `mae_16` mean: `-2.480330%`

This is the cleaner weak local profile inside the exact nine-row target cluster.
The subset is negative across the full `fwd_8` and `fwd_16` surface, has no positive `fwd_16` rows, and also has materially worse downside than the aged-weak subset.

### 2. `AGED_WEAK_CONTINUATION_GUARD` is mixed rather than cleanly weak

For the exact `AGED_WEAK_CONTINUATION_GUARD` subset (`4` rows):

- `fwd_4` mean: `+0.699883%`
- `fwd_8` mean: `+0.969128%`
- `fwd_16` mean: `+0.076218%`
- `fwd_16` median: `-0.339361%`
- `fwd_16 > 0` share: `25%`
- `mfe_16` mean: `+2.341886%`
- `mae_16` mean: `-1.216025%`

This is not a uniformly healthy subset — the median is still negative and only `1 / 4` rows is positive on `fwd_16` — but it is materially less weak than the `insufficient_evidence` subset on the same local proxy surface.

### 3. The weaker subset is also weaker on the local strength proxies

Compared with the `AGED_WEAK_CONTINUATION_GUARD` subset, the exact `insufficient_evidence` rows are also weaker on the already-emitted strength fields:

- `bars_since_regime_change` mean: `281.4` vs `281.0` (`+0.4` later for `insufficient_evidence`)
- `action_edge` mean: `0.027769` vs `0.056509`
- `confidence_gate` mean: `0.513884` vs `0.528254`
- `clarity_score` mean: `36.2` vs `37.75`

So the local 2024 reason split is not just an outcome split.
The `insufficient_evidence` rows are also weaker on the already-emitted edge/confidence/clarity surface, even though the regime-age difference between the two reason subsets is very small.

## Interpretation

This note is observational and local to one fixed 2024 regression pocket.
It carries no runtime, promotion, or cross-year authority and makes no causal router-rule claim.

Within that bounded envelope, the reason split supports a narrower reading than the previous pocket note:

> the exact 2024 pocket does not look like one uniformly weak blocked cluster. Its local weakness is carried more clearly by the `insufficient_evidence` rows, while the `AGED_WEAK_CONTINUATION_GUARD` rows remain mixed and closer to flat on `fwd_16`.

That is useful, but still bounded.
It does **not** mean that `AGED_WEAK_CONTINUATION_GUARD` is benign globally, and it does **not** mean that the local 2024 pocket is now explained cleanly enough to justify a router change.

## What this slice supports

- the exact 2024 pocket weakens more clearly on the `insufficient_evidence` subset than on the `AGED_WEAK_CONTINUATION_GUARD` subset
- the `AGED_WEAK_CONTINUATION_GUARD` subset remains mixed rather than cleanly strong or cleanly weak
- the exact 2024 nine-row target cluster is therefore more structured than a single undifferentiated blocked mass

## What this slice does **not** support

- runtime weakening of `insufficient_evidence`
- runtime weakening of `AGED_WEAK_CONTINUATION_GUARD`
- year-level generalization from this local split alone
- reopening raw-source mining from this note
- promotion/readiness claims

## Consequence

The 2024 line is now tighter than before:

- the full pocket remained a compact suppression/displacement blend
- the internal blocked-target split now says the clearest local weakness sits on the `insufficient_evidence` side, not evenly across both blocker reasons

If this lane is reopened again, the next honest bounded move should now be comparative rather than rediscovery-oriented, for example:

1. compare the exact 2024 `insufficient_evidence` subset against one similarly fixed non-March negative-year subset outside the exhausted March 2021 / March 2025 loop, or
2. compare the exact 2024 `insufficient_evidence` subset against the already-established nearby stable context only if a new explicit packet opens that comparison surface.

## Validation notes

- fixed row-membership check held: `4 + 5 = 9`
- the note used only the already-emitted 2024 pocket artifact and committed anchor notes
- no new helper, test, or artifact was added in this slice
- all claims in this note remain observational and local only
