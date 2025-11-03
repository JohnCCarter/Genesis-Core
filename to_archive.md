# Arkivförslag 2025-11-03

- `decision_backup.py` – backup av tidigare beslutslogik, inte importerad i koden.
- `docs/THRESHOLD_OPTIMIZATION_RESULTS.md` – rapport från 2025-10-10, ersatt av senare fib-gate dokumentation.
- `config/models/registry.json.backup` – äldre kopia av modellregistret, nu ersatt av `registry.json`.
- `config/models/backup_old_models/` – multi-timeframe modeller som flyttats ur drift (cleanup-script har redan lagt dem här).
- `config/models/backup_tbtcusd_outdated/` – gamla tBTCUSD-modeller som inte längre används.
- `config/models/backup_tbtcusd_metrics/` – motsvarande metrics-filer för föråldrade modeller.
- `config/models/v7_final_top7_6m.json/` – äldre topp7-konfiguration som enbart refereras i arkiv-skript.
- `test_optuna_new_20251023_old.db` – Optuna-databas från tidiga tester före dagens preflight-process.
- `bandit-report.json` och `bandit-report.txt` – tidigare säkerhetskörning; resultat refereras redan i dokumentationen.
- `tmp_aggressive_candidate.json` – temporär testkonfiguration (ej refererad av kod).
- `tmp_champion_clone.json` – kopia av champion-konfig för manuella tester.
- `tmp_htf_edge.json` – experimentell HTF-konfig, ej aktiv.
- `tmp_ltf_only.json` – experimentell LTF-konfig, ej aktiv.
- `tmp_no_htf.json` – experiment utan HTF-filter.
- `tmp_reason_counts.py` – ad-hoc analysverktyg, ej integrerat i pipelines.
- `tmp_relaxed_combo.json` – äldre kombinatorisk konfig.
- `tmp_relaxed_combo_ltf.json` – variant av ovan.
- `tmp_threshold_relax.json` – experimentellt threshold-case.
