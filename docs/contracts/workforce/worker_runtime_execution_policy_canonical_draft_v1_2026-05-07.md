# Worker runtime execution policy canonical draft v1

Status: `proposed / non-authoritative / manual-draft`
Scope: `docs-only`
Runtime authority: `none`
Dispatch authority: `none`
Promotion authority: `none`
Skill Usage: no repository skill explicitly identified for this docs-contract drafting slice; no skill coverage claim is made.

This document is a proposed, non-authoritative draft for manual planning only. It does not enable dispatch, does not change runtime behavior, and remains subordinate to current workforce governance/envelope docs, dependency-closure drafts, and existing runtime implementation such as `scripts/run/run_backtest.py`.

## Purpose

This companion policy explains how a future year-worker runtime chain could be compiled without mutating config truth, widening scope, or bypassing dependency closure.

The intended compiled chain is:

> baseline config ref
> → generated year overlay
> → runtime execution manifest
> → dependency closure validation
> → clean-clone/cloud dispatch
> → `run_backtest.py`
> → artifacts
> → scoped validation
> → output contract
> → integration queue

The policy is descriptive only. It is not launch authority and it does not prove that the current repo surface already supports automated year-worker execution end to end.

## Run-config acquisition model

A year-worker should receive run-config in two layers:

1. **Immutable baseline config ref**
   - pinned by path, selector, and SHA256
   - examples: `config/strategy/champions/...:merged_config`, `config/runtime.seed.json`, or a separately reviewed runtime payload
2. **Generated year overlay**
   - deterministic carrier derived from the admitted baseline
   - produced for worker-local execution only
   - never treated as config truth
   - must be hash-pinned before dispatch review

This preserves the critical distinction:

- baseline config ref = admitted source of config identity
- generated overlay = executable carrier for one bounded worker run

## Immutable baseline + generated overlay

### Baseline rules

- baseline config ref must be immutable for the slice
- baseline config ref must be explicitly hash-pinned
- workers may read the baseline ref but may not rewrite it

### Overlay rules

- the overlay must be generated deterministically from admitted inputs
- the overlay must be disposable and worker-local
- the overlay must never be treated as new champion/config truth
- if the overlay cannot be materialized without changing semantics, the slice must stop

### Current recommended year-worker posture

For the current docs-only design, the safest profile is:

- **complete merged_config carrier**
- **no cfg delta**
- year variation lives in manifest runtime-window fields, not in config mutation

That is the simplest way to prevent silent year-by-year config drift.

## Allowed overlay keys policy

Profile: `year_window_locked_v1`

Allowed top-level keys in the generated overlay carrier:

- `merged_config`
- `runtime_version`
- `baseline_config_ref`
- `overlay_profile`
- `generation_meta`

Allowed nested `cfg` keys:

- none

Policy consequence:

- the overlay may carry a frozen effective config copy
- the overlay may not carry a year-specific strategy delta
- any non-empty `cfg` delta under this profile is treated as tuning and must fail closed

## Forbidden config keys policy

Under `year_window_locked_v1`, workers must not mutate or search within these config families as part of year execution:

- `thresholds/**`
- `gates/**`
- `risk/**`
- `exit/**`
- `multi_timeframe/**`
- `htf_exit_config/**`
- `htf_fib/**`
- `ltf_fib/**`
- `ev/**`
- `features/**`
- `intelligence/**`

Interpretation:

- workers must not tune thresholds
- workers must not change champion semantics between years
- workers must not mutate runtime or champion truth files
- if a year-run needs config-key changes to remain meaningful, that is a different governed slice, not a year-window execution slice

## Lock policy for start/end/warmup/data source/seed

The following fields should be locked in the runtime execution manifest rather than hidden in an overlay:

- `symbol`
- `timeframe`
- `start`
- `end`
- `warmup_bars`
- `data_source_policy`
- `random_seed`
- `fast_window`
- `precompute_features`

This is important because these are execution-shape parameters, not strategy-identity parameters.

The design goal is:

- years may vary by `start` and `end`
- comparable year-workers must not drift in warmup, seed, execution mode, or data-source policy unless explicitly reviewed

## Command template contract

The canonical command surface should be stored as a **structured template**, not as one shell-specific string.

Required command elements should map only to repo-proven runner surfaces:

- entrypoint: `scripts/run/run_backtest.py`
- env keys:
  - `GENESIS_RANDOM_SEED`
  - `GENESIS_FAST_WINDOW`
  - `GENESIS_PRECOMPUTE_FEATURES`
  - `GENESIS_MODE_EXPLICIT`
- required args:
  - `--symbol`
  - `--timeframe`
  - `--start`
  - `--end`
  - `--warmup`
  - `--data-source-policy`
  - `--config-file`
