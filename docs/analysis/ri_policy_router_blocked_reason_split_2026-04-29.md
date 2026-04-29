# RI policy router blocked baseline-long reason split

Date: 2026-04-29
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / docs-only read-only blocker split / next policy seam clarified`

This slice is a read-only follow-up to the shared-pocket outcome-quality chain.
It asks a narrower policy-improvement question:
when blocked baseline `LONG` rows look less weak in the negative years than in the positive years,
is that signal mainly carried by `AGED_WEAK_CONTINUATION_GUARD`, by `insufficient_evidence`, or by
continuation-style displacement that only appears blocked at the action layer?

This slice does **not** modify runtime/config/default/family surfaces, does **not** rerun backtests,
and does **not** authorize tuning by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `LOW` — why: this slice reads already-generated annual action-diff JSONs plus curated
  candles only and writes one research artifact plus one analysis note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the blocked
  baseline-long cohort already looks like the clearest annual divider, so the next honest step is
  to split that cohort by blocker reason before proposing any runtime packet.
- **Objective:** determine whether the blocked baseline-long annual split concentrates in one
  blocker reason or whether it first needs to be separated into continuation displacement versus
  true no-trade suppression.
- **Candidate:** `blocked baseline-long reason split`
- **Base SHA:** `a19ca7b1`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`

## Evidence inputs

