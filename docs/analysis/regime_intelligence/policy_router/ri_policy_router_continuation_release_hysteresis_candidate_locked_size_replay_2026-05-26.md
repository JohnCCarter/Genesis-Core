# RI policy router continuation_release_hysteresis candidate locked-size replay — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed local action-position equivalence slice.

Question:

> for the `2021-04` candidate only, does the dormant locked-size gap survive past the shared unlock boundary, or does it expire before the next shared entry?

This slice is observational only.

It does **not** reopen the control comparison, promote `2021-04` to a hidden harm case, change runtime/config surfaces, or reinterpret the earlier candidate-local asymmetry as if it had already become execution divergence.

## Inputs

- action-position equivalence artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_2026-05-26.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_20260526.py`

## What changed and what did not

- **Changed:** one new read-only post-processing helper isolated the `2021-04` rows already labeled `size_diff_absorbed_by_locked_position` and traced that dormant gap forward to the shared unlock row and the next shared open-position row.
- **Did not change:** no runtime/config files changed, no new pairwise month comparison was introduced, and no claim was made that the candidate's latent size disagreement ever became a realized trade or equity divergence.

## Observed

### 1. The candidate has exactly one locked-size episode

The replay recovered one candidate-only locked-position episode:

- locked position entry time: `2021-04-16T09:00:00+00:00`
- side: `LONG`
- locked current size: `0.0065`
- trigger row count: `2`
- trigger timestamps:
  - `2021-04-17T03:00:00+00:00`
  - `2021-04-17T12:00:00+00:00`

So the candidate's dormant size asymmetry is not spread across multiple independent local pockets.

It lives inside one bounded locked-position episode.

### 2. The size gap is large relative to the locked position, but still fully dormant

At both trigger rows:

- baseline proposed size: `0.006`
- `release_zero` proposed size: `0.012`
- requested size gap: `0.006`
- max requested size gap as share of locked size: `0.923077`

Relative to the locked `0.0065` position, this is a large latent disagreement.

But the execution effect at both rows remains:

> hold the existing `LONG`

So the disagreement is materially large as a dormant request, yet still execution-inert.

### 3. The gap survives while the lock survives, then crosses the unlock boundary only as policy drift

From the first trigger at `2021-04-17T03:00:00+00:00` to the shared unlock at `2021-04-17T18:00:00+00:00`:

- hours until unlock: `15`
- rows until unlock: `6`
- router-internal-only rows while still locked: `3`
- execution divergence rows before unlock: `0`

The replay trace is:

1. `03:00` — locked-size trigger
2. `06:00` — router-internal-only, still same locked `LONG`
3. `09:00` — router-internal-only, still same locked `LONG`
4. `12:00` — second locked-size trigger
5. `15:00` — router-internal-only, still same locked `LONG`
6. `18:00` — shared flat unlock boundary, but policy and switch-reason drift still remain

So the latent size gap does **not** disappear immediately after the first trigger.

It survives throughout the locked episode and even reaches the shared flat boundary as a policy-only difference.

### 4. The gap is fully gone by the next shared entry

The first shared open-position row after unlock is:

- timestamp: `2021-04-17T21:00:00+00:00`
- hours after unlock: `3`
- baseline effect: `open_position`
- `release_zero` effect: `open_position`
- baseline size: `0.02`
- `release_zero` size: `0.02`
- requested size gap: `0.0`
- selected policy match: `true`

So the dormant gap does not carry into the next shared `LONG` entry.

It is fully reharmonized before re-entry.

### 5. The replay supports expiry, not persistence

The artifact status is:

> `candidate_locked_size_gap_expires_before_next_shared_entry`

That status is supported by three observed facts:

- no execution divergence before unlock
- policy drift still present at unlock
- full size and policy harmonization at the next shared entry

So the candidate's dormant size asymmetry is real, but bounded and short-lived.

## Inferred

### 1. The candidate's negative-like edge currently dies at the unlock/re-entry boundary

The smallest honest inference is:

> the `2021-04` locked-size gap persists while the same `LONG` remains open, but it expires before the next shared entry instead of propagating into a new execution path.

That is narrower than “dormant local harm.”

It is a bounded pre-execution episode with finite lifetime.

### 2. The lock is not just absorbing the gap — it is containing it until it vanishes

The earlier slice established that the same-position lock absorbs the size disagreement.

This replay sharpens that claim:

> the lock contains the disagreement long enough for it to disappear entirely by the next common entry.

So the best current reading is not latent carry-forward, but latent expiry.

### 3. The next admissible slice should only chase residual dormant state inside this one episode

Because the size gap is gone by the next shared entry, another broader replay of entries or equity will likely just restate the same conclusion.

The only honest next question is now:

> inside this same candidate-only episode, does any router/debug field remain informative after the size gap has already been shown to expire?

## Unverified

The following remain open:

1. whether the candidate's remaining non-economic fields inside this episode are purely descriptive router-debug drift or still form a reusable dormant-state signature
2. whether the `execution_equivalent_other` rows adjacent to the locked-size triggers carry any additional bounded structure beyond what this replay already captured
3. whether another negative-like widening candidate shows a locked-size episode that does **not** expire before the next shared entry

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_20260526.py` -> emitted artifact with status `candidate_locked_size_gap_expires_before_next_shared_entry`
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_candidate_locked_size_replay_20260526.py` -> pass

## Bottom line

This slice tightens the candidate story again.

What is now supported is:

> `2021-04` contains one bounded locked-size episode where baseline and `release_zero` disagree materially on requested size while sharing the same open `LONG`, but that disagreement fully expires before the next shared entry and never becomes execution divergence.

So the next honest continuation is now even smaller:

> a candidate-only dormant-state read of this same episode, not another attempt to stretch the gap into post-unlock behavior.
