# RI vs legacy — slice 3 structural survival / override map

Datum: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: arbetsdokument / analysunderlag / ingen runtime-ändring

## Syfte

Detta dokument fortsätter RI-vs-legacy-rollkartan med fokus på **slice 3: structural survival / override**.

Målet är att svara på en av handoffens kärnfrågor:

> När beter sig HTF/LTF-veto + adaptive override som legitim permission/survival-policy, och när börjar det i praktiken fungera som dold entrymotor?

Analysen är kodförankrad i:

- `src/core/strategy/decision.py`
- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_fib_gating_helpers.py`
- `tests/utils/test_decision_fib_gating_contract.py`
- `config/strategy/champions/tBTCUSD_3h.json`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml`

## Call-order och varför den spelar roll

`src/core/strategy/decision.py` visar att slice 3 ligger **mellan** kandidatval och post-fib-cadence:

1. `select_candidate(...)`
2. `apply_fib_gating(...)`
3. `apply_post_fib_gates(...)`
4. `apply_sizing(...)`

Det betyder att fib-gating inte skapar en kandidat från tomma intet.

Men det betyder också att fib-lagret kan avgöra om en redan vald kandidat:

- stoppas helt,
- släpps igenom,
- eller **räddas** via override innan cadence och sizing ens får säga sitt.

Det är just override-räddningen som gör denna yta strategiskt känslig.

## Huvuddom för slice 3

Den mest robusta läsningen just nu är:

> HTF/LTF-fiblagret är i grunden ett **permission/survival-lager**. Det blir först entry-drivande när override-vägarna gör strukturellt blockerade kandidater systematiskt tradebara igen.

Med andra ord:

- **utan override** är detta främst ett veto-/filterlager
- **med aggressiv override** blir det lätt en dold entrymotor

## Arbetsmatris — structural survival / override

| Yta                                        | Primär tänkt roll                  | Faktisk observerad roll i koden                                                                                             | Entry-påverkan | Filtering | Management | Bedömning                                       |
| ------------------------------------------ | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | -------------- | --------- | ---------- | ----------------------------------------------- |
| `multi_timeframe.use_htf_block`            | slå på/av HTF-veto                 | avgör om HTF-gaten ens körs; defaultar till `True` i `decision.py` om värdet saknas                                         | indirekt       | hög       | låg        | tydlig permission-flagga                        |
| `htf_fib.entry.*`                          | strukturell HTF-permission         | kan blockera på `CONTEXT_ERROR`, `UNAVAILABLE`, `NO_PRICE`, off-target eller nivåbrott; kan även passera via `TARGET_MATCH` | indirekt       | hög       | låg        | legitim survival-policy                         |
| `multi_timeframe.allow_ltf_override`       | tillåt confidence-baserad räddning | öppnar override-vägen för HTF-blockade kandidater                                                                           | hög när aktiv  | medel     | låg        | första tydliga entry-riskytan                   |
| `multi_timeframe.ltf_override_threshold`   | minsta confidence för räddning     | används i `_try_multi_timeframe_threshold_override(...)` för att konvertera HTF-block till pass                             | hög            | medel     | låg        | låg threshold gör lagret entry-drivande         |
| `multi_timeframe.ltf_override_adaptive`    | adaptiv override-tröskel           | bygger historik per riktning och kan sänka/höja effektiv tröskel via percentilregim                                         | hög            | medel     | låg        | stark dold-entry-risk om den blir för permissiv |
| `ltf_fib.entry.override_confidence`        | smal override-range                | separat override-path när multi-timeframe-threshold override inte används                                                   | hög            | medel     | låg        | explicit backdoor runt HTF-veto                 |
| `ltf_fib.entry.*`                          | lokal strukturell entry-kontroll   | blockerar efter HTF-pass om priset ligger fel mot LTF-nivåerna                                                              | indirekt       | hög       | låg        | legitim lokal filteryta                         |
| `gates.hysteresis_steps` / `cooldown_bars` | cadence/stabilisering              | ligger efter fib-lagret och påverkar persistence/timing, inte HTF/LTF-struktur direkt                                       | indirekt       | medel     | låg        | inte slice 3-kärnan                             |