- `scripts/analyze/ri_policy_router_blocked_reason_split_20260429.py`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/*_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_blocked_reason_split_2026-04-29.json`
- `docs/analysis/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
- `docs/analysis/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md`
- `docs/analysis/ri_policy_router_blocked_vs_substituted_same_window_phase_ordering_2026-04-29.md`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_blocked_reason_split_20260429.py --base-sha a19ca7b1`

## Cohort definition

Blocked baseline-long rows were defined as:

- absent action = `LONG`
- enabled action = `NONE`
- `zone = low`
- `candidate = LONG`
- `bars_since_regime_change >= 8`

This preserves the same low-zone late-pocket family already identified in the annual and shared-
pocket notes, but it splits that blocked cohort by `switch_reason` and evaluates each reason on the
same timestamp-close observational proxy surface.

## Compared year groups

### Clearly negative full years

- `2019`
- `2021`
- `2024`

### Clearly positive full years

- `2018`
- `2020`
- `2022`
- `2025`

## Main result

The blocked baseline-long cohort is **not** dominated by one pure suppressor.
It first splits into three meaningful masses:

1. `stable_continuation_state`
2. `AGED_WEAK_CONTINUATION_GUARD`
3. `insufficient_evidence`

That means the blocked action-layer cohort is still a mixed surface containing both:

- continuation-style displacement / handoff rows, and
- true no-trade suppression rows.

So the first policy lesson is structural:

> the blocked baseline-long annual split must be separated into displacement versus suppression
> before one suppressor is promoted as the next runtime target.

## Reason hierarchy inside the blocked cohort

### Negative full years (`1092` blocked rows)

Top reasons:

- `stable_continuation_state = 410`
- `AGED_WEAK_CONTINUATION_GUARD = 408`
- `insufficient_evidence = 240`

Smaller tails:

- `switch_blocked_by_min_dwell = 27`
- `continuation_state_supported = 5`
- `confidence_below_threshold = 2`

### Positive full years (`1559` blocked rows)

Top reasons:

- `stable_continuation_state = 690`
- `AGED_WEAK_CONTINUATION_GUARD = 490`
- `insufficient_evidence = 321`

Smaller tails:

- `switch_blocked_by_min_dwell = 51`
- `continuation_state_supported = 7`

## What the hierarchy means

### 1. The largest blocked bucket is `stable_continuation_state`, not a no-trade blocker

This is the most important new finding.

On the blocked action-layer surface, the largest reason in both year groups is:

- `stable_continuation_state`

Those rows are therefore **not** cleanly read as a pure suppressor seam.
They belong to a continuation/displacement family that still lands in enabled `NONE` on this
aggregate action-diff surface.

So the blocked cohort is not identical to “rows vetoed by one over-strict no-trade rule”.
A large share is still a **timing / handoff / displacement** story.

### 2. Among the true suppressors, `insufficient_evidence` looks more suspect than `AGED_WEAK_CONTINUATION_GUARD`

Shared-reason comparison on `fwd_16`:

#### `insufficient_evidence`

- negative rows: `240`
- positive rows: `321`
- negative `fwd_16` mean: `+0.763427%`
- positive `fwd_16` mean: `-0.121386%`
- negative `fwd_16` median: `+0.436870%`
- positive `fwd_16` median: `-0.521135%`
- gap (`negative - positive`):
  - mean `+0.884813%`
  - median `+0.958005%`

#### `AGED_WEAK_CONTINUATION_GUARD`

- negative rows: `408`
- positive rows: `490`
- negative `fwd_16` mean: `+0.116523%`
- positive `fwd_16` mean: `-0.206125%`
- negative `fwd_16` median: `+0.002827%`
- positive `fwd_16` median: `-0.153108%`
- gap (`negative - positive`):
  - mean `+0.322648%`
  - median `+0.155936%`

Interpretation:

- `AGED_WEAK_CONTINUATION_GUARD` remains a large suppressive bucket and cannot be dismissed.
- But the stronger directional separation inside the true suppressor pair now sits on
  `insufficient_evidence`.
- So if the next policy-improvement question must pick **one suppressor to localize first**,
  `insufficient_evidence` is currently the sharper suspect.

### 3. `switch_blocked_by_min_dwell` is not the leading explanation here

- negative rows: `27`
- positive rows: `51`
- `fwd_16` mean gap runs the opposite way (`-0.471708%`)

That does **not** make min-dwell irrelevant globally.
It only means this blocked baseline-long annual split does not currently point to min-dwell as the
first policy-improvement seam.

## Descriptive verdict

This slice supports a narrower and more useful reading than the starting hypothesis:

1. the blocked baseline-long annual split is **not** purely a no-trade suppressor story
2. the largest blocked bucket is continuation-style displacement under `stable_continuation_state`
3. among the two large true suppressors, `insufficient_evidence` currently shows the stronger
   negative-vs-positive quality gap
4. therefore the next honest improvement path is **not** “weaken `AGED_WEAK_CONTINUATION_GUARD`
   first and hope”, but rather:
   - keep displacement separate from suppression, and
   - localize one exact `insufficient_evidence` carrier window first

## Consequence for policy improvement

If the goal is to improve policy behavior rather than just extend analysis, the next smallest honest
follow-up should still remain read-only and local:

1. choose **one exact negative-year `insufficient_evidence` carrier window** inside the blocked
   low-zone bars-`8+` cohort
2. compare it against a nearby `stable_continuation_state` displacement window so the two mechanisms
   do not get mixed again
3. only then decide whether a future default-off runtime candidate should target the
   `insufficient_evidence` seam

## What this slice does not justify

- weakening `AGED_WEAK_CONTINUATION_GUARD` directly from annual aggregates alone
- reopening low-zone runtime tuning from counts alone
- treating `stable_continuation_state` as if it were a simple veto or suppressor
- promoting one helper family as the whole explanation for annual sign split
- runtime/default/family/readiness/promotion claims

## Validation notes

This slice used a read-only helper only.
The helper:

- imports no runtime modules from `src/**`
- reads only existing JSON/parquet evidence inputs
- emits one deterministic JSON summary artifact

## Bottom line

The next policy-improvement seam is now clearer.
The blocked baseline-long divider is a mixed surface, not a single veto bucket.
The largest mass is still `stable_continuation_state` displacement, but among the true suppressors,
`insufficient_evidence` now looks more over-binding than `AGED_WEAK_CONTINUATION_GUARD` on the
current annual proxy surface.
