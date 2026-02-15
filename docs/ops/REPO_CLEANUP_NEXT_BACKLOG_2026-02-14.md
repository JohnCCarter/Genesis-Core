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

## D7 minimal execution pilot (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D7_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D7_EXEC_REPORT_2026-02-15.md`
- Scoped move-only pilot genomförs för exakt 1 fil:
  - `results/hparam_search/run_seeds/run_meta.json`
  - `archive/_orphaned/results/hparam_search/run_seeds/run_meta.json`
- Ingen övrig `results/**` execution ingår i D7.

## D8 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D8_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D8_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_test/run_meta.json`
  - `results/hparam_search/run_20251227_180204/trial_001.log`
  - `results/hparam_search/run_20251227_180204/trial_002.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_test/`
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Ingen övrig `results/**` execution ingår i D8.

## D9 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D9_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D9_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_003.log`
  - `results/hparam_search/run_20251227_180204/trial_004.log`
  - `results/hparam_search/run_20251227_180204/trial_005.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Carry-forward i denna tranche:
  - newline/format-normalisering för redan orphaned filer `run_meta.json`, `trial_001.log`, `trial_002.log`
- Ingen övrig `results/**` execution ingår i D9.

## D10 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D10_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D10_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_006.log`
  - `results/hparam_search/run_20251227_180204/trial_007.log`
  - `results/hparam_search/run_20251227_180204/trial_008.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Ingen övrig `results/**` execution ingår i D10.

## D11 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D11_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D11_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_009.log`
  - `results/hparam_search/run_20251227_180204/trial_010.log`
  - `results/hparam_search/run_20251227_180204/trial_011.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Carry-forward i denna tranche:
  - newline-normalisering för redan orphaned filer `trial_003.log` till `trial_008.log`
- Ingen övrig `results/**` execution ingår i D11.

## D12 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D12_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D12_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_012.log`
  - `results/hparam_search/run_20251227_180204/trial_013.log`
  - `results/hparam_search/run_20251227_180204/trial_014.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Carry-forward i denna tranche:
  - newline-normalisering för redan orphaned filer `trial_009.log` till `trial_011.log`
- Ingen övrig `results/**` execution ingår i D12.

## D13 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D13_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D13_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_015.log`
  - `results/hparam_search/run_20251227_180204/trial_016.log`
  - `results/hparam_search/run_20251227_180204/trial_017.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Carry-forward i denna tranche:
  - newline-normalisering för redan orphaned filer `trial_012.log` till `trial_014.log`
- Ingen övrig `results/**` execution ingår i D13.

## D14 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D14_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D14_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_018.log`
  - `results/hparam_search/run_20251227_180204/trial_019.log`
  - `results/hparam_search/run_20251227_180204/trial_020.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Carry-forward i denna tranche:
  - newline-normalisering för redan orphaned filer `trial_015.log` till `trial_017.log`
- Ingen övrig `results/**` execution ingår i D14.

## D15 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D15_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D15_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_021.log`
  - `results/hparam_search/run_20251227_180204/trial_022.log`
  - `results/hparam_search/run_20251227_180204/trial_023.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Carry-forward i denna tranche:
  - newline-normalisering för redan orphaned filer `trial_018.log` till `trial_020.log`
- Ingen övrig `results/**` execution ingår i D15.

## D16 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D16_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D16_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_024.log`
  - `results/hparam_search/run_20251227_180204/trial_025.log`
  - `results/hparam_search/run_20251227_180204/trial_026.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Ingen övrig `results/**` execution ingår i D16.

## D17 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D17_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D17_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_027.log`
  - `results/hparam_search/run_20251227_180204/trial_028.log`
  - `results/hparam_search/run_20251227_180204/trial_029.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Noterad residual risk i denna tranche:
  - basename-referenser i run-artefakter (`trial_027/028/029.json` och `_cache/*.json`) är accepterade inom move-only scope.
- Ingen övrig `results/**` execution ingår i D17.

## D18 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D18_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D18_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_030.log`
  - `results/hparam_search/run_20251227_180204/trial_031.log`
  - `results/hparam_search/run_20251227_180204/trial_032.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Noterad residual risk i denna tranche:
  - basename-referenser i run-artefakter (`trial_030/031/032.json` och `_cache/*.json`) är accepterade inom move-only scope.
- Carry-forward i denna tranche:
  - newline-normalisering för redan orphaned filer `trial_027.log` till `trial_029.log`
  - newline-normalisering för `docs/ops/REPO_CLEANUP_D17_EXEC_CONTRACT_2026-02-15.md`
  - newline-normalisering för `docs/ops/REPO_CLEANUP_D17_EXEC_REPORT_2026-02-15.md`
- Ingen övrig `results/**` execution ingår i D18.

## D19 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D19_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D19_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_033.log`
  - `results/hparam_search/run_20251227_180204/trial_034.log`
  - `results/hparam_search/run_20251227_180204/trial_035.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Noterad residual risk i denna tranche:
  - basename-referenser i run-artefakter (`trial_033/034/035.json` och `_cache/*.json`) är accepterade inom move-only scope.
- Ingen övrig `results/**` execution ingår i D19.

## D20 minimal execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D20_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D20_EXEC_REPORT_2026-02-15.md`
- Scoped move-only execution genomförs för exakt 3 filer:
  - `results/hparam_search/run_20251227_180204/trial_036.log`
  - `results/hparam_search/run_20251227_180204/trial_037.log`
  - `results/hparam_search/run_20251227_180204/trial_038.log`
- Mål under:
  - `archive/_orphaned/results/hparam_search/run_20251227_180204/`
- Noterad residual risk i denna tranche:
  - basename-referenser i run-artefakter (`trial_036/037/038.json` och `_cache/*.json`) är accepterade inom move-only scope.
- Ingen övrig `results/**` execution ingår i D20.

## D21 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D21_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D21_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 1 mapp:
  - `results/hparam_search/phase7b_grid_3months/**`
- Noterad bakgrund i denna tranche:
  - kandidaten var tidigare dokumenterad som låg extern ref-risk i D4A.
- Ingen övrig `results/**` execution ingår i D21.

## D22 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D22_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D22_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 3 filer:
  - `results/backtests/tBTCUSD_1h_20251022_152515.json`
  - `results/backtests/tBTCUSD_1h_20251022_152517.json`
  - `results/backtests/tBTCUSD_1h_20251022_152519.json`
- Noterad residual risk i denna tranche:
  - basename-referenser i legacy run-artefakter (`results/hparam_search/phase7b_optuna/**`) är accepterade inom delete-only scope.
- Ingen övrig `results/**` execution ingår i D22.

## D23 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D23_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D23_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 10 filer:
  - `results/backtests/tBTCUSD_1h_20251022_153336.json`
  - `results/backtests/tBTCUSD_1h_20251022_153337.json`
  - `results/backtests/tBTCUSD_1h_20251022_154020.json`
  - `results/backtests/tBTCUSD_1h_20251022_154021.json`
  - `results/backtests/tBTCUSD_1h_20251022_154030.json`
  - `results/backtests/tBTCUSD_1h_20251022_154822.json`
  - `results/backtests/tBTCUSD_1h_20251022_154828.json`
  - `results/backtests/tBTCUSD_1h_20251022_154838.json`
  - `results/backtests/tBTCUSD_1h_20251022_160630.json`
  - `results/backtests/tBTCUSD_1h_20251022_160723.json`
- Noterad residual risk i denna tranche:
  - referenser i legacy run-artefakter (`results/hparam_search/phase7b_optuna/**`, `results/hparam_search/phase7b_optuna_quick/**`) är accepterade inom delete-only scope.
- Ingen övrig `results/**` execution ingår i D23.

## D24 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D24_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D24_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 10 filer:
  - `results/backtests/tBTCUSD_1h_20251022_160814.json`
  - `results/backtests/tBTCUSD_1h_20251022_161401.json`
  - `results/backtests/tBTCUSD_1h_20251022_161453.json`
  - `results/backtests/tBTCUSD_1h_20251022_161544.json`
  - `results/backtests/tBTCUSD_1h_20251022_161901.json`
  - `results/backtests/tBTCUSD_1h_20251022_161954.json`
  - `results/backtests/tBTCUSD_1h_20251022_162052.json`
  - `results/backtests/tBTCUSD_1h_20251022_162200.json`
  - `results/backtests/tBTCUSD_1h_20251022_162250.json`
  - `results/backtests/tBTCUSD_1h_20251022_162341.json`
- Noterad residual risk i denna tranche:
  - referenser i legacy run-artefakter (`results/hparam_search/phase7b_optuna_quick/**`, `results/hparam_search/phase7b_grid_baseline/**`, `results/hparam_search/phase7b_grid_ultra_low/**`) är accepterade inom delete-only scope.
- Ingen övrig `results/**` execution ingår i D24.

## D25 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D25_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D25_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 10 filer:
  - `results/backtests/tBTCUSD_1h_20251022_164122.json`
  - `results/backtests/tBTCUSD_1h_20251022_164446.json`
  - `results/backtests/tBTCUSD_1h_20251022_164752.json`
  - `results/backtests/tBTCUSD_1h_20251022_165101.json`
  - `results/backtests/tBTCUSD_1h_20251022_165813.json`
  - `results/backtests/tBTCUSD_1h_20251022_170314.json`
  - `results/backtests/tBTCUSD_1h_20251022_170619.json`
  - `results/backtests/tBTCUSD_1h_20251022_170930.json`
  - `results/backtests/tBTCUSD_1h_20251022_171438.json`
  - `results/backtests/tBTCUSD_1h_20251022_171912.json`
- Noterad residual risk i denna tranche:
  - referenser i legacy run-artefakter (`results/hparam_search/phase7b_grid_simple/**`, `results/hparam_search/phase7b_grid_fixed/**`) är accepterade inom delete-only scope.
- Ingen övrig `results/**` execution ingår i D25.

## D26 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D26_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D26_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 7 filer:
  - `results/backtests/tBTCUSD_1h_20251022_172222.json`
  - `results/backtests/tBTCUSD_1h_20251022_172529.json`
  - `results/backtests/tBTCUSD_1h_20251022_172854.json`
  - `results/backtests/tBTCUSD_1h_20251022_175346.json`
  - `results/backtests/tBTCUSD_1h_20251022_175710.json`
  - `results/backtests/tBTCUSD_1h_20251022_180017.json`
  - `results/backtests/tBTCUSD_1h_20251022_180346.json`
- Noterad residual risk i denna tranche:
  - referenser i legacy run-artefakter (`results/hparam_search/phase7b_grid_simple/**`, `results/hparam_search/phase7b_grid_fixed/**`, `results/hparam_search/phase7b_grid_final_test/**`) är accepterade inom delete-only scope.
- Ingen övrig `results/**` execution ingår i D26.

## D27 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D27_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D27_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 10 filer:
  - `results/backtests/tBTCUSD_1h_20251026_205559.json`
  - `results/backtests/tBTCUSD_1h_20251026_210913.json`
  - `results/backtests/tBTCUSD_1h_20251026_212223.json`
  - `results/backtests/tBTCUSD_1h_20251026_213537.json`
  - `results/backtests/tBTCUSD_1h_20251026_214848.json`
  - `results/backtests/tBTCUSD_1h_20251026_220156.json`
  - `results/backtests/tBTCUSD_1h_20251026_221503.json`
  - `results/backtests/tBTCUSD_1h_20251026_222814.json`
  - `results/backtests/tBTCUSD_1h_20251027_155000.json`
  - `results/backtests/tBTCUSD_1h_20251027_230343.json`
- Noterad residual risk i denna tranche:
  - referenser i legacy run-artefakter (`results/hparam_search/run_20251026_194233/**`) är accepterade inom delete-only scope.
- Ingen övrig `results/**` execution ingår i D27.

## D28 minimal delete execution tranche (2026-02-15)

- Separat execution-kontrakt + rapport:
  - `docs/ops/REPO_CLEANUP_D28_EXEC_CONTRACT_2026-02-15.md`
  - `docs/ops/REPO_CLEANUP_D28_EXEC_REPORT_2026-02-15.md`
- Scoped delete-only execution genomförs för exakt 10 filer:
  - `results/backtests/tBTCUSD_1h_20251225_171516.json`
  - `results/backtests/tBTCUSD_1h_20251225_171704.json`
  - `results/backtests/tBTCUSD_1h_20251225_172521.json`
  - `results/backtests/tBTCUSD_1h_20251225_175455.json`
  - `results/backtests/tBTCUSD_1h_20251225_175753.json`
  - `results/backtests/tBTCUSD_1h_20251225_175923.json`
  - `results/backtests/tBTCUSD_1h_20251225_180035.json`
  - `results/backtests/tBTCUSD_1h_20251225_180142.json`
  - `results/backtests/tBTCUSD_1h_20251225_180507.json`
  - `results/backtests/tBTCUSD_1h_20251225_180544.json`
- Noterad residual risk i denna tranche:
  - inga externa referensträffar observerades i `results/hparam_search/**` för dessa filer vid genomförandet.
- Ingen övrig `results/**` execution ingår i D28.
