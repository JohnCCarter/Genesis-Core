# RI policy router insufficient-evidence local window

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only fixed-window evidence / bounded negative-year seam check`

This slice is a read-only follow-up to the blocked-reason split note.
It freezes one exact negative-year `insufficient_evidence` cluster, compares it against nearby `stable_continuation_state` displacement rows, and keeps the remaining local rows as context only.
It does not reopen runtime work, default semantics, promotion surfaces, or the parked aged-weak chain.

All returns and excursion values in this slice are timestamp-close observational proxies on existing evidence rows only.
They are descriptive only and do not establish realized trade PnL, fill-aware row truth, causal superiority, runtime authority, or promotion readiness.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads one fixed annual action-diff file plus curated candles only and emits one bounded JSON artifact plus this note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: annual blocker evidence already pointed at `insufficient_evidence`, so the missing step was one exact local seam check before any broader policy framing.
- **Objective:** localize one exact negative-year `insufficient_evidence` carrier window inside the blocked low-zone bars-`8+` cohort and compare it against nearby `stable_continuation_state` displacement rows so suppression and displacement do not get mixed again.
- **Candidate:** `2021-03-26 insufficient-evidence local window`
- **Base SHA:** `1cf34904ac2922f3aa7b062fd3e55200c9069038`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_local_window_packet_2026-04-29.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_blocked_reason_split_2026-04-29.md`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2021_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_insufficient_evidence_local_window_2026-04-29.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_local_window_20260429.py --base-sha 1cf34904ac2922f3aa7b062fd3e55200c9069038`

## Fixed subject that actually materialized

### Exact `insufficient_evidence` target cluster

The helper recovered the exact fixed `<=24h` adjacency group specified in the packet:

- `2021-03-26T12:00:00+00:00`
- `2021-03-27T06:00:00+00:00`
- `2021-03-27T15:00:00+00:00`
- `2021-03-28T00:00:00+00:00`

Shared target context:

- year = `2021`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `71..72`

### Exact displacement comparison rows

Only true nearby `stable_continuation_state` displacement rows were kept in the comparison cohort:

- `2021-03-26T15:00:00+00:00`
- `2021-03-29T00:00:00+00:00`

Shared comparison context:

- absent action = `NONE`
- enabled action = `LONG`
- switch reason = `stable_continuation_state`
- selected policy = `RI_continuation_policy`
- bars since regime change = `71..72`

### Context-only local rows

The local envelope `2021-03-25T12:00:00+00:00 -> 2021-03-29T00:00:00+00:00` also contains four context-only rows:

- three `AGED_WEAK_CONTINUATION_GUARD` suppressions (`LONG -> NONE`)
- one `stable_continuation_state` row with action pair `LONG -> NONE`

These rows are intentionally not mixed into the target-versus-displacement comparison.

## Main result

### 1. The fixed `insufficient_evidence` target rows are not weak on the first proxy surface

All four target rows remain positive on `fwd_16`:

- row count: `4`
- `fwd_16` mean: `+3.692905%`
- `fwd_16` median: `+3.712830%`
- `fwd_16 > 0` share: `100%`
- `mfe_16` mean: `+4.893823%`
- `mae_16` mean: `-1.689717%`

So the packeted `insufficient_evidence` cluster does **not** read like a local group of obviously weak baseline longs.
On this first descriptive proxy surface, it reads like a locally favorable continuation/rebound segment that the router suppressed via `RI_no_trade_policy`.

### 2. The nearby displacement rows are also positive and slightly stronger

The two nearby `stable_continuation_state` displacement rows are also positive on the same proxy surface:

- row count: `2`
- `fwd_16` mean: `+5.141805%`
- `fwd_16` median: `+5.141805%`
- `fwd_16 > 0` share: `100%`
- `mfe_16` mean: `+6.437556%`
- `mae_16` mean: `-0.728333%`

Descriptive gap versus the target cohort:

- `fwd_16` mean gap (`insufficient_evidence` minus displacement): `-1.448900%`
- `mfe_16` mean gap: `-1.543733%`
- `mae_16` mean gap: `-0.961384%`

So this local window is **not** a case where the target `insufficient_evidence` rows dominate the nearby displacement rows.
The displacement rows still look somewhat stronger on the same proxy surface.

### 3. The remaining local context is positive too, especially on the aged-weak side

The context-only rows are not dead weight or obviously bad local leftovers.
They include three `AGED_WEAK_CONTINUATION_GUARD` suppressions with `fwd_16` values `+6.583552%`, `+6.299114%`, and `+6.960388%`, plus one context-only `stable_continuation_state` row at `+1.431091%`.

So the fixed March 2021 envelope reads less like:

> one isolated `insufficient_evidence` over-blocking seam

and more like:

> a broader locally favorable low-zone rebound segment where multiple suppressive reasons coexist while nearby continuation displacement also remains positive.

## Interpretation

This slice still adds something real and useful.
It shows that a fixed negative-year `insufficient_evidence` cluster can contain blocked baseline-long rows that look locally favorable on the first proxy surface.
So `insufficient_evidence` remains a credible suppressor candidate and is not dismissed by this local reread.

But this slice **does not** isolate `insufficient_evidence` as a uniquely clean local handle.
Inside the same envelope:

- the nearby displacement rows are also positive,
- the context-only `AGED_WEAK_CONTINUATION_GUARD` suppressions are positive too,
- and the whole interval looks like a broadly favorable late low-zone continuation/rebound segment rather than a single-mechanism pocket.

So the strongest bounded reading is:

> the March 2021 negative-year window confirms that `insufficient_evidence` can suppress locally favorable baseline longs, but it does **not** prove that this harm is separable from the wider low-zone suppression/displacement cluster in the same interval.

## Consequence for the robust-policy question

This slice narrows the larger question in an honest way.
What it now supports is **not**:

- “flip `insufficient_evidence` and the problem is solved”, or
- “the local harm is purely a displacement artifact”.

What it does support is:

- `insufficient_evidence` is part of a real harmful local negative-year cluster,
- but the cluster is not mechanism-pure,
- so any future robust-policy proposal still needs a protected control that checks whether the same local shape appears in positive years or in other negative-year windows with different outcome direction.

## What this slice does not prove

This slice does **not** prove:

- exact realized trade contribution
- exact one-to-one row pairing between blocked and displaced rows
- runtime-authoritative row truth
- that `insufficient_evidence` is the unique local root cause
- that the parked aged-weak chain should be reopened
- that any runtime/default/policy tuning is justified now

## Next admissible step

If this line is reopened, the cheapest honest move should remain read-only and control-oriented:

1. compare this fixed March 2021 `insufficient_evidence` window against one positive-year `insufficient_evidence` local window with the same comparison framing, or
2. compare it against one clearly weaker negative-year `insufficient_evidence` window where the target rows are actually negative on `fwd_16`.

That would test selectivity for the robust-policy goal without reopening runtime work.

## What is not justified from this slice

- new router tuning
- default-policy changes
- reopening aged-weak runtime work
- claiming that the negative-year harm is now cleanly isolated to `insufficient_evidence`
- claiming promotion or readiness from this local proxy window