## Kodförankrade observationer

### 1. HTF-veto är ett riktigt veto, inte kosmetika

`apply_htf_fib_gate(...)` kan returnera `_none_result(...)` tidigt på flera vägar:

- `HTF_FIB_CONTEXT_ERROR`
- `HTF_FIB_UNAVAILABLE`
- `HTF_FIB_NO_PRICE`
- `HTF_FIB_LONG_BLOCK`
- `HTF_FIB_SHORT_BLOCK`

Detta är alltså inte bara debug eller scoring-metadata. HTF-lagret kan stoppa kandidaten innan post-fib gates och sizing körs.

### 2. Override-vägen är den strategiska känsligheten

Det som ändrar rollkaraktären är inte själva HTF-vetot, utan att `try_override_htf_block(...)` kan omvandla ett block till pass via:

- `_try_multi_timeframe_threshold_override(...)`
- `_try_ltf_entry_range_override(...)`

Detta markeras uttryckligt i reasons som:

- `HTF_OVERRIDE_LTF_CONF`

Så snart denna väg börjar användas ofta är vi inte längre i ett rent survival-lager. Då räddar fib-lagret kandidater som annars skulle ha dött.

### 3. Sparse config är inte semantiskt neutral här

I `decision.py` gäller:

- `use_htf_block` defaultar till `True`
- `allow_ltf_override` defaultar däremot via `bool(mtf_cfg.get("allow_ltf_override"))`, vilket blir `False` om fältet saknas

Det innebär att en gles optimizer-YAML som bara sätter `multi_timeframe.ltf_override_threshold` **inte** i sig bevisar att override är aktiv. Den verkliga override-posturen beror på vad som kommer in via merged config/defaults uppströms.

Detta är en viktig slice 3-regel framåt:

> Läs inte override-semantiken från enstaka leafs i YAML. Läs den från den **faktiskt mergeresolverade configen** som når `decide(...)`.

## Config-resolution — vad sparse YAML faktiskt blir

För optimizer-spår är mergekedjan nu tillräckligt tydlig för en arbetsdom:

1. `runner_config._get_default_config()` laddar default config via `ConfigAuthority`
2. `transform_parameters(...)` expanderar dotted leafs som `multi_timeframe.ltf_override_threshold`
3. `_deep_merge(default_cfg, transformed_params)` bygger den slutliga trial-configen
4. den mergeresolverade configen skrivs sedan ut som både `cfg` och `merged_config`

Praktiskt betyder det att sparse optimizer-parametrar **inte** ersätter hela `multi_timeframe`- eller fib-subträdet. De läggs ovanpå default-configen.

### Viktig default-postur från runtime

`config/runtime.json` visar att default-surface redan innehåller:

- `multi_timeframe.use_htf_block = true`
- `multi_timeframe.allow_ltf_override = true`
- `multi_timeframe.ltf_override_threshold = 0.85`
- `multi_timeframe.ltf_override_adaptive.enabled = true`

Det betyder att en sparse RI-YAML som bara sätter t.ex.:

- `multi_timeframe.ltf_override_threshold = 0.38`
- `htf_fib.entry.*`
- `ltf_fib.entry.*`

med hög sannolikhet resulterar i en mergeresolverad config där:

- HTF-veto fortfarande är på
- LTF override fortfarande är tillåten
- override-threshold är sänkt från `0.85` till research-värdet
- adaptive override fortfarande kan vara aktiv om inte den explicit stängs av uppströms

Detta skärper slice 3-frågan ytterligare:

> En låg `ltf_override_threshold` i RI är sannolikt inte en isolerad leaf-ändring. I mergeresolverad form är den troligen en **sänkning av en redan aktiv override-mekanism**.

## Legacy vs RI — vad som syns redan nu

### Legacy 3h champion

`config/strategy/champions/tBTCUSD_3h.json` visar en relativt tydlig legacy-postur:

