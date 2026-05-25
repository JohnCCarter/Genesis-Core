# Scripts i Genesis-Core

Status: `current scripts lifecycle guide / operational taxonomy pointer / docs-only`

> Current status note (2026-05-22, `feature/genesis-topology-lifecycle-authority-map`): this
> README describes the current `scripts/` taxonomy and lifecycle reading in the checked-in tree.
> It does not by itself authorize runtime changes, archive moves, or wrapper-based compatibility
> policy. For repo-wide placement rules, see `docs/repository-layout-policy.md`.

Detta dokument beskriver hur script i `scripts/` organiseras och hur deras livscykel ska läsas i
nuvarande repo.

## Kategorier

- **purpose-based subfolders**
  - Den primära modellen i aktuell tree är att script grupperas efter uppgift, till exempel
    `analyze/`, `audit/`, `build/`, `deploy/`, `extract/`, `fetch/`, `mcp/`, `ops/`, `optimize/`,
    `preflight/`, `promote/`, `run/`, `train/` och `validate/`.
- **root-level helper entrypoints**
  - Ett litet antal script ligger fortfarande direkt under `scripts/` som kvarhållna helper- eller
    entrypoint-ytor. Dessa ska behandlas som explicita undantag, inte som standardmönster.
- **docs**
  - `scripts/docs/` beskriver scripts-zonen och ska spegla den aktuella taxonomin i tree.
- **historical / archive-prep**
  - Historiska eller avvecklingskandidater ska först behandlas i en separat bounded audit/move-slice.
    Utgå inte från att wrapper-baserad kompatibilitet finns eller ska skapas som default.

## Aktuell lifecycle-regel

1. **Föredra canonical purpose-based placement.**
2. Om ett aktivt script hör hemma i en annan scripts-undermapp, flytta det direkt till den
   canonical platsen i samma slice.
3. **Skapa inte wrappers, mappings eller duplicerade launchers som default.** Sådana kräver
   explicit motivering och ska inte antas bara för att ett path byts.
4. Behandla archive/deprecation som en separat bounded lifecycle-slice med referenskontroll, inte
   som en implicit wrapper-rutin.
5. Låt dokumentation bara peka på verktyg och flöden som faktiskt finns i den checkade tree:n.

## Hur scripts-zonen ska auditeras just nu

Det finns för närvarande ingen checkad repo-bred lifecycle-CLI på de gamla namnen
`scripts/audit_scripts.py` eller `scripts/deprecate_move.py`.

Använd i stället en bounded audit-metod:

- läs aktuell taxonomi i `scripts/` och `scripts/docs/README.md`
- verifiera repo-regler i `docs/repository-layout-policy.md`
- gör fokuserad referenssökning för den kandidat eller undermapp som granskas
- skriv resultatet i en bounded `docs/audit/**`-yta när slice-storleken kräver det

## Rekommenderat arbetssätt

1. Inventera den aktuella kandidatens funktion, referenser och nuvarande hemvist.
2. Avgör om scriptet ska:
   - stanna kvar där det är,
   - flyttas direkt till en canonical purpose-based undermapp, eller
   - tas upp i en separat archive-prep-slice.
3. Om ett aktivt script flyttas: uppdatera referenser och docs i samma bounded slice.
4. Om ett script ser historiskt ut: gör först referens- och lineage-kontroll innan någon archive-
   eller delete-diskussion öppnas.
5. Validera berörda docs, anrop och verifieringsytor efter varje lifecycle-ändring.

## Archive-prep checklista

Öppna inte archive/move bara för att ett script ser gammalt ut. Kontrollera minst att:

1. aktuell referensyta är liten nog att uppdatera sanningsenligt
2. ingen aktiv docs-, test-, scheduler-, CI- eller operativ väg fortfarande kräver gamla pathen
3. destinationen är en explicit icke-aktiv historisk yta
4. historisk/provenance-dokumentation uppdateras sanningsenligt i samma slice eller i en tydligt
   kopplad uppföljning
