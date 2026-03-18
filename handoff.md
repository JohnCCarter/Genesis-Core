# HANDOFF — Genesis-Core till hemdator / nästa Copilot-session

Senast uppdaterad: 2026-03-18

> Detta dokument är en transient operativ handoff/statussnapshot för en specifik tidpunkt och maskinkontext. Det är inte en governance authority source och får inte överstyra aktuell repo-status eller högre ordningens styrdokument, inklusive `.github/copilot-instructions.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md` och `AGENTS.md`. Verifiera alltid branch, HEAD och working-tree-status direkt i aktuell arbetskopia innan påståenden i detta dokument används.

## Kort lägesbild

- **Aktiv branch nu:** `master`
- **HEAD:** `4881b86a`
- **Senaste verifierade remote HEAD:** `4881b86a` (`origin/master`)
- **Repo-status på denna maskin:** arbetskopian är **inte ren**; det finns omfattande lokala deletioner under `config/**` som inte ska tolkas som mergat repo-läge utan som lokal working-tree-state på denna dator.
- **Det säkra repo-läget att utgå från för nästa session:** senaste `origin/master` vid `4881b86a`
- **Senaste viktiga commits på `master`:**
  1. `4881b86a` — `docs(handoff): update RI test campaign status`
  2. `1c2f38ad` — `refactor(regime): close RI shim migration`
  3. `d58fe2f0` — `test: add research system integration verification`
  4. `c937bdb1` — `api: add research orchestrator v1 slice`
  5. `6520b85a` — `api: add parameter intelligence v1 slice`
  6. `1d958946` — `api: implement intelligence ledger adapter`
  7. `5dc9b4de` — `api: implement intelligence processing stages`
  8. `4b5ff08b` — `api(intelligence): scaffold deterministic pipeline contracts`

## Vad som är klart

Följande arbetskedjor är **fullbordade och införda i `master`**:

1. **Research Ledger v1-substrat infört**
   - Package under `src/core/research_ledger/`
   - Fokuserade tester under `tests/core/research_ledger/`
   - Auditunderlag under `docs/audit/research_ledger/`

2. **Intelligence-grunden är införd, inte bara prepad**
   - Kanoniska event-/validator-kontrakt under `src/core/intelligence/events/`
   - Paketgränser för `collection`, `normalization`, `features`, `evaluation`, `ledger_adapter`
   - Prep-specarna under `docs/intelligence/` är fortfarande viktiga boundary-docs, men repo:t innehåller nu också faktisk implementation ovanpå dem

3. **Deterministiska intelligence processing stages är införda**
   - `src/core/intelligence/collection/processing.py`
   - `src/core/intelligence/normalization/processing.py`
   - `src/core/intelligence/features/processing.py`
   - `src/core/intelligence/evaluation/processing.py`
   - Täcks av `tests/intelligence/test_pipeline_processing.py`

4. **Intelligence ledger adapter är införd**
   - `src/core/intelligence/ledger_adapter/processing.py`
   - Deterministisk översättning från `ValidatedIntelligenceEvent` till Research Ledger-artifact records
   - Täcks av `tests/intelligence/test_ledger_adapter_contracts.py` och `tests/intelligence/test_ledger_adapter_processing.py`

5. **Parameter Intelligence v1 är införd**
   - `src/core/intelligence/parameter/`
   - Advisory-only analyslager, inte runtime-mutation
   - Täcks av `tests/intelligence/test_parameter_intelligence.py`

6. **Research Orchestrator v1 är införd**
   - `src/core/research_orchestrator/`
   - Ligger ovanpå intelligence-/ledger-fundamentet
   - Täcks av `tests/research_orchestrator/test_workflow.py`

7. **Regime Intelligence-lagret är extraherat och runtime-closure är genomförd**
   - Package under `src/core/intelligence/regime/`
   - `src/core/intelligence/regime/risk_state.py` är nu kanonisk RI risk-state-yta
   - Legacy-shimmen `src/core/strategy/regime_intelligence.py` är **borttagen**
   - Runtime går via kanoniska intelligence/config-helpers i stället för via shim-lager
   - Shadow-observability täcks fortsatt av `tests/backtest/test_regime_shadow_artifacts.py`

