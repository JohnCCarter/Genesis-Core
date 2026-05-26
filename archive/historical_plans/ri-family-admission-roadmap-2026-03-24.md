# RI family admission roadmap

Date: 2026-03-24
Branch context: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `historical / parked / archive-only / not active on current branch / no-behavior-change roadmap`

> Current status note:
>
> - `ARCHIVED 2026-05-05`: This roadmap belongs to the earlier `feature/ri-role-map-implementation-2026-03-24` branch context and is not current branch guidance on `feature/next-slice-2026-05-05`.
> - Resolve any current branch guidance from current branch state, higher-order governance docs, and later anchored evidence rather than from this archived roadmap.
> - Preserve it as archived historical refactor-planning context for family-admission work.
> - Reopen only via explicit user request or a fresh packet that deliberately re-enters this family-admission refactor surface.

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
