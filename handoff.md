# HANDOFF — Genesis-Core till hemdator / nästa Copilot-session

Senast uppdaterad: 2026-03-17

## Kort lägesbild

- **Aktiv branch nu:** `master`
- **HEAD:** `6205f202`
- **Repo-status:** ren working tree
- **Senaste viktiga commits på `master`:**
  1. `6205f202` — `merge(test): add decide() scenario behavior coverage`
  2. `85f6603f` — `merge(test): add RI decision seam contract coverage`
  3. `b41a2422` — `refactor(server): extract deterministic regime intelligence layer`
  4. `003fef58` — `feat(research-ledger): add canonical ledger substrate`

## Vad som är klart

Följande arbetskedjor är **fullbordade och införda i `master`**:

1. **Research Ledger v1-substrat infört**
   - Package under `src/core/research_ledger/`
   - Fokuserade tester under `tests/core/research_ledger/`
   - Auditunderlag under `docs/audit/research_ledger/`

2. **Regime Intelligence-lagret extraherat och mergat**
   - Package under `src/core/intelligence/regime/`
   - Legacy-kompatibilitet finns fortfarande via `src/core/strategy/regime_intelligence.py`
   - Shadow-observability täcks av `tests/backtest/test_regime_shadow_artifacts.py`

3. **Direkt seam coverage för RI-känsliga beslutssömmar införd**
   - `tests/utils/test_decision_sizing.py`
   - `tests/utils/test_decision_gates_contract.py`
   - `tests/utils/test_decision_fib_gating_contract.py`
   - CI false positive för governance-hashar hanterad via `.secrets.baseline`

4. **Scenario-nära full-path coverage för `decide()` införd**
   - `tests/utils/test_decision_scenario_behavior.py`
   - Täcker:
     - RI risk-state stress utan action-drift
     - transition-window recovery via propagated state
     - adaptiv HTF/LTF override-progression över flera `decide()`-anrop

## Brancher som redan är mergade och bortstädade

Följande brancher **finns inte längre** som aktiva arbetsbrancher och ska inte återupplivas utan särskilt skäl:

- `feature/research-ledger-v1` → mergad, remote deleted, local deleted
- `feature/regime-intelligence-layer-migration` → mergad, remote deleted, local deleted
- `feature/regime-intelligence-value-behavior-tests-v1` → mergad, remote deleted, local deleted
- `feature/regime-intelligence-scenario-behavior-tests-v1` → mergad, remote deleted, local deleted

## Viktiga verifieringar som passerat i den senaste RI-testkedjan

Före merge av de två senaste test-PR:erna passerade bland annat:

- `python -m pytest -q tests/utils/test_decision.py tests/utils/test_decision_sizing.py tests/utils/test_decision_scenario_behavior.py`
- `python -m pytest -q tests/utils/test_decision_scenario_behavior.py tests/utils/test_decision_fib_gating_contract.py`
- `python -m pytest -q tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/utils/test_feature_cache.py`
- `pre-commit run --files tests/utils/test_decision_scenario_behavior.py`

## Det viktigaste för nästa Copilot på hemdatorn

### Du ska utgå från detta

- Börja från **`master`**.
- Anta att följande nu redan är **klart och mergat**:
  - Research Ledger v1-substratet
  - RI layer-migrationen
  - RI decision seam contract coverage
  - RI `decide()` scenario behavior coverage

### Du ska inte göra detta igen

- Återskapa inte `feature/regime-intelligence-value-behavior-tests-v1`
- Återskapa inte `feature/regime-intelligence-scenario-behavior-tests-v1`
- Försök inte åter-mergea decision seam-slicen eller scenario-slicen igen
- Lägg inte mer tid på fler helper-lågnivåtester för `decide()` om inte en ny konkret regression kräver det

## Viktiga filer som nu är kanoniska att känna till för detta område

### Regime Intelligence / runtime-ytor

- `src/core/intelligence/regime/__init__.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/intelligence/regime/clarity.py`
- `src/core/intelligence/regime/contracts.py`
- `src/core/intelligence/regime/htf.py`
- `src/core/intelligence/regime/risk_state.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/decision_fib_gating.py`

### Testytor att lita på för RI beslutskedja

- `tests/backtest/test_regime_shadow_artifacts.py`
- `tests/governance/test_regime_intelligence_cutover_parity.py`
- `tests/utils/test_decision.py`
- `tests/utils/test_decision_sizing.py`
- `tests/utils/test_decision_gates_contract.py`
- `tests/utils/test_decision_fib_gating_contract.py`
- `tests/utils/test_decision_scenario_behavior.py`

## Om du fortsätter arbetet hemma: rekommenderad startpunkt

1. Hämta senaste `master`
2. Verifiera att HEAD är `6205f202` eller senare
3. Skapa **ny** branch från `master` för nästa uppgift
4. Behandla seam- och `decide()`-scenarioarbetet som avslutat

## Rekommenderat nästa arbetsområde

Den mest logiska fortsättningen är **ett lager upp** i kedjan:

### Ny rekommenderad branch

- `feature/regime-intelligence-pipeline-scenario-tests-v1`

### Första rekommenderade slice

- Scenario-nära tester på **`evaluate_pipeline`-nivå**
- Fokusera på att verifiera att RI sizing-/observability-beteende håller genom hela pipeline-flödet, inte bara via handbyggda `decide()`-inputs

### Vad första slicen bör försöka bevisa

- baseline vs RI-stressad pipeline-körning ger samma `action` där det ska vara sizing-only
- `size` påverkas där risk-state / clarity ska påverka sizing
- exported RI-observability finns och förblir konsekvent i pipeline-resultatet
- inga oväntade pipeline-drifter i reason-/action-path

## Beslutslogg i en mening

RI-arbetet på `decide()`-nivå är nu väl täckt och mergat; nästa session bör börja från `master` på en ny branch och flytta upp testningen till `evaluate_pipeline`-/systemnivå.
