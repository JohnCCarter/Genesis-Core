# Terminal Tool Access Playbook (2026-02-14)

## Syfte

Stabilisera arbetssättet när chattagenten tillfälligt saknar terminalåtkomst, trots att lokal terminal fungerar.

Detta är en **operativ process-rutin** (docs-only) och ändrar inte runtime-kod, API-kontrakt eller CI-beteende.

## Scope

- Gäller Codex/Opus-flöden i VS Code chattsessioner.
- Gäller incidenttyp: “terminal command tool unavailable/disabled” i agent-session.

## Detektion

Incident anses inträffad när något av följande observeras:

1. Agenten får explicit fel att terminalverktyg är avstängt/otillgängligt.
2. Samma kommando fungerar manuellt i lokal terminal men inte via agentkörning.
3. Problemet sammanfaller med mode-/handoff-/reload-övergång.

## Triage (snabb klassificering)

1. **Session/behörighet**: Är det en tillfällig verktygsbegränsning i aktuell chatt?
2. **Mode-lås**: Är konversationen i Plan-läge när implementation krävs?
3. **Miljö-lås**: Fungerar kommandon lokalt i terminaln ändå?

Målet är att särskilja **chattsession-begränsning** från faktisk lokal miljöstörning.

## Fallback-flöde

1. Verifiera lokalt med ett simpelt kommando (t.ex. git-status).
2. Reload av VS Code-fönster.
3. Säkerställ rätt agent/mode för implementation.
4. Om terminalverktyg fortfarande är otillgängligt i chatten:
   - fortsätt via read-only kontroller i chatten,
   - kör nödvändiga kommandon manuellt lokalt,
   - återför output till chatten för fortsatt governance-gating.
5. Om tillgängligt: återgå till normal körning (gates + commit-protokoll).

## Verifiering efter återhämtning

Incidenten anses återställd när:

1. Ett enkelt terminalkommando kan köras via agenten.
2. Scope- och gate-kontroller kan genomföras utan workaround.
3. Arbetsflödet återgår till standard: Opus pre-code → implementation → Opus diff-audit → gates → commit.

## Kommunikationsmall (kort)

- “Terminalåtkomst i chatten var tillfälligt blockerad; lokal terminal fungerade.”
- “Fallback användes utan att ändra scope eller governance-krav.”
- “Normal terminalåtkomst verifierad och standardflöde återupptaget.”

## Governance-notering

- Status för processidéer följer fortsatt `föreslagen`/`införd`-disciplin.
- Denna playbook introducerar **ingen** ny blockerande CI/pre-commit-regel.
