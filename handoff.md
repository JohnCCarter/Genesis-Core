# HANDOFF — RI/R1 vs legacy role-map kickoff

Senast uppdaterad: 2026-03-27

> Detta dokument är en operativ handoff för nästa agent/session. Det är **inte** en governance authority source och får inte överstyra `.github/copilot-instructions.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md` eller `AGENTS.md`. Verifiera alltid live branch, HEAD, remote-status och working tree i aktuell arbetskopia innan arbete fortsätter.

## Uppdatering 2026-03-27 — nuvarande takeover-status

Den här handoffen är nu kompletterad för den aktuella branchen:

- **Aktiv branch:** `feature/ri-role-map-implementation-2026-03-24`
- **HEAD / origin:** `4bea3fb9` (`docs(config): add transition-guard decision slice artifacts`)
- **Working tree:** clean
- **Remote-sync:** lokal branch matchar `origin/feature/ri-role-map-implementation-2026-03-24`
- **Öppen PR:** ingen aktiv PR finns just nu för branchen
- **Viktig regel:** öppna **inte** automatiskt en ny PR mot `master`; target/base-branch måste beslutas explicit först

### Vad som blev klart i den senaste sessionen

Följande är genomfört och pushat:

1. **Kategoriserad commit- och push-städning**
   - ändringarna delades upp i logiska commits i stället för att lämnas som en stor osorterad stack
2. **Governance mode / SSOT-förtydliganden**
   - uppdateringar landade i `docs/governance_mode.md`, `.github/copilot-instructions.md` och `docs/OPUS_46_GOVERNANCE.md`
3. **Kodsteg för regime-definition**
   - konfigurerbar `multi_timeframe.regime_intelligence.regime_definition` har förts genom authority/schema/evaluate/regime med tillhörande tester
4. **RI-signal- och decision-slices**
   - nya optimizer-configs och governance/evidence-spår för SIGNAL, SIGNAL + regime-definition, DECISION EV-edge och DECISION `transition_guard`
5. **Transition-guard evidens**
   - bounded smoke + fresh canonical run genomfördes i tidigare steg
   - bästa observerade validation-tuple för den slicen var `mult=0.55` och `guard_bars=1`

### Viktiga commits högst i stacken

- `4bea3fb9` `docs(config): add transition-guard decision slice artifacts`
- `c4d79fb2` `docs(config): add decision EV-edge slice research artifacts`
- `85c7d5d2` `docs(config): add RI signal research lanes and evidence`
- `46711d3d` `feat(regime): enable configurable regime-definition thresholds`
- `442c6e8c` `docs(governance): clarify mode ssot and operating expectations`

### PR-status och varför nästa agent måste känna till det

- En draft-PR `#74` skapades tillfälligt mot `master` som publicerings-/reviewpaket.
- Den PR:n **stängdes utan merge** efter explicit användarstyrning.
- Historiken finns kvar på GitHub som stängd PR, men **inget** har mergats till `master`.
- Nästa agent ska därför behandla branchen som **pushad men ännu inte korrekt targetad för merge/review**.

### Vad nästa agent ska göra härnäst

Starta **inte** med att öppna PR eller mer optuna-körning. Nästa agent bör istället:

1. läsa denna handoff + relevanta governance-/analysis-filer för att förstå den nuvarande RI-stackens läge
2. bekräfta vilken branchstrategi som faktiskt gäller för fortsatt integration (ingen implicit `master`-PR)
3. fortsätta från den nu etablerade RI research stacken och avgöra nästa minsta admissible steg
4. om ny review/publicering behövs: först fastställ rätt target-branch och om arbetet ska vara draft, stacked eller internt viloläge

### Kort takeover-bedömning

Ja — repot är **redo för nästa agent** på hemdatorn i den meningen att:

- branchen är ren och pushad
- senaste arbetet är commitat
- ingen öppen PR blockerar eller skapar merge-risk just nu

