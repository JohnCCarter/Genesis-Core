# RI policy router weak pre-aged single-veto release fail-set evidence

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / fail-set evidence only / negative result`

This packet is a bounded `RESEARCH` evidence run against the already-implemented seam-A single-veto candidate.
It does not modify runtime/config/schema/authority surfaces and does not constitute promotion, readiness, champion, or runtime-authority evidence.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice runs bounded research-evidence backtests and row comparisons against the already-implemented enabled-only seam-A single-veto variant, but does not modify runtime/config authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the bounded seam-A implementation is already complete and validated, and the next unknown is whether the single-veto de-chaining change improves the December fail windows without reopening seam-B or cooldown semantics.
- **Objective:** run the same bounded December fail-set windows used for the prior seam-A evidence and determine whether the single-veto variant removes or honestly bounds the repeated no-trade chaining / two-bar displacement mechanism.
- **Candidate:** `weak pre-aged single-veto release guard`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Skill Usage

- **Applied repo-local spec:** `backtest_run`
  - reason: this slice must use canonical deterministic backtest env and exact paired command shapes.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: row-level interpretation must stay anchored to switch/gate behavior rather than top-line metrics alone.
- **Conditional repo-local spec:** `genesis_backtest_verify`
  - reason: only if this slice later needs ledger-style artifact comparison beyond decision-row evidence; not expected for the first pass.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/governance/ri_policy_router_weak_pre_aged_release_failset_evidence_2026-04-24.md`
  - `docs/governance/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md`
  - `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_implementation_packet_2026-04-27.md`
  - `results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_a_2023_dec_micro_candidate_decision_rows.ndjson`
  - `results/backtests/ri_policy_router_weak_pre_aged_release_guard_20260424/fail_b_2023_dec_candidate_decision_rows.ndjson`
- **Candidate / comparison surface:**
  - current working-tree implementation in `src/core/strategy/ri_policy_router.py`
  - same bounded evidence carrier config at `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
  - same bounded baseline config at `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- **Vad ska förbättras:**
  - reduce or eliminate repeated same-guard no-trade chaining in the seam-A pocket
  - reduce or honestly bound the two-bar replacement-entry displacement pattern on the December fail windows
- **Vad får inte brytas / drifta:**
  - no claim that seam-B / `2023-12-24 21:00` is solved unless evidence shows it explicitly
  - no reopening of cooldown semantics, sizing, defensive routing, or strong continuation semantics
  - no keep-set or stress-set promotion from this slice alone
- **Reproducerbar evidens som måste finnas:**
  - exact paired backtest commands on the previous December fail windows
  - captured decision rows for baseline and current single-veto candidate
  - row-level comparison against the prior fail-set diagnosis around `2023-12-21 -> 2023-12-25`

## Scope

### Scope IN

- paired fail-set backtests on the same `tBTCUSD` / `3h` December windows
- decision-row capture for baseline vs current single-veto candidate
- one new governance evidence note
- four exact `.ndjson` evidence artifacts under `results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/`

### Scope OUT

- further runtime edits
- config edits
- keep-set verification (`2024`, `2025`)
- stress-set verification (`2018`, `2020 H1`)
- seam-B runtime intervention
- family/default/champion/promotion/readiness claims
- findings-bank bundle / ledger / index writes for this first pass because the candidate evidence carrier remains under `tmp/`

## Canonical env for all runs

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`

## Fixed read-only evidence inputs

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`

These inputs are fixed evidence carriers for this slice and are out of edit scope.

## Exact commands to run

### Fail B: December full local-failure window

Baseline:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-31 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_b_2023_dec_baseline_decision_rows.ndjson --decision-rows-format ndjson`

Candidate:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-31 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_b_2023_dec_candidate_decision_rows.ndjson --decision-rows-format ndjson`

### Fail A: December micro-window anchor

Baseline:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-24 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_a_2023_dec_micro_baseline_decision_rows.ndjson --decision-rows-format ndjson`

Candidate:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2023-12-01 --end 2023-12-24 --warmup 120 --data-source-policy curated_only --fast-window --precompute-features --no-save --config-file tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json --decision-rows-out results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_a_2023_dec_micro_candidate_decision_rows.ndjson --decision-rows-format ndjson`

## Actual emitted artifacts

- `results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_b_2023_dec_baseline_decision_rows.ndjson`
- `results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_b_2023_dec_candidate_decision_rows.ndjson`
- `results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_a_2023_dec_micro_baseline_decision_rows.ndjson`
- `results/backtests/ri_policy_router_weak_pre_aged_single_veto_release_20260427/fail_a_2023_dec_micro_candidate_decision_rows.ndjson`

No findings-bank artifacts were written in this first pass because the candidate evidence carrier remains under `tmp/`.

## Outcomes

### Fail B summary (`2023-12-01 -> 2023-12-31`)

- baseline return: `-0.10%`
- candidate return: `-0.24%`
- baseline trades: `15`
- candidate trades: `13`
- baseline Sharpe: `0.069`
- candidate Sharpe: `-0.126`
- baseline max drawdown: `0.25%`
- candidate max drawdown: `0.34%`
- baseline profit factor: `1.38`
- candidate profit factor: `0.71`
- baseline score: `0.1057`
- candidate score: `-100.1563`
- verdict: **worse**

### Fail A summary (`2023-12-01 -> 2023-12-24`)

