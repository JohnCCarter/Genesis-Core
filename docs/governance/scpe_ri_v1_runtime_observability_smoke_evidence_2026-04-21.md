# SCPE RI V1 runtime-observability smoke evidence

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
Status: `smoke-run-completed / evidence-captured`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/*`
- **Category:** `obs`
- **Risk:** `LOW` — bounded observationskontroll av en redan implementerad opt-in-yta utan kodändring
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** verifiera bounded opt-in-paritet för `/strategy/evaluate` över tre request-varianter med identisk baspayload
- **Candidate:** `SCPE RI runtime observability smoke/evidence lane`
- **Base SHA:** `6b399064`
- **Skill Usage:** repo-local `python_engineering` användes som kör-/kvalitetsguardrail; ingen ny implementation eller scope-utvidgning gjordes här

### Scope

- **Scope IN:**
  - en kort smoke-körning mot `/strategy/evaluate` via `fastapi.testclient.TestClient`
  - `artifacts/diagnostics/scpe_ri_v1_runtime_observability_smoke_2026-04-21.json`
  - `docs/governance/scpe_ri_v1_runtime_observability_smoke_evidence_2026-04-21.md`
- **Scope OUT:**
  - alla kodändringar under `src/**`, `tests/**`, `config/**`, `scripts/**`
  - alla ändringar i `docs/governance/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md`
  - readiness-, promotion-, paper-shadow-, router/policy- eller behavior-change-tolkningar
- **Expected changed files:**
  - `artifacts/diagnostics/scpe_ri_v1_runtime_observability_smoke_2026-04-21.json`
  - `docs/governance/scpe_ri_v1_runtime_observability_smoke_evidence_2026-04-21.md`
- **Max files touched:** `2`

### Gates required

- bounded smoke execution against `/strategy/evaluate`
- file-scoped validation on the two new files only

### Stop Conditions

- någon skillnad mellan `state = {}` och `state = {"observability": {"scpe_ri_v1": false}}` på bounded projection
- `meta["observability"]["scpe_ri_v1"]` närvarande utan opt-in
- avvikande allowlist/form på `meta["observability"]["scpe_ri_v1"]` när opt-in är `true`
- varje formulering som antyder readiness, promotion eller policybedömning

## Observation scope

Denna smoke-körning är en begränsad observationskontroll av `/strategy/evaluate` för tre request-varianter med identisk baspayload. Resultatet verifierar endast bounded opt-in-paritet/nyckelnärvaro i denna enskilda kontroll och innebär ingen readiness-, promotion- eller policybedömning.

## Smoke setup

Tre varianter kördes mot samma baspayload:

1. `state = {}`
2. `state = {"observability": {"scpe_ri_v1": false}}`
3. `state = {"observability": {"scpe_ri_v1": true}}`

Maskinläsbar artifact:

- `artifacts/diagnostics/scpe_ri_v1_runtime_observability_smoke_2026-04-21.json`

## Bounded outcomes

### Transportnivå

- alla tre varianter returnerade `status_code = 200`
- `absent == false` på transportnivå

### Default-off parity

- `result.action` var `NONE` för både `absent` och `false`
- `meta["observability"]["shadow_regime"]` hade identisk bounded projection för `absent` och `false`
- `meta["observability"]["scpe_ri_v1"]` saknades för både `absent` och `false`

### Opt-in true

När `state["observability"]["scpe_ri_v1"] = true`:

- `meta["observability"]["scpe_ri_v1"]` var närvarande
- payloaden bar fortsatt observationskaraktär:
  - `family_tag = "ri"`
  - `lane = "runtime_observability"`
  - `observational_only = true`
  - `decision_input = false`
  - `enabled_via = "state.observability.scpe_ri_v1"`
- regimvärdena i den nya payloaden speglade den bounded `shadow_regime`-observationen i denna körning:
  - `authority_mode = "legacy"`
  - `authority_mode_source = "default_legacy"`
  - `authoritative_regime = "balanced"`
  - `shadow_regime = "balanced"`
  - `regime_mismatch = false`

## Evidence summary

Artifactens parity-flaggor blev alla gröna:

- `status_code_absent_equals_false = true`
- `result_action_absent_equals_false = true`
- `shadow_projection_absent_equals_false = true`
- `ri_payload_absent_omitted = true`
- `ri_payload_false_omitted = true`
- `ri_payload_true_present = true`

## Commands run

- en kort Python-körning via `TestClient(app)` som postade tre request-varianter till `/strategy/evaluate` och serialiserade endast bounded projection till artifact-innehållet

## Notes

- Artifacten `artifacts/diagnostics/scpe_ri_v1_runtime_observability_smoke_2026-04-21.json` ligger i en ignorerad output-zon och hölls därför lokal i denna lane; rapporten ovan är skriven för att vara självbärande utan att force-add:a genererade outputs till git.
- Den redan smutsiga filen `docs/governance/scpe_ri_v1_runtime_observability_slice1_implementation_report_2026-04-21.md` lämnades orörd och utanför scope.
- Ingen kod, inga tester och ingen runtime-konfiguration ändrades i denna smoke/evidence-lane.
