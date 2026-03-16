# HANDOFF — Genesis-Core till hemdator / nästa Copilot-session

Senast uppdaterad: 2026-03-16

## Kort lägesbild

- **Aktiv branch nu:** `master`
- **HEAD:** `b41a2422`
- **Repo-status:** ren working tree
- **Senaste viktiga commits på `master`:**
  1. `b41a2422` — `refactor(server): extract deterministic regime intelligence layer`
  2. `003fef58` — `feat(research-ledger): add canonical ledger substrate`
  3. `d49879a5` — `tooling: stabilize trial key cache performance test`

## Vad som är klart

Följande arbetskedja är **fullbordad och införd i `master`**:

1. **Flaky optimizer-performance test stabiliserat**
   - `tests/utils/test_optimizer_performance.py`
   - `test_trial_key_caching` använder nu repeated samples + median istället för single-sample micro-benchmark.

2. **Research Ledger v1-substrat infört**
   - Ny package under `src/core/research_ledger/`
   - Fokuserade tester under `tests/core/research_ledger/`
   - Auditunderlag under `docs/audit/research_ledger/`

3. **Regime Intelligence-lagret extraherat och mergat**
   - Ny package under `src/core/intelligence/regime/`
   - Legacy-shim kvar i `src/core/strategy/regime_intelligence.py`
   - Fokuserade tester under `tests/core/intelligence/regime/`
   - Shadow-observability-regression täcks av `tests/backtest/test_regime_shadow_artifacts.py`

## Brancher som redan är mergade och bortstädade

Följande brancher **finns inte längre** som aktiva arbetsbrancher och ska inte återupplivas utan särskilt skäl:

- `feature/research-ledger-v1` → mergad, remote deleted, local deleted
- `fix/flaky-trial-key-caching` → remote deleted, local deleted
- `feature/regime-intelligence-layer-migration` → mergad, remote deleted, local deleted

## Viktiga verifieringar som redan passerat

Under denna kedja kördes och passerade följande verifieringar innan merge:

- `python scripts/validate/validate_registry.py`
- `pre-commit run --all-files`
- `python -m bandit -r src -c bandit.yaml -f txt -o bandit-report.txt`
- `python -m pytest -q`

Dessutom passerade riktade guardrails för determinism/cache/pipeline, inklusive:

- `tests/backtest/test_backtest_determinism_smoke.py`
- `tests/utils/test_features_asof_cache_key_deterministic.py`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## Det viktigaste för nästa Copilot på hemdatorn

### Du ska utgå från detta

- Börja från **`master`**, inte från någon gammal feature-branch i den här kedjan.
- Anta att arbetet kring:
  - flaky trial-key caching,
  - Research Ledger v1-substrat,
  - Regime Intelligence-lagret
    redan är **klart och mergat**.

### Du ska inte göra detta igen

- Återskapa inte `feature/research-ledger-v1`
- Återskapa inte `fix/flaky-trial-key-caching`
- Återskapa inte `feature/regime-intelligence-layer-migration`
- Försök inte åter-mergea samma migrationsslice eller ledger-substrat igen

## Viktiga filer som nu är kanoniska på `master`

### Research Ledger

- `src/core/research_ledger/__init__.py`
- `src/core/research_ledger/enums.py`
- `src/core/research_ledger/indexes.py`
- `src/core/research_ledger/models.py`
- `src/core/research_ledger/queries.py`
- `src/core/research_ledger/service.py`
- `src/core/research_ledger/storage.py`
- `src/core/research_ledger/validators.py`

### Regime Intelligence

- `src/core/intelligence/__init__.py`
- `src/core/intelligence/regime/__init__.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/intelligence/regime/clarity.py`
- `src/core/intelligence/regime/contracts.py`
- `src/core/intelligence/regime/htf.py`
- `src/core/strategy/regime_intelligence.py`

### Testytor att lita på för detta område

- `tests/core/research_ledger/test_storage.py`
- `tests/core/research_ledger/test_validators.py`
- `tests/core/research_ledger/test_service.py`
- `tests/core/intelligence/regime/test_authority.py`
- `tests/core/intelligence/regime/test_clarity.py`
- `tests/core/intelligence/regime/test_contracts.py`
- `tests/core/intelligence/regime/test_htf.py`
- `tests/backtest/test_regime_shadow_artifacts.py`
- `tests/utils/test_optimizer_performance.py`

## Om du fortsätter arbetet hemma: rekommenderad startpunkt

1. Hämta senaste `master`
2. Verifiera att HEAD är `b41a2422` eller senare
3. Skapa **ny** branch från `master` för nästa uppgift
4. Behandla tidigare migrationsarbete som avslutat

## Troliga nästa arbetsområden

Detta är **inte blockerade restpunkter** från den nyss avslutade kedjan, utan bara rimliga nästa kandidater:

1. **Champion-promotion / post-freeze-arbete**
   - Om relevant, använd redan existerande analysunderlag
   - Var fortsatt försiktig med `config/strategy/champions/**` om freeze-regler fortfarande gäller

2. **Övriga feature-spår som inte hör till denna kedja**
   - Exempelvis `feature/Optuna-Phased-v4` om det är nästa prioritet

3. **Vanligt underhåll / cleanup**
   - Bara som nya, separata, scoped uppgifter från `master`

## Beslutslogg i en mening

Allt som behövdes från ledger-v1-, flaky-fix- och regime-intelligence-migration-spåren är nu infört i `master`; dessa brancher är avslutade och nästa session ska fortsätta från `master` med en ny branch.
