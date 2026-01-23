# Daily Summary - 2026-01-23

## Summary of Work

Dagens fokus var att **verifiera P0 determinism-lockdown i praktiken** och skapa **canonical mode-dokumentation (P1.1)** som SSOT för framtida Optuna-körningar.

Arbetet inkluderade Optuna sanity-run (smoke test), gate-dominance diagnostik och skapande av operatörschecklista för långa optimeringar.

## Key Changes

- **Canonical mode dokumentation (P1.1)**:
  - `docs/canonical/CANONICAL_MODE.md` (400+ rader)
    - Canonical contract: tillåtna env-vars (`PYTHONHASHSEED=0`, `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_RANDOM_SEED=42`)
    - Förbjudna env-vars: `GENESIS_FAST_HASH=1` (bevisad icke-deterministisk), `GENESIS_MODE_EXPLICIT` (debug only)
    - Fail-fast conditions: mixed mode, fast hash violations, preflight timeouts, champion mismatches
    - Canonical Optuna execution: 4-stegs preflight checklista
    - Non-canonical mode: när det är OK och hur det markeras
    - Troubleshooting: olika resultat, identiska scores, preflight-failures
    - Best practices: alltid canonical för quality decisions, dokumentera undantag, verifiera determinism

  - `docs/canonical/PREFLIGHT_CHECKLIST.md` (350+ rader)
    - Pre-run validation: 10-stegs checklista (config validering, preflight check, baseline smoke test)
    - Environment setup: canonical env-vars, cache management, database management
    - Search space validation: champion reproducibility, breadth checks
    - System resources: disk space (>=10GB), RAM (<80%), concurrency settings
    - Final checklist: 11-item pre-launch verification
    - Monitoring: real-time checks för DB growth, cache hits, I/O errors
    - Post-run: result summary, trial diversity, export for analysis
    - Emergency procedures: graceful abort, DB backup, resume process
    - Troubleshooting: DB locked errors, identical trial scores, zero trades

- **Optuna sanity-run (determinism verification)**:
  - **Körning #1**: 3 trials, 8-dagars period (2024-12-03 till 2024-12-11)
    - Trial 0: score -500.0 (zero-trade abort)
    - Trial 1: score -250.14 (best, 0 trades)
    - Trial 2: score -500.0 (zero-trade abort)
    - Runtime: ~16 sekunder
    - Result: ✅ Olika scores → search space varierar korrekt

  - **Körning #2** (determinism check):
    - Trial 0: score -500.0 (identiskt)
    - Trial 1: score -250.143629436112 (identiskt, 15+ decimaler precision)
    - Trial 2: score -500.0 (identiskt)
    - Result: ✅ **100% deterministisk** - samma seed/config ger exakt samma resultat

  - **Environment korrekt satt**:
    - `PYTHONHASHSEED=0` (P0.2 preflight-krav)
    - `GENESIS_FAST_WINDOW=1`
    - `GENESIS_PRECOMPUTE_FEATURES=1`
    - `GENESIS_RANDOM_SEED=42`

- **Gate-dominance diagnostik**:
  - **Trial 002 analys** (bästa från smoke run):
    - Period: 2024-12-03 till 2024-12-11 (43 bars efter warmup)
    - RANGING regime (37/43 bars = 86%):
      - `ZONE:high@0.350` - 17 bars (46%) ← dominerande blocker
      - `COOLDOWN_ACTIVE` - 11 bars (30%)
      - `ENTRY_LONG` + `ENTRY_SHORT` - 7 bars (19%) passerade gates men ingen trade
    - BEAR regime (6/43 bars = 14%):
      - `HYST_WAIT` - 3 bars (50%)
      - `COOLDOWN_ACTIVE` - 2 bars (33%)

  - **Champion analys** (samma period):
    - RANGING regime (37 bars):
      - `ZONE:high@0.380` - 21 bars (57%) ← VÄRRE än trial 002
      - `ENTRY_SHORT` + `ENTRY_LONG` - 15 bars (41%) passerade gates men ingen trade
    - BEAR regime (6 bars):
      - `ZONE:high@0.380` - 4 bars (67%)

  - **Insikter**:
    - ZONE-gaten (ATR-baserad threshold) blockerar 46-57% av bars (för tight för kort period)
    - Champion får 2× fler ENTRY-bars (41% vs 19%) trots högre zone-threshold
    - Trial 002 har aggressiv COOLDOWN (30% av RANGING) som champion inte har
    - **Problemet är INTE bara ZONE-gaten**: 15-41% bars passerar entry-gates men resulterar INTE i trades
    - Downstream-filter (EV/risk/edge) stoppar alla trades som passerat confidence/zone/fib gates

- **.env uppdatering**:
  - Lade till `PYTHONHASHSEED=0` i .env för automatisk laddning (tidigare måste sättas manuellt i PowerShell)

## Verification

- **Determinism-test**: ✅ Dubbelkörning av Optuna smoke ger identiska scores (15+ decimaler precision)
- **P0.2 preflight**: ✅ Passerar med `PYTHONHASHSEED=0` satt
- **Gate-diagnostik**: ✅ CSV-export + meta JSON genererad för både trial och champion
- **Preflight scripts**: ✅ `validate_optimizer_config.py` och `preflight_optuna_check.py` passerar smoke-config

## Artifacts

- Optuna runs:
  - `results/hparam_search/run_20260123_104624/` (första smoke run)
  - `results/hparam_search/run_20260123_104641/` (determinism check)

- Gate-diagnostik:
  - `artifacts/diagnostics/gate_dominance/smoke_trial_002/`
    - `gate_dominance_summary.csv` (9 rader: år/regim/blocker breakdown)
    - `gate_dominance_meta.json` (period/symbol/config fingerprint)
  - `artifacts/diagnostics/gate_dominance/champion_smoke_period/`
    - `gate_dominance_summary.csv` (6 rader: champion blockers)
    - `gate_dominance_meta.json`

## Next Steps

- **Dokumentation**:
  - ⏳ P1.1 Task 3: Länka till canonical docs från OPTUNA_BEST_PRACTICES.md och AGENTS.md (ej klart)
  - ⏳ P1.2: Champion merge transparency (backtest_info logging, comparison scripts)
  - ⏳ P1.3: Gate dominance diagnostics (enhance analyze_gate_dominance.py output)

- **Optuna förbättringar**:
  - Bredda search space baserat på gate-diagnostik:
    - Sänk ZONE-trösklar: `zones.high.entry_conf_overall: 0.25-0.35` (från 0.35-0.38)
    - Lägg till cooldown i search space: `exit.cooldown_bars: 0-5`
    - Sänk min_edge: `thresholds.min_edge: 0.003-0.010`

- **Debug downstream-filter**:
  - Kör längre period (3 månader) för att se om zero-trade är periodspecifikt
  - Kör med `--log-level DEBUG` för att granska EV/risk/edge-beräkningar för bars som passerar ENTRY-gates

## Notes

- **Canonical mode fungerar**: P0-lockdown ger 100% reproducerbarhet när alla env-vars är korrekt satta
- **PYTHONHASHSEED=0 är kritiskt**: P0.2 preflight failar utan det (nu i .env för automatisk laddning)
- **Zero-trade i smoke är förväntat**: 8-dagars period + höga trösklar, men determinism är verifierad
- **Gate-diagnostik avslöjar fler insikter än bara ZONE-blocks**: Downstream-filter (EV/risk) är nästa debug-punkt
