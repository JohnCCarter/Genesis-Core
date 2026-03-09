# Shard A — Breadth-first audit av `scripts/**` och `scripts/archive/**` (2026-03-06)

Mode: RESEARCH (source=branch mapping `feature/*`)

## 1) Inventering (full yta)

Källa: `docs/audit/refactor/evidence/shard_a_breadth_inventory_final_2026-03-06.json`

- Total script file count (`scripts/**`): **300**
- Total archive file count (`scripts/archive/**`): **220**
- Non-archive scripts: **80**

## 2) Gruppindelning (pattern/familjer)

Källor:

- `docs/audit/refactor/evidence/shard_a_breadth_grouping_final_2026-03-06.json`
- `docs/audit/refactor/evidence/shard_a_archive_external_refscan_final_summary_2026-03-06.json`
- `docs/audit/refactor/evidence/shard_a_git_history_families_2026-03-06.json`
- `docs/audit/refactor/evidence/jscpd_scripts_final_summary_2026-03-06.json`
- `docs/audit/refactor/evidence/vulture_scripts_2026-03-06.txt`

Högsignal-familjer som granskats:

- Duplicated scripts / near-identical logic
- Wrapper-only scripts
- Legacy experiment scripts
- Obsolete CLI utilities
- Archive scripts replaced by active scripts
- Scripts that appear unused in active surface

## 3) Klassificering per större grupp

### A. Deprecated wrapper family (`archive/deprecated_2026-02`)

- Klass: **REMOVE** (huvuddel), **ALLOWLIST** (2 kvarvarande shim-filer)
- Åtgärdat i denna pass: stor wrapper-batch C borttagen (32 filer) + tidigare batcher i samma shard-flöde.
- Kvarvarande wrapper-only:
  - `archive/deprecated_2026-02/diagnose_optuna_issues.py`
  - `archive/deprecated_2026-02/diagnose_zero_trades.py`
- Bedömning kvarvarande: låg materialitet (2 filer i deprecated-ytan), påverkar inte aktiv runtime-surface.

### B. Archive replaced by active scripts (split-brain risk)

- Klass: **MOVE** / **REFACTOR**
- Status: **åtgärdad i denna pass** genom canonicalization av parity-skript:
  - Aktiv path innehåller nu implementation: `scripts/audit/audit_optuna_objective_parity.py`
  - Archive-kopian borttagen: `scripts/archive/deprecated_2026-02/audit_optuna_objective_parity.py`
- Resultat: `archive_replaced_by_active_count = 0`.

### C. Duplicate / near-identical logic

- Klass: **KEEP (ruled out as low signal)**
- Evidens: `jscpd` final summary visar
  - `clones_detected: 0`
  - `duplicated_lines: 0`
  - `percentage: 0`
- Slutsats: ingen materiell dupliceringsskuld kvar i scripts-ytan.

### D. Legacy experiment scripts (`archive/2026-02`, `archive/debug`, `archive/experiments`, `archive/test_prototypes`)

- Klass: **ALLOWLIST** (bevaras arkiverade)
- Skäl:
  - historiska reproducerbarhets-/forensikvärden
  - flera är dokument-/analysstöd och inte aktiva entrypoints
  - hög churn-kostnad, låg operativ nytta att flytta till aktiv yta

### E. Obsolete CLI utilities (främst i `archive/test_prototypes` + delar av `archive/2026-02/analysis`)

- Klass: **ALLOWLIST**
- Skäl:
  - låg aktiv referensgrad men tydligt historisk experimentkaraktär
  - ändring/rensning ger låg runtime-vinst och kan bryta historisk spårbarhet

### F. Unused-like archive scripts (extern-referenssignal)

- Klass: **KEEP/ALLOWLIST**
- Evidens:
  - `archive_total_files: 220`
  - `archive_unused_like_files: 155` (~70.45%)
- Tolkning:
  - detta är väntat för archive-surface och indikerar inte i sig aktiv teknisk skuld
  - används som signal för prioritering, inte som automatisk borttagningsregel

## 4) Vilka grupper togs bort/refaktorerades i denna pass

- **REMOVED:** `deprecated_wrapper_batch_C` (32 filer) i `archive/deprecated_2026-02`.
- **MOVE/REFACTOR:** parity-script split-brain eliminerad (archive -> active canonicalization).

## 5) Vilka grupper hölls arkiverade avsiktligt

- `archive/2026-02`
- `archive/analysis`
- `archive/debug`
- `archive/experiments`
- `archive/model_registry_update`
- `archive/test_prototypes`

Motivering: historik, reproducerbarhet, och låg marginalnytta/riskbalans för bred borttagning.

## 6) Vilka grupper rulades ut som lågvärde/risk att ändra nu

- Mass-rensning av legacy/prototype-ytor utan separat historikplan (risk > nytta).
- Duplicering som orsak till aktiv skuld (ruled out av `jscpd` = 0).
- Dead-code i scripts via statisk symbolsignal (vulture-rapport tom i denna pass).

## 7) Slutlig signalbedömning

- Unresolved high-signal **duplication**: **Nej** (0 i final `jscpd`).
- Unresolved high-signal **archive->active replacement risk**: **Nej** (parity-split-brain åtgärdad).
- Kvarvarande high-signal obsolete wrappers: **2 st**, klassade som låg-materialitets **ALLOWLIST** i deprecated-archive-surface.

## 8) Shard A completion-gate (bred audit-kriterium)

Den breda audit-kontrollen över `scripts/**` + `scripts/archive/**` är genomförd med evidens och klassificering.

Bedömning: inga **materiella** strukturella opportunities kvar i aktiv scripts-surface. Archive-surface har avsiktligt bevarade historikgrupper samt två låg-materialitets shim-filer i allowlist.