Det som **inte** är förifyllt är beslutet om nästa integrationssteg. Nästa agent måste alltså få eller bekräfta:

- om arbetet bara ska fortsätta på branchen,
- om en ny PR senare ska öppnas,
- och i så fall mot **vilken** base-branch.

## Uppdatering 2026-03-23 — vad som nu faktiskt är etablerat

Detta dokument började som en kickoff för en öppen rollmap-fråga. Efter vidare analys på branchen ska nästa agent **inte** läsa de tidiga formuleringarna här som en slutdom. Följande är nu kod- och artefaktförankrat:

- `legacy` och `ri` behandlas i repot som två separata `strategy_family`-ytor, inte som “legacy plus ett litet RI-lager”.
- Den första verkliga family-driften uppstår **uppströms** i:
  1.  **authority resolution**
  2.  **regime-aware calibration**
- Den första plats där denna drift blir **faktiskt trade/no-trade / candidate/no-candidate** är:
  1.  **threshold / candidate surface** i `src/core/strategy/decision_gates.py`
  2.  därefter **cadence / post-gates**
- `clarity_score` och `risk_state` beter sig i nuvarande evidens främst som **sizing/management**, inte som första action-driftkälla.

### Konkret status efter genomförd kartläggning

Följande är nu genomläst och korskopplat:

- `handoff.md`
- `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/analysis/ri_legacy_role_map_2026-03-20.md`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_fib_gating_helpers.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/confidence.py`
- högsignal-tester kring authority parity, signal adaptation, hysteresis/cooldown, edge och sizing-only-beteende

### Slice 1 — authority + calibration

Det som nu är fastställt:

- `src/core/config/authority_mode_resolver.py` resolve:ar deterministiskt `authority_mode` med canonical path före alias och fail-closed tillbaka till `legacy`.
- `src/core/strategy/evaluate.py` använder detta för att välja **authoritative regime path**.
- `src/core/strategy/prob_model.py` använder sedan authoritative regime för att välja **`calibration_by_regime`** när modellen erbjuder det.
- `config/models/tBTCUSD_3h.json` har explicita regime-specifika calibration-koefficienter för `buy` och `sell`, vilket gör authority-bytet till en verklig probability-surface-förändring — inte bara metadata.

Arbetsdom efter slice 1:

> Den första topologiska RI-vs-legacy-driften uppstår i **authority + calibration** innan threshold-, fib- eller sizing-lagren får säga sitt.

### Slice 2 — threshold / candidate surface + cadence

Det som nu är fastställt:

- `src/core/strategy/decision_gates.py::select_candidate(...)` är den primära **candidate surface** där uppströms drift först blir konkret `LONG` / `SHORT` / `NONE`.
- `signal_adaptation` överstyr baströsklarna när den är aktiv; detta är låst av `tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_zone_overrides_base_thresholds`.
- Den aktuella legacy champion-surface för `tBTCUSD_3h` och RI challenger-surface i `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice2_2024_v1.yaml` har **olika threshold-form**, inte bara globalt högre/lägre siffror.
- `apply_post_fib_gates(...)` beter sig som ett separat **cadence/stabiliseringslager** via `CONF_TOO_LOW`, `EDGE_TOO_SMALL`, `HYST_WAIT` och `COOLDOWN_ACTIVE`.

Arbetsdom efter slice 2:

> `decision_gates.py` är den plats där authority+calibration-drift först blir **praktiskt tradingbeteende**, medan post-gates främst formar **timing och persistence**.

### Nästa rimliga steg

Nästa agent bör starta med **slice 3: structural survival / override** och fokusera på:

- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_fib_gating_helpers.py`
- `docs/analysis/ri_legacy_role_map_slice3_structural_survival_2026-03-30.md`

Kärnfråga för slice 3:

