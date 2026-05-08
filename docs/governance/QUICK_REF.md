# Genesis-Core Governance Quick Reference

> Load this at session start. Read full governance docs only when executing a gated commit.

## Mode Resolution (deterministic, A→D)

| Priority | Rule                       | Result                                                                                                               |
| -------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| A        | `GENESIS_GOV_MODE` env var | Explicit override (STRICT/RESEARCH/SANDBOX only; invalid→STRICT)                                                     |
| B        | Branch name                | `master`, `release/*`, `champion/*` → STRICT; `feature/*`, `research/*` → RESEARCH; `sandbox/*`, `spike/*` → SANDBOX |
| C        | Freeze escalation          | Any touch of `config/strategy/champions/` or champion-freeze-guard workflow → STRICT                                 |
| D        | Default                    | STRICT (fail-closed)                                                                                                 |

**Banner**: every response starts with `Mode: <MODE> (source=<resolution reason>)`

## Change Class → Governance Path

| Class                | Examples                                                                                                  | Opus Pre       | Opus Post           | Path                                   |
| -------------------- | --------------------------------------------------------------------------------------------------------- | -------------- | ------------------- | -------------------------------------- |
| Trivial              | README, comment, editor metadata                                                                          | Optional       | Optional            | Quick path                             |
| Non-trivial low-risk | Tests, tooling, scripts                                                                                   | Mode-dependent | Mode-dependent      | Smallest admissible                    |
| Runtime/contract     | API, config/env, execution logic                                                                          | Required       | Required            | Full protocol                          |
| High-sensitivity     | `src/core/strategy/*`, `src/core/backtest/*`, `src/core/optimizer/*`, runtime authority, paper/live edges | Required       | Required (blocking) | Full protocol + deterministic evidence |

**Quick-path eligibility** (ALL must be true):

1. ≤2 files touched
2. No runtime behavior change (docs/comments/metadata/editor config only)
3. No dependency, API contract, env/config, or schema changes
4. No high-sensitivity files touched

## Required Gates (non-trivial / high-sensitivity)

```
pre-commit / lint → smoke tests → determinism replay → feature cache invariance → pipeline invariant
```

## High-Sensitivity Zones (extra strict — always require Opus)

- `src/core/strategy/*`
- `src/core/backtest/*`
- `src/core/optimizer/*`
- Runtime/config authority paths
- Paper/live execution and API edges
- `config/strategy/champions/`

## Authority Order (conflict resolution)

1. Explicit user request
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

## Status Vocabulary

- `föreslagen` = proposed, not yet in repo
- `införd` = implemented and verified in repo

## Cloud Worker Defaults

- Defaultmodell: `autonomous slice worker`
- Samma grundroll bör normalt återanvändas på olika bounded slices/windows
- Skillnader mellan workers ska främst ligga i dispatch/envelope, inte i olika agentpersonligheter
- Aktivering är explicit per worker/slice; att starta A startar inte automatiskt B
- Cloud workers får bara lita på repo-synliga inputs om inte workflow/dispatch uttryckligen provisionerar mer
- Daterade asymmetriska wave-roller (`primary`, `corroborative`, `fallback`) ska tolkas som pilot-routing, inte som global worker-SSOT

När du definierar eller adjudikerar en cloud-worker-slice, läs även:

- `workforce_roadmap.md`
- `docs/governance/worker_governance_envelope.md`

## Full Docs (load only when running gates)

- `docs/OPUS_46_GOVERNANCE.md` — 3-gate protocol
- `docs/governance_mode.md` — full mode resolution SSOT
- `AGENTS.md` — constitutional governance
- `.github/copilot-instructions.md` — operational contract
