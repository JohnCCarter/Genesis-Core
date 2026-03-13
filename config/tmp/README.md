# `config/tmp/`

Den här katalogen är en liten stagingyta för tillfälliga eller ännu oplacerade
konfigurationsartefakter. Innehållet här är **inte authority** för pipeline,
backtest eller champion-laddning.

## Nuvarande innehåll

- `trial_004_breakthrough.json`
  - En sparad experiment-/kandidatartifact med en fristående config payload.
  - Behålls här tills den antingen kasseras, arkiveras eller flyttas till en
    mer permanent plats.

- `quality_v2_variants/`
  - Kandidatvarianter för `tBTCUSD` 1h med olika quality-v2-upplägg.
  - Används som experimentyta för A/B-jämförelser innan eventuell promotion.

## Regler för den här katalogen

- Lägg bara filer här om de är tydligt temporära, experimentella eller väntar på
  bättre placering.
- Om en fil blir en riktig kandidat eller långlivad referens, flytta den till
  `config/strategy/` eller `config/optimizer/`.
- Behåll inte gamla mellanresultat eller stegvisa tuning-snapshots här längre än
  nödvändigt.
- Uppdatera den här README:n när innehållet i katalogen förändras, så att den
  beskriver verkligheten och inte ett arkeologiskt lager.