- `use_htf_block: true`
- `allow_ltf_override: true`
- `ltf_override_threshold: 0.45`
- `htf_fib.entry.tolerance_atr: 3.0`
- `ltf_fib.entry.tolerance_atr: 1.25`

Detta ser ut som:

- HTF-veto påslaget
- override tillåtet
- men override kräver ändå måttlig confidence

### RI transition-guard slice1

`config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_decision_risk_state_transition_guard_slice1_2024_v1.yaml` visar i denna slice bl.a.:

- `multi_timeframe.ltf_override_threshold = 0.38`
- `htf_fib.entry.tolerance_atr = 4.0`
- `ltf_fib.entry.tolerance_atr = 1.5`
- samma huvudsakliga nivåcutoffs som legacy på HTF/LTF-fib

Det här pekar mot en **mjukare structural survival-surface** än legacy:

- lägre override-threshold
- större HTF-tolerans
- större LTF-tolerans

och, givet den nu verifierade mergekedjan, sannolikt ovanpå en runtime-default där override redan är tillåten.

Det är inte i sig fel. Men det ökar sannolikheten att fib-lagret går från filter till räddningsmotor.

## Materialiserat bevis — första faktiska RI-trialen

Ett bounded proof kördes därefter via den faktiska optimizer-materialiseringen:

1. `expand_parameters(...)` på transition-guard-slicens YAML-spec
2. `transform_parameters(...)` på den första konkreta trial-kombinationen
3. `_deep_merge(_get_default_config(), transformed_trial)`
4. direkt anrop till `apply_fib_gating(...)` med den mergeresolverade configen

Den första materialiserade trialen hade bl.a.:

- `multi_timeframe.allow_ltf_override = true`
- `multi_timeframe.ltf_override_adaptive.enabled = true`
- `multi_timeframe.ltf_override_threshold = 0.38`
- `multi_timeframe.use_htf_block = true`

Alltså: override-posturen är **aktiv**, inte bara antydd.

### Men fib-gating gick ändå inte in

Samma materialiserade config gav i ett representativt HTF/LTF-state:

- ingen `htf_fib_entry_debug`
- ingen `ltf_fib_entry_debug`
- `fib_gate_summary.htf.status = "missing"`
- `fib_gate_summary.ltf.status = "missing"`
- inga fib-relaterade reasons

Detta är starkt förenligt med att båda fib-gates **skippas helt** i materialiserad form.

## Konfigurationsmatris — legacy champion vs första RI-trial

Ett uppföljande bounded proof normaliserade legacy champion till dess mergeresolverade `merged_config` och jämförde sedan samma nycklar mot den första materialiserade RI-trialen.

| Nyckel                                          | Legacy champion | Första RI-trial | Tolkning                                           |
| ----------------------------------------------- | --------------- | --------------- | -------------------------------------------------- |
| `multi_timeframe.use_htf_block`                 | `true`          | `true`          | HTF-veto aktivt i båda ytorna                      |
| `multi_timeframe.allow_ltf_override`            | `true`          | `true`          | override tillåten i båda ytorna                    |
| `multi_timeframe.ltf_override_threshold`        | `0.45`          | `0.38`          | RI är mer permissiv än legacy                      |
| `multi_timeframe.ltf_override_adaptive.enabled` | `None`          | `true`          | RI bär dessutom adaptiv override från defaults     |
| `htf_fib.entry.enabled`                         | `true`          | `None`          | legacy aktiverar HTF-fib explicit, RI gör det inte |
| `htf_fib.entry.missing_policy`                  | `"pass"`        | `None`          | legacy har explicit missing-policy, RI saknar den  |
| `ltf_fib.entry.enabled`                         | `true`          | `None`          | legacy aktiverar LTF-fib explicit, RI gör det inte |
| `ltf_fib.entry.missing_policy`                  | `"pass"`        | `None`          | legacy har explicit missing-policy, RI saknar den  |
| `htf_fib.entry.tolerance_atr`                   | `3.0`           | `4.0`           | RI tillåter större HTF-tolerans                    |
| `ltf_fib.entry.tolerance_atr`                   | `1.25`          | `1.5`           | RI tillåter större LTF-tolerans                    |