> När beter sig HTF/LTF-veto + adaptive override som legitim **permission/survival-policy**, och när börjar det i praktiken fungera som **dold entrymotor**?

Aktuell status för slice 3:

- En första arbetsmatris finns nu i `docs/analysis/ri_legacy_role_map_slice3_structural_survival_2026-03-30.md`.
- Den viktigaste nya observationen därifrån är att `use_htf_block` defaultar till `True`, medan `allow_ltf_override` inte gör det.
- Därför måste nästa agent läsa **mergeresolverad config**, inte bara sparse optimizer-leafs, innan override-semantik tolkas.
- Ett materialiserat proof visar dessutom att transition-guard-slicens första konkreta RI-trial får `allow_ltf_override=true` och `ltf_override_adaptive.enabled=true`, men att `htf_fib.entry.enabled` och `ltf_fib.entry.enabled` saknas i mergeresolverad config.
- En uppföljande config-matris visar att legacy champion däremot har `htf_fib.entry.enabled=true`, `ltf_fib.entry.enabled=true` och explicit `missing_policy="pass"`, medan första RI-trialen saknar dessa grindaktiverande nycklar trots aktiv override-postur.
- Ett bounded 2x2-experiment visar dessutom att `allow_ltf_override` är inert när fib-grindarna saknar `entry.enabled`; först när grindarna aktiveras blir override en verklig rescue-path (`HTF_OVERRIDE_LTF_CONF`) ovanpå ett aktivt HTF-veto.
- Exekveringskedjan är nu också verifierad: default-Optuna kör direct execution via `_run_backtest_direct(...)` utan ny schema-validering, så saknade `entry.enabled` förblir saknade; om shell-vägen används i stället fyller schema `enabled=false` och `missing_policy="pass"`, vilket fortfarande lämnar HTF/LTF-gating inaktiv.
- Repo-bred inventory visar samma mönster i hela den aktuella RI optimizer-familjen: **21/21** RI-YAML har `htf_fib.entry.*` och `ltf_fib.entry.*` leafs, men **0/21** sätter `htf_fib.entry.enabled`, `ltf_fib.entry.enabled` eller motsvarande `missing_policy` explicit.
- Första bounded baseline-vs-enabled-backtesten på transition-guard trial #1 gav dock **ingen observerad skillnad**: sample och validation fick identiska metrics, och sample-fönstrets decision rows var hash-identiska (`rows_equal=true`). Det betyder att HTF/LTF-entry-surface är strukturellt missad i authoring-kedjan, men samtidigt praktiskt icke-bindande för just denna trial/path.
- En uppföljande missing-vs-false-kontroll gav också identiskt utfall (`rows_equal=true`), vilket stärker att saknat `entry.enabled` och explicit `entry.enabled=false` är operativt samma sak för denna trial/path.
- En ny hook-baserad per-bar-debug på sample-fönstret för samma trial förklarar nu _varför_ `enabled=true` ändå inte ändrade något: baseline gav `htf=missing` och `ltf=missing` på alla `1417` fib-rader, medan explicit aktivering gav `htf=UNAVAILABLE_PASS` och `ltf=PASS` på samma `1417/1417` rader, fortfarande utan en enda fib-relaterad reason eller block. Första HTF-debugpayloaden var `{reason: UNAVAILABLE_PASS, policy: pass, raw: {}}`, vilket betyder att HTF aldrig blev en faktisk veto-yta i detta sample; LTF var samtidigt bara `PASS`.
- Den egentliga rotnyckeln är nu spårad i featurekedjan: `src/core/strategy/features_asof_parts/context_bundle_utils.py` bygger bara HTF/LTF fib-context för `1h`, `30m`, `6h` och `15m`. Eftersom den aktuella trialen körs på `3h` returneras både `htf_fibonacci_context` och `ltf_fibonacci_context` som `{}` redan i featuresteget. Därför når beslutslagret tomma dictar på varje bar, och 3h-fib-gating blir praktiskt inert oavsett om `entry.enabled` saknas eller sätts explicit. LTF visas dessutom som `PASS` snarare än `UNAVAILABLE_PASS` därför att dess gate skriver över debugstatus till `PASS` när den fortsätter med tom `levels = {}`.
- Nästa agent bör därför först avgöra om fib-gating i dessa RI optimizer-trials är avsiktligt eller oavsiktligt **inaktivt** innan vidare tuning eller rolltolkning görs.

