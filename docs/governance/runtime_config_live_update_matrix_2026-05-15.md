# Runtime config live-update matrix

Date: 2026-05-15
Branch: `feature/editor-worker-orchestrator`
Status: `current-state reference / docs-only / no behavior change / no new authority`

> Current status note:
>
> - This note documents the **current observed boundary** between `RuntimeConfig`, `/config/runtime/validate`, and `/config/runtime/propose`.
> - It does **not** change the whitelist, API behavior, or runtime/config-authority semantics.
> - It should be read as a reference note that reduces confusion around live-updatability, not as approval for expanding the live-write surface.

## Purpose

This note answers one narrow question only:

- which runtime-config surfaces are declared in the runtime schema, which are accepted by validation, and which are currently writable through the live propose path?

## Scope boundary

### In scope

- declared `RuntimeConfig` surfaces in `src/core/config/schema.py`
- observed `ConfigAuthority.validate(...)` behavior
- observed `ConfigAuthority.propose_update(...)` whitelist behavior
- user-facing API semantics in `src/core/api/config.py`
- current repo reading of which fields are live-writable now

### Out of scope

- changing the whitelist
- deciding future live-update policy
- changing API error granularity
- changing runtime defaults or config-authority behavior
- treating this matrix as SSOT or implementation authority

## Observed current API behavior

### `GET /config/runtime`

- returns the current canonical snapshot: `{ cfg, version, hash }`

### `POST /config/runtime/validate`

Observed behavior:

- uses `ConfigAuthority.validate(...)`
- validates the provided payload against `RuntimeConfig`
- canonicalizes the `regime_unified` compatibility alias into the canonical RI authority path when applicable
- returns `{ valid, errors, cfg? }`
- hides internal exception details behind `invalid_config`

Important boundary:

- this endpoint validates the **payload as a config object**, not as a live patch merged onto the current runtime file
- it does **not** apply the live-update whitelist
- it therefore cannot be read as "this payload is live-writable"

### `POST /config/runtime/propose`

Observed behavior:

- requires `BEARER_TOKEN`
- requires `expected_version`
- expects a `patch` payload
- runs `ConfigAuthority.propose_update(...)`
- enforces a path-based whitelist before merge/persist
- merges the allowed patch onto the current runtime config
- writes atomically to `config/runtime.json`
- appends audit entries to `logs/config_audit.jsonl`
- returns generic `400 bad_request` for `ValueError` cases and `409 version_conflict` for optimistic-lock conflicts

Important boundary:

- this endpoint is the actual live-write surface
- current live-updatability should be judged from this path, not from schema support alone

## Caveat: declared fields vs permissive extras

`RuntimeSection` uses `extra="allow"`, which means validation can admit additional undeclared keys in some cases.

This matrix intentionally tracks the **declared and repo-cited runtime surfaces** rather than treating permissive extras as an endorsed public contract.

Practical reading rule:

- if a field is not declared in `RuntimeConfig` or explicitly documented by the config API surfaces, do **not** treat validate-time permissiveness as evidence that it is an intended live-update surface

## Top-level matrix

| Surface           | Declared in `RuntimeConfig` | `validate` accepts payload | `propose` accepts live patch | Current repo reading                             | Notes                                                                                                                                                  |
| ----------------- | --------------------------- | -------------------------- | ---------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `strategy_family` | Yes                         | Yes                        | Yes                          | Live-writable                                    | Values restricted to `legacy` / `ri`; family validation still applies.                                                                                 |
| `thresholds`      | Yes                         | Yes                        | Yes                          | Live-writable                                    | No extra whitelist narrowing inside `thresholds`; schema/default validation still applies.                                                             |
| `gates`           | Yes                         | Yes                        | Yes                          | Live-writable                                    | No extra whitelist narrowing inside `gates`; schema/default validation still applies.                                                                  |
| `risk`            | Yes                         | Yes                        | Partial                      | Live-writable only for `risk_map`                | Any nested key other than `risk_map` is rejected by whitelist.                                                                                         |
| `ev`              | Yes                         | Yes                        | Partial                      | Live-writable only for `R_default`               | Any nested key other than `R_default` is rejected by whitelist.                                                                                        |
| `exit`            | Yes                         | Yes                        | No                           | Schema-valid but live-blocked                    | Top-level whitelist rejects `exit`.                                                                                                                    |
| `multi_timeframe` | Yes                         | Yes                        | Partial                      | Live-writable only for allowlisted nested leaves | See nested matrix below; canonical dump may omit disabled/default-equivalent research leaves.                                                          |
| `warmup_bars`     | Yes                         | Yes                        | No                           | Schema-valid but live-blocked                    | Top-level whitelist rejects `warmup_bars`.                                                                                                             |
| `htf_exit_config` | Yes                         | Yes                        | No                           | Schema-valid but live-blocked                    | Top-level whitelist rejects `htf_exit_config`.                                                                                                         |
| `htf_fib`         | Yes                         | Yes                        | No                           | Schema-valid but live-blocked                    | Top-level whitelist rejects `htf_fib`.                                                                                                                 |
| `ltf_fib`         | Yes                         | Yes                        | No                           | Schema-valid but live-blocked                    | Top-level whitelist rejects `ltf_fib`.                                                                                                                 |
| `features`        | Yes                         | Yes                        | No                           | Schema-valid but live-blocked                    | Top-level whitelist rejects `features`.                                                                                                                |
| `regime_unified`  | Compatibility alias only    | Yes                        | Yes, via canonicalization    | Input-only compatibility bridge                  | Alias is accepted as input, canonicalized into `multi_timeframe.regime_intelligence.authority_mode`, and not persisted as a top-level canonical field. |