Det här är den viktigaste skärpningen hittills i slice 3:

> Skillnaden mellan legacy och RI är inte bara att RI är mjukare på override/tolerans. Skillnaden är också att legacy bär en **operativ** fib-surface med explicita `enabled`- och `missing_policy`-flaggor, medan den första materialiserade RI-trialen saknar just dessa grindaktiverande nycklar.

Det gör att nästa arbetsfråga blir ännu mer precis:

- Är RI-slicens sparse fib-leafs avsiktligt skrivna för en annan merge-authority som fyller `enabled` uppströms senare?
- Eller kör optimizer-trialerna faktiskt med en semantik där override-posturen är aktiv, men själva fib-grindarna aldrig blir operativa?

### Varför det händer

Den mergeresolverade RI-trialen innehåller:

- `htf_fib.entry.long_max_level`
- `htf_fib.entry.short_min_level`
- `htf_fib.entry.tolerance_atr`
- `ltf_fib.entry.long_max_level`
- `ltf_fib.entry.short_min_level`
- `ltf_fib.entry.tolerance_atr`

men den innehåller **inte**:

- `htf_fib.entry.enabled`
- `ltf_fib.entry.enabled`
- `htf_fib.entry.missing_policy`
- `ltf_fib.entry.missing_policy`

Eftersom helper-logiken kollar `entry.enabled` för både HTF och LTF blir den praktiska effekten att fib-lagret inte aktiveras alls i den materialiserade trial-konfigen.

### Skärpt arbetsdom

Detta förändrar slice 3-läget på ett viktigt sätt:

> För denna RI-slice är huvudfrågan inte bara om override är aggressiv. Den mer omedelbara frågan är om fib-lagret över huvud taget är aktivt i optimizer-trialerna.

Så nästa bounded steg bör inte börja med ny tuning. Det bör börja med att avgöra om RI-slices avsiktligt eller oavsiktligt körs med en mergeresolverad fib-surface där override är aktivt i `multi_timeframe`, men där HTF/LTF-fib-grindarna själva saknar `enabled`-flaggor och därför aldrig blir operativa.

## 2x2-bevis — enabled är gatekeeper, override är rescue

För att isolera semantiken kördes därefter ett mycket litet 2x2-experiment på den första materialiserade RI-trialen. Samma HTF/LTF-state användes i alla fall; endast två saker togglades:

1. `htf_fib.entry.enabled` + `ltf_fib.entry.enabled`
2. `multi_timeframe.allow_ltf_override`

Teststate valdes så att HTF-nivån faktiskt blockerar när fib-grinden är aktiv, medan LTF-sidan fortfarande kan passera efter en legitim override.

| Fall                    | Fib enabled | Override enabled | Utfall                                                             | Tolkning                                                                            |
| ----------------------- | ----------- | ---------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| `disabled_override_off` | nej         | nej              | `fib_gate_summary.htf = missing`, `fib_gate_summary.ltf = missing` | utan aktiva fib-grindar händer inget alls                                           |
| `disabled_override_on`  | nej         | ja               | exakt samma utfall som ovan                                        | override-flaggan är inert när grindarna saknas                                      |
| `enabled_override_off`  | ja          | nej              | `action = NONE`, reason `HTF_FIB_LONG_BLOCK`                       | aktiva grindar utan override beter sig som rent survival-veto                       |
| `enabled_override_on`   | ja          | ja               | HTF-block räddas via `multi_timeframe_threshold`, LTF passerar     | override fungerar som rescue-path **först efter** att fib-grinden faktiskt är aktiv |

Detta ger en ännu skarpare arbetsdom:

> `allow_ltf_override` är inte i sig en fristående entrymotor. Den får operativ betydelse först när fib-surface är aktiverad via `entry.enabled`, och fungerar då som en explicit rescue-path ovanpå ett redan aktivt structural survival-lager.

