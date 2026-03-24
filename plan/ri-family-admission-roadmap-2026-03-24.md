# RI family admission roadmap

Date: 2026-03-24
Branch context: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Default constraint: `NO BEHAVIOR CHANGE` unless a narrower packet explicitly says otherwise.

## Objective

Refactor optimizer/preflight family guardrails so the repository distinguishes three concerns cleanly:

1. structural validity
2. family identity (`legacy` vs `ri`)
3. family admission policy for a specific `run_intent`

This roadmap exists because the current system has outgrown a shared validator/preflight model. The slice7 blocker exposed that `strategy_family=ri` currently implies a single canonical RI signature, which is too strict for research slices and too implicit for governance.

## Target architecture

### Layer 1 — Structural validation

Responsibility:

- YAML/config structure
- required top-level sections
- storage/resume sanity
- timeout/sample-range/data coverage checks
- canonical mode flag checks
- generic search-space sanity

Must not decide:

- strategy family identity
- run-intent admissibility
- canonical RI freeze/promotion policy

### Layer 2 — Family identity

Responsibility:

- determine whether a config is `legacy` or `ri`
- fail fast on explicit family mismatch
- fail fast on hybrid or incompatible authority/surface combinations

Should live primarily in:

- `src/core/strategy/family_registry.py`

Must not carry:

- full research/candidate/promotion/freeze policy
- Optuna-specific launch admission semantics

### Layer 3 — Family admission policy

Responsibility:

- decide whether a config is admissible for a specific `run_intent`
- apply family-specific rules above identity
- keep hard fail-fast for known mixed/suppressive surfaces

Initial `run_intent` values:

- `research_slice`
- `candidate`
- `promotion_compare`
- `champion_freeze`

Candidate home:

- new module(s) under `src/core/strategy/` or `src/core/optimizer/` dedicated to family admission policy

## Design principles

- Keep `family_registry.py` focused on family identity, not full canonical RI freeze policy.
- Use one common structural validator/preflight flow with explicit family-aware dispatch.
- Make `run_intent` first-class and mandatory where admission policy matters.
- Allow RI research slices to vary within explicit whitelists without pretending they are promotion-admissible.
- Preserve hard fail-fast for known mixed or suppressive surfaces.
- Keep diffs incremental and reversible.
- Prefer adding tests before widening admissibility.

## Current observed blocker

The current RI contract effectively treats these as identity requirements:

- authority_mode = `regime_module`
- `thresholds.signal_adaptation.atr_period = 14`
- `gates.hysteresis_steps = 3`
- `gates.cooldown_bars = 2`
- canonical RI threshold cluster exactness

That means a config can be a legitimate RI research slice but still fail because the guardrails collapse identity + admission into one rule set.

Preflight also undercounts searchable parameters because `int` ranges are not counted as searchable.

## Phase roadmap

## Phase 0 — Freeze diagnosis and scope packet

Goal:

- package the discovered problem as a governed implementation task before changing any runtime-adjacent tooling logic

Deliverables:

- command packet for family-admission refactor
- explicit Scope IN/OUT
- selected file list
- required gates

Scope IN (expected):

- `src/core/strategy/family_registry.py`
- new admission-policy module(s)
- `scripts/validate/validate_optimizer_config.py`
- `scripts/preflight/preflight_optuna_check.py`
- focused tests under `tests/core/strategy/` and `tests/utils/`

Scope OUT:

- `config/runtime.json`
- `config/strategy/champions/**`
- `src/core/backtest/**`
- `src/core/optimizer/runner.py` unless absolutely necessary
- committed `results/**`

Exit criteria:

- Opus pre-code approval on contract + plan

## Phase 1 — Introduce `run_intent` contract

Goal:

- define `run_intent` as a typed concept instead of an implicit idea spread across docs and scripts

Tasks:

- add a canonical run-intent type/constant surface
- define allowed values:
  - `research_slice`
  - `candidate`
  - `promotion_compare`
  - `champion_freeze`
- decide where it enters optimizer/preflight config interpretation
- keep backward compatibility explicit for configs that do not yet declare intent

Preferred approach:

- default optimizer/preflight behavior should not silently reinterpret legacy configs as promotion-grade RI configs
- if missing, use an explicit safe default for the relevant surface and report it clearly

Tests:

- allowed values accepted
- unknown values rejected
- missing intent handled deterministically

Exit criteria:

- typed run-intent surface exists
- tests prove deterministic handling

## Phase 2 — Shrink `family_registry.py` back to identity

Goal:

- keep family classification and hybrid detection there, while moving run-purpose strictness out

Tasks:

- identify which current RI rules are true identity markers vs admission policy
- preserve hybrid fail-fast behavior
- remove canonical RI freeze semantics from identity validation if they belong to admission

Identity should still answer:

- is this RI?
- is this Legacy?
- is this a hybrid/invalid mismatch?

Identity should not fully answer:

- is this promotion-admissible RI?
- is this freeze-admissible RI?
- is this a legal RI research slice?

Tests:

- existing family classification tests updated, not discarded
- keep hybrid mismatch rejection
- ensure canonical RI still classifies as RI
- ensure research-variant RI can still classify as RI when identity markers remain intact

Exit criteria:

- family identity is narrower and cleaner
- no run-intent policy remains hidden in identity logic

## Phase 3 — Add family admission policy layer

Goal:

- create a dedicated policy layer above identity

Tasks:

- add family-aware admission API, e.g. conceptually:
  - `validate_family_admission(config, family, run_intent)`
- encode separate policy for:
  - legacy + research_slice
  - legacy + candidate
  - RI + research_slice
  - RI + candidate
  - RI + promotion_compare
  - RI + champion_freeze