8. **RI seam- och scenario-coverage för beslutskedjan är införd**
   - `tests/utils/test_decision_sizing.py`
   - `tests/utils/test_decision_gates_contract.py`
   - `tests/utils/test_decision_fib_gating_contract.py`
   - `tests/utils/test_decision_scenario_behavior.py`

9. **Research system integration verification är införd som test-slice**
   - Integrationskontroller för orchestrator, ledger roundtrip, parameter intelligence och workflow finns under `tests/integration/`
   - Detta var en verifierings-/testslice, inte en runtime-arkitekturomläggning

## Viktig governance-nyans

Det här måste hållas isär:

- **Implementation/fundament:** intelligence-lagret och RI runtime-closure är i praktiken införda i `master`
- **RI default cutover-governance:** fortfarande **inte** automatiskt liktydigt med “färdig default-promotion”

Nuvarande säkra tolkning är:

- RI opt-in path finns
- RI shim-retirement i runtime är genomförd
- default `authority_mode` ska fortfarande behandlas som **legacy** tills uttrycklig governance säger annat
- parity/provenance-dokumenten kring P1 OFF måste fortfarande respekteras som governance-underlag

## Brancher som redan är mergade och bortstädade

Följande brancher **finns inte längre** som aktiva arbetsbrancher och ska inte återupplivas utan särskilt skäl:

- `feature/research-ledger-v1` → mergad, remote deleted, local deleted
- `feature/regime-intelligence-layer-migration` → mergad, remote deleted, local deleted
- `feature/regime-intelligence-value-behavior-tests-v1` → mergad, remote deleted, local deleted
- `feature/regime-intelligence-scenario-behavior-tests-v1` → mergad, remote deleted, local deleted
- `feature/research-system-integration-v1` → mergad, remote deleted, local deleted
- `feature/regime-intelligence-migration-closure-v1` → mergad, remote deleted, local deleted

## Viktiga verifieringar som passerat

Följande verifieringsytor har explicit passerat i de relevanta slicarna:

