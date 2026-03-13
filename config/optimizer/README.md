# Optimizer config layout

`config/optimizer/` är organiserad per timeframe först och per kampanj därefter.

## Struktur

- `1h/`
  - Enstaka eller små optimizer-specar för 1h.
- `3h/`
  - Enstaka 3h-specar.
  - `phased_v3/`
    - Faskonfigurationer (`phaseA`–`phaseE_oos`)
    - `best_trials/` för kampanjens spårade artifact-JSON
    - `PHASED_V3_RESULTS.md` för sammanställd evidens och resultat

## Regler för nya filer

- Lägg nya optimizer-YAML:er under rätt timeframe-katalog (`1h/`, `3h/`, framtida `6h/`, osv.).
- Om en timeframe får en flerfasig eller namngiven kampanj, skapa en egen kampanjmapp under timeframe-katalogen.
- Håll filnamn stabila när möjligt; flytta hellre in dem i rätt mapp än att döpa om allt i onödan.
- Lägg kampanjspecifika artifact-JSON i kampanjens egen `best_trials/`-katalog, inte löst i `config/optimizer/`.

## Viktig not om resume-signaturer

Optimizerns resume-signatur inkluderar repo-relativ config-sökväg. Om en YAML flyttas till en ny path kan äldre Optuna-studier som pekar på den gamla sökvägen inte antas vara resumabla utan uttrycklig hantering.
