# RI policy router insufficient-evidence truth-surface correction

Date: 2026-04-30
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only exact-subject truth-surface correction / observational only`

This slice is a bounded follow-up to the closed exact `2024`-vs-`2020` counterfactual-screen null.
It replaces the closed weak `2024-11` target side with one exact **non-March** negative-year `insufficient_evidence` subset that actually materializes as locally favorable on the same chosen offline `fwd_16` proxy surface, while keeping the positive-year weak `2020` control side frozen.

This slice does **not** reopen March 2021 / March 2025 as the primary subject.
It does **not** authorize runtime tuning, config/default changes, or payoff-state admission into runtime.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Research-evidence`
- **Objective:** rerun the bounded `insufficient_evidence` counterfactual-screen logic with a corrected exact negative-year target that is locally favorable on the same chosen offline `fwd_16` proxy surface.
- **Candidate:** `2024-07-13/14 exact insufficient_evidence target vs frozen 2020 positive-year weak control`
- **Base SHA:** `9e39b6db11637593941b0cbdb3e947dab5b2e47a`
- **Skill Usage:** `decision_gate_debug`, `python_engineering`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

## Evidence inputs

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_truth_surface_correction_precode_packet_2026-04-30.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`
- `scripts/analyze/ri_policy_router_insufficient_evidence_truth_surface_correction_20260430.py`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2024_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2020_enabled_vs_absent_action_diffs.json`
- `data/curated/v1/candles/tBTCUSD_3h.parquet`
- `results/evaluation/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.json`

## Exact command run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_insufficient_evidence_truth_surface_correction_20260430.py --base-sha 9e39b6db11637593941b0cbdb3e947dab5b2e47a`

## Fixed row lock

### Corrected `2024` target side — exact non-March negative-year `insufficient_evidence` subset (`3` rows)

- `2024-07-13T09:00:00+00:00`
- `2024-07-14T09:00:00+00:00`
- `2024-07-14T18:00:00+00:00`

Shared target context:

- year = `2024`
- zone = `low`
- candidate = `LONG`
- absent action = `LONG`
- enabled action = `NONE`
- switch reason = `insufficient_evidence`
- selected policy = `RI_no_trade_policy`
- bars since regime change = `166`

### Nearby `2024` descriptive rows retained for context only

True displacement rows (`2`):

- `2024-07-12T09:00:00+00:00`
- `2024-07-12T18:00:00+00:00`

Stable blocked context rows (`2`):

- `2024-07-12T15:00:00+00:00`
- `2024-07-13T00:00:00+00:00`

Exact local envelope:

- `2024-07-12T09:00:00+00:00` -> `2024-07-15T18:00:00+00:00`
- local envelope row lock: `7` rows exactly
- additional unlabeled local rows: `0`

### Frozen `2020` control side — exact positive-year weak `insufficient_evidence` cluster (`4` rows)

- `2020-10-31T21:00:00+00:00`
- `2020-11-01T06:00:00+00:00`
- `2020-11-01T15:00:00+00:00`
- `2020-11-02T00:00:00+00:00`

Nearby `2020` descriptive rows retained for context only:

- displacement rows:
  - `2020-11-02T03:00:00+00:00`
  - `2020-11-02T21:00:00+00:00`
- stable blocked context rows:
  - `2020-11-02T09:00:00+00:00`
  - `2020-11-03T03:00:00+00:00`

## Main result

### 1. The corrected truth surface is genuinely opposed on the chosen offline `fwd_16` proxy

The emitted artifact reports:

- corrected `2024` target `fwd_16` mean: `+6.726739%`
- frozen `2020` control `fwd_16` mean: `-0.875411%`
- corrected `2024` target positive on mean `fwd_16`: `true`
- frozen `2020` control negative on mean `fwd_16`: `true`
- corrected `2024` target mean exceeds frozen `2020` control mean: `true`
- `truth_surface_is_opposed = true`

So unlike the closed weak `2024-11` branch, this corrected bounded pair does carry the intended harmful-vs-correct polarity on the chosen offline `fwd_16` proxy surface.

### 2. The helper emitted `surviving_single_field_screen`

The final artifact status is:

- `surviving_single_field_screen`

The winning bounded candidate was:

- `bars_since_regime_change <= 166`

Its exact target/control behavior was:

- selects `3 / 3` corrected `2024` target rows
- selects `0 / 4` frozen `2020` control rows
- balanced accuracy on fixed target/control rows: `1.0`

### 3. The surviving field also selects the whole fixed July `2024` envelope

The same winning rule also selects:

- `2 / 2` nearby `2024` displacement rows
- `2 / 2` nearby `2024` stable blocked context rows
- `0 / 2` nearby `2020` displacement rows
- `0 / 2` nearby `2020` stable blocked context rows

So the surviving field does **not** isolate only the corrected `2024` target rows inside the exact July envelope.
It behaves as a coarse **cross-envelope separator** between the entire July `2024` low-zone local state (`bars 164..166`) and the frozen `2020` weak control family (`bars 302..304`).

That is still a real surviving bounded screen on the fixed target/control surface.
But it is **not** the same thing as a clean within-envelope target-versus-displacement discriminator.

## Cohort readout

### Corrected `2024` target side is strongly locally favorable

For the corrected target side (`3` rows):