### Viktig tolkningsregel framåt

Den tidiga kickoff-idén i detta dokument — att RI/R1 kanske borde ”återföras” till management/filter — ska nu behandlas som en **historisk arbetshypotes**, inte som slutdom.

Det som just nu är bäst förankrat i kod och tester är i stället:

1. **RI och legacy är separata strategy families**
2. **första driftlagret är authority + calibration**
3. **första praktiska action-lagret är threshold / candidate surface**
4. **sizing-lagret är senare och mer management-präglat i nuvarande evidens**

## Läs detta först — vad nästa agent måste förstå direkt

Den viktigaste insikten från den senaste sessionen är **inte** bara att RI är en separat strategy family. Den viktigaste insikten är också att den ursprungliga idén med **R1/RI** verkar ha varit:

- **management/filter-lager**
- **overlay-lager**
- **inte en primary entry-driver**

Under implementationen gled arbetet sannolikt bort från den idén utan att det upptäcktes direkt. Det upptäcktes först i efteranalys/brainstorming.

### Kritisk arbetsfråga framåt

Nästa agent ska därför **inte** börja med mer bred parameteroptimering.

Nästa agent ska först fråga:

> **Vilka delar i RI/R1 är egentligen tänkta att vara context/filter/management — och vilka delar har i praktiken börjat bete sig som entry-motor?**

Detta är sannolikt nyckeln till nästa edge.

## Live repo-status vid denna handoff

- **Aktiv branch vid handoff:** `feature/ri-legacy-role-map-2026-03-19`
- **HEAD vid handoff:** `f9cb996d`
- **Working tree vid handoff:** clean
- **Senast pushad commit på master före brancharbete:** `8d5d7d80` — `docs(ri): align strategy-family architecture terminology`
- **Remote-status som observerades:** `origin/master` pekade på samma commit när branchen skapades

## Vad som blev klart precis innan denna handoff

### 1. Strategy-family-separationen är redan landad

Följande är redan infört och ska **inte** återdebatteras som om det vore öppet:

- `strategy_family` är kanoniskt `legacy | ri`
- hybrida ytor fail-closed i stället för att accepteras som tredje family label
- RI behandlas som separat strategy family, inte som legacy-overlay i canonical modellen

### 2. Repo-guidance har just alignats semantiskt

En docs-slice landades för att städa aktiv guidance så att den matchar nuvarande architecture truth:

- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/governance/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
- `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_repo_wide_architecture_alignment_2026-03-19.md`

Den slicen verifierades med riktade STRICT-sentinels och pushades till `master` innan denna nya branch skapades.

## Det viktigaste resonemanget att bevara

### Kärntes

Edge ser just nu mer sannolikt ut att komma från:

- **regime-aware permissioning**
- **continuation bias**
- **no-trade state detection**
- **management / exit intelligence**

…än från bredare parameteroptimering av nuvarande RI-baseline.

### Arbetsantagande

Det är möjligt att RI/R1 har blivit för entry-drivande under implementationen och därmed tappat sin avsedda roll som filter/management-lager.

### Viktig konsekvens

Nästa steg bör därför vara **rollkartläggning**, inte ny Optuna-jakt.

## Hypoteser som nästa agent ska bära vidare