Det betyder också att den första materialiserade RI-trialens saknade `enabled`-flaggor inte bara är ett kosmetiskt config-glapp. De ändrar hela slice 3-semantiken genom att göra både veto och override praktiskt overksamma.

## Exekveringsdom — Optuna/backtest reaktiverar inte HTF/LTF-grindarna

Den sista öppna frågan var om optimizer/backtest-spåret senare fyller i saknade fib-flaggor, så att HTF/LTF ändå blir aktiva under körning.

Här är den nu verifierade domen:

1. `src/core/optimizer/runner.py` använder **direkt exekvering som default** så länge `GENESIS_FORCE_SHELL != 1`.
2. Den vägen anropar `src/core/optimizer/runner_trial_backtest.py::_run_backtest_direct(...)`.
3. `_run_backtest_direct(...)` läser payloadens `merged_config` och skickar den vidare direkt till `engine.run(...)` med `meta.skip_champion_merge = True`.
4. Den vägen kör **inte** `ConfigAuthority.validate(...)` på nytt före backtesten.

Det betyder att default-Optuna/backtest-vägen inte fyller i saknade `htf_fib.entry.enabled` eller `ltf_fib.entry.enabled` över huvud taget. Om de saknas i payloaden förblir de saknade i den config som når strategin.

### Om shell/subprocess-vägen används i stället

Om man tvingar shell-vägen via `GENESIS_FORCE_SHELL=1` går körningen genom `scripts/run/run_backtest.py`.

Där sker detta i stället:

1. `merged_config` används direkt som komplett config när den finns i trialfilen
2. configen valideras via `authority.validate(merged_cfg)`
3. schema-defaultar appliceras

`src/core/config/schema.py::FibEntryConfig` visar då att:

- `enabled` defaultar till `false`
- `missing_policy` defaultar till `"pass"`

Det vill säga: shell-vägen reaktiverar inte heller fib-grindarna. Den gör bara den implicita inaktiviteten explicit.

### Skärpt svar på huvudfrågan

Detta gör svaret betydligt mindre tvetydigt:

> Ja — för just denna RI-slice ser det ut som att HTF/LTF entry-gating i praktiken **missas i Optuna/backtest-körningarna**.

Mer exakt:

- i default direct-execution-spåret förblir `enabled` saknat och grindarna blir därför aldrig operativa
- i shell/validated-spåret fylls `enabled=false`, vilket fortfarande betyder att grindarna inte körs

Så den praktiska effekten är densamma i båda vägarna: RI-trialerna kör inte med en aktiv HTF/LTF entry-surface så länge `entry.enabled` inte explicit sätts till `true` i den mergeresolverade configen.

## Repo-bred RI-inventering — 21 av 21 saknar fib-grindflaggor

För att avgöra om transition-guard-slicen var ett isolerat undantag eller ett repo-mönster gjordes därefter en inventory över alla nuvarande RI-optimizer-YAML under `config/optimizer/**`.

Inventeringen gav följande totalsiffror:

- RI-filer med `strategy_family: ri`: **21**
- filer som har någon `htf_fib.entry.*`-surface: **21/21**
- filer som har någon `ltf_fib.entry.*`-surface: **21/21**
- filer som explicit sätter `htf_fib.entry.enabled`: **0/21**
- filer som explicit sätter `ltf_fib.entry.enabled`: **0/21**
- filer som explicit sätter `htf_fib.entry.missing_policy`: **0/21**
- filer som explicit sätter `ltf_fib.entry.missing_policy`: **0/21**

Detta gäller inte bara transition-guard-slicen utan även de andra aktuella RI-spåren, inklusive:

- `config/optimizer/3h/ri_challenger_family_v1/*`
- `config/optimizer/3h/phased_v3/*`
- `config/optimizer/3h/ri_train_validate_blind_v1/*`

Det viktiga mönstret är alltså:

> RI-konfigarna beskriver konsekvent **fib-leafs** som nivåer och toleranser, men de beskriver inte själva **grindaktiveringen**.

