# AGENTS History (Archive)

## Last update: 2026-02-14

Detta dokument innehåller historiska leverabler och handoff-noteringar som tidigare låg i `AGENTS.md`.

Aktiv driftguide finns nu i:

- `AGENTS.md`

Kanonisk regelordning finns i:

- `.github/copilot-instructions.md`
- `docs/OPUS_46_GOVERNANCE.md`

## Sammanfattad historik (utdrag)

### 2025-12-26

- HTF FIB context integrity + invalid swing hardening + Optuna smoke safety.
- Strikt AS-OF/no-lookahead i HTF-context.
- Schema-/bounds-hardening och consumer-förstärkningar för HTF-exit.

### 2025-12-25

- Quality v2 scoped (gate vs sizing), exit-stabilitet och A/B-runbook.
- Paper canary-operationalisering.

### 2025-12-18

- Explore→Validate Optuna recovery + promotion safety.
- Canonical mode policy (1/1) dokumenterad och QA-grön.

### 2025-12-17

- Churn-smoke + long-window validation.
- Champion path fix och backcompat-hardening.

### 2025-12-16

- Config-equivalence proof + backtest correctness.
- Drift-check CLI och förbättrad reproducerbarhet i artifacts.

### 2025-12-15

- Optuna hardening + cost-aware scoring.
- Churn/fee-constraints och champion-format normalisering.

### 2025-12-11

- Stabilization plan slutförd (determinism, frozen data, pipeline-unifiering).

### 2025-11

- Mode enforcement (canonical fast/precompute som default för jämförbarhet).
- Reproducerbarhetsfixar och omfattande Optuna-/backtest-förbättringar.
- Flera bugfixar i ATR, reporting, max-hold och parameterexpansion.

## Notering om full historik

Detaljerad, fullständig historik finns i Git-historiken för tidigare versioner av `AGENTS.md`.

Denna arkivfil är avsedd som snabb orientering, inte komplett forensisk logg.
