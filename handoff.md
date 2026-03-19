# HANDOFF — efter merge av strategy-family-slicen

Senast uppdaterad: 2026-03-18

> Detta dokument är en operativ handoff för nästa session på hemdatorn. Det är inte en governance authority source och får inte överstyra aktuell repo-status eller högre ordningens styrdokument, inklusive `.github/copilot-instructions.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md` och `AGENTS.md`. Verifiera alltid branch, HEAD, remote-status och working tree direkt i den aktuella arbetskopian.

## Kort lägesbild

- **Aktiv branch nu:** `master`
- **HEAD vid denna handoff:** `e4a79d2d`
- **Senaste viktiga merge:** PR **#70** — `refactor(strategy-family): enforce explicit RI family separation`
- **Feature-branch-status:** `feature/ri-optuna-train-validate-blind-v1` är mergad och borttagen
- **Det säkra läget att utgå från hemma:** senaste `origin/master`, inte någon gammal feature-branch

## Vad som nu är klart

Strategy-family-slicen är färdig, mergad och landad på `master`.

Det som ingår i den mergade slicen:

- kanonisk strategy-family registry i `src/core/strategy/family_registry.py`
- explicit och obligatorisk `strategy_family` på aktiva runtime/champion/optimizer-ytor
- fail-closed validering för legacy/RI-mismatch
- family-aware ledger-tagging
- family-aware shadow-summary
- additive family wrappers i research orchestrator
- uppdaterade tester, governance-packet och förklarande docs

## Viktig slutpoäng från slicen

Regime Intelligence behandlas nu som **egen strategy family**, inte som overlay på legacy.

Det betyder att systemet nu hard-failar för bland annat:

- `legacy` + `authority_mode=regime_module`
- `ri` utan exakt RI-kluster (`authority_mode=regime_module`, kanonisk ATR/gates och kanoniska threshold-värden)
- `legacy` med RI-signaturmarkörer i runtime-surface

Dessutom är runtime-seed normaliserad tillbaka till riktig legacy-signatur där det behövs.

## Verifiering som passerade innan merge

Följande verifieringar är gröna för den mergade slicen:

### Fokuserade selectors

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

### Governance

- Opus post-diff re-audit: **APPROVED**

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

## Exakt startläge på hemdatorn

På hemdatorn ska nästa session börja så här:

1. hämta senaste remote
2. checka ut `master`
3. pulla senaste `origin/master`
4. verifiera att HEAD är `e4a79d2d` eller senare
5. säkerställ ren working tree
6. skapa ny branch först när nästa uppgift är tydlig

## Det du inte behöver göra igen

- återöppna `feature/ri-optuna-train-validate-blind-v1`
- återskapa strategy-family-slicen
- återinföra legacy/RI-overlay-tolkning
- lägga till mjuka warnings där family-mismatch nu hard-failar

## Rekommenderat nästa steg hemma

Utgå från att strategy-family-separationen redan är mergad.

Nästa arbete bör därför ske **ovanpå `master`**, till exempel:

- uppföljande RI-challenger-analys
- fortsatt optimizer-/campaign-arbete
- eller nästa governance-godkända runtime-/research-slice

## Enradig beslutslogg

Strategy-family-slicen är nu mergad till `master`, feature-branchen är borttagen, och nästa säkra startpunkt på hemdatorn är därför senaste `origin/master`.
