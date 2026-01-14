## Feature/Indicator Audit Runbook (Genesis-Core) 2026-01-14

Syfte: Detta dokument är en **metod/runbook** (inte en färdig analys) för att producera en **read-only, evidence-based** karta över:

- vilka indikatorer/features som **faktiskt** används,
- var Single Source of Truth (SSOT) för feature-beräkning ligger,
- var risk för drift/implicit fallback finns,
- och hur detta mappar till modell‑schema, scorer, Optuna objective och champion‑merge.

Detta är en repo-anpassad version (verifierade paths/flags) av det som tidigare låg i `tmp/Analys.md`.

## Non‑negotiables

- Gissa inte. Rapportera bara det som kan verifieras i kod/config.
- Ingen lookahead bias. Respektera strict AS‑OF semantik.
- Föredra explicit beteende framför implicit.
- Om kontext saknas: skriv det som **MISSING** och lista exakt vad som saknas.
- Inga beteendeförändringar här. Om ändringsförslag behövs: lista dem separat + föreslå tester.

## 0) Kör‑header (fyll i per felsökning)

- Symbol/timeframe:
- Run-id och/eller config-path:
- Datumintervall (snapshot_id eller sample_start/end):
- Canonical mode (förväntat):
  - GENESIS_FAST_WINDOW=1
  - GENESIS_PRECOMPUTE_FEATURES=1
  - GENESIS_MODE_EXPLICIT=0
- Hypotes (1 mening):

### Acceptanskriterier (”klart när”)

1. Alla features i modellens schema för det valda symbol/timeframe kan spåras till en producer i SSOT (fil/funktion).
2. Alla env flags som kan ändra feature/decision path är listade med sin effekt.
3. Eventuella fallbacks/slow-paths är verifierade i kod (och helst i logg/telemetri).

## 1) Repo‑paths att inspektera (verifierade i Genesis-Core)

Starta här (hot path):

- Feature SSOT: `src/core/strategy/features_asof.py`
  - `_extract_asof(...)` är dokumenterad som SSOT för feature calculation.
  - `extract_features(...)` orkestrerar precompute vs slow-path.
- Pipeline/env policy: `src/core/pipeline.py` (canonical 1/1 mode defaults)
- Orkestrering: `src/core/strategy/evaluate.py` (`evaluate_pipeline(...)`)
- Decision/gating: `src/core/strategy/decision.py`
- Champion merge/load: `src/core/strategy/champion_loader.py`
- Optuna runner/objective/backtest: `src/core/optimizer/runner.py`

Indikatorer (implementationer): `src/core/indicators/` (RSI/ATR/ADX/EMA/Bollinger/Fibonacci/HTF).

Modeller/schema:

- `config/models/` (modellfiler + schema/feature-list)
- `config/models/registry.json` (om tillämpligt)

## 2) Söktermer (grep) som brukar ge snabbast bevis

### Feature keys / schema

- `schema` / `features` / `feature_names` / `model` / `registry`

### Env flags som påverkar paths (verifierade i repo)

- `GENESIS_FAST_WINDOW`
- `GENESIS_PRECOMPUTE_FEATURES`
- `GENESIS_MODE_EXPLICIT`
- `GENESIS_FAST_HASH` (feature cache key i `features_asof.py`)
- `GENESIS_DISABLE_METRICS` (metrics i `evaluate.py`)
- `GENESIS_DISABLE_INDICATOR_CACHE` / `GENESIS_FEATURE_CACHE_SIZE` (cache i `features_asof.py`)

### Implicit fallback / slow path / cache

- `precomputed_features` / `use_precompute` / `slow` / `fallback`
- `_global_index` (backtest-mode; påverkar champion-merge i `evaluate_pipeline`)

## 3) Uppgift A: Identifiera SSOT för feature computation (AS‑OF)

### 3.1 SSOT‑definition

SSOT = den kod som producerar de feature keys som modellen faktiskt konsumerar, under strict AS‑OF.

### 3.2 Praktiskt arbetssätt

1. Läs `_extract_asof(...)` i `src/core/strategy/features_asof.py` och lista:

   - vilka feature keys den skriver (features‑dict)
   - vilka upstream indikatorer som används (t.ex. RSI/ATR/EMA/ADX/Bollinger/Fibonacci)
   - vilka inputkolumner som krävs (OHLCV)

2. Kartlägg precompute:
   - Hur `precomputed_features` injiceras (BacktestEngine/pipeline/runner)
   - Vilka keys som förväntas finnas i `precomputed_features`
   - Vad som händer när `GENESIS_PRECOMPUTE_FEATURES=1` men precompute saknas (varning vs fail)

Outputformat (tabell):

| feature_key | producer (fil:funktion) | inputs | indikatorer | notes |
| ----------- | ----------------------- | ------ | ----------- | ----- |

## 4) Uppgift B: Inventory av indikator‑implementationer

Hitta implementationsfiler under `src/core/indicators/` och bygg tabell:

| indikator | implementation (fil) | används av (feature keys / decision / exits) | dubblering? |
| --------- | -------------------- | -------------------------------------------- | ----------- |

Viktigt: Markera indikatorer som beräknas men aldrig används downstream (dead compute) – men skriv beviset (vem importerar, vem läser key).

## 5) Uppgift C: Overlap / risk (med bevis)

Flagga (om de finns) med konkret impact:

1. Dubbla beräkningar av samma indikator i flera paths
2. Precompute key mismatch vs runtime lookup key
3. Implicit fallback som gör Optuna trials icke‑jämförbara
4. Silent behavior change när precompute saknas

För varje risk: skriv “Evidence” (fil + funktion + relevant kodstycke) och “Impact” (vad kan bli fel: determinism, jämförbarhet, prestanda).

## 6) Mappa till modell/schema + scorer + Optuna + champion

### 6.1 Modell/schema

För `tBTCUSD_1h` (och ev. fler aktiva):

- Lista schema features (från `config/models/`)
- Markera features som SSOT kan producera men som inte ingår i schema

### 6.2 Orkestrering och determinism

Verifiera i `src/core/strategy/evaluate.py`:

- `_global_index` i configs => **explicit_backtest_config** (skip champion merge)
- annars: champion merge sker via `ChampionLoader` + deep merge

Verifiera i `src/core/pipeline.py`:

- canonical policy: om inte explicit_mode => fast_window=1 + precompute=1

Verifiera i `src/core/optimizer/runner.py`:

- optimizer tvingar canonical mode och failar om precompute saknas i canonical mode
- HTF exits togglas via `GENESIS_HTF_EXITS` när trial config begär det

### 6.3 Leverera kedjan (diagram)

Raw candles -> indicators -> features (SSOT) -> model(schema) -> proba -> confidence -> decision -> backtest metrics

## 7) Rekommendationer (utan kod)

Prioritera:

1. correctness/determinism
2. testability/traceability
3. performance (endast om safe)

## 8) (Optional) Förslag på guardrail

Föreslå (men implementera inte utan explicit önskemål):

- Ett litet test/script som assertar att alla schema feature names existerar i SSOT‑output.
- Ett test som failar om `GENESIS_PRECOMPUTE_FEATURES=1` och precompute saknas utan att det märks.

Not: Själva rapporten bör skrivas per run-id (t.ex. `reports/feature_audit/<run_id>.md`).
