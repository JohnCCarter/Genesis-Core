# RI policy router weak pre-aged release cooldown displacement diagnosis

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `docs-only / analysis-lane diagnosis / no runtime authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice refines the interpretation of an already executed fail-set result, but does not modify runtime, config, tests, or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the seam-A implementation and fail-set evidence already exist, and the next honest need is to explain the loss mechanism before any new candidate is framed.
- **Objective:** explain why the seam-A guard now hits the intended `2023-12-22 15:00` release seam but still worsens December through broader churn in the `2023-12-21 -> 2023-12-25` pocket.
- **Base SHA:** `HEAD`

## Scope

### Scope IN

- existing seam-A fail-set decision rows
- existing seam-A fail-set evidence doc
- existing seam-A implementation semantics in `src/core/strategy/ri_policy_router.py`
- one new docs-only diagnosis note

### Scope OUT

- runtime edits
- config edits
- further backtest execution
- keep-set or stress-set verification
- seam-B runtime intervention

## Evidence inputs

- `docs/governance/ri_policy_router_weak_pre_aged_release_failset_evidence_2026-04-24.md`
- `docs/governance/ri_policy_router_weak_pre_aged_release_implementation_packet_2026-04-24.md`
- `results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_b_2023_dec_baseline_decision_rows.ndjson`
- `results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_b_2023_dec_candidate_decision_rows.ndjson`
- `src/core/strategy/ri_policy_router.py`

## Diagnosis

### 1. The seam-A guard is not pointwise; it is state-carrying

The implemented guard does not merely veto one isolated row.

It retains the prior `RI_no_trade_policy` when all of the following hold:

- previous policy is `RI_no_trade_policy`
- the new raw decision is weak continuation
- `raw_switch_reason = "continuation_state_supported"`
- `mandate_level = 2`
- `bars_since_regime_change < stable_bars_strong`

Because the selected policy remains `RI_no_trade_policy`, the next row can arrive with the same previous-policy condition still true.

Bounded implication:

- one intended seam-A veto can turn into a **repeated weak-release suppression pocket** rather than a one-row correction.

### 2. The observed pocket becomes a chained no-trade streak before release

In the core pocket:

- `2023-12-21T18:00:00+00:00`
  - baseline: `LONG`
  - candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`
- `2023-12-22T09:00:00+00:00`
  - baseline: `LONG`
  - candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`
- `2023-12-22T15:00:00+00:00`
  - baseline: `NONE / COOLDOWN_ACTIVE`
  - candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`
- `2023-12-22T18:00:00+00:00`
  - baseline: `LONG`
  - candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`

This means the candidate is not only blocking the intended `2023-12-22 15:00` seam.
It is maintaining a broader no-trade pocket through adjacent weak-release opportunities.

### 3. Release then occurs into a two-bar displacement loop

Once the candidate finally releases:

- `2023-12-23T00:00:00+00:00`
  - baseline: `NONE / COOLDOWN_ACTIVE`
  - candidate: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`

From there the candidate repeatedly enters **two bars after** blocked baseline longs while the baseline is still on cooldown.

Observed substitution episodes on the full fail window:

- `12` replacement episodes
- every replacement occurred exactly `2` bars after the blocked baseline long

Representative sequence:

- `2023-12-22T18:00:00+00:00`
  - baseline: `LONG`
  - candidate: `RESEARCH_POLICY_ROUTER_NO_TRADE`
- `2023-12-23T00:00:00+00:00`
  - baseline: `NONE / COOLDOWN_ACTIVE`
  - candidate: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`

This same `blocked long -> two bars later replacement long` pattern repeats across:

- `2023-12-23 03 -> 2023-12-23 09`
- `2023-12-23 12 -> 2023-12-23 18`
- `2023-12-23 21 -> 2023-12-24 03`
- `2023-12-24 06 -> 2023-12-24 12`
- `2023-12-24 15 -> 2023-12-24 21`
- and later continuation-local pockets after that

### 4. The worsening mechanism is therefore a phase shift, not just a missed row

The new negative result is not best described as:

- “the seam-A row was missed” — it was hit
- or “seam B was accidentally solved” — it was not

The more precise mechanism is:

1. the guard creates a chained no-trade pocket because previous policy stays `RI_no_trade_policy`
2. the first later release then lands while baseline is cooling down
3. unchanged `cooldown_bars = 2` turns that shifted release into a recurring cadence displacement
4. the result is broader action churn and worse fail-set outcomes

### 5. Seam B remains separate

At `2023-12-24T21:00:00+00:00`:

- baseline: `NONE / COOLDOWN_ACTIVE`
- candidate: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`

This continues to show that the already-strong continuation question remains distinct from the seam-A release problem.

## Bounded conclusion

The seam-A candidate is fail-set-negative **not** because it fails to hit the intended target seam.
It is fail-set-negative because the implemented release guard interacts with state carry and unchanged cooldown timing to create a broader continuation-entry phase shift.

Short version:

- the seam-A row is hit
- the local no-trade pocket persists longer than intended
- later continuation entries then substitute into baseline cooldown bars
- December worsens through displacement, not through a single-row miss

## Next admissible implication

A future seam-A candidate must not merely say “block the weak pre-aged release.”
It must explicitly prove how it avoids turning one release veto into a **repeated no-trade chain plus two-bar displacement loop**.

That next step should remain continuation-local and should not, by default, reopen:

- strong continuation semantics
- generic cooldown semantics
- seam B
- sizing or defensive routing

## Output of this slice

- one repo-visible diagnosis that explains the seam-A fail-set loss mechanism more precisely than the earlier summary evidence file
- one sharper basis for the next bounded candidate/analysis packet
