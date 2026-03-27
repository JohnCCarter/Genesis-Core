# Governance Mode (SSOT)

This document is the single source of truth (SSOT) for Governance Mode resolution and policy enforcement.

## Allowed modes

- STRICT
- RESEARCH
- SANDBOX

Default: STRICT

Explicit override: `GENESIS_GOV_MODE`

## Deterministic resolution (A/B/C/D)

Resolution is deterministic and must be evaluated in this exact order.

### A) Explicit override

If `GENESIS_GOV_MODE` is set:

- Accept only `STRICT`, `RESEARCH`, `SANDBOX`.
- Invalid value must fail-closed to `STRICT`.

### B) Branch mapping (exact)

- `master -> STRICT`
- `release/* -> STRICT`
- `champion/* -> STRICT`
- `feature/* -> RESEARCH`
- `research/* -> RESEARCH`
- `sandbox/* -> SANDBOX`
- `spike/* -> SANDBOX`

### C) Freeze escalation

Force `STRICT` if either condition is true:

- A touched path is under `config/strategy/champions/`, OR
- `.github/workflows/champion-freeze-guard.yml` is modified.

### D) Default fallback

If no prior rule resolves a mode, use `STRICT`.

## Fail-closed policy

- Invalid override values always resolve to `STRICT`.
- Unresolved or ambiguous states always resolve to `STRICT`.
- Governance mode resolution must remain deterministic and fail-closed.

## Mandatory mode banner

Every response must begin with this exact format:

`Mode: <MODE> (source=<resolution reason>)`

Examples:

- `Mode: STRICT (source=branch:master)`
- `Mode: RESEARCH (source=branch:feature/composable-v2)`
- `Mode: STRICT (source=freeze-signal)`
- `Mode: SANDBOX (source=branch:spike/idea-x)`

## Operational expectations per mode

Mode is an active operating constraint, not a decorative banner.

### STRICT

- Packet-first for non-trivial work.
- Require explicit authority before entering behavior/config/runtime/comparison/champion surfaces.
- Fail closed on ambiguity.

### RESEARCH

- Prefer the smallest admissible research step.
- Prefer the minimum artifacts/docs needed for traceability.
- Do not add STRICT-style process unless a strict-only surface is touched or mode re-resolves to `STRICT`.
- Avoid unnecessary packet proliferation or governance expansion when authority is already clear.

### SANDBOX

- Prefer fast exploration, sketches, and disposable work.
- No production-near, merge-ready, or `införd` claims.
- Keep experimentation clearly separated from tracked governed artifacts.

## Policy by mode

### STRICT

- Full gates required: pre-commit/lint, smoke tests, determinism replay, feature cache invariance, pipeline invariant.
- No behavior change by default.
- Behavior changes require an explicit exception.

### RESEARCH

- Determinism replay required.
- Pipeline invariant required.
- Refactors allowed.
- Behavior change is allowed only if behind a flag/version.
- Default behavior must remain unchanged.
- A parity test must prove identical default behavior.
- Structural improvements may be proposed.

### SANDBOX

- Rapid experimentation is allowed.
- Determinism replay is optional.
- No process may be marked `införd`.
- Must NOT modify `config/strategy/champions/`.
- Must NOT modify freeze guard workflows.
- Must NOT modify `runtime.json` (if production-critical).
- Cannot be merged to `master` without passing STRICT gates.

## RESEARCH is not STRICT-by-default

- RESEARCH must be operated as `RESEARCH`.
- Do not apply extra STRICT-style process unless:
  - branch/override/freeze escalation resolves to `STRICT`, OR
  - the task explicitly enters a strict-only surface listed below.
- Applying STRICT process inside RESEARCH without a strict-only trigger is considered a governance violation.
- If stricter handling is used, state the exact triggering path, concept, or rule.

## When to use SANDBOX vs RESEARCH

- Use `SANDBOX` for early exploration, sketches, and non-reproducible experiments.
- Use `RESEARCH` for tracked, reproducible experiments and artifacts.
- If the work is intended to support later review with traceable evidence, prefer `RESEARCH`.
- If the work is intentionally rough, disposable, or not yet reproducible, prefer `SANDBOX`.

## Strict-only surfaces

This is an operational stop/escalate list only. It does not change the deterministic resolution logic above.

- `config/strategy/champions/`
- `.github/workflows/champion-freeze-guard.yml`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- runtime-default authority surfaces
- comparison surfaces
- readiness surfaces
- promotion surfaces
- champion surfaces
- family-rule surfaces

## Mode proof requirement

Before any non-trivial action, the agent must briefly state:

- why the current mode applies
- what the current mode allows for the present task
- what remains forbidden for the present task
- what exact path or concept would require `STRICT` escalation

## Constraints

- Do not modify existing governance enforcement logic.
- Do not remove gates from STRICT.
- Do not weaken freeze protection.
- Do not allow SANDBOX to override freeze escalation.
- Keep governance mode resolution deterministic and fail-closed.
