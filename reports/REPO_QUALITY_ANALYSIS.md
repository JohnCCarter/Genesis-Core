# Genesis-Core: Fullständig Repoanalys & Refaktoreringsplan

**Datum:** 2026-02-14
**Syfte:** Ärlig genomlysning av hela repot, med fokus på var tid faktiskt läggs vs. var den borde läggas.

---

## 1. Viktkarta — Var ligger koden?

| Område | Rader (Python) | Andel | Kommentar |
|--------|---------------:|------:|-----------|
| `scripts/` | 42 874 | 35% | **Största kodbasen.** Mest engångsskript |
| `src/core/` | 24 548 | 20% | Produktionskoden |
| `tests/` | 20 578 | 17% | Testsviten |
| `config/` | 22 649 | 18% | Mest Optuna YAML-konfigar (20+ st) |
| `docs/` | 44 283 | — | Markdown, ej Python |
| `mcp_server/` | 2 865 | 2% | MCP-integration |
| `registry/` | 411 | <1% | Governance-scheman |
| `.github/` | 1 590 | 1% | Agents + Skills + CI |

**Observation:** `scripts/` är nästan dubbelt så stor som `src/core/`. Majoriteten av utvecklingstiden har gått till verktyg, analys och infrastruktur — inte till kärnstrategin.

---

## 2. Kärnstrategi — Tillståndsrapport

### 2.1 decision.py — 1 200 rader, CC ~45

**Diagnos: God Function-antimönster.**

`decide()` är en enda funktion på ~1 091 rader med:
- 146 branch points (106 if, 10 elif, 14 else, 11 try)
- HTF Fibonacci-gating: ~180 rader nestade villkor
- LTF Fibonacci-gating: ~130 rader som duplicerar HTF-logiken (~95% identisk)
- 11 parametrar (3 av dem dicts med 10+ nycklar vardera)
- Blandar ingångsbeslut, tillståndhantering (hysteresis/cooldown), sizing, loggning

**Konsekvens:** Extremt svår att testa isolerat, debugga eller utöka med nya gates.

### 2.2 features_asof.py — 1 022 rader, CC ~35

**Diagnos: Multipla ansvarsområden + 3-nivå cache.**

- `_extract_asof()` hanterar: indikatorberäkning, cache-lookup (3 nivåer), Fibonacci-features, HTF/LTF-kontext
- 8+ upprepade fast/slow-path-mönster (precomputed → indicator_cache → compute_fresh)
- Globalt muterbart state (OrderedDict, räknare)
- Fibonacci-kontextassembly (~90 rader) hör hemma i beslutlagret, inte feature-lagret

### 2.3 evaluate.py — 488 rader, CC ~12

**Diagnos: Acceptabel men underutnyttjad.**

Bra orkestreringslogik. Men pipelinen är hårdkodad — trots att en komponentarkitektur finns under `strategy/components/`.

### 2.4 Komponentarkitekturen — Finns, men används inte

`strategy/components/` innehåller:
- `base.py` — Rent ABC-interface (ComponentResult, immutable)
- `strategy.py` — ComposableStrategy med first-veto-princip
- `context_builder.py` — Mapping pipeline → komponenter
- `htf_gate.py` — Regim-gate
- `attribution.py` — Statistikspårning

**Problem:** `evaluate_pipeline()` anropar aldrig `ComposableStrategy`. Komponenterna existerar men är inte inkopplade i huvudflödet. decide()-funktionen gör allt manuellt.

### 2.5 Dödkod i strategy/

| Fil | Rader | Status |
|-----|------:|--------|
| `regime.py` | 184 | **DÖD** — ersatt av `regime_unified.py` |
| `features.py` | 41 | **ÖVERGIVEN** — deprecated wrapper |
| `example.py` | 12 | **ÖVERGIVEN** — demo |
| `ema_cross.py` | 31 | **ÖVERGIVEN** — demo |
| `e2e.py` | 36 | **ÖVERGIVEN** — smoke test utanför pytest |

