# HANDOFF — strategy-family-slicen till hemdatorn

Senast uppdaterad: 2026-03-18

> Detta dokument är en operativ handoff för pågående arbete på en feature-branch. Det är inte en governance authority source och får inte överstyra aktuell repo-status eller högre ordningens styrdokument, inklusive `.github/copilot-instructions.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md` och `AGENTS.md`. Verifiera alltid branch, HEAD, remote-status och working tree direkt i den aktuella arbetskopian.

## Kort lägesbild

- **Aktiv branch:** `feature/ri-optuna-train-validate-blind-v1`
- **Utgångs-remote för branchen före denna slutstädning:** `origin/feature/ri-optuna-train-validate-blind-v1` på `eb005af4`
- **Branchens lokala commit-stack i denna session före handoff-commit:**
  1. `7d3c27dc` — `tooling: add RI challenger family slice-3 campaign`
  2. `79d606a3` — `refactor(strategy-family): enforce explicit family separation`
  3. `1749835f` — `docs(strategy-family): add RI family design notes`
- **Basbranch för senare PR:** `master` (`origin/master` på `12c2a1cc` när denna handoff skrevs)
- **Mål på hemdatorn:** fortsätt från samma feature-branch, inte från `master`

## Vad som är gjort i denna slice

### 1. Strategy family är nu explicit och obligatorisk

Följande är infört:

- kanonisk registry i `src/core/strategy/family_registry.py`
- kompatibilitetsshimm i `src/core/strategy/families.py` som endast re-exporterar
- `strategy_family` är obligatorisk i runtime-configs
- RI behandlas som separat strategy family, inte som overlay på legacy-champion

### 2. Hard-fail för family-mismatch är på plats

Systemet hard-failar nu deterministiskt för felaktiga kombinationer, bland annat:

- `legacy` + `authority_mode=regime_module`
- `ri` utan exakt `authority_mode=fixed regime_module` i optimizer-config
- `ri` utan ATR $14$
- `ri` utan gates $(3,2)$
- `legacy` med RI-signaturmarkörer i runtime-surface

Det viktiga slutfixet i denna session var att stänga hybridluckan där legacy-deklarerade runtime-surfaces kunde bära RI-ankare utan att stoppas.

### 3. Ledger / orchestrator / shadow är family-aware

Infört i kod:

- default ledger-persist path taggar `strategy_family` och `strategy_family_source`
- shadow-flödet löser family från `merged_config` och skriver ut family i summary
- additive family wrappers finns i research orchestrator utan kontraktsdrift på:
  - `ResearchTask`
  - `ResearchResult`
  - `ParameterAnalysisRequest`
  - `ParameterRecommendation`

### 4. Aktiv config-yta har märkts upp

Följande kategorier bär nu explicit `strategy_family`:

- runtime seed
- aktiva champion-filer
- aktiva optimizer YAML-filer

Legacy-ytor är normaliserade till legacy-signatur, och RI-ytor är låsta till RI-kompatibelt kluster.

## Viktig slutfix från denna session

Det som blockerade post-audit först var:

- `config/runtime.json` / `config/runtime.seed.json` var deklarerade som `legacy` men bar RI-lika ankare

Det är nu korrigerat så att legacy-runtime matchar legacy-signatur:

- `strategy_family: legacy`
- `authority_mode: legacy`
- `atr_period: 28`
- `gates: 2/0`
- legacy-tröskelkluster

Dessutom finns explicit regressionstäckning för att stoppa samma hybrid i framtiden.

## Verifierat grönt i denna session

### Fokuserade selectors

Följande passerade efter hybridfixen:

- `tests/core/strategy/test_families.py`
- `tests/governance/test_config_ssot.py`
- `tests/integration/test_config_endpoints.py`
- `tests/integration/test_config_api_e2e.py`

### Repo-hooks

- `pre-commit run --all-files` ✅

### Strikta guardrails

- `tests/governance/test_authority_mode_resolver.py` ✅
- `tests/backtest/test_backtest_determinism_smoke.py` ✅
- `tests/utils/test_features_asof_cache_key_deterministic.py` ✅
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` ✅

### Governance-resultat

Opus post-diff re-audit för den slutliga koden: **APPROVED**

## Viktiga filer att känna till hemma

### Kärnimplementation

- `src/core/strategy/family_registry.py`
- `src/core/strategy/families.py`
- `src/core/config/schema.py`
- `src/core/config/authority.py`
- `scripts/validate/validate_optimizer_config.py`
- `src/core/research_ledger/service.py`
- `src/core/intelligence/ledger_adapter/processing.py`
- `src/core/research_orchestrator/families.py`
- `src/core/research_orchestrator/__init__.py`
- `src/core/backtest/intelligence_shadow.py`

### Viktiga testytor

- `tests/core/strategy/test_families.py`
- `tests/utils/test_validate_optimizer_config.py`
- `tests/core/research_ledger/test_service.py`
- `tests/integration/test_config_endpoints.py`
- `tests/integration/test_config_api_e2e.py`
- `tests/governance/test_config_ssot.py`
- `tests/research_orchestrator/test_family_wrappers.py`
- `tests/backtest/test_run_backtest_intelligence_shadow.py`

### Styrande / förklarande docs

- `docs/audit/refactor/regime_intelligence/command_packet_strategy_family_system_separation_2026-03-18.md`
- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/governance/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`

## Exakt arbetsläge att utgå från hemma

På hemdatorn ska nästa session börja så här:

1. hämta senaste remote
2. checka ut `feature/ri-optuna-train-validate-blind-v1`
3. pulla senaste ändringarna på just den branchen
4. verifiera att working tree är ren
5. fortsätt därifrån — inte från `master`

## Vad som återstår efter denna handoff

Kod- och docs-arbetet i denna slice är färdigt. Det som återstår är rent integrationsflöde:

1. pusha branchens nya commits
2. öppna / uppdatera PR mot `master`
3. låt CI bli grön
4. merga
5. delete branch lokalt och remote efter merge

## Rekommenderad PR-/merge-etikett

Det här är i praktiken en:

- `refactor(strategy-family)` + `config` + `tests` + `docs`

med kärnpåståendet:

> RI är nu explicit separerad strategy family med fail-closed validering, family-aware ledger/shadow/orchestrator-stöd och obligatorisk family-märkning på aktiva configytor.

## Saker du inte ska göra hemma

- börja om från `master` och återskapa samma slice
- återöppna legacy/RI-overlay-tolkningen
- återintroducera mjuka warnings för family-mismatch
- "snabbfixa" runtime till RI-default utan separat governance-slice

## Enradig beslutslogg

Den här branchen innehåller nu en governance-godkänd, testverifierad och fail-closed implementation av explicit strategy-family-separation där Regime Intelligence behandlas som egen family och inte som overlay på legacy-systemet.
