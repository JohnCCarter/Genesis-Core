# AI Agent Reading Order

Date: 2026-05-26
Mode: `RESEARCH`
Status: `docs-only / non-authorizing / reading-order aid / no behavior change`

## Purpose

This document gives humans and AI agents a safe first-pass reading order for Genesis-Core.
It is a navigation aid only. It does not create new authority, change governance rules, or promote any research surface.

## Scope

### Scope IN

- reduce cold-start ambiguity for AI agents
- clarify which files should be read before interpreting research, runtime, or governance surfaces
- preserve existing authority hierarchy
- separate current authority from research, audit, archive, and historical evidence surfaces

### Scope OUT

- runtime behavior changes
- config changes
- governance authority changes
- promotion/readiness claims
- file moves
- document deletion or archival
- replacement of existing SSOT documents

## Primary reading order for non-trivial work

1. `AGENTS.md`
   - Constitutional governance layer.
   - Read first to understand stable boundaries, agent roles, no-behavior-change default, freeze rules, and authority hierarchy.

2. `.github/copilot-instructions.md`
   - Practical operating contract for Copilot/Codex/Opus work.
   - Read after `AGENTS.md` to resolve workflow sizing, risk paths, and high-sensitivity zones.

3. `docs/governance_mode.md`
   - Mode-resolution source.
   - Read before deciding whether the task is RESEARCH, STRICT, or another governed lane.

4. `docs/OPUS_46_GOVERNANCE.md`
   - Governance reviewer rules and risk-audit expectations.
   - Required for non-trivial governed work and any high-sensitivity surface.

5. `docs/CURRENT_AUTHORITY_INDEX.md`
   - Derivative current-use classification aid.
   - Use as an orientation map only; do not treat it as broader authority than it explicitly claims.

6. `docs/repository-layout-policy.md`
   - Practical file-placement and layout guidance.
   - Subordinate to higher-order governance documents.

7. `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`
   - Current bounded reading aid for RI vs Legacy friction.
   - Use when interpreting family, router, shared-backbone, and admission terminology.

8. `docs/RESEARCH_TAXONOMY_RI_LEGACY_SHARED.md`
   - Proposed taxonomy aid for classifying research surfaces as RI-only, Legacy-only, or Shared.
   - Non-authorizing until separately promoted or incorporated by an existing authority path.

## Reading rule for research and historical surfaces

Treat the following as non-authorizing unless a current authority surface explicitly says otherwise:

- `plan/**`
- `docs/audit/**`
- `docs/archive/**`
- `docs/analysis/**`
- `docs/decisions/**`
- `results/research/**`
- `results/evaluation/**`
- `artifacts/diagnostics/**`

These surfaces may contain valuable evidence, negative results, historical context, and reproducibility artifacts.
They must not be treated as current runtime authority, promotion authority, or implementation approval merely because they are detailed.

## RI / Legacy reading guardrails

Use these guardrails before interpreting RI or Legacy work:

- Shared runtime backbone does not imply shared strategy family.
- `authority_mode = regime_module` does not by itself prove a valid RI family surface.
- RI policy-router placement inside shared decision orchestration does not make it a cross-family router.
- Preserved overlay evidence does not override current two-family contract reading.
- Historical wording drift must be resolved through current authority surfaces, not by isolated older documents.

## Recommended cold-start path by task type

### Runtime, config, or backtest changes

Read:

1. `AGENTS.md`
2. `.github/copilot-instructions.md`
3. `docs/governance_mode.md`
4. `docs/OPUS_46_GOVERNANCE.md`
5. the exact touched code/config/test surfaces
6. relevant decision/audit docs only after authority and scope are resolved

### Research or analysis-only work

Read:

1. `AGENTS.md`
2. `.github/copilot-instructions.md`
3. `docs/governance_mode.md`
4. `docs/repository-layout-policy.md`
5. `docs/RESEARCH_TAXONOMY_RI_LEGACY_SHARED.md`
6. the bounded research packet or analysis surface for the task

### RI vs Legacy interpretation

Read:

1. `AGENTS.md`
2. `.github/copilot-instructions.md`
3. `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`
4. `docs/RESEARCH_TAXONOMY_RI_LEGACY_SHARED.md`
5. current code surfaces or packets explicitly named by the task

## Non-claims

This file does not claim:

- full repository coverage
- that all historical documents have been reviewed
- that all current authority ambiguity has been resolved
- that any file is safe to move, merge, archive, or delete
- that RI/Legacy architecture should be changed
- that a repo split or cherry-pick migration is unnecessary forever

## Remaining verification gaps

The following remain unverified by this docs-only slice:

- complete local clone inspection
- complete file counts by directory
- complete verification of every docs/results/artifacts surface
- local tests or static analysis
- cold-agent navigation study proving that this reading order is sufficient

## Summary

Use this as a practical first-pass map.
If it conflicts with higher-order governance or an explicit current task instruction, follow the higher-order source and record the conflict.
