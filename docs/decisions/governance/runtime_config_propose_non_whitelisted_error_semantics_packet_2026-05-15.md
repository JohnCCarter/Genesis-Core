# Runtime config propose non-whitelisted error semantics packet

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `packet-defined / docs-only / non-authorizing`

This document is a planning/decision artifact in `RESEARCH` and grants no implementation, runtime, config-authority, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin source, test, config, or API behavior changes.

> Current implementation-status note:
>
> - The candidate framed by this packet has since been landed in a separate bounded slice limited to `src/core/api/config.py`, `tests/integration/test_config_endpoints.py`, and `tests/integration/test_config_api_e2e.py`.
> - Verification on that later slice was green on touched-file `black --check` / `ruff check`, focused config endpoint/e2e tests, and the same runtime-adjacent determinism/parity/pipeline/feature-cache checks used for earlier sensitive slices.
> - Executed selectors / outcomes for that later slice:
>   - `black --check src/core/api/config.py tests/integration/test_config_endpoints.py tests/integration/test_config_api_e2e.py` → `pass`
>   - `ruff check src/core/api/config.py tests/integration/test_config_endpoints.py tests/integration/test_config_api_e2e.py` → `pass`
>   - `pytest tests/integration/test_config_endpoints.py tests/integration/test_config_api_e2e.py -v --tb=short` → `10 passed`
>   - `pytest tests/backtest/test_backtest_determinism_smoke.py tests/governance/test_regime_intelligence_cutover_parity.py tests/governance/test_pipeline_fast_hash_guard.py tests/integration/test_precompute_vs_runtime.py tests/utils/test_feature_parity.py tests/utils/test_features_asof_cache_isolation.py -v --tb=short` → `24 passed`
> - This packet remains the historical pre-code framing artifact and does not retroactively authorize wider config-authority or API work.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Category:** `security`
- **Risk:** `LOW-MED` — why: this slice would touch a runtime/config-authority API edge, but only to make one existing guarded failure mode more explicit; the main risk is accidentally widening live-write authority or leaking internal validation details
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why: even a small user-visible change on `/config/runtime/propose` touches an authority edge and therefore cannot stay concept-only
- **Objective:** define the narrowest config-authority alignment candidate that clarifies the guarded live-write boundary without changing whitelist scope or runtime mutability policy
- **Candidate:** `return an explicit public non_whitelisted_field error for schema-valid but live-blocked propose patches`
- **Base SHA:** `66f97acc`
- **Skill Usage:** no suitable repository skill found for this narrow config-authority error-semantics slice; no skill coverage claim is made in this packet, and any future skill addition is only `föreslagen`

### Scope

