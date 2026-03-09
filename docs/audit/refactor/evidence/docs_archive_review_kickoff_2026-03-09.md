# Docs Archive Review – Kickoff (2026-03-09)

## Scope (read-only kickoff)

- In-scope: `docs/archive/**` (inventering och riskklassning)
- Out-of-scope: kod, runtime-konfig, scripts, produktionstexter utanför arkiv
- Constraint: NO BEHAVIOR CHANGE

## Baslinje

- Aktiv branch: `feature/docs-archive-review-2026-03-09`
- Arbetsyta vid start: ren

## Inventering

- Total filer i `docs/archive`: **127**
- Filtyper:
  - `.md`: **123**
  - `.py`: **2**
  - `.ipynb`: **2**

Top-level fördelning:

- `deprecated_2026-02-24`: 119
- `phase6`: 5
- `CHANGELOG-legacy.md`: 1
- `original_genesis`: 1
- `STRATEGY_SPEC_phase3.md`: 1

## Identifierade riskobjekt

Icke-markdownfiler (historiska analysfiler) under:

- `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_analysis.ipynb`
- `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_analysis.py`
- `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_v4_analysis.ipynb`
- `docs/archive/deprecated_2026-02-24/docs/analysis/optimization_v4_analysis.py`

Riskklassning (kickoff):

- `.md` i archive: **Låg**
- `.ipynb` i archive: **Medel** (binära artefakter, svårare diffbarhet)
- `.py` i archive: **Medel/Hög** (körbar text, kan misstolkas som aktivt material)

## Externa referenser (utanför `docs/archive/**`)

Bekräftade aktiva referenser till arkivmarker:

- `.cursor/rules/README.md` -> `docs/archive/CHANGELOG-legacy.md`
- `.cursor/rules/architecture.md` -> `docs/archive/CHANGELOG-legacy.md`
- `CHANGELOG.md` -> `docs/archive/CHANGELOG-legacy.md`

Övriga träffar domineras av tidigare audit/manifest-evidens under `docs/audit/refactor/**`.

## Förslag nästa batch (föreslagen)

1. **Batch D1 (safe docs hygiene):**
   - Read-only kvalitetsgranskning av `phase6/*.md` + top-level `CHANGELOG-legacy.md`/`STRATEGY_SPEC_phase3.md`.
   - Kontrollera intern länk-konsistens och om marker-texter fortfarande stämmer.

2. **Batch D2 (archive non-md curation plan):**
   - Ta fram exakt old->new-manifest för 4 non-md-filer till tydlig karantän/curated-struktur inom `docs/archive`.
   - Kör referenscheck före flytt (förväntan: inga aktiva beroenden).

3. **Batch D3 (execution, om godkänt):**
   - Genomför rena rename/move utan innehållsändringar.
   - Verifiera att externa referenser till `CHANGELOG-legacy.md` förblir intakta.