---

## 3. ML-pipeline — Tillståndsrapport

### 3.1 Bedömning: Väldesignad, aktivt använd

| Modul | Rader | Använd? | Kvalitet |
|-------|------:|---------|----------|
| `evaluation.py` | 527 | Ja (scripts) | Utmärkt |
| `labeling.py` | 462 | Ja (training) | Utmärkt |
| `labeling_fast.py` | 206 | Ja (Numba-opt) | Bra |
| `label_cache.py` | 183 | Ja (caching) | Bra |
| `calibration.py` | 292 | Delvis | Isotonic broken |
| `decision_matrix.py` | 288 | Ja (champion) | Utmärkt |
| `visualization.py` | 373 | Ja (rapporter) | Bra |
| `overfit_detection.py` | 68 | Nej | Bra men oanvänd |

**Slutsats:** ML-pipelinen är lean och funktionell. Inga stora förändringar behövs. Kalibreringsmodulen har en bugg (isotonic kan inte laddas från disk).

### 3.2 Integration med live-strategi

Modeller tränas → sparas som JSON → laddas av `ModelRegistry` → `predict_proba_for()` → används i `decision.py`. **Kedjan fungerar.**

---

## 4. Infrastruktur & Overhead

### 4.1 Governance/Registry — 240 + 411 rader

**Runtime-påverkan: NOLL.** Gating sker bara i CI (`validate_registry.py`). Inget i `src/core/` importerar governance. Om ingen kör `run_skill.py`, är det dödkod.

### 4.2 MCP Server — 2 865 rader

**Runtime-påverkan: NOLL.** Helt frikopplad från `src/core/`. Optional dependency `[mcp]`. Värdefull om AI-assisterad utveckling, annars overhead.

### 4.3 Agents & Skills — 1 590 rader

4 boundade agents, 17+ skills (JSON-scheman). **Framework, inte runtime-kod.** Underhållskostnad finns om de inte faktiskt används.

### 4.4 Scripts — 42 874 rader (!)

**Det verkliga problemet.** Uppskattning:

| Kategori | Rader | Antal filer |
|----------|------:|------------:|
| Aktivt använda (CI, backtest, optimizer) | ~3 500 | ~8 |
| Engångsanalys (analyze_*, debug_*, compare_*) | ~25 000 | ~40 |
| Arkiverade | ~14 000 | ~20 |

**~85% av scripts/ körs aldrig i CI och importeras inte av tester.** De representerar ackumulerade utforskningar och felsökningssessioner.

### 4.5 Config — 22 649 rader

20+ Optuna YAML-konfigurationer för tBTCUSD 1h och 3h. Varje konfiguration ~250-325 rader. Många varianter av samma search space med marginella skillnader.

### 4.6 Docs — 44 283 rader

Omfattande dokumentation men stora delar refererar till passerade faser (phase3, phase6) eller arkiverade sessioner.

---

## 5. Tester — Tillståndsrapport

### 5.1 Övergripande

- **863 testfunktioner** i 165 filer
- Test/kod-ratio: 0.84 (bra)
- 84% av moduler har tester

### 5.2 Problem

| Problem | Omfattning |
|---------|-----------|
| Integration-test som heter unit-test | ~52 filer (32%) |
| Performance-test med brittla timing-assertions | 5 filer, 760 rader |
| Governance/infra-tester med lågt ROI | ~10 filer, 500 rader |
| Implementationsdetaljtest (tripwires) | ~40 tester |
| Alla 165 filer i root-katalogen | Svårnavigerat |
| `test_paper_trading_runner.py` | 19 963 rader (!!) |

### 5.3 Otestade kritiska moduler

- `utils/crypto.py` — Kryptografisk signering, INGA tester
- `utils/data_loader.py` — Dataladdning, INGA tester
- `utils/optuna_helpers.py` — Optuna-config, INGA tester
- `utils/provenance.py` — Metadata, INGA tester

