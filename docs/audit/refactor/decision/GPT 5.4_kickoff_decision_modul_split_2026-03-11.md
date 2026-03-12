# GPT 5.4 Kickoff - feature/decision-modul-split

Datum: 2026-03-11
Dedikerad till: GPT 5.4 Code (VS Code extension)

## Syfte

Starta arbete med `feature/decision-modul-split` snabbt och effektivt utan att tumma på governance.
Målbild: små no-behavior-change slices med tydlig evidens och snabb feedback-loop.

## Måste läsas först (i denna ordning)

1. `.github/copilot-instructions.md`
2. `AGENTS.md`
3. `docs/governance_mode.md`
4. `docs/OPUS_46_GOVERNANCE.md`

## Arbetsgren och workingtree-policy

- Använd en dedikerad workingtree för `feature/decision-modul-split`.
- Basera workingtree på senaste `master` för att undvika branch-drift.
- Arbeta endast i decision-workingtree under denna uppgift.
- Rör inte andra aktiva feature-brancher i samma pass.

## Scope för decision-modul-split (startyta)

### Primära kodfiler

- `src/core/strategy/decision.py`
- `src/core/ml/decision_matrix.py`

### Primära tester

- `tests/utils/test_decision.py`
- `tests/utils/test_decision_edge.py`
- `tests/utils/test_decision_matrix.py`
- `tests/backtest/test_run_backtest_decision_rows.py`

## Governance-krav (obligatoriskt)

- Klassificera arbetet som high-sensitivity om `src/core/strategy/*` berörs.
- Kör full gated protocol för icke-triviala ändringar.
- Default constraint: **NO BEHAVIOR CHANGE**.
- Opus pre-code review krävs innan implementation.
- Opus post-diff audit krävs innan READY_FOR_REVIEW.

## Arbetsmodell: smart + snabb + säker

1. Skapa commit-contract med Scope IN/OUT och tydliga done-kriterier.
2. Bygg context-map för beroenden/importer/testselectors.
3. Implementera en minimal slice i taget (1 ansvar, liten diff).
4. Kör gates direkt efter varje slice.
5. Dokumentera resultat kort men komplett.
6. Repetera nästa slice.

### Rekommenderad slice-storlek

- 45-90 minuter per slice.
- Högst 3-8 filer per slice.
- Undvik opportunistisk städning utanför Scope IN.

## Gate-minimum per decision-slice

- pre-commit/lint
- relevant import/smoke selector
- determinism replay selector
- feature cache invariance selector
- pipeline invariant selector
- focused decision-selectors för berörd logik

## Stop conditions

Stoppa direkt och eskalera om något av följande inträffar:

- Scope drift utanför Scope IN
- Oavsiktlig behavior/API-förändring
- Beröring av config-authority/freeze paths utan explicit godkännande
- Gate-fail med oklar root cause

## Krav för READY_FOR_REVIEW

Följande måste vara dokumenterat i evidens:

- mode/risk/path (med källa)
- Scope IN/OUT
- exakta gates + PASS/FAIL
- relevanta selectors/artifacts
- residual risk och nästa steg

## Kickoff-brief till GPT 5.4 (copy/paste)

Arbeta i dedikerad workingtree för `feature/decision-modul-split` baserad på senaste `master`.
Läs styrfiler i denna ordning: `.github/copilot-instructions.md`, `AGENTS.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md`.
Skapa commit-contract + context-map före kod.
No behavior change är default.
Kör Opus pre-code review, implementera minimal slice, kör gates, kör Opus post-diff audit.
Rapportera endast evidensdrivna resultat med scope, gates och risker.