- RI beslutskedja / seams / scenario-beteende:
  - `tests/utils/test_decision.py`
  - `tests/utils/test_decision_sizing.py`
  - `tests/utils/test_decision_gates_contract.py`
  - `tests/utils/test_decision_fib_gating_contract.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- RI runtime-/pipeline-invarianter:
  - `tests/backtest/test_evaluate_pipeline.py`
  - `tests/backtest/test_evaluate_regime_precomputed_index.py`
  - `tests/backtest/test_regime_shadow_artifacts.py`
  - `tests/governance/test_authority_mode_resolver.py`
  - `tests/governance/test_phase2_merge_authority_bypass_contracts.py`
  - `tests/governance/test_regime_intelligence_cutover_parity.py`
- Intelligence foundation / stages / adapter / parameter:
  - `tests/intelligence/test_event_schema.py`
  - `tests/intelligence/test_stage_contracts.py`
  - `tests/intelligence/test_pipeline_processing.py`
  - `tests/intelligence/test_ledger_adapter_contracts.py`
  - `tests/intelligence/test_ledger_adapter_processing.py`
  - `tests/intelligence/test_parameter_intelligence.py`
- Cross-cutting guardrails:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/utils/test_feature_cache.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `pre-commit run --all-files`

## Det viktigaste för nästa Copilot på hemdatorn

### Du ska utgå från detta

- Börja från **senaste `master` / `origin/master`**.
- Verifiera att HEAD är **`4881b86a` eller senare**.
- Anta att följande nu redan är **klart och mergat**:
  - Research Ledger v1-substratet
  - Intelligence kontrakts-/eventgrund
  - Intelligence processing stages
  - Intelligence ledger adapter
  - Parameter Intelligence v1
  - Research Orchestrator v1
  - RI shim-retirement / runtime-closure
  - RI seam- och scenario-coverage
  - Research system integration verification

### Du ska inte göra detta igen

- Återskapa inte redan mergade RI testbrancher eller closure-brancher
- Bygg inte om `src/core/intelligence/**` som om det bara vore prep-skelett
- Återinför inte `src/core/strategy/regime_intelligence.py`
- Lägg inte ny runtime-logik bakom ett nytt shim-lager när kanoniska intelligence-/config-moduler redan finns
- Tolka inte handoff- eller March sign-off-text som att default RI cutover därmed är governance-godkänd om inte aktuell governance-slice uttryckligen säger det

## Viktiga filer som nu är kanoniska att känna till

### Intelligence foundation

- `src/core/intelligence/events/models.py`
- `src/core/intelligence/events/validators.py`
- `src/core/intelligence/collection/interface.py`
- `src/core/intelligence/collection/processing.py`
- `src/core/intelligence/normalization/interface.py`
- `src/core/intelligence/normalization/processing.py`
- `src/core/intelligence/features/interface.py`
- `src/core/intelligence/features/processing.py`
- `src/core/intelligence/evaluation/interface.py`
- `src/core/intelligence/evaluation/processing.py`
- `src/core/intelligence/ledger_adapter/interface.py`
- `src/core/intelligence/ledger_adapter/processing.py`
- `src/core/intelligence/parameter/interface.py`
- `src/core/intelligence/parameter/processing.py`

### Regime Intelligence / runtime-ytor

- `src/core/intelligence/regime/__init__.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/intelligence/regime/clarity.py`
- `src/core/intelligence/regime/contracts.py`
- `src/core/intelligence/regime/htf.py`
- `src/core/intelligence/regime/risk_state.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/decision_fib_gating.py`

### Ovanpåliggande orchestration

- `src/core/research_orchestrator/models.py`
- `src/core/research_orchestrator/orchestrator.py`
- `src/core/research_orchestrator/workflow.py`

### Testytor att lita på

- `tests/backtest/test_regime_shadow_artifacts.py`
- `tests/backtest/test_evaluate_pipeline.py`
- `tests/governance/test_regime_intelligence_cutover_parity.py`
- `tests/utils/test_decision.py`
- `tests/utils/test_decision_sizing.py`
- `tests/utils/test_decision_gates_contract.py`
- `tests/utils/test_decision_fib_gating_contract.py`
- `tests/utils/test_decision_scenario_behavior.py`
- `tests/intelligence/test_event_schema.py`
- `tests/intelligence/test_stage_contracts.py`
- `tests/intelligence/test_pipeline_processing.py`
- `tests/intelligence/test_ledger_adapter_contracts.py`
- `tests/intelligence/test_ledger_adapter_processing.py`
- `tests/intelligence/test_parameter_intelligence.py`
- `tests/research_orchestrator/test_workflow.py`

## Om du fortsätter arbetet hemma: rekommenderad startpunkt

1. Hämta senaste `master`
2. Verifiera att HEAD är `4881b86a` eller senare
3. Säkerställ **ren working tree** innan ny branch skapas; ignorera inte lokala deletioner under `config/**` på denna maskin utan avgör först om de ska resetas eller sparas separat
4. Skapa **ny** branch från `master` för nästa uppgift
5. Behandla prep-fasen för intelligence som passerad; bygg ovanpå befintliga kanoniska moduler
6. Behandla RI shim-retirement och `decide()`-scenarioarbetet som avslutat

## Rekommenderat nästa arbetsområde

Det mest logiska nästa steget beror på om fokus är **RI runtime-beteende** eller **bredare intelligence-system**.

### Om fokus är RI runtime / systembeteende

- Fortsätt ett lager upp på **`evaluate_pipeline`-nivå**
- Verifiera sizing-only invariants, observability shape och frånvaro av action-drift genom hela pipeline-flödet
- Rimlig branch-idé: `feature/regime-intelligence-pipeline-scenario-tests-v1`

### Om fokus är intelligence-systemet bredare

- Utgå från att contracts/stages/ledger-adapter/parameter/orchestrator redan finns
- Nästa arbete bör ske ovanpå dessa lager, inte genom att återskapa prep-kontrakt eller duplicera lokala schemas
- Håll advisory-only-/determinism-/boundary-reglerna intakta

## Beslutslogg i en mening

Repo:t har nu passerat ren intelligence-prep: det finns ett infört deterministiskt intelligence-fundament, RI runtime-shimmen är pensionerad, och nästa säkra steg ska bygga vidare ovanpå `master` utan att backa in i gamla prep- eller shim-spår.