---

## 6. Beroendeanalys

### 6.1 Positivt

- **Inga cirkulära beroenden** — rent acykliskt
- Governance importeras INTE av produktionskoden
- MCP är helt frikopplad
- Server.py har bara 6 core-imports (tunn adapter)

### 6.2 Kritisk stig

```
server.py / pipeline.py
  └─► backtest/engine.py (1 572 rader)
       └─► strategy/evaluate.py (488 rader)
            ├─► strategy/features_asof.py (1 022 rader)
            │    └─► indicators/* (alla)
            ├─► strategy/decision.py (1 200 rader)
            ├─► ml/prob_model.py
            └─► strategy/confidence.py + regime_unified.py
```

### 6.3 Borttagbara utan att bryta pipelinen

| Modul | Rader | Beroenden |
|-------|------:|-----------|
| `governance/` | 240 | Inga i core |
| `mcp_server/` | 2 865 | Inga i core |
| `ml/visualization.py` | 373 | Bara scripts |
| `ml/decision_matrix.py` | 288 | Bara scripts |
| `ml/overfit_detection.py` | 68 | Bara tester |

---

## 7. Sammanfattande diagnos

### Styrkor
- Ren beroendestruktur (acyklisk, lager-separerad)
- ML-pipeline är lean och funktionell
- Bra testbredd (84% modultäckning)
- Deterministisk backtesting-arkitektur
- Solid config-validering (Pydantic + SSOT)

### Svagheter
- **decision.py är en 1 200-raders god function** — projektets största tekniska skuld
- **features_asof.py** blandar feature-extraction med caching och kontextassembly
- **Komponentarkitekturen finns men är inte inkopplad** i huvudpipelinen
- **scripts/ är 35% av all Python-kod** och mestadels engångsanalys
- **Config-explosion:** 20+ Optuna YAML-varianter med marginella skillnader
- **Dokumentationen** refererar till passerade faser och har ackumulerats utan rensning

---

## 8. Refaktoreringsplan — Prioriterad

### Fas 0: Rensning (1-2 dagar, noll risk)

**Mål: Ta bort brus, minska mental belastning.**

