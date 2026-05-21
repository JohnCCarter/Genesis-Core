# Precompute-cache config-identity follow-up selection packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `follow-up-selected / docs-only / non-authorizing`

This packet records the next bounded `#2` follow-up after the Wave 3 `#2 + #12` reframe. It grants no runtime, backtest, test, script, workflow, env/config, determinism, readiness, paper/live, launch, or promotion authority. It must not be read as approval to begin `src/**`, `tests/**`, or CI/workflow changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/*`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but it chooses the next `#2` line near backtest/cache semantics where wording drift could be mistaken for approval to change cache keys or env/default behavior immediately
- **Required Path:** `Quick`
- **Lane:** `Concept` — why: this slice selects the next bounded `#2` follow-up only; it does not implement runtime or CI behavior
- **Objective:** determine which exact `#2` line remains live after the Wave 3 reframe, given the current repo state of the selector-policy validator and cache-key tests
- **Candidate line:** `#2 post-reframe first bounded follow-up`
- **Base SHA:** `49a8070f`
- **Skill Usage:** `none required`

### Scope

- **Scope IN:** this packet; one small live-note adjustment in `handoff.md`; explicit observed/inferred/unverified framing; exact current state of the `#2` selector-policy validator path; explicit selection of the next bounded `#2` line after that guardrail
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `.github/**`, `config/**`, `results/**`, and `artifacts/**`; all changes to `GENESIS_PRECOMPUTE_CONFIG_HASH` semantics; all cache-key changes; all `PRECOMPUTE_SCHEMA_VERSION` changes; all CI/workflow activation; all `#12` writer/schema-owner work; all claims that the selected follow-up is already implemented
- **Expected changed files:** `docs/decisions/governance/precompute_cache_config_identity_followup_selection_packet_2026-05-21.md`, `handoff.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual path audit for every named validator/test/code path
- manual wording audit that current selector-policy validation is described as current branch state, not as a new implementation in this slice
- manual wording audit that the chosen follow-up stays explicitly `föreslagen` / next-step only rather than approved source work
- manual wording audit that `#12` remains out of scope and that `GENESIS_PRECOMPUTE_CONFIG_HASH` policy is not silently changed here
- self-review for hidden behavior impact

### Stop Conditions

- any wording that treats the selector-policy validator path as absent or merely future-tense on the current branch
- any wording that treats this packet as approval to change `_precompute_cache_key(...)`, `_precompute_cache_key_material()`, or env/default semantics now
- any wording that makes `GENESIS_PRECOMPUTE_CONFIG_HASH` mandatory in this slice
- any wording that reopens `#12` in the same packet
- any wording that jumps ahead to runtime/backtest implementation without a fresh governance pass

## Purpose

This packet answers one narrow question only:

- after the Wave 3 reframe, what should the next truthful `#2` follow-up be?

## What changed in this slice

- one new packet records the next `#2` line after the reframe
- `handoff.md` gets a small live-note refinement so the next agent does not spend a slice re-choosing an already tracked guardrail

## What did not change

- no runtime/backtest/cache behavior changed
- no tests, scripts, workflows, or env/config semantics changed
- no selector-policy validator logic changed
- no cache-key logic changed
- no `#12` writer/schema-owner grounding changed

## Governing basis

### Observed

1. `scripts/validate/validate_precompute_cache_selector_policy.py` currently exists in the tracked repo and dispatches a focused pytest selector bundle when edits touch the tracked precompute-cache contract surface in `src/core/backtest/engine.py`.
2. That validator currently watches:
   - `PRECOMPUTE_SCHEMA_VERSION`
   - `_precompute_cache_key_material()`
   - `_build_precompute_cache_metadata(...)`
   - `_validate_metadata_bearing_precompute_cache(...)`
   - `_precompute_cache_key(...)`
   - the `prepare_precomputed_features(...)` call-site inside `load_data()`
3. `tests/utils/test_validate_precompute_cache_selector_policy.py` currently proves both no-op behavior for non-target edits and selector dispatch for tracked-surface edits.
4. `src/core/backtest/engine.py::_precompute_cache_key(...)` still only adds a config-context segment when `GENESIS_PRECOMPUTE_CONFIG_HASH` is provided and non-empty.
5. `tests/backtest/test_precompute_cache_key.py` currently proves that:
   - unset/empty `GENESIS_PRECOMPUTE_CONFIG_HASH` preserves the legacy key shape with no `_cfg...` segment
   - non-empty `GENESIS_PRECOMPUTE_CONFIG_HASH` changes the key while keeping the raw env value out of the path
6. `handoff.md`, `docs/audit/BACKTEST_ENGINE_AUDIT.md`, and `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` still describe the open `#2` seam as optional config-context isolation plus manual schema-bump discipline, not as absence of a selector-policy guardrail.
7. `docs/decisions/governance/precompute_feature_cache_medium_track_reframe_packet_2026-05-21.md` explicitly left the next `#2` candidate unresolved between the selector-policy / validator path and a stronger deterministic config-subset identity candidate.

### Inferred

- The selector-policy / validator path is already part of the current tracked `#2` guardrail surface on `feature/risk-hardening-wave3`.
- Re-spending the next bounded slice on choosing that same validator path again would duplicate already-grounded current branch state.
- The remaining truthful `#2` line is therefore narrower: how to tighten config-context identity for the on-disk precompute cache without widening into `#12` or silently changing defaults.
- The next bounded `#2` follow-up should therefore center the `deterministic config-subset identity / config-context isolation` question rather than the already-tracked selector-policy carrier.

### Unverified in this packet

- the exact config subset that should participate in deterministic cache identity
- whether later implementation should keep `GENESIS_PRECOMPUTE_CONFIG_HASH` as an override-only escape hatch, convert it into a fallback, or supersede it entirely
- the exact code locus for a later implementation-bearing candidate (`_precompute_cache_key_material()`, `_precompute_cache_key(...)`, or another minimal helper)
- the final focused test bundle a later implementation slice would require beyond the existing selector-policy/tests

## Boundary decision

### Current standing conclusion

For `feature/risk-hardening-wave3`, the next truthful `#2` follow-up should be:

- `precompute-cache deterministic config-subset identity / config-context isolation`

This means:

- do **not** spend the next bounded `#2` slice re-choosing the selector-policy / validator path as if it were not already present
- do **not** bundle `#12` back into the same packet
- do **not** jump straight into runtime edits yet

### Next admissible packet shape

If `#2` continues from here, the next admissible move should be a **separate pre-code packet** that defines:

- the exact config subset candidate to identity-hash for cache isolation
- the exact minimal code locus for the candidate
- what default behavior must remain unchanged unless explicitly reopened
- what focused tests/gates must prove parity and no hidden cache-path regressions

### What this decision does not mean

This decision does **not** mean:

- that config-subset identity is already implemented
- that `GENESIS_PRECOMPUTE_CONFIG_HASH` policy has already changed
- that the existing selector-policy validator is sufficient to close `#2`
- that `#12` has changed status

## Bottom line

Wave 3 no longer needs another packet to decide whether the `#2` selector-policy validator path should exist — it already exists on the current branch. The remaining live `#2` question is the narrower config-identity line: how to make cache-context identity stronger, truthfully and minimally, without smuggling in runtime changes or `#12` drift.
