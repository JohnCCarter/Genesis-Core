# Command Packet — engine-modul-split Slice 2

Datum: 2026-03-12
Branch: worktree-engine-modul-split
Base SHA: 45fef051 (slice 1 commit)

---

## Scope IN

- Extrahera `BacktestEngine._build_results()` (engine.py rad 1455–1540, 86 rader) till nytt modul `src/core/backtest/engine_result_builder.py`
- Uppdatera `engine.py`: ta bort `_build_results`, ersätt anropet på rad 1030 med `return build_results(self)`
- Fixa `tests/backtest/test_precompute_cache_key_versioning.py`: monkeypatch-target korrigeras från `engine_mod` till `cache_mod` (kvarleva från slice 1 som nu ger testfail)

## Scope OUT

- Inga beteendeändringar i backtest-loopen
- Inga ändringar i `_initialize_position_exit_context`, `_check_htf_exit_conditions`, `run()` utöver delegationsanropet
- Inga ändringar i `composable_engine.py`
- `build_results` läggs INTE till i `__init__.py`

## Done-kriterier

- `engine_result_builder.py` skapad med `build_results(engine)` — identisk logik med original `_build_results`
- `engine.py` delegerar via `return build_results(self)`
- Gates: black PASS, ruff PASS, bandit (projekts skip-lista) PASS, pytest tests/backtest/ PASS
- No behavior change

---

## Pre-code Review (Opus-dispatch, 2026-03-12)

**Utfall: APPROVE**

Granskning utfördes av Opus-subagent (se session-logg 2026-03-12). Sammanfattning:

1. **Cirkulärimport-risk**: Ingen — `TYPE_CHECKING`-guard är korrekt mönster, ingen runtime-import av `BacktestEngine`
2. **Behavior-change-risk**: Ingen — alla 9 direktattribut + 5 `getattr`-anrop verifierade komplett mot original
3. **Bandit B607-skydd**: Bevaras — `shutil.which`-mönstret är load-bearing och kopieras verbatim
4. **Föredragen engine.py-variant**: Direkt ersättning på rad 1030, ta bort `_build_results` helt (ingen tunn wrapper)
5. **Övrigt**: Inline-kommentarer (`# Convert to fraction`, `# Add top-level metrics`) ska bevaras — bekräftades

---

## Implementering

Ändrade filer:
- `src/core/backtest/engine.py` — `import subprocess` borttaget, `_build_results` borttaget (86 rader), `build_results` importerat och kallat
- `src/core/backtest/engine_result_builder.py` — ny fil, 97 rader
- `tests/backtest/test_precompute_cache_key_versioning.py` — monkeypatch-target: `engine_mod` → `cache_mod`

---

## Gate-resultat

| Gate | Resultat |
|------|---------|
| black | PASS — 2 filer oförändrade |
| ruff | PASS — 0 issues |
| bandit (projekts skip: B404,B603,B101,B311,B324) | PASS — 0 nya issues |
| pytest tests/backtest/ | **202 passed, 13 skipped** |

---

## Post-diff Audit (Opus-dispatch, 2026-03-12)

**Utfall: APPROVE (BLOCK hävt efter skapande av detta dokument)**

Opus-subagent bekräftade:
- Diff matchar plan — inga oväntade ändringar
- Verbatim-extraktion verifierad fält för fält
- `subprocess`-borttagning ur engine.py korrekt (0 kvarvarande referenser)
- Testfixen (cache_mod-patch) korrekt och i scope
- Gate-resultat godkända

Ursprunglig BLOCK-grund var avsaknad av detta dokument. Teknisk APPROVE var given.

---

## Residual risk

- Ingen identified — ren data-assembling utan sidoeffekter utom git subprocess (non-fatal)

## Nästa steg (Slice 3)

Extrahera `_check_traditional_exit_conditions` (engine.py ~rad 1403–1451, 48 rader) till `engine_exit_utils.py`.
