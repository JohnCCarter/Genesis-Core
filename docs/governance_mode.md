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

- `main -> STRICT`
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

- `Mode: STRICT (source=branch:main)`
- `Mode: RESEARCH (source=branch:feature/composable-v2)`
- `Mode: STRICT (source=freeze-signal)`
- `Mode: SANDBOX (source=branch:spike/idea-x)`

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
- Cannot be merged to `main` without passing STRICT gates.

## Constraints

- Do not modify existing governance enforcement logic.
- Do not remove gates from STRICT.
- Do not weaken freeze protection.
- Do not allow SANDBOX to override freeze escalation.
- Keep governance mode resolution deterministic and fail-closed.