- encode fail-fast mixed-surface checks explicitly here

Initial RI policy split:

- `research_slice`
  - allow whitelisted bounded exploration surfaces
  - allow non-canonical but RI-compatible gates if packeted for research
- `candidate`
  - stricter than research_slice
  - preserve RI-compatible cluster constraints
- `promotion_compare`
  - require comparability-safe shape and family-consistent candidate semantics
- `champion_freeze`
  - require exact canonical/frozen surface

Tests:

- RI research slice with gate sweep admissible
- RI promotion compare rejects same config if it is not comparison-safe
- RI champion freeze requires exact frozen/canonical contract
- mixed legacy/RI suppressive surfaces fail fast

Exit criteria:

- admission policy exists as a separate tested layer
- slice7-like config can be expressed as RI + research_slice instead of being forced into canonical RI identity

## Phase 4 — Refactor optimizer validator to use the three layers

Goal:

- make `validate_optimizer_config.py` call:
  1. structural checks
  2. family identity checks
  3. family + run_intent admission checks

Tasks:

- keep current structural champion/repro logic where still relevant
- stop encoding full RI canonical strictness directly in the optimizer validator
- improve messages so failures say whether they are:
  - structural
  - family identity
  - family admission / run intent

Tests:

- structural failure message stays structural
- RI identity mismatch message stays identity-specific
- RI research-admission failure says admission/run_intent, not generic invalid RI cluster

Exit criteria:

- validator error messages map cleanly to the correct layer

## Phase 5 — Refactor preflight to become family-aware and intent-aware

Goal:

- make `preflight_optuna_check.py` aware of family + run_intent rather than delegating all meaning to the validator

Tasks:

- preserve generic preflight checks
- dispatch to family admission logic for intent-aware checks
- fix searchable parameter counting to include `int` ranges
- ensure preflight output distinguishes:
  - no searchable params
  - searchable params exist but not admissible for intent
  - admissible research slice

Tests:

- `int` ranges counted as searchable
- RI research_slice with int gate ranges no longer reported as fully fixed
- admission failure still blocks preflight when policy requires it

Exit criteria:

- preflight accurately reports searchability and admission

## Phase 6 — Add regression tests for the discovered slice7 class

Goal:

- permanently encode the discovered failure class as a regression suite

Add focused tests for:

- slice7-style RI config with gate range sweep under `research_slice`
- same shape rejected under `champion_freeze`
- mixed legacy authority + RI markers rejected hard
- candidate/promotion compare stricter than research slice
- structural validator still rejects malformed config independently of family admission

Exit criteria:

- regression suite proves the architectural split actually works

## Phase 7 — Revalidate slice7 under the new model

Goal:

- prove the refactor solves the real blocked workflow rather than only cleaning architecture

Tasks:

- update slice7 config to declare the correct `run_intent`
- rerun:
  - file-scoped pre-commit
  - validator
  - preflight
  - determinism smoke
  - feature-cache invariance
  - pipeline invariant
  - authority-mode resolver
- if all gates are green, package execution as a separate governed step

Exit criteria:

- slice7 either becomes launchable under `research_slice`, or fails for a better explicit reason than today

## Phase 8 — Follow-on family surfaces audit

Goal:

- inventory what else should become family-aware after optimizer validator/preflight are fixed

Audit candidates:

- comparison / promotion workflows
- champion freeze semantics
- research ledger tagging or intent metadata
- config API validation surfaces
- future family-specific candidate admission docs

This phase is inventory-first, not mandatory for the first implementation slice.

Exit criteria:

- prioritized backlog of next family-aware surfaces

## Recommended implementation order

1. Phase 0 packet + approval
2. Phase 1 run_intent surface
3. Phase 2 identity cleanup in `family_registry.py`
4. Phase 3 admission policy layer
5. Phase 4 validator integration
6. Phase 5 preflight integration + int-range fix
7. Phase 6 regression tests
8. Phase 7 slice7 revalidation
9. Phase 8 follow-on audit

## Verification gates by phase

Minimum recurring gates:

- targeted pytest for changed modules
- `ruff check` on touched `src/`, `scripts/`, `tests/`
- relevant preflight/validator command checks

Expected targeted tests to extend:

- `tests/core/strategy/test_families.py`
- `tests/utils/test_validate_optimizer_config.py`
- `tests/utils/test_preflight_optuna_check.py`

Likely additional tests to add:

- new admission-policy tests under `tests/core/strategy/`

Before any slice7 relaunch:

- `tests/backtest/test_backtest_determinism_smoke.py`
- `tests/utils/test_features_asof_cache_key_deterministic.py`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `tests/governance/test_authority_mode_resolver.py`

## Stop conditions

Stop and repacket if any of the following happens:

- runtime behavior outside validator/preflight/admission surfaces must change
- `runner.py` or backtest execution semantics need modification
- the scope expands into champion defaults or runtime authority
- admission rules cannot be separated without breaking identity classification invariants
- tests reveal that RI/legacy family boundaries are used implicitly in additional high-sensitivity paths not yet packeted

## Definition of done for the first implementation slice

The first correct implementation slice is done when all of the following are true:

- `family_registry.py` focuses on identity, not full canonical RI freeze policy
- a separate family admission layer exists
- admission is `run_intent` aware
- validator is family-aware + intent-aware
- preflight is family-aware + intent-aware
- preflight counts `int` ranges as searchable
- mixed/suppressive surfaces still fail fast
- a slice7-style RI research config can be validated for `research_slice`
- the same config is still rejected for stricter intents where appropriate

## Immediate next action

Create a command packet for the first implementation slice covering phases 0-5 plus the minimum regression tests needed to prove the split.