Det betyder att frågan inte längre ser ut som ett enstaka config-misstag i en slice. Just nu ser det snarare ut som en repo-bred RI-authoring-konvention där HTF/LTF entry-surface anges partiellt, men utan explicita `enabled`- eller `missing_policy`-flaggor.

Givet exekveringsdomen ovan innebär det i praktiken att nuvarande RI optimizer/backtest-spår mycket sannolikt kör utan aktiv HTF/LTF entry-gating i hela denna konfigfamilj, inte bara i ett enstaka experiment.

## Första bounded backtest-jämförelsen — ingen observerad skillnad för trial #1

Efter inventory- och exekveringsdomen kördes en faktisk bounded jämförelse på den **första materialiserade trialen** från transition-guard-slicen:

- baseline = nuvarande RI-trial som den kör idag
- enabled = samma mergeresolverade trial, men med
  - `htf_fib.entry.enabled = true`
  - `ltf_fib.entry.enabled = true`
  - `missing_policy = "pass"`

Jämförelsen kördes på både sample- och validation-fönster.

### Sample-fönster (`2023-12-21 .. 2024-06-30`)

- baseline: `66` trades, PF `3.4173`, max DD `0.01679`, return `4.1197%`
- enabled: **identiskt** utfall

Dessutom gjordes en per-bar-jämförelse av beslut på engine-vägen:

- `row_count = 1417` i båda körningarna
- action-fördelning identisk: `LONG=458`, `SHORT=1`, `NONE=958`
- decision-row hash identisk i båda fallen
- `rows_equal = true`

Det betyder att explicit aktivering av HTF/LTF entry-gating **inte ändrade ett enda observerat beslut** i just denna trial på sample-fönstret.

### Validation-fönster (`2024-07-01 .. 2024-12-31`)

- baseline: `63` trades, PF `2.1237`, max DD `0.02780`, return `3.2120%`
- enabled: **identiskt** utfall även här

### Viktig tolkning

Detta motsäger inte den tidigare domen att RI-familjen saknar operativ HTF/LTF entry-gating i config-/exekveringskedjan. Det visar i stället något mer nyanserat:

> För den första materialiserade transition-guard-trialen var HTF/LTF-surface, även när den aktiverades explicit, **operativt irrelevant** för den faktiskt realiserade beslutsbanan på både sample- och validation-fönster.

Alltså:

- **strukturdom**: RI-konfigarna missar idag explicit grindaktivering repo-brett
- **första effektjämförelse**: att återaktivera grindarna ändrade ändå inte denna specifika trial/path

Den rimligaste arbetsdomen efter detta är därför att HTF/LTF-fib kan vara både:

1. **strukturellt frånkopplad** i nuvarande RI-authoring, och
2. **praktiskt icke-bindande** för åtminstone vissa RI-trials även när den kopplas in igen

Nästa jämförelse bör därför sannolikt riktas mot:

- en trial/slice där HTF/LTF-nivåerna faktiskt borde bita, eller
- en kontrollerad debugkörning som räknar hur ofta HTF/LTF-surface är `PASS` vs `BLOCK` vs `missing`

## Missing vs explicit false — ingen semantisk skillnad i trial #1

En sista bounded kontroll kördes därefter för att stänga luckan mellan:

- `entry.enabled` **saknas** helt, och
- `entry.enabled = false` sätts explicit

På sample-fönstret för samma transition-guard trial gav jämförelsen:

- identisk action-fördelning: `LONG=458`, `SHORT=1`, `NONE=958`
- identisk decision-row hash
- identiska metrics (`66` trades, PF `3.4173`, return `4.1197%`, max DD `0.01679`)
- `rows_equal = true`

Det betyder att för denna trial/path är:

> `missing` och explicit `false` operativt ekvivalenta på HTF/LTF entry-surface.

Det stärker exekveringsdomen ytterligare:

- default direct-path lämnar grindarna implicit frånkopplade genom saknade flaggor
- shell/schema-path gör samma sak explicit genom `enabled=false`

I båda fallen blir den praktiska semantiken densamma för denna trial.

## Per-bar fib-status debug — varför `enabled=true` ändå inte ändrade något

