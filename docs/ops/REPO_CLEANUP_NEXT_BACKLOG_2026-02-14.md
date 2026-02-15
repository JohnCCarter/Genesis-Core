# Repo Cleanup Next Backlog (2026-02-14)

## Syfte

Samla kvarvarande cleanup-kandidater efter D1/D2 och tydliggöra varför nästa
destruktiva steg är högre risk och fortsatt **föreslagna**.

## Kvarvarande kandidatområden

1. `results/hparam_search/**` (stor volym)
2. `results/backtests/*`
3. `scripts/debug_*.py`
4. `scripts/diagnose_*.py`
5. `scripts/test_*.py`

## Riskdrivare

- **Referensdrift:** flera historiska docs refererar uttryckligen till debug/diagnose-script paths.
- **Operativ osäkerhet:** vissa scripts kan fortfarande användas ad hoc i felsökning.
- **Stor diffyta:** `results/**` innebär hög volym och större risk för scope-drift.

## Rekommenderad nästa ordning (föreslagen)

1. D3: kandidatvis referenskartläggning per mönster (read-only rapportering).
2. D4: små, separata move-only commits per artefaktklass.
3. D5: eventuell radering först efter flytt- och retentionbeslut i separata kontrakt.

## Kriterier innan nästa destruktiva steg

1. Tight kontrakt per artefaktklass.
2. Opus pre-code och post-code APPROVED.
3. Explicit godkännande från requester.
4. Inga out-of-scope ändringar i code/runtime-zoner.

## Status

- D3/D4/D5 i denna backlog är fortsatt **föreslagna**.
- Ingen ny destruktiv åtgärd är införd i detta dokument.

## D4A trackability blocker (2026-02-14)

- Pilotkandidat `results/hparam_search/phase7b_grid_3months` (10 filer, 0 externa refs) testades för move-only.
- Ingen spårbar git-diff uppstod eftersom `.gitignore:212` innehåller `results/`.
- D4A execution i denna iteration genomförs därför som docs-only blocker-dokumentation.
- Faktisk `results/**` move-only execution är fortsatt **föreslagen** tills separat policybeslut finns.

## D4B policyspår (2026-02-14)

- Beslutsunderlag för policyalternativ är framtaget i:
  - `docs/ops/REPO_CLEANUP_D4B_POLICY_OPTIONS_2026-02-14.md`
- D4B i denna iteration är docs-only.
- Ignore-policyändring är fortsatt **föreslagen** och kräver separat kontrakt + explicit godkännande.

## D5 out-of-band execution guide (2026-02-14)

- Operativ vägledning är dokumenterad i:
  - `docs/ops/REPO_CLEANUP_D5_OOB_EXECUTION_GUIDE_2026-02-14.md`
- D5 i denna iteration är docs-only.
- Git-spårad `results/**` execution är fortsatt **föreslagen** under nuvarande policy.

## D6 policy tranche (2026-02-15)

- Separat policykontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D6_POLICY_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D6_POLICY_REPORT_2026-02-15.md`
- Ignore-policy har justerats minimalt för att tillåta git-spårning av enbart:
  - `archive/_orphaned/results/**`
- Ingen `results/**` move/delete execution ingår i D6.
