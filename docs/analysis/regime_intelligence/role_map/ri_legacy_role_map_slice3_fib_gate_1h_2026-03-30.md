# RI vs legacy — 1h fib-gating bounded outcome

Datum: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: research-artefakt / config+analys only / ingen runtime-ändring

## Syfte

Detta dokument stänger den bounded 1h-uppföljningen efter att 3h-fib-lanen klassats som strukturellt icke-informativ.

Målet här var snävare:

> Testa om HTF/LTF fib entry-gating ger mätbar effekt på en timeframe där fib-context faktiskt byggs i featurekedjan.

Ingen kod i `src/core/**` ändrades. Ingen ändring gjordes i `_ELIGIBLE_TIMEFRAMES`. Ingen champion/default/runtime-lane öppnades.

## Använd research-config

- Config: `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_fib_gate_matrix.yaml`
- Run id: `ri_role_map_slice3_fib_gate_1h_20260330`
- Run-dir: `results/hparam_search/ri_role_map_slice3_fib_gate_1h_20260330`

Configen höll hela 1h-ytan fixerad och varierade endast två grindar:

- `htf_fib.entry.enabled`
- `ltf_fib.entry.enabled`

Det gav följande deterministiska matris:

| Trial       | Postur       | HTF gate | LTF gate |
| ----------- | ------------ | -------- | -------- |
| `trial_001` | control      | off      | off      |
| `trial_002` | mixed_ltf_on | off      | on       |
| `trial_003` | mixed_htf_on | on       | off      |
| `trial_004` | candidate    | on       | on       |

Alla övriga parametrar hölls fixerade till samma 1h legacy-family-surface.

## Validering före körning

Följande verifierades före exekvering:

- config-validering kördes mot `scripts/validate/validate_optimizer_config.py`
- preflight kördes mot `scripts/preflight/preflight_optuna_check.py`
- preflight passerade efter att canonical env-par sattes i shell-sessionen:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`

Champion-valideraren gav endast varningar kopplade till dotted-key-stilen i `parameters` och blockerade inte körningen.

## Sample-resultat (2024-01-01 .. 2024-12-31)

Optimizer-trial-artifakterna i run-dir visar identiskt utfall för alla fyra posturer:

| Trial       |          Score | Trades |             PF |    Max DD |     Return |
| ----------- | -------------: | -----: | -------------: | --------: | ---------: |
| `trial_001` | `0.0243934172` |  `413` | `1.1478503182` | `1.8587%` | `-1.2328%` |
| `trial_002` | `0.0243934172` |  `413` | `1.1478503182` | `1.8587%` | `-1.2328%` |
| `trial_003` | `0.0243934172` |  `413` | `1.1478503182` | `1.8587%` | `-1.2328%` |
| `trial_004` | `0.0243934172` |  `413` | `1.1478503182` | `1.8587%` | `-1.2328%` |

Det betyder att både mixed states och full candidate (`on/on`) blev metrisk-identiska med control (`off/off`) på sample-fönstret.

## Validation-resultat (2025-01-01 .. 2025-10-01)

Validation-reruns i `results/hparam_search/ri_role_map_slice3_fib_gate_1h_20260330/validation` gav åter exakt samma utfall för alla fyra posturer:

| Trial       |             Score | Trades |             PF |    Max DD |     Return | Constraint-status                 |
| ----------- | ----------------: | -----: | -------------: | --------: | ---------: | --------------------------------- |
| `trial_001` | `-100.1569786457` |  `261` | `0.7645861755` | `3.4143%` | `-3.1964%` | fail (`min_profit_factor < 1.05`) |
| `trial_002` | `-100.1569786457` |  `261` | `0.7645861755` | `3.4143%` | `-3.1964%` | fail (`min_profit_factor < 1.05`) |
| `trial_003` | `-100.1569786457` |  `261` | `0.7645861755` | `3.4143%` | `-3.1964%` | fail (`min_profit_factor < 1.05`) |
| `trial_004` | `-100.1569786457` |  `261` | `0.7645861755` | `3.4143%` | `-3.1964%` | fail (`min_profit_factor < 1.05`) |

Det finns alltså ingen kontroll-vs-candidate-separation heller på validation-fönstret.

## Starkare evidens än bara slutmetrics

För att undvika en falsk plateau-dom baserad enbart på aggregerade metrics jämfördes även normaliserade trade-banors innehåll i de genererade result-JSON-filerna.

Verifiering i sessionen gav:

- sample: identisk normaliserad trade-path-hash för alla fyra posturer
  - `b6baa95baaa258f3`
- validation: identisk normaliserad trade-path-hash för alla fyra posturer
  - `24a4f64a0cb0a8ca`

Detta betyder att inte bara score/metrics utan även själva realiserade trade-sekvensen var oförändrad mellan:

- control (`off/off`)
- mixed states (`off/on`, `on/off`)
- candidate (`on/on`)

## Klassning

Utfallsklassning för denna bounded 1h-slice är:

> **plateau**

Mer precist:

- **ingen uplift** observerades när fib-gating aktiverades
- **ingen degradation-differens** observerades mellan posturerna
- **ingen mixed-state-effekt** observerades heller

## Tolkning

Det viktiga här är att detta inte är samma förklaring som på 3h.

På 3h var huvudproblemet att fib-context inte byggdes alls på timeframe-nivå. Här kördes i stället en eligible timeframe (`1h`) där fib-context-kedjan faktiskt får chans att existera.

Den bounded 1h-domen blir därför skarpare:

> På denna fixerade 1h-surface var HTF/LTF fib entry-gating praktiskt icke-bindande även när grindarna aktiverades explicit.

Detta visar inte att fib-gating alltid är irrelevant på 1h. Det visar däremot att den här specifika 1h-posturen/fönsterkombinationen inte får någon mätbar beslutseffekt av att slå på HTF/LTF entry-gates.

## Scope-gräns som hölls

Följande hölls explicit utanför scope:

- inga ändringar i `src/core/**`
- ingen ändring av `_ELIGIBLE_TIMEFRAMES`
- ingen champion-promotion
- ingen default-cutover
- ingen runtime/config-authority-ändring
- ingen fortsättning på 3h fib-slice

## Enradig slutsats

Den bounded 1h-uppföljningen visar att HTF/LTF fib-gating, trots eligible timeframe och explicit aktivering, gav **ingen observerbar effekt** på varken metrics eller trade-path för denna fixerade yta; klassningen är därför **plateau**.