För att förklara varför explicit aktivering av HTF/LTF fortfarande gav identiska beslut kördes en liten hook-baserad debug på sample-fönstret för samma första transition-guard-trial. I stället för att bara jämföra slutmetrics räknades fib-status direkt från `meta["decision"]["state_out"]` per bar.

Lokal artefakt från körningen:

- `tmp/ri_fib_status_debug_output.json`

Två fall mättes:

1. baseline RI-trial med saknade `entry.enabled`
2. samma trial med

- `htf_fib.entry.enabled = true`
- `ltf_fib.entry.enabled = true`
- båda `missing_policy = "pass"`

### Baseline

På alla `1417` sample-rader där fib-surface nåddes blev utfallet:

- `htf_status = missing` på `1417/1417`
- `ltf_status = missing` på `1417/1417`
- inga fib-relaterade reasons alls
- action-fördelning oförändrad: `LONG=458`, `SHORT=1`, `NONE=958`

Detta visar återigen att baseline-pathen inte kör med operativ fib-gating; den producerar bara summary-status `missing` när kandidatraden passerar fib-lagret.

### Enabled=true + `missing_policy="pass"`

När samma trial kördes med HTF/LTF aktiverade blev utfallet fortfarande helt jämnt över alla `1417` sample-rader:

- `htf_status = UNAVAILABLE_PASS` på `1417/1417`
- `ltf_status = PASS` på `1417/1417`
- inga fib-relaterade reasons alls
- exakt samma action-fördelning och exakt samma metrics som baseline

Första observerade debug-payload gav dessutom:

- HTF: `{ "reason": "UNAVAILABLE_PASS", "policy": "pass", "raw": {} }`
- LTF: `reason = "PASS"` med tom `levels = {}`

Detta är den viktiga förklaringen till varför `enabled=true` fortfarande var inert i just denna trial/path:

> HTF producerade aldrig ett enda strukturellt block — den var `UNAVAILABLE_PASS` på varje fib-rad — och LTF producerade aldrig heller något block, utan bara `PASS`.

Med andra ord: explicit aktivering bytte bara metadataetiketten från `missing` till `UNAVAILABLE_PASS`/`PASS`; den skapade ingen faktisk veto-yta på sample-fönstret.

### Skärpt arbetsdom efter debugkörningen

Det är nu mer precist att beskriva trial #1 så här:

1. baseline RI-authoring lämnar HTF/LTF-grindarna strukturellt frånkopplade
2. om grindarna aktiveras explicit i denna trial blir HTF ändå bara `UNAVAILABLE_PASS`
3. LTF blir samtidigt bara `PASS`
4. därför uppstår varken HTF-block, LTF-block eller override-rescues på den observerade sample-banan

Det betyder att skillnaden mellan legacy och RI i denna slice inte längre bara kan beskrivas som “enabled saknas”. För just denna trial måste man också konstatera att:

> även efter återaktivering verkar den observerade HTF/LTF-fib-surface vara praktiskt icke-bindande, eftersom den inte producerar några block över huvud taget i sample-fönstret.

## Rotorsak i featurekedjan — `3h` bygger inga fib-context alls

Den sista förklaringslänken kom efter läsning av featurekedjan, inte bara debug-outputen.

`src/core/strategy/features_asof_parts/context_bundle_utils.py` innehåller i dag:

- `_ELIGIBLE_TIMEFRAMES = {"1h", "30m", "6h", "15m"}`

och bygger bara HTF/LTF-fib-context när den aktuella timeframe ligger i just den mängden.

Det betyder att för den aktuella RI-trialen på **`3h`** sker detta redan i featuresteget:

1. `build_fibonacci_context_bundle(...)` initierar

- `htf_fibonacci_context = {}`
- `ltf_fibonacci_context = {}`

2. eftersom `3h` **inte** är en eligible timeframe körs varken

- `build_htf_context_fn(...)`
- eller `build_ltf_context_fn(...)`

3. `meta_utils.build_feature_meta(...)` skickar sedan vidare just dessa tomma dictar till

