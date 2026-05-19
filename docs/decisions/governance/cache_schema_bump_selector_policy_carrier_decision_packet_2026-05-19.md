# Cache schema-bump selector-policy carrier decision packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the exact future repo-visible carrier strategy to use if the `#2` precompute-cache schema-bump enforcement line is reopened after the selector-policy packet. It grants no source, test, workflow, runtime, cache, determinism, readiness, paper/live, launch, or promotion authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice chooses one bounded future carrier only and does not modify scripts, tests, workflows, runtime behavior, or env/config semantics
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this packet records a docs-only carrier decision for the already-selected `#2` locus (`touch-triggered pytest selector policy`); it does not implement enforcement
- **Objective:** choose one exact future repo-visible carrier for the already-selected `#2` selector-policy locus without widening into CI activation, runtime assertion, `#12`, or config-hash policy
- **Candidate line:** `#2 precompute-cache schema-bump enforcement`
- **Chosen future carrier:** `scripts/validate/validate_precompute_cache_selector_policy.py`
- **Base SHA:** `4ef5f745`
- **Skill Usage:** `ingen matchande skill identifierad`

### Scope

- **Scope IN:** `docs/decisions/governance/cache_schema_bump_selector_policy_carrier_decision_packet_2026-05-19.md` only; explicit observed/inferred/unverified framing; exact future carrier selection for the already-chosen selector-policy locus; explicit comparison of why `.pre-commit-config.yaml` and direct `.github/workflows/ci.yml` are not chosen first; explicit likely future implementation IN/OUT if the validator carrier is later implemented; explicit statement that `#12` and `GENESIS_PRECOMPUTE_CONFIG_HASH` remain out of scope
- **Scope OUT:** all edits under `scripts/**`, `.github/workflows/**`, `.pre-commit-config.yaml`, `src/**`, `tests/**`, `config/**`, `results/**`, and `artifacts/**`; all claims that the validator carrier already exists; all claims that CI enforcement already exists; all claims that pre-commit or workflow carriers are rejected generally; all widening into repo-wide feature-diff detection; all reopening of `#12` or `GENESIS_PRECOMPUTE_CONFIG_HASH` policy
- **Expected changed files:** `docs/decisions/governance/cache_schema_bump_selector_policy_carrier_decision_packet_2026-05-19.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this packet
- manual path audit for every named file path and future-carrier reference
- manual wording audit that the chosen validator carrier remains future-tense / `föreslagen` rather than implemented
- manual wording audit that later CI invocation remains a separate follow-up rather than silently bundled into the carrier decision
- manual wording audit that `.pre-commit-config.yaml` and `.github/workflows/ci.yml` remain alternatives not chosen first rather than globally rejected paths
- manual wording audit that `#12` and `GENESIS_PRECOMPUTE_CONFIG_HASH` stay explicitly outside this carrier decision

### Stop Conditions

- any wording that treats `scripts/validate/validate_precompute_cache_selector_policy.py` as already present in the repo
- any wording that treats `.github/workflows/ci.yml` as already carrying `#2`-specific enforcement
- any wording that collapses carrier choice and CI activation into the same approved move
- any wording that widens the validator into a repo-wide feature-change detector
- any wording that reopens `#12` or changes `GENESIS_PRECOMPUTE_CONFIG_HASH` policy
- any wording that implies runtime, test, or workflow implementation authority from this packet alone

## Purpose

This packet answers one narrow question only:

- after choosing `touch-triggered pytest selector policy` as the first `#2` locus, what exact future repo-visible carrier should that policy use first?

## What changed in this slice

- the `#2` line now has one explicit future carrier instead of leaving selector-policy encoding implicit
- the repo now records which nearby surfaces are pattern anchors versus non-primary alternatives for the first `#2` carrier

## What did not change

- no source, test, workflow, runtime, cache, or config behavior
- no CI activation for `#2`
- no pre-commit hook policy for `#2`
- no `#12` carrier-trace progress
- no `GENESIS_PRECOMPUTE_CONFIG_HASH` policy change

## Governing basis

### Observed

