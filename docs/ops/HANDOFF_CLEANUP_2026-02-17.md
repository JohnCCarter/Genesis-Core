# Handoff — Repo Cleanup (2026-02-17)

## Syfte

Detta dokument sammanfattar aktuell status i cleanup-spåret (Fas C) och beskriver hur arbetet fortsätter hemma med samma governance-disciplin (Codex 5.3 + Opus 4.6).

## Baseline (verifierad)

- Branch: `feature/composable-strategy-phase2`
- Senaste pushade commit: `2e5782e` (`tooling: C8 move stale compare scripts`)
- Senaste trancher i ordning:
  - `dddb476` C1
  - `58c7815` C2
  - `13f74a9` C3
  - `5935e36` C4
  - `878495e` C5
  - `b692565` C6
  - `b865431` C7 (evidence-classifier)
  - `2e5782e` C8

## Genomfört i Fas C hittills

- Arkiverade/flyttade scripts: **24 st**
- Raderade scripts i Fas C: **0 st** (move-only)
- Extra tooling infört: `scripts/classify_script_activity.py` (C7)

## Kvarvarande lokala filer (carry-forward)

`git status --porcelain` visar följande fyra:

1. `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md` (modified)
2. `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md` (untracked)
3. `reports/script_activity_latest.json` (untracked)
4. `reports/script_activity_latest.md` (untracked)

## Rekommenderad hantering av de fyra filerna

Välj ett av dessa spår innan C9:

- Behåll som carry-forward (ostagade) och fortsätt direkt med C9.
- Gör separat docs/artefakt-commit om du vill nollställa arbetsytan.
- Kassera lokala `reports/*` om de endast var tillfälligt analysunderlag.

## Arbetssätt som ska fortsätta (governance)

### 1) Commit-kontrakt först

Varje tranche ska ha:

- Category (`tooling` i cleanup-fall)
- Scope IN/OUT med exakt fillista
- Constraints (default: `NO BEHAVIOR CHANGE`)
- Required gates (BEFORE + AFTER)
- Stop condition
- Done criteria

### 2) BEFORE-gates

Minimikrav:

- pre-commit/lint
- smoke test
- determinism replay
- feature-cache invariance
- pipeline invariant
- scope/reference checks

### 3) Opus pre-code review

Ingen implementation innan `APPROVED`.

### 4) Implementation (minimal diff)

- Endast scopeade filer
- Move-only i cleanup-trancher
- Inga opportunistiska sidofixar

### 5) AFTER-gates

Samma gate-stack igen + verifierad scope/reference-status.

### 6) Opus post-code diff-audit

Måste vara `APPROVED` före commit/push.

### 7) Commit + push

- Staga endast Scope IN
- Lämna carry-forward utanför staging

## Statusspråk i docs (disciplin)

- `föreslagen` = inte implementerat/verifierat ännu
- `införd` = implementerat och verifierat i repo

## Startpunkt hemma (praktiskt)

1. Pull/synka branch `feature/composable-strategy-phase2`.
2. Kontrollera att baseline matchar commit `2e5782e`.
3. Ta aktivt beslut om de fyra kvarvarande filerna.
4. Starta C9 med nytt tranche-kontrakt + Opus pre-review.

## Notering

Allt ovan är avsett att ge en säker återstart utan att tappa governance-spårbarhet eller scope-disciplin.