- canonical flags:
  - `--fast-window`
  - `--precompute-features`

Optional args may include:

- `--decision-rows-out`
- `--decision-rows-format`
- `--intelligence-shadow-out`
- `--compare`
- `--no-save`

The manifest should not pretend that interpreter path, shell quoting, or platform-specific rendering is already standardized for cloud. Those remain environment-specific until separately bound.

## Artifact namespace contract

A year-worker should declare a namespace root for explicit worker outputs, for example:

- `results/workforce/year_workers/{dispatch_id}/`

Inside that root, the worker should place explicit, non-timestamped outputs when possible, such as:

- decision rows
- worker-local summary artifacts
- manifest-adjacent execution notes

Current runtime reality must also be acknowledged:

- `TradeLogger.save_all(...)` still emits timestamped outputs under `results/backtests/` and `results/trades/`
- therefore exact JSON/CSV filenames are not fully determined by the command surface alone today

Because of that, the contract must require:

- declared globs for timestamped runner outputs
- a capture step that records the actual generated filenames in the worker output contract
- fail-closed behavior if those filenames cannot be attributed unambiguously to the manifest run

## merged_config_hash and provenance validation

The design should distinguish between three levels:

1. **baseline config hash**
   - already pin-able now
2. **generated overlay hash**
   - pin-able once the overlay exists
3. **merged_config hash**
   - desirable, but only once a deterministic canonical serialization method is explicitly bound

Current repo-visible evidence already supports provenance expectations from `run_backtest.py`:

- `config_provenance`
- `merged_config`
- `runtime_version`
- `runtime_version_current`

Therefore the honest current rule is:

- provenance fields are required
- merged effective config must be recoverable from results
- exact canonical `merged_config_hash` binding is still a draft requirement, not a currently proven live standard

## Config drift detection across years

Cross-year comparability should be checked against a tuple that stays constant across the year batch:

- baseline config ref hash
- overlay policy profile
- overlay generation mode
- runner entrypoint hash
- execution mode profile
- random seed
- data source policy
- warmup bars

Allowed year variance should normally be limited to:

- `start`
- `end`
- subject year label
- dispatch id
- worker namespace root

If anything else drifts, the slice should fail closed or escalate.

## How tuning is prevented

Tuning is prevented by a layered fence:

1. **overlay profile** — `cfg` delta forbidden
2. **forbidden config key families** — no threshold/risk/exit/gate mutation
3. **dependency closure** — undeclared local state or hidden config sources block admission
4. **runtime manifest locks** — year window and execution mode are explicit and comparable
5. **integration review** — any attempt to widen the lane beyond year-window execution must be reclassified

This means a worker cannot honestly “just tweak the year overlay a little” without leaving the admitted slice.

## Clean-clone runtime admission

A year-worker runtime slice should fail closed unless all of the following are true:

- baseline config ref is repo-visible or explicitly bundled
- generated overlay exists and is hash-pinned
- all runtime inputs are declared
- no undeclared local state is required
- dependency closure has been evaluated and is not blocked
- command template can be rendered entirely from declared inputs
- bounded output surfaces are reviewable and attributable

If any one of those fails, the honest answer is:

- do not dispatch
- keep `dispatch_allowed: false`
- record the blocker explicitly

## Worker preflight/runtime validation checklist

### Preflight

- confirm `base_sha`
- confirm baseline config ref path + selector + hash
- confirm overlay profile
- confirm overlay materialization status + hash
- confirm runtime window locks
- confirm execution mode locks
- confirm runner entrypoint hash
- confirm dependency closure status
- confirm clean-clone sufficiency

### Runtime

- render command from structured template only
- forbid undeclared env/config/data inputs
- execute only the declared entrypoint and declared outputs
- capture explicit outputs and actual timestamped runner filenames

### Post-run

- verify `config_provenance`
- verify `merged_config`
- verify runtime version fields
- verify canonical execution mode stayed locked
- verify actual output paths map back to manifest namespace
- verify output contract includes `observed / inferred / unverified / what_this_does_not_prove`

## Known gaps / what this does not prove

This draft does **not** prove:

- that automation already exists for overlay generation or manifest enforcement
- that current cloud workers can already execute year backtests from this contract alone
- that exact `merged_config_hash` canonicalization has been standardized
- that timestamped result filenames are already deterministic enough to skip a capture/mapping step
- that any current year-worker should receive `dispatch_allowed: true`

## Recommended next step

Use this draft together with the example year-worker manifest to open one bounded runtime-admission closure slice that tests whether a frozen champion baseline plus empty-cfg generated carrier can be expressed honestly without touching runtime/config truth or introducing schema drift.
