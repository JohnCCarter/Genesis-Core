# RI policy router enabled-vs-absent curated annual evidence

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / read-only annual evidence / broad historical surface / mixed verdict`

This slice extends the earlier frozen annual enabled-vs-absent evidence by replaying the same fixed RI carrier on the broader `curated_only` historical surface.
It does not modify runtime/config/schema/authority surfaces and does not constitute promotion, readiness, or challenger-to-incumbent replacement evidence.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice runs deterministic annual backtests on a high-sensitivity router carrier, but remains read-only and does not alter runtime or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the frozen annual note already showed a mixed signal, and the next honest question was whether the same fixed carrier remains useful on the broader validated curated history.
- **Objective:** compare the same fixed RI carrier with `research_policy_router` enabled versus absent across all years available on the curated `tBTCUSD 3h/1D` surface, and determine whether the active state-router leaf has broader historical value beyond the short frozen horizon.
- **Candidate:** `research_policy_router curated annual enabled-vs-absent evidence`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Evidence inputs

- `docs/analysis/ri_policy_router_enabled_vs_absent_annual_evidence_2026-04-28.md`
- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- `tmp/policy_router_evidence/verify_router_enabled_vs_absent_all_years_20260428.py`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/verify_router_enabled_vs_absent_all_years_20260428.py --data-source-policy curated_only`

## Curated coverage

- LTF source: `data/curated/v1/candles/tBTCUSD_3h.parquet`
- HTF source: `data/curated/v1/candles/tBTCUSD_1D.parquet`
- Common start: `2016-06-07T00:00:00+00:00`
- Common end: `2026-04-15T00:00:00+00:00`

Windows emitted by the probe:

- `2016` partial (`2016-06-07 .. 2016-12-31`)
- `2017` .. `2025` full years
- `2026` partial (`2026-01-01 .. 2026-04-15`)

## Outcome summary

### Positive years for enabled

- `2016` partial
- `2018`
- `2020`
- `2022`
- `2025`

### Negative years for enabled

- `2019`
- `2021`
- `2024`

### Mixed years

- `2017`
- `2023`
- `2026` partial

## Why the result still matters

The curated annual picture is broader than the frozen annual picture and confirms two important facts:

1. the active router leaf is **material**, not cosmetic
   - action diffs remain large across all years (`167` to `892` depending on year/window)
2. the active router leaf is still **not broadly robust-positive**
   - the broader historical surface stays mixed rather than cleanly beneficial

## Interpretation

The curated evidence upgrades the earlier frozen-only conclusion in one specific way:

- it strengthens the claim that the policy router **contributes real behavior change** across multiple historical environments

But it does **not** upgrade the router into a generally validated annual subbaseline because the sign of benefit still flips across full years.

Full-year curated reading:

- clearly positive: `2018`, `2020`, `2022`, `2025`
- clearly negative: `2019`, `2021`, `2024`
- mixed: `2017`, `2023`

## Consequence

The correct current posture remains:

- keep the bounded contribution proof
- keep the broader annual verdict as mixed
- do **not** treat the leaf as broadly annualized or promotion-ready
- treat the next honest question as a pocket-isolation question rather than a new tuning question

## Next admissible move

If this line is reopened beyond aggregate annual evidence, the next admissible step should remain docs-first and read-only:

1. isolate whether the already-documented `2024` regression is concentrated in one recurring state pocket on the annual surface, and
2. add the newly surfaced `2021` curated regression to that same pocket-isolation framing instead of treating the aggregate year score alone as the mechanism.

What is **not** justified by this slice alone:

- new router tuning
- challenger-vs-incumbent promotion comparison
- any claim that the static state-router leaf is broadly beneficial across the full curated history
