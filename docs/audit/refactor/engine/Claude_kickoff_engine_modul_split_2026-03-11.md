# Claude Kickoff - feature/engine-modul-split

Datum: 2026-03-11
Dedikerad till: Claude Code

## Syfte

Starta arbete med `feature/engine-modul-split` snabbt och effektivt utan att tumma på governance.
Målbild: små no-behavior-change slices med tydlig evidens, snabb feedback-loop och ren handoff till nästa agent.

## Måste läsas först (i denna ordning)

1. `.github/copilot-instructions.md`
2. `AGENTS.md`
3. `docs/governance_mode.md`
4. `docs/OPUS_46_GOVERNANCE.md`

## Arbetsgren och workingtree-policy

- Använd en dedikerad workingtree för `feature/engine-modul-split`.
- Basera workingtree på senaste `master` för att undvika branch-drift.
- Arbeta endast i engine-workingtree under denna uppgift.
- Rör inte andra aktiva feature-brancher i samma pass.

## Scope för engine-modul-split (startyta)

### Primära kodfiler

- `src/core/backtest/engine.py`
- `src/core/backtest/composable_engine.py`
- `src/core/pipeline.py`

### Viktiga beroenden att kartlägga före första slice

- `src/core/backtest/__init__.py`
- `src/core/backtest/htf_exit_engine.py`
- `src/core/strategy/htf_exit_engine.py`
- `src/core/config/merge_policy.py`
- `src/core/strategy/evaluate.py`

### Primära tester

- `tests/backtest/test_backtest_engine.py`
- `tests/backtest/test_composable_backtest_engine.py`
- `tests/backtest/test_backtest_engine_hook.py`
- `tests/integration/test_new_htf_exit_engine_adapter.py`
- `tests/backtest/test_htf_exit_engine.py`
- `tests/backtest/test_htf_exit_engine_selection.py`
- `tests/backtest/test_htf_exit_engine_htf_context_schema.py`

## Governance-krav (obligatoriskt)

- Klassificera arbetet som high-sensitivity om `src/core/backtest/*` eller andra känsliga runtime-paths berörs.
- Kör full gated protocol för icke-triviala ändringar.
- Default constraint: **NO BEHAVIOR CHANGE**.
- Opus pre-code review krävs innan implementation.
- Opus post-diff audit krävs innan READY_FOR_REVIEW.
- Bevara publik och observerbar runtime-semantik om inte explicit undantag godkänts.

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

### Lämpliga första slice-kandidater

- liten intern helper-extraktion i `engine.py` utan ändrad runtime-semantik
- isolering av ren metadata-/resultatbyggande logik
- ren wrapper-/adapterstädning mellan `ComposableBacktestEngine` och `BacktestEngine`

Undvik som första slice:

- bred omstrukturering av backtest-loopen
- ändringar i env/config-authority
- semantiska ändringar i HTF-exit-val eller precompute-policy

## Gate-minimum per engine-slice

- pre-commit/lint
- relevant import/smoke selector
- determinism replay selector
- feature cache invariance selector
- pipeline invariant selector
- focused engine-selectors för berörd logik

## Stop conditions

Stoppa direkt och eskalera om något av följande inträffar:

- Scope drift utanför Scope IN
- Oavsiktlig behavior/API-förändring
- Beröring av config-authority/freeze paths utan explicit godkännande
- Gate-fail med oklar root cause
- Blandning av engine-refactor och annan sidostädning i samma slice

## Krav för READY_FOR_REVIEW

Följande måste vara dokumenterat i evidens:

- mode/risk/path (med källa)
- Scope IN/OUT
- exakta gates + PASS/FAIL
- relevanta selectors/artifacts
- residual risk och nästa steg

## Vad som ska delas i handoff till nästa agent

Följande ska alltid delas vidare, även om arbetet bara nått halva slicen:

1. workingtree/branch och faktisk git-branch från terminalen
2. base SHA och senaste lokala commit-SHA
3. exakt Scope IN/OUT för aktiv slice
4. ändrade filer och kort varför varje fil ändrats
5. exakta gates som körts, med selectors och PASS/FAIL
6. eventuella artifacts/loggar/dokument som skapats
7. kvarvarande blockerare, risker eller öppna frågor
8. out-of-scope filer i working tree som inte får följa med commit
9. nästa minsta rekommenderade slice
10. om någon observerbar semantik kan ha påverkats: exakt var och hur det verifierades

### Minsta handoff-paket

- branch/worktree
- base SHA + senaste commit
- Scope IN/OUT
- ändrade filer
- gates + resultat
- blockerare / nästa steg

## Kort checklista mellan Claude och GPT 5.4

Om arbetet ska lämnas vidare mellan agenter räcker följande mikrolista:

- vilken slice som är aktiv nu
- vad som redan är grönt
- vad som absolut inte får röras
- vilka filer som är out-of-scope i working tree
- vilken minsta nästa säkra diff är

## Kickoff-brief till Claude Code (copy/paste)

Arbeta i dedikerad workingtree för `feature/engine-modul-split` baserad på senaste `master`.
Läs styrfiler i denna ordning: `.github/copilot-instructions.md`, `AGENTS.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md`.
Skapa commit-contract + context-map före kod.
No behavior change är default.
Kör Opus pre-code review, implementera minimal slice, kör gates, kör Opus post-diff audit.
Rapportera endast evidensdrivna resultat med scope, gates, risker och tydlig handoff-info till nästa agent.