1. `docs/decisions/governance/cache_schema_bump_touch_triggered_selector_policy_packet_2026-05-19.md` already chose the `#2` locus as `touch-triggered pytest selector policy` and explicitly left the exact later carrier unverified.
2. `.github/workflows/ci.yml` already contains a repo-local diff-aware validation pattern on pull requests by fetching the PR base and invoking `python scripts/validate/validate_registry.py --ci-diff-base origin/${{ github.base_ref }}`.
3. `scripts/validate/` is already a tracked validation family in the current repo, including `scripts/validate/validate_registry.py` and `scripts/validate/validate_optimizer_config.py`.
4. `.pre-commit-config.yaml` currently contains only standard third-party hooks and does not currently define a repo-local `repo: local` carrier for custom selector-policy logic.
5. `.github/workflows/ci.yml` currently runs `pre-commit run --all-files` and a global `pytest -q`, but does not currently carry a `#2`-specific selector-policy step.
6. `docs/decisions/governance/cache_schema_bump_enforcement_boundary_packet_2026-05-18.md` and the newer selector-policy packet both require that `#2` stay separate from `#12`, runtime assertion, and config-hash policy drift.

### Inferred

- The smallest honest future carrier is a repo-local diff-aware validator under `scripts/validate/` because that matches an existing repo pattern while keeping activation separate from policy encoding.
- Choosing a validator script as the carrier is narrower than choosing `.github/workflows/ci.yml` directly, because the workflow file would collapse carrier choice and CI activation into the same first implementation move.
- Choosing a validator script as the carrier is narrower than choosing `.pre-commit-config.yaml`, because the repo currently has no custom local-hook pattern and CI already runs `pre-commit --all-files`, which would blur staged-file behavior and PR-diff behavior.
- The chosen carrier should stay pinned to the already-defined `#2` touch surface and selector bundle; it must not widen into a repo-wide detector for arbitrary feature changes.
- `GENESIS_PRECOMPUTE_CONFIG_HASH` and `#12` remain adjacent but separate policy lines, not part of the first carrier choice.

### Unverified in this packet

- the exact future internal diff-detection logic inside `scripts/validate/validate_precompute_cache_selector_policy.py`
- the exact later CI invocation semantics if a separate activation slice is opened
- whether a later implementation slice can stay bounded to one validator script plus one focused validator test file without needing additional tooling surfaces
- the exact command-line UX of the future validator beyond the carrier path chosen here

## Boundary decision

### Current standing conclusion

If the `#2` line is reopened after the selector-policy packet, the exact future repo-visible carrier should be:

- `scripts/validate/validate_precompute_cache_selector_policy.py`

This is a carrier-selection conclusion only. It is **not** approval to implement the validator or to invoke it from CI.

### Primary carrier versus nearby non-primary surfaces

Treat the following as the **primary future carrier** for the first `#2` implementation slice:

- `scripts/validate/validate_precompute_cache_selector_policy.py`

Treat the following as **not** the primary carrier for that first slice:

- `.github/workflows/ci.yml` (later activation surface only)
- `.pre-commit-config.yaml` (alternative not chosen first)
- `scripts/validate/validate_registry.py` (pattern anchor only)
- `scripts/validate/validate_optimizer_config.py` (pattern anchor only)
- `src/core/backtest/engine.py`
- `tests/backtest/**`

### Likely future implementation scope

If this carrier is later implemented, the smallest honest starting scope is likely:

- one new repo-local validator at `scripts/validate/validate_precompute_cache_selector_policy.py`
- one focused validator test file, likely `tests/utils/test_validate_precompute_cache_selector_policy.py`

### Likely future implementation scope OUT

A later implementation slice should keep the following out of scope unless separately reopened:

- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`
- `src/core/backtest/engine.py`
- existing cache-contract tests under `tests/backtest/**`
- `GENESIS_PRECOMPUTE_CONFIG_HASH` semantics
- `#12` carrier-trace work
- repo-wide feature-diff detection

## Hard stop and reopen rule

If a future implementation slice discovers any of the following, it must stop and reopen as a separate bounded packet:

- the validator carrier cannot work without a simultaneous CI/workflow edit
- the validator carrier cannot work without a new `.pre-commit-config.yaml` local-hook pattern
- the validator carrier needs to inspect or change runtime behavior in `src/core/backtest/engine.py`
- the validator carrier needs to widen beyond the already-defined `#2` touch surface and selector bundle
- `#12` or `GENESIS_PRECOMPUTE_CONFIG_HASH` starts to become coupled to the same implementation move

## Bottom line

The `#2` locus has already been chosen as a `touch-triggered pytest selector policy`; the next unresolved question was its future repo-visible carrier. The smallest honest answer is a **new repo-local diff-aware validator under `scripts/validate/`**, not a direct workflow carrier and not a new pre-commit local-hook pattern. CI invocation, if wanted later, remains a separate explicit follow-up.