- `bars_since_regime_change` mean: `166.0`
- `action_edge` mean: `0.027348`
- `confidence_gate` mean: `0.513674`
- `clarity_score` mean: `36.333333`
- `fwd_4` mean: `+2.264106%`
- `fwd_8` mean: `+4.182629%`
- `fwd_16` mean: `+6.726739%`
- `fwd_16 > 0` share: `100%`
- `mfe_16` mean: `+8.109025%`
- `mae_16` mean: `-0.460665%`

This is a materially favorable local blocked cluster on the chosen proxy surface.

### Nearby `2024` displacement/context rows are also positive, but weaker than the target side

Nearby `2024` displacement rows (`2`):

- `bars_since_regime_change` mean: `164.5`
- `fwd_16` mean: `+4.747165%`
- `fwd_16 > 0` share: `100%`

Nearby `2024` stable blocked context rows (`2`):

- `bars_since_regime_change` mean: `164.5`
- `fwd_16` mean: `+5.576332%`
- `fwd_16 > 0` share: `100%`

Descriptive gaps versus the corrected target side:

- corrected target minus nearby displacement `fwd_16` mean gap: `+1.979574%`
- corrected target minus nearby stable blocked context `fwd_16` mean gap: `+1.150407%`

So the corrected target side is the strongest local positive mass inside the exact July envelope, but the whole local envelope is favorable rather than mechanism-pure.

### Frozen `2020` control side remains locally weak while nearby continuation/context rows are healthier

For the frozen `2020` control side (`4` rows):

- `bars_since_regime_change` mean: `302.0`
- `action_edge` mean: `0.027054`
- `confidence_gate` mean: `0.513527`
- `clarity_score` mean: `36.0`
- `fwd_4` mean: `-0.734117%`
- `fwd_8` mean: `-1.670759%`
- `fwd_16` mean: `-0.875411%`
- `fwd_16 > 0` share: `25%`
- `mfe_16` mean: `+1.103043%`
- `mae_16` mean: `-4.077616%`

Nearby `2020` displacement rows (`2`) remain materially healthier:

- `fwd_16` mean: `+2.555433%`

Nearby `2020` stable blocked context rows (`2`) are healthier still:

- `fwd_16` mean: `+4.749690%`

So the frozen `2020` control still behaves like a locally weak blocked cluster beside stronger nearby continuation/context rows.

## Interpretation

The bounded conclusion is now different from the closed weak `2024-11` null.
The previous branch failed because the chosen weak `2024-11` target side never re-materialized as favorable on the chosen offline `fwd_16` proxy surface.
This corrected July `2024` branch **does** re-materialize as favorable, so the bounded screen survives.

But the surviving field is still narrow in a specific way:

> `bars_since_regime_change <= 166` survives as a bounded target/control separator because the corrected July `2024` envelope sits at `164..166` bars while the frozen `2020` weak control family sits at `302..304` bars. It is a real exact-subject cross-envelope separator, but not a clean within-envelope discriminator that picks only the corrected target rows over nearby July displacement/context rows.

So the honest reading is:

- the truth-surface correction succeeded
- the corrected pair now supports one surviving bounded screen
- the surviving screen is still best understood as a **descriptive regime-age envelope separator** on this exact corrected pair, not as runtime-ready proof of a clean local unlock rule

Bounded read:

> `bars_since_regime_change <= 166` survives only as an exact-subject envelope separator on the corrected July `2024` versus frozen `2020` surface. Because it also selects all nearby July `2024` displacement/context rows and none of the nearby `2020` rows, this slice does **not** establish a within-envelope target-only discriminator and does **not** authorize runtime or policy promotion.

## What this slice supports

- the closed weak `2024-11` null was limited by target-truth selection, not by a universal absence of bounded separators
- the corrected exact July `2024` target plus the frozen `2020` weak control produces a genuinely truth-opposed bounded surface on the chosen offline `fwd_16` proxy
- one single-field screen survives on that fixed surface: `bars_since_regime_change <= 166`
- the winning field separates the corrected July `2024` envelope from the frozen `2020` weak control family cleanly on the exact locked rows

## What this slice does **not** support

- a runtime threshold change
- a router-policy change
- a claim that `bars_since_regime_change <= 166` is now ready for runtime admission
- a claim that the winning field uniquely isolates the corrected target rows from nearby July `2024` displacement/context rows
- reopening March 2021 / March 2025 as the primary closed subject
- promotion, readiness, or family/champion claims

## Consequence

The next honest interpretation step, if this line is reopened, is still cheaper than runtime:

1. keep this corrected result as a **bounded surviving screen on an exact corrected pair**, and
2. if more pressure-testing is desired, falsify whether the same field remains merely a broad envelope separator on one additional bounded pair or one tighter within-envelope test.

This slice remains observational only.
Any surviving field/rule combination is research evidence on the chosen offline `fwd_16` proxy surface only.

## Validation notes

- the helper enforced the exact July `2024` row lock and confirmed `7` local envelope rows with no unlabeled extras
- the helper enforced the frozen exact `2020` control and nearby comparison/context row locks
- the emitted artifact status is `surviving_single_field_screen`
- targeted `black --check` passes on `scripts/analyze/ri_policy_router_insufficient_evidence_truth_surface_correction_20260430.py`
- repo-wide `black --check .` remains externally red outside this slice's scope because the repository baseline is not globally Black-clean
- all claims in this note remain exact-subject, bounded, observational, and non-authoritative
