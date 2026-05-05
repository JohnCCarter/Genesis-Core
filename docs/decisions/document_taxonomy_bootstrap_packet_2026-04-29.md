# Document taxonomy bootstrap packet — 2026-04-29

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `LOW`
- **Required Path:** `Lite`
- **Lane:** `Concept` — cheapest admissible lane because this slice only bootstraps documentation placement and does not migrate or reinterpret runtime surfaces
- **Skill Usage:** `repo_clean_refactor` — repository-local documentation structure/taxonomy work under no-behavior-change constraints
- **Objective:** Bootstrap a forward-looking documentation taxonomy for new materials only. This slice does **not** migrate, rename, or reclassify historical documents, and it does **not** alter governance authority or runtime behavior.
- **Candidate:** `N/A`
- **Base SHA:** `23314c1e`

### Lane framing

#### Concept lane

- **Hypotes / idé:** Genesis blir lättare att styra och söka i om governance, contracts, decisions och research/evidence får tydligare framåtriktade hemvister.
- **Varför det kan vara bättre:** Det minskar authority-drift, gör governance-review billigare och hjälper både människor och agenter att skilja mellan beslut, bevis och experiment.
- **Vad skulle falsifiera idén:** Om de nya zonerna inte går att beskriva utan att omedelbart kräva en stor historikmigrering eller om den nya taxonomin skapar mer oklarhet än den tar bort.
- **Billigaste tillåtna ytor:** `docs/README.md`, `docs/decisions/**`, `docs/contracts/**`, `docs/governance/README.md`, `docs/analysis/README.md`, `results/research/README.md`
- **Nästa bounded evidence-steg:** Börja använda den nya taxonomin för nya dokument; eventuell historikmigrering får vara en separat godkänd slice senare.

### Scope

- **Scope IN:**
  - skapa `docs/README.md`
  - skapa `docs/decisions/README.md`
  - skapa `docs/contracts/README.md`
  - skapa `results/research/README.md`
  - skapa detta bootstrap-packet under `docs/decisions/`
  - uppdatera `docs/governance/README.md`
  - uppdatera `docs/analysis/README.md`
- **Scope OUT:**
  - inga runtime-/kod-/configändringar
  - inga historiska filflyttar eller massmigreringar
  - ingen `.gitignore`-, CI- eller enforcement-ändring
  - inga strict-only surfaces
- **Expected changed files:** `7`
- **Max files touched:** `7`

### Gates required

- `pre-commit run --files docs/README.md docs/decisions/README.md docs/contracts/README.md results/research/README.md docs/decisions/document_taxonomy_bootstrap_packet_2026-04-29.md docs/governance/README.md docs/analysis/README.md`
- `git diff --stat`
- `git diff`
- focused manual review of wording and local references in touched README files

### Stop Conditions

- scope drift beyond the seven named docs files
- wording that implies governance authority moved or migration completed
- any need to repair `.gitignore` or CI in order to finish the slice
- any request to reinterpret runtime/default/champion surfaces through this taxonomy bootstrap

### Non-goals

- no migration completed
- no historical file relocation
- no governance authority moved
- no attempt to deduplicate or archive historical packets in this slice
- no claim that all existing docs already follow the new taxonomy

### Output required

- implementation report with exact files changed
- explicit note if any file required force-add due to existing ignore rules
- scope containment proof via `git diff --stat`