1. **Ta bort dödkod i strategy/**
   - Radera: `regime.py`, `features.py`, `example.py`, `ema_cross.py`, `e2e.py` (~304 rader)

2. **Arkivera engångsskript**
   - Flytta ~40 skript till `scripts/archive/` (~25 000 rader)
   - Behåll: `run_backtest.py`, `optimizer.py`, `preflight_optuna_check.py`, `validate_optimizer_config.py`, `train_model.py`, `select_champion.py`, `fetch_historical.py`, `paper_trading_runner.py`

3. **Konsolidera Optuna-konfigar**
   - Arkivera gamla YAML-varianter (keep senaste per symbol/timeframe)
   - Flytta till `config/optimizer/archive/`

4. **Rensa docs/**
   - Flytta passerade faser till `docs/archive/`
   - Behåll aktiva referensdokument

**Resultat:** ~30 000 rader mindre att underhålla. Ingen kodbytning.

### Fas 1: Bryt upp decision.py (3-5 dagar, medium risk)

**Mål: Gå från 1 200-raders god function till komponenter.**

1. **Extrahera FibonacciGate**
   - HTF + LTF gating → en komponent med `side` parameter
   - Eliminerar ~300 rader duplicerad kod

2. **Extrahera SizingCalculator**
   - Position sizing med 4 multiplikatorer → egen modul
   - ~150 rader extraherade

3. **Extrahera ProbabilityGate**
   - EV-filter + sannolikhetströsklar → komponent
   - ~100 rader

4. **Extrahera HysteresisGate + CooldownGate**
   - Tillståndshantering → egna komponenter
   - ~80 rader vardera

5. **Koppla in komponentarkitekturen**
   - Uppdatera `evaluate_pipeline()` att använda `ComposableStrategy`
   - Varje gate blir testbar isolerat
   - Attribution tracking "gratis"

**Resultat:** `decide()` reduceras från 1 091 → ~300 rader orkestrering. Varje komponent testbar.

### Fas 2: Rensa features_asof.py (2-3 dagar, medium risk)

**Mål: Separera ansvarsområden.**

1. **Extrahera IndicatorComputer-klass**
   - Fast/slow-path-mönstret abstraheras en gång
   - Ersätter 8 upprepade versioner

2. **Flytta Fibonacci-kontext till egen modul**
   - HTF/LTF-kontextassembly hör till beslutlagret
   - ~90 rader ut ur feature-extraction

3. **Ersätt globalt cache-state med klass**
   - `FeatureCache` med konfigurbar storlek
   - Trådsäkert (om multi-threading)
   - Inget globalt muterbart state

**Resultat:** features_asof.py reduceras från 1 022 → ~450 rader. Cache-logik testbar.

### Fas 3: Test-konsolidering (2-3 dagar, låg risk)

**Mål: Snabbare, mer fokuserade tester.**

1. **Strukturera om tests/**
   - Skapa `tests/unit/`, `tests/integration/`, `tests/regression/`
   - Spegla `src/core/`-strukturen

2. **Bryt upp `test_paper_trading_runner.py`**
   - 19 963 rader → 3-4 filer

3. **Ta bort brittla performance-tester**
   - Ersätt med relativa jämförelser

4. **Lägg till tester för otestade utils**
   - `crypto.py`, `data_loader.py`, `optuna_helpers.py`, `provenance.py`

### Fas 4: Infrastruktur-beslut (1 dag, diskussion)

**Beslut som behöver tas:**

| Fråga | Om JA | Om NEJ |
|-------|-------|--------|
| Använder ni MCP-servern aktivt? | Behåll, underhåll | Ta bort `mcp_server/` |
| Kör ni `run_skill.py`? | Behåll governance | Ta bort `governance/`, agents, skills |
| Behövs isotonic calibration? | Fixa serialisering | Ta bort metoden ur `calibration.py` |
| Behövs `overfit_detection.py`? | Integrera i pipeline | Markera som experimental |

---

## 9. Förväntad effekt

| Mätpunkt | Före | Efter (Fas 0-3) |
|----------|------|------------------|
| `scripts/` Python-rader | 42 874 | ~8 000 |
| `decision.py` rader | 1 200 | ~300 |
| `features_asof.py` rader | 1 022 | ~450 |
| Dödkod i strategy/ | 304 rader | 0 |
| Config YAML-filer | 20+ | ~5 aktiva |
| Testfiler i root | 165 | Organiserade i underkataloger |
| Komponentarkitektur | Existerar, oanvänd | Inkopplad, aktiv |

**Totaleffekt:** ~40 000 rader mindre att underhålla. Kärnstrategin blir modulär och testbar. Nya gates kan läggas till som komponenter utan att röra `decide()`.

---

## 10. Rekommenderad ordning

```
Fas 0: Rensning           ▓▓░░░░░░░░  (1-2 dagar, noll risk)
Fas 1: decision.py        ░░▓▓▓▓░░░░  (3-5 dagar, kräver tester först)
Fas 2: features_asof.py   ░░░░░░▓▓░░  (2-3 dagar, efter Fas 1)
Fas 3: Test-konsolidering ░░░░░░░░▓▓  (2-3 dagar, parallellt med Fas 2)
Fas 4: Infrastruktur      ░░░░░░░░░▓  (1 dag beslut)
```

**Totalt: 9-14 arbetsdagar** för fullständig transformation.

Fas 0 kan göras omedelbart utan risk. Fas 1 är den viktigaste — den löser den största tekniska skulden och möjliggör framtida strategiutveckling.
