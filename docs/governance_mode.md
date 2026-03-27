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

## Operational clarity

### Operational expectations per mode

- `STRICT`: packet-first, explicit authority, fail closed on ambiguity.
- `RESEARCH`: take the smallest admissible research step, prefer minimal tracked artifacts, and avoid unnecessary strict process.
- `SANDBOX`: optimize for fast exploration; no production-near claims.

### RESEARCH is not STRICT-by-default

- `RESEARCH` follows `RESEARCH` policy, not `STRICT` policy.
- Applying STRICT process inside RESEARCH without a strict-only trigger is considered a governance violation.
- Do not apply full `STRICT` packet/gate process in `RESEARCH` unless a strict-only surface is touched or the work otherwise resolves/escalates to `STRICT` under the existing rules.
- Prefer minimal, reproducible research artifacts over heavyweight process when `STRICT` is not required.

### When to use SANDBOX vs RESEARCH

- Use `SANDBOX` for early exploration, sketches, and non-reproducible experiments.
- Use `RESEARCH` for tracked, reproducible experiments and retained research artifacts.
- If work starts in `SANDBOX` but becomes something to retain, reproduce, or govern, move it into `RESEARCH` or `STRICT` as appropriate.

### Strict-only surfaces

The following surfaces are operationally strict-only. This clarifies working posture only and does not change mode resolution, authority rules, or freeze enforcement.

- `src/core/strategy/family_registry.py`
- family admission semantics and related contract decisions
- `config/strategy/champions/**`
- runtime defaults, including `config/runtime.json`
- comparison lane opening or comparison-eligibility decisions
- readiness lane opening or readiness-eligibility decisions
- promotion lane opening or promotion-eligibility decisions

### Mode proof requirement

When beginning a task, briefly state:

- why the current mode applies
- what the mode allows
- what is forbidden in the current mode
- what would require escalation to `STRICT`

## Constraints

- Do not modify existing governance enforcement logic.
- Do not remove gates from STRICT.
- Do not weaken freeze protection.
- Do not allow SANDBOX to override freeze escalation.
- Keep governance mode resolution deterministic and fail-closed.