- baseline return: `-0.03%`
- candidate return: `-0.11%`
- baseline trades: `8`
- candidate trades: `7`
- baseline Sharpe: `0.117`
- candidate Sharpe: `-0.056`
- baseline max drawdown: `0.25%`
- candidate max drawdown: `0.25%`
- baseline profit factor: `1.49`
- candidate profit factor: `0.88`
- baseline score: `-99.8385`
- candidate score: `-100.0645`
- verdict: **worse**

## Decision-row findings

### The intended seam-A target remains hit

At the intended seam-A target `2023-12-22T15:00:00+00:00`:

- baseline: `NONE` with `COOLDOWN_ACTIVE`
- previous seam-A candidate: `NONE` with `RESEARCH_POLICY_ROUTER_NO_TRADE`
- current single-veto candidate: `NONE` with `RESEARCH_POLICY_ROUTER_NO_TRADE`

So the single-veto variant continues to hit the intended weak pre-aged release seam.

### The repeated same-pocket displacement loop is removed

The prior fail-set diagnosis identified repeated no-trade chaining plus replacement entries exactly `2` bars later.

That mechanism is no longer present on this run:

- full fail window substitution episodes: prior `12` -> current `0`
- micro fail window substitution episodes: prior `3` -> current `0`

Key row reversions that show the prior displacement loop has been removed:

- `2023-12-22T18:00:00+00:00`
  - baseline: `LONG`
  - previous candidate: `NONE / RESEARCH_POLICY_ROUTER_NO_TRADE`
  - current candidate: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`
- `2023-12-23T00:00:00+00:00`
  - baseline: `NONE / COOLDOWN_ACTIVE`
  - previous candidate: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`
  - current candidate: `NONE / COOLDOWN_ACTIVE`
- `2023-12-24T21:00:00+00:00`
  - baseline: `NONE / COOLDOWN_ACTIVE`
  - previous candidate: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`
  - current candidate: `NONE / COOLDOWN_ACTIVE`

This means the single-veto latch does remove the earlier repeated same-pocket re-blocking and the associated two-bar continuation-entry displacement cadence.

### Action drift collapses materially, but not to zero

Relative to baseline, current action drift is much smaller than the prior seam-A candidate:

#### Full fail window (`Fail B`)

- baseline vs prior candidate action diffs: `34`
- baseline vs current candidate action diffs: `5`
- prior vs current candidate action diffs: `29`

Remaining full-window action diffs are now limited to direct blocked baseline longs at:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

#### Micro fail window (`Fail A`)

- baseline vs prior candidate action diffs: `10`
- baseline vs current candidate action diffs: `3`
- prior vs current candidate action diffs: `7`

Remaining micro-window action diffs are limited to:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`

### The candidate is still worse even after de-chaining

Removing the repeated no-trade chain and two-bar replacement cadence does **not** turn the candidate positive on either December fail window.

Compared with the prior seam-A candidate documented on `2026-04-24`, the mechanism is better behaved but the top-line outcomes are still negative and slightly worse:

- full fail window return: prior `-0.21%` -> current `-0.24%`
- micro fail window return: prior `-0.07%` -> current `-0.11%`

So the remaining problem is no longer the old displacement loop.
It is the residual suppression of a smaller set of baseline longs without compensating improvement elsewhere.

## Bounded interpretation

The single-veto seam-A variant succeeds at exactly the mechanism it was designed to test:

1. it preserves the intended seam-A veto point,
2. it prevents the same guard from recursively re-blocking the next same-pocket weak bar,
3. it removes the previously diagnosed two-bar replacement-entry displacement loop.

However, the candidate remains fail-set-negative because it still blocks a smaller set of baseline longs directly, including an earlier low-zone row on `2023-12-20T03:00:00+00:00` and two later low-zone rows on `2023-12-28T09:00:00+00:00` and `2023-12-30T21:00:00+00:00`.

That means the mechanism-level story has changed:

- **old seam-A candidate:** negative primarily through repeated no-trade chaining plus two-bar displacement
- **single-veto seam-A candidate:** negative through a much smaller residual set of direct blocked baseline entries

## Conclusion

The implemented `weak pre-aged single-veto release guard` is still a **negative fail-set result**.

More precise statement:

- it preserves the intended seam-A target behavior,
- it materially reduces action churn,
- it removes the previously diagnosed displacement loop,
- but it still worsens both fail-set windows.

Therefore the candidate should **not** advance to keep-set or stress-set verification in its current form.

## Next admissible step

The next honest move is no longer to debug repeated same-pocket chaining; that mechanism is now bounded by evidence.

The next bounded step should instead explain why the smaller residual set of blocked baseline longs still leaves the candidate fail-set-negative, with special focus on:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

That follow-up should remain a bounded research-evidence / diagnosis slice unless it proves that a new runtime seam must be reopened.

## Stop Conditions

- any need to change runtime/config surfaces to make the evidence run expressible
- any claim that seam-B or cooldown semantics are solved without explicit row evidence
- any unexpected default-path drift on the baseline surface

## Output required

- one repo-visible evidence note for the single-veto fail-set result
- one precise statement of whether the chained no-trade / two-bar displacement mechanism is removed, reduced, or merely shifted
- no findings-bank update in this first pass; findings-bank promotion is deferred until the candidate carrier is frozen outside `tmp/` or a later slice explicitly authorizes that write surface