1. **Edge ligger troligen i permissioning, inte i ny entry-logik.**
2. **RI tappade sin design när den började påverka entryytan för mycket.**
3. **Continuation-aware filtering är mer lovande än allmän regime-entry.**
4. **Exit/management kan ge större edge än ytterligare entry-tuning.**
5. **No-trade state detection kan vara mer värdefull än ökad signalaggressivitet.**

## Rekommenderad nästa uppgift — bygg en rollkarta

Nästa agent bör ta fram en **rollkarta för RI/R1 och legacy**.

### Syftet med rollkartan

Att svara på:

- vad ansvarar **legacy** för?
- vad borde **RI/R1** ansvara för?
- vilka intelligence-moduler hör hemma i **context/filter/management**?
- vilka delar har glidit över till att bli **entry-drivare**?

### Rekommenderade ansvarshinkar

Nästa agent bör gruppera allt i åtminstone dessa fyra kategorier:

1. **Context / regime**
   - marknadsläge, struktur, volatilitet, persistence, state
2. **Permission / filtering**
   - trade allowed / not allowed, veto, cooldown, hysteresis, confidence gating
3. **Management**
   - sizing, exits, partials, hold, aggressivitetsjustering
4. **Entry-driving logic**
   - allt som i praktiken skapar eller kraftigt flyttar entry-beteendet

### Kritisk designregel

RI/R1 bör huvudsakligen leva i:

- **Permission / filtering**
- **Management**

…och endast mycket försiktigt i **Entry-driving logic**.

## Konkreta frågor nästa agent bör driva

1. **Vilka indikatorer används faktiskt i legacy vs RI/R1?**
2. **Vilka parametrar finns per modul och vilken roll spelar de egentligen?**
3. **Vilka moduler har testats isolerat, och vilka har bara testats i kluster?**
4. **Vilka moduler är orthogonala, och vilka är bara redundans/komplexitet?**
5. **Vilka delar bör behållas, förenklas, flyttas eller stängas av?**

## Viktigt: börja inte härifrån på fel sätt

Nästa agent ska **inte** börja med att:

- köra ny bred Optuna-kampanj
- öka/minska parametrar blint
- anta att “mer RI” automatiskt är bättre
- behandla alla intelligence-moduler som lika viktiga
- låta overlay-/filter-lagret fortsätta mutera till dold entrymotor

## Bättre arbetsordning

1. **Inventory**
   - lista alla intelligence-moduler + indikatorer + centrala parametrar
2. **Intent audit**
   - var modulen tänkt som filter/management eller beter den sig som entry-driver?
3. **Ablation plan**
   - modul av/på, modul som filter-only, modul som management-only, kombinationspar
4. **Parameter policy först efteråt**
   - diskutera först därefter om något ska upp, ner, frysas eller tas bort

## Filer nästa agent sannolikt bör läsa tidigt

### För arkitektur / definitioner

- `src/core/strategy/family_registry.py`
- `src/core/strategy/families.py`
- `src/core/backtest/intelligence_shadow.py`
- `scripts/validate/validate_optimizer_config.py`

### För styrande/förklarande kontext

- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/governance/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
- `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`

### För test-/guardrail-surface

- `tests/core/strategy/test_families.py`
- `tests/utils/test_validate_optimizer_config.py`
- `tests/governance/test_pipeline_fast_hash_guard.py`
- `tests/governance/test_regime_intelligence_cutover_parity.py`

## Om nästa agent ska skriva något först

Det bästa första artefaktförslaget är **inte kod** utan en tydlig arbetsmatris, till exempel:

- modul / indikator
- tänkt roll
- faktisk observerad roll
- påverkar entry?
- påverkar filtering?
- påverkar management?
- misstanke (behåll / förenkla / flytta / avaktivera)

## Enradig sammanfattning

RI är redan separerad från legacy i canonical modellen, men nästa stora arbete är att återföra RI/R1 till sin sannolika ursprungsroll som **management/filter-lager** genom att först bygga en tydlig **rollkarta för RI/R1 vs legacy** innan mer optimering sker.