- **Scope IN:** one docs-only packet; explicit statement of the current API seam where `validate` may accept a payload that `propose` rejects, yet `/config/runtime/propose` currently returns a generic `bad_request`; exact likely future source/test scope for one bounded implementation slice only; explicit done criteria and stop conditions for that later slice
- **Scope OUT:** all whitelist expansion; all new live-writable fields; all config default changes; all schema changes; all auth changes; all leaked internal exception text or raw field paths; all paper/live, readiness, promotion, or shared-truth claims; all claims that implementation is already approved
- **Expected changed files:** `docs/decisions/governance/runtime_config_propose_non_whitelisted_error_semantics_packet_2026-05-15.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual wording audit that this packet remains docs-only and non-authorizing
- manual wording audit that the candidate stays narrower than whitelist expansion or broader API redesign
- manual wording audit that current runtime authority boundaries remain unchanged in the packet language

### Stop Conditions

- any wording that treats this packet as implementation approval
- any wording that widens the change from public error semantics into whitelist or schema policy changes
- any wording that leaks internal exception-derived detail, nested field paths, or raw validation messages into the public API contract
- any wording that silently absorbs `authority.py` whitelist expansion, auth changes, or UI/runtime behavior changes into the same future slice

## Purpose

This packet answers one narrow question only:

- what is the smallest admissible config-authority alignment slice now that the repo already documents the asymmetry between `validate` and `propose`?

## Governing basis

### Observed

1. `src/core/api/config.py` currently maps all `ValueError` failures from `authority.propose_update(...)` to a generic HTTP `400` with detail `bad_request`
2. `src/core/config/authority.py` already distinguishes internal failure causes such as `non_whitelisted_field`, `non_whitelisted_field:*`, `invalid_value:*`, and `validation_error`
3. `docs/governance/runtime_config_live_update_matrix_2026-05-15.md` and user-facing docs already make the current asymmetry explicit: some surfaces are schema-valid but intentionally live-blocked
4. because `/config/runtime/propose` currently collapses those guarded rejections into `bad_request`, a caller can know from docs that the field is live-blocked but still receive an undifferentiated API error
5. `RuntimeConfig` accepts top-level fields such as `warmup_bars`, but `ConfigAuthority.propose_update(...)` only whitelists top-level keys `{strategy_family, thresholds, gates, risk, ev, multi_timeframe}`; `warmup_bars` is therefore a concrete schema-valid but live-blocked proof seam
6. a targeted search of `src/**` for exact `bad_request` coupling found only the current `src/core/api/config.py` mapping site and no in-repo caller branching on this specific error detail

### Inferred

- the smallest useful alignment is not whitelist expansion, but a bounded public error code for the existing guarded failure mode
- the safest public code is likely a stable coarse detail such as `non_whitelisted_field`, without leaking nested internal suffixes or raw exception text
- this candidate can likely remain contained to `src/core/api/config.py` plus focused integration/API tests
- the match predicate must stay token-safe: only exact `non_whitelisted_field` or `non_whitelisted_field:`-prefixed authority failures are admissible for remapping in this slice

### Unverified in this packet

- whether the final implementation should map only `non_whitelisted_field*` to a public specific detail, or also normalize other guarded `ValueError` families into additional coarse codes
- whether a small docs clarification is needed after implementation, depending on how explicit the public error contract becomes

## Boundary decision

### Current standing conclusion

The next bounded config-authority candidate should be framed as:

- **return an explicit public `non_whitelisted_field` error for guarded propose rejections caused by live-blocked fields**

This is a candidate-selection conclusion only. It is **not** approval to edit the runtime config API yet.

### Likely future implementation scope

If this candidate is reopened as a real pre-code implementation packet, the smallest honest starting scope is likely:

- `src/core/api/config.py`
- `tests/integration/test_config_api_e2e.py`
- `tests/integration/test_config_endpoints.py`

`src/core/config/authority.py` remains **OUT** for the initial slice unless inspection shows a strictly necessary helper or test seam that cannot be handled from the API layer alone. If that becomes necessary, the work must stop, amend the packet/contract, and obtain fresh pre-code review before editing it.

### Likely future implementation scope OUT

A future packet for this candidate should keep the following out of scope unless separately reopened:

- `src/core/config/authority.py` whitelist contents
- `src/core/config/schema.py`
- live-write surface expansion
- auth/bearer behavior
- UI error handling
- paper/live, readiness, promotion, or champion implications

## What that future pre-code packet must define

A future implementation-bearing packet for this candidate must define at minimum:

- the exact `ValueError` family being made public as a coarse stable error detail
- the exact token-safe predicate: `str(exc) == "non_whitelisted_field"` or `str(exc).startswith("non_whitelisted_field:")`
- whether only `non_whitelisted_field*` is remapped in this slice
- the exact public detail string to expose
- what must remain unchanged for all other propose failure paths
- that the `ValueError` catch must not be widened beyond the existing `authority.propose_update(...)` call site
- the smallest focused tests needed to prove no authority widening and no exception-detail leakage
- what code paths remain explicitly out of scope

## Expected verification stack for the implementation slice

If the future implementation slice is opened, the expected minimum verification stack should be:

- touched-file `black --check`
- touched-file `ruff check`
- `pytest tests/integration/test_config_endpoints.py tests/integration/test_config_api_e2e.py -v --tb=short`
- `pytest tests/backtest/test_backtest_determinism_smoke.py tests/governance/test_regime_intelligence_cutover_parity.py tests/governance/test_pipeline_fast_hash_guard.py tests/integration/test_precompute_vs_runtime.py tests/utils/test_feature_parity.py tests/utils/test_features_asof_cache_isolation.py -v --tb=short`

## Future done criteria for the implementation slice

If the future implementation slice is opened, it should be considered done only if all of the following are true:

- schema-valid but live-blocked propose patches no longer collapse to indistinguishable `bad_request` when the failure cause is `non_whitelisted_field*`
- the public error detail remains coarse and does not expose nested internal suffixes or raw exception text
- whitelist scope and runtime mutability policy remain unchanged
- non-whitelist propose failures retain their previous behavior unless explicitly approved in the packet
- focused tests prove `validate` success plus guarded `propose` rejection for `warmup_bars`, with the new coarse error detail and no leaked internals

## Hard stop and reopen rule

If the future slice needs to change any of the following, it must stop and reopen as a separate bounded packet:

- whitelist contents or live-writable field set
- schema support
- public error detail for additional unrelated error families
- bearer/auth behavior
- UI/runtime behavior beyond the coarse API detail
- config-authority semantics beyond this one guarded failure seam

## Bottom line

The next smallest config-authority alignment move is not whitelist expansion. It is a separate bounded pre-code packet for **making guarded non-whitelisted propose failures explicit at the public API edge**, while keeping whitelist scope, schema support, and runtime mutability policy unchanged.