- `meta["htf_fibonacci"]`
- `meta["ltf_fibonacci"]`

4. `evaluate.py` lägger dem oförändrat i state som

- `state["htf_fib"] = {}`
- `state["ltf_fib"] = {}`

Det här är den nuvarande root cause för trial #1:

> På `3h` byggs ingen HTF/LTF fib-context alls i featurekedjan, så beslutslagret får tomma dictar redan innan `entry.enabled` eller `missing_policy` hinner spela någon praktisk roll.

### Hur detta förklarar debugutfallet exakt

Detta förklarar nu hela kedjan utan luckor:

- baseline med saknade `enabled` ger `missing/missing`, eftersom fib-summary byggs ovanpå frånvarande debugpayloads
- explicit aktivering ger `htf = UNAVAILABLE_PASS`, eftersom HTF-grinden ser `{}` och tillåts passera via `missing_policy="pass"`
- LTF syns samtidigt som `PASS`, inte `UNAVAILABLE_PASS`, därför att `apply_ltf_fib_gate(...)` först passerar missing-fallet och sedan skriver över debugstatus till `PASS` när den fortsätter igenom med tom `levels = {}`

Alltså:

1. authoring-problemet finns fortfarande (RI-YAML saknar explicit grindaktivering)
2. men för denna **3h-slice** är den djupare förklaringen att fib-context aldrig materialiseras över huvud taget
3. därför kan HTF/LTF-entry-surface inte bli bindande på denna timeframe utan en kodändring i featurekedjans timeframe-gating

Detta skärper nästa arbetsfråga ytterligare:

> Om målet är att förstå HTF/LTF-entry-roll på `3h`, räcker det inte att jämföra YAML och `enabled`-flaggor. Man måste först avgöra om `3h` över huvud taget ska vara en supportad fib-context-timeframe i `features_asof`.

## Vad kontraktstesterna redan låser

`tests/utils/test_decision_fib_gating_contract.py` låser flera viktiga slice 3-egenskaper:

- HTF-short-circuit stoppar före LTF-summary
- LTF-short-circuit stoppar efter HTF-pass
- adaptive override-debug exporteras och historik uppdateras
- `ltf_entry_range` kan rädda en HTF-blockad kandidat

Det viktigaste testbudskapet här är:

> repot betraktar override-räddning som en **avsiktlig del av kontraktet**, inte som ett undantag som råkat smyga in.

Det stärker slutsatsen att nästa steg inte är “ta bort override blint”, utan att mäta och klassificera dess roll.

## Aktuell arbetsdom

Slice 3 bör därför beskrivas så här:

1. **HTF/LTF fib utan override** = permission / structural survival
2. **threshold override** = möjlig dold entrymotor
3. **range override** = ännu tydligare explicit rescue path
4. **adaptive override** = risk för gradvis semantikglidning om percentil/floor/regim-multipliers blir för permissiva

## Nästa minsta admissible steg efter detta dokument

Innan ny Optuna eller ny branchpolicy bör nästa steg vara ett bounded bevissteg:

1. jämför den **faktiskt mergeresolverade** override-posturen för en legacy-ytan och en RI-ytan
2. bevisa om `allow_ltf_override` verkligen är aktiv i de RI-slices som ser ut att ha låg `ltf_override_threshold`
3. klassificera override-vägen som:
   - sällsynt rescue-path,
   - regelbunden survival-policy,
   - eller praktisk entrymotor

Det betyder att nästa artefakt rimligen bör vara antingen:

- en liten config-resolution-matris för legacy vs RI på fib/override-surface, eller
- ett bounded experimentupplägg som isolerar **fib enabled/disabled + override ON/OFF** utan att öppna en bred ny optimizer-kampanj

## Enradig slutsats

Slice 3 visar att HTF/LTF-fib i grunden är ett **permission/survival-lager**, men att `allow_ltf_override`, `ltf_override_threshold`, adaptiv thresholding och `override_confidence` är de punkter där lagret kan glida över till att fungera som **dold entrymotor**.
