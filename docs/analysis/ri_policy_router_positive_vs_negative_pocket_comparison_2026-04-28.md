# RI policy router positive-vs-negative pocket comparison

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / docs-only read-only comparison / shared-shape result`

This slice is a read-only follow-up to the first negative-year pocket isolation.
It compares the clearly negative curated years against the clearly positive curated years using the same action-diff pocket summary workflow.
It does not modify runtime/config/schema/authority surfaces and does not authorize tuning, promotion, or any new router packet.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice only compares already-generated annual diff artifacts through a repo-local read-only summary helper.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the negative-year pocket note already exists, so the next honest question is whether that pocket shape is unique to negative years or also present in clearly positive years.
- **Objective:** compare the recurring pocket shape in clearly negative curated years (`2019`, `2021`, `2024`) against clearly positive curated years (`2018`, `2020`, `2022`, `2025`).
- **Candidate:** `shared pocket-shape comparison`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Evidence inputs

- `docs/analysis/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
- `tmp/policy_router_evidence/analyze_negative_year_pockets_20260428.py`
- `results/research/ri_policy_router_negative_year_pockets_20260428/negative_year_pocket_summary.json`
- `results/research/ri_policy_router_positive_year_pockets_20260428/positive_year_pocket_summary.json`

## Exact commands run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/analyze_negative_year_pockets_20260428.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/analyze_negative_year_pockets_20260428.py --years 2018 2020 2022 2025 --output-root-relative results/research/ri_policy_router_positive_year_pockets_20260428 --summary-filename positive_year_pocket_summary.json`

## Compared year sets

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

The first comparison does **not** support the claim that the negative-year pocket shape is unique to negative years.

The clearly positive years show the same broad action-diff structure:

- many baseline `LONG -> NONE` suppressions, and
- many later `NONE -> LONG` continuation substitutions

They also share the same dominant context:

- mostly `zone = low`
- overwhelmingly `bars_since_regime_change >= 8`
- recurring suppressive reasons: `AGED_WEAK_CONTINUATION_GUARD` and `insufficient_evidence`
- recurring release reason: `stable_continuation_state`

## Evidence summary

### Negative years

Across `2019`, `2021`, and `2024`:

- top flow is always `LONG -> NONE`
- second flow is always `NONE -> LONG`
- low-zone counts dominate each year
- `8+` bars-since-regime-change dominates each year
- selected-policy mass splits mainly between `RI_no_trade_policy` and `RI_continuation_policy`

### Positive years

Across `2018`, `2020`, `2022`, and `2025`:

- top flow is also always `LONG -> NONE`
- second flow is also always `NONE -> LONG`
- low-zone counts still dominate each year
- `8+` bars-since-regime-change still dominates each year
- selected-policy mass again splits mainly between `RI_no_trade_policy` and `RI_continuation_policy`

Representative examples:

- `2018`: `LONG -> NONE = 586`, `NONE -> LONG = 301`, low-zone `664`, bars `8+ = 878`
- `2020`: `LONG -> NONE = 531`, `NONE -> LONG = 245`, low-zone `547`, bars `8+ = 781`
- `2022`: `LONG -> NONE = 564`, `NONE -> LONG = 307`, low-zone `599`, bars `8+ = 872`
- `2025`: `LONG -> NONE = 501`, `NONE -> LONG = 236`, low-zone `485`, bars `8+ = 719`

These shapes are qualitatively very close to the negative-year summaries.

## Interpretation

The earlier negative-year isolation remains useful, but its first mechanism guess must now be tightened.

What the evidence now supports:

- the router has a recurring late low-zone suppression + later continuation displacement shape
- that shape is present in both clearly negative and clearly positive years

What the evidence does **not** support:

- that the mere existence of this shape explains why a year is negative
- that a direct retune of the suppression/displacement shape is justified from annual pocket counts alone

So the problem is probably **not**:

> “negative years have a unique pocket that positive years do not have”

The more honest next hypothesis is:

> the router may be applying a broadly similar pocket shape across years, but the **outcome quality** of the blocked entries and the later substituted continuation entries differs by environment.

## Consequence

The next admissible slice should stay read-only and comparative, but move one level deeper:

1. compare whether the blocked baseline longs inside the shared pocket are beneficial or harmful in positive vs negative years, and
2. compare whether the later substituted continuation entries repair or worsen those blocked opportunities across the same year groups.

That is a different question from simply counting the presence of the pocket.

## What is not justified from this slice

- new router tuning
- reopening aged-weak runtime work
- reopening low-zone runtime work
- claiming that `AGED_WEAK_CONTINUATION_GUARD` or `insufficient_evidence` is itself the sole annual failure mechanism
