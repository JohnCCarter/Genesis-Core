# RI policy router shared-pocket outcome quality proxy comparison

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / docs-only read-only proxy comparison / blocked-cohort signal first`

This slice is a read-only follow-up to the shared-shape comparison.
It does not reopen runtime work.
It uses one bounded helper to join annual action-diff timestamps against curated `3h` candles and report descriptive observational proxies only.

This slice uses timestamp-close observational proxies only. Reported differences are descriptive, not authoritative, and do not equal realized trade PnL, fill-aware MFE/MAE, one-to-one pocket pairing, or row-level runtime truth.

The output is used only to inform whether a later higher-fidelity replay slice is worth proposing.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `LOW` — why: this slice reads existing JSON/parquet inputs only and writes one new research artifact plus one governance note.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the pocket-shape presence question is already answered, so the next honest question is descriptive outcome quality inside that shared shape.
- **Objective:** compare blocked baseline `LONG` rows and later substituted continuation `LONG` rows inside the shared low-zone, bars-`8+` pocket across clearly negative and clearly positive curated years.
- **Candidate:** `shared pocket outcome-quality proxy comparison`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `tmp/policy_router_evidence/analyze_shared_pocket_outcome_quality_20260428.py`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/*_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/research/ri_policy_router_shared_pocket_outcome_quality_20260428/shared_pocket_outcome_quality_summary.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/analyze_shared_pocket_outcome_quality_20260428.py --base-sha 989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

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

## Cohort definitions used

### Blocked baseline longs

Rows where:

- baseline / absent action is `LONG`
- enabled action is `NONE`
- `zone = low`
- `bars_since_regime_change >= 8`
- `candidate = LONG`
- `switch_reason in {AGED_WEAK_CONTINUATION_GUARD, insufficient_evidence}`

### Substituted continuation longs

Rows where:

- baseline / absent action is `NONE`
- enabled action is `LONG`
- `zone = low`
- `bars_since_regime_change >= 8`
- `candidate = LONG`
- `selected_policy = RI_continuation_policy`
- `switch_reason in {stable_continuation_state, continuation_state_supported}`

## Proxy metrics used

The helper reports descriptive timestamp-close observational proxies only:

- forward close return at `+4`, `+8`, and `+16` bars
- `mfe_16_pct` from future highs over the next `16` bars
- `mae_16_pct` from future lows over the next `16` bars

These are descriptive market-path proxies, not realized fill-aware trade outcomes.

## Main result

The first proxy signal is clearer on the **blocked baseline-long cohort** than on the substituted continuation cohort.

### 1. Blocked baseline longs separate by year-group direction

For blocked baseline longs:

- **negative years** (`2019`, `2021`, `2024`)
  - row count: `648`
  - `fwd_16` median: `+0.076866%`
  - `fwd_16` mean: `+0.356117%`
  - `fwd_16 > 0` share: `51.08%`
- **positive years** (`2018`, `2020`, `2022`, `2025`)
  - row count: `811`
  - `fwd_16` median: `-0.261849%`
  - `fwd_16` mean: `-0.172585%`
  - `fwd_16 > 0` share: `45.99%`

That is a meaningful directional split.

Descriptive reading only:

- in the clearly positive years, the blocked baseline longs look weaker on this first proxy surface
- in the clearly negative years, the blocked baseline longs look closer to flat / mildly positive on this same proxy surface

So the first proxy pass is consistent with a simple explanation:

> the router helps in the positive group partly because it suppresses more ex-post weak baseline longs there, while in the negative group it suppresses a set of baseline longs that looks less weak and sometimes mildly positive.

### 2. Substituted continuation longs do not yet separate cleanly

For substituted continuation longs:

- **negative years**
  - row count: `415`
  - `fwd_16` median: `+0.182040%`
  - `fwd_16` mean: `+0.458476%`
  - `fwd_16 > 0` share: `53.49%`
- **positive years**
  - row count: `698`
  - `fwd_16` median: `+0.212351%`
  - `fwd_16` mean: `-0.307565%`
  - `fwd_16 > 0` share: `52.44%`

This is not a clean one-direction separation.

The medians remain positive in both year groups, and the positive-share values are close.
The means diverge, which suggests tail-distribution differences or year-mix skew rather than a simple clean group rule.

So this first proxy pass does **not** justify the stronger claim:

> “the continuation substitutions are uniquely good in positive years and uniquely bad in negative years”

That would be overreach from the current descriptive surface.

## Interpretation

The shared pocket shape still exists in both positive and negative groups.
What changes more clearly on the first proxy pass is the **quality of the blocked baseline-long set**.

What this slice now supports:

- the blocked baseline-long cohort looks directionally worse in the positive year group than in the negative year group on the first `fwd_16` proxy
- the substituted continuation cohort does not yet show an equally clean group separation on the same first proxy surface

So the current best bounded read is:

> the annual sign split may be driven more by which baseline longs get suppressed than by a simple “substituted continuations are obviously better in positive years” story.

## What this slice does not prove

This slice does **not** prove:

- exact realized trade-level contribution
- exact one-to-one blocked-versus-substituted pocket pairing
- fill-aware trade outcome superiority
- runtime-authoritative row truth
- that the continuation-substitution side is irrelevant

It only says the first descriptive proxy signal is stronger on the blocked cohort than on the substituted cohort.

## Next admissible step

If this lane is reopened again, the next honest step should stay read-only and move one level more local:

1. inspect year-level or pocket-level tail dispersion inside the substituted continuation cohort, especially the positive-group mean/median split,
2. compare blocked versus substituted rows inside smaller local pocket windows rather than only year-group aggregates, and
3. keep all claims descriptive unless a higher-fidelity replay surface is explicitly proposed later.

## What is not justified from this slice

- new router tuning
- runtime reopen on low-zone or aged-weak surfaces
- claiming that continuation substitutions are already explained cleanly by this proxy alone
- claiming exact contribution proof from timestamp-close candle joins