## `multi_timeframe` nested live-write matrix

| Path                                                                  | `validate` accepts                           | `propose` accepts         | Current repo reading               | Notes                                                                                                                                                                                                                              |
| --------------------------------------------------------------------- | -------------------------------------------- | ------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `multi_timeframe.use_htf_block`                                       | Yes                                          | Yes                       | Live-writable                      |                                                                                                                                                                                                                                    |
| `multi_timeframe.allow_ltf_override`                                  | Yes                                          | Yes                       | Live-writable                      |                                                                                                                                                                                                                                    |
| `multi_timeframe.ltf_override_threshold`                              | Yes                                          | Yes                       | Live-writable                      |                                                                                                                                                                                                                                    |
| `multi_timeframe.ltf_override_adaptive.*`                             | Yes                                          | Yes, allowlisted          | Live-writable                      | Allowed keys: `enabled`, `window`, `percentile`, `min_history`, `min_floor`, `max_ceiling`, `fallback_threshold`, `regime_multipliers`.                                                                                            |
| `multi_timeframe.research_bull_high_persistence_override.*`           | Yes                                          | Yes, allowlisted          | Live-writable                      | Allowed keys: `enabled`, `min_persistence`, `max_probability_gap`, `min_size_base`, `require_non_penalized_volatility_for_min_size_base`.                                                                                          |
| `multi_timeframe.research_defensive_transition_override.*`            | Yes                                          | Yes, allowlisted          | Live-writable                      | Allowed keys: `enabled`, `guard_bars`, `max_probability_gap`.                                                                                                                                                                      |
| `multi_timeframe.research_current_atr_high_vol_multiplier_override.*` | Yes                                          | Yes, allowlisted          | Live-writable                      | Allowed keys: `enabled`, `current_atr_threshold`, `high_vol_multiplier_override`.                                                                                                                                                  |
| `multi_timeframe.research_policy_router.*`                            | Yes                                          | Yes, allowlisted          | Live-writable                      | Allowed keys: `enabled`, `switch_threshold`, `hysteresis`, `continuation_release_hysteresis`, `min_dwell`, `defensive_size_multiplier`. Canonical dump may omit disabled leaves or equal-valued `continuation_release_hysteresis`. |
| `multi_timeframe.htf_selector.*`                                      | Yes                                          | Yes, allowlisted          | Live-writable                      | Allowed keys: `mode`, `default_timeframe`, `default_multiplier`, `fallback_timeframe`, `per_timeframe`; per-timeframe rules allow `timeframe`, `multiplier`, `label`.                                                              |
| `multi_timeframe.regime_intelligence.authority_mode`                  | Yes                                          | Yes                       | Live-writable                      | Allowed values: `legacy`, `regime_module`.                                                                                                                                                                                         |
| `multi_timeframe.regime_intelligence.regime_definition.*`             | Yes                                          | Yes, exact shape required | Live-writable                      | Exact required key set: `adx_trend_threshold`, `adx_range_threshold`, `slope_threshold`, `volatility_threshold`.                                                                                                                   |
| Any other `multi_timeframe.*` path                                    | Possibly, depending on permissive validation | No                        | Not a supported live-write surface | Do not infer live support from validate-time permissiveness.                                                                                                                                                                       |

## Practical reading

### Observed now

The current repo surface behaves like this:

1. `validate` answers: can this payload instantiate a runtime config object?
2. `propose` answers: can this patch be live-written through the guarded authority path?
3. The live-write surface is intentionally narrower than the full declared runtime schema.

### Inferred current policy reading

Based on current code plus `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`, the repository currently behaves closest to:

- **B1 (safety-model reading):** keep a stricter live whitelist and document it clearly

This is an **inference about current behavior**, not a claim that the future policy decision is permanently settled.

## Do not confuse these surfaces

### Runtime config SSOT

- `config/runtime.json`
- `ConfigAuthority`
- `RuntimeConfig`
- `/config/runtime*` API endpoints

### Legacy helper surface

- `core.config.validator.validate_config`
- `core.config.validator.diff_config`
- `schema_v1.json`

These legacy helpers are explicitly described as test-only / legacy helpers and must not be mistaken for the current runtime live-update contract.

## What changed in this slice

- created a docs-only reference note that maps schema support, validate acceptance, and propose/live-write allowance
- made the current whitelist boundary easier to cite in later packets, notes, and reviews

## What did not change

- no code
- no whitelist expansion
- no API behavior change
- no runtime/config-authority semantic change
- no new live-update permission
- no new SSOT

## Bottom line

The current Genesis-Core runtime-config surface is deliberately asymmetric: **schema-valid** is broader than **live-writable**. The safe reading for current work is therefore: use `validate` to test config shape, use `propose` to judge live authority, and do not treat successful validation as evidence that a field is intended to be mutable at runtime.
