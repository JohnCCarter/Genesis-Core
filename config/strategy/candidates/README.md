# Candidate config bank

`config/strategy/candidates/` är den körbara kandidatbanken för strategi-configs som är värda att kunna återköra exakt.

## Syfte

Lägg filer här när configen är tillräckligt viktig för att:

- bevaras som en explicit kandidat
- kunna köras igen via backtest eller annan styrd research-körning
- jämföras mot baseline eller annan kandidat utan att bli champion-authority

Den här ytan är **config-only**.

Den är inte hemvist för:

- backtest-resultat
- execution summaries
- jämförelsedokument
- tillfälliga analysartefakter

Det betyder i praktiken:

- configs stannar här
- körresultat hör hemma i `results/`
- tolkning och styrda beslut hör hemma i `docs/governance/`

## Struktur

Kandidater organiseras först per timeframe:

- `candidates/1h/`
- `candidates/3h/`

Skapa inte nya timeframe-mappar spekulativt.
En ny timeframe-mapp ska motiveras av minst en faktisk kandidatfil.

## Namngivningskonvention för nya filer

Använd följande format för **nya** kandidatfiler:

`<symbol>_<timeframe>_<subject>_<role>_<theme>_<yyyymmdd>.json`

### Fält

- `symbol`
  - till exempel `tBTCUSD`
- `timeframe`
  - till exempel `1h`, `3h`
- `subject`
  - den stabila ankaren för ytan eller experimentet, till exempel `slice8`, `runtime`, `ri`
- `role`
  - en av:
    - `baseline`
    - `candidate`
    - `experimental`
    - `snapshot`
- `theme`
  - kort slug för vad som skiljer configen från närliggande filer, till exempel:
    - `runtime_bridge`
    - `defensive_transition`
    - `high_freq`
    - `cooldown_gate`
- `yyyymmdd`
  - frys- eller skapandedatum

## Exempel på bra namn

- `tBTCUSD_3h_slice8_baseline_runtime_bridge_20260326.json`
- `tBTCUSD_3h_slice8_candidate_defensive_transition_20260423.json`
- `tBTCUSD_3h_slice8_experimental_cooldown_gate_20260423.json`
- `tBTCUSD_1h_runtime_candidate_high_freq_20260423.json`

## Regler

- En kandidatfil ska beskriva **en tydlig idé** eller variant, inte flera samtidigt.
- Lägg inte in resultat i filnamnet, till exempel inte `score_042`, `pf_227` eller `wr_58`.
- Om en fil är värd att återköra men ännu inte champion-authority, hör den normalt hemma här.
- Om en fil bara är ett mellanled i analys eller ett engångsartefakt, hör den normalt inte hemma här.

## Nuvarande packet-förankrade filer

Redan citerade kandidatfiler får ligga kvar med sina nuvarande namn tills en separat cleanup-slice uttryckligen tar hand om namnbyte eller flytt.

Det här undviker onödig referensdrift i governance-packets och execution summaries.

Exempel på sådana nuvarande filer:

- `3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`

Nya filer bör däremot följa konventionen ovan.
