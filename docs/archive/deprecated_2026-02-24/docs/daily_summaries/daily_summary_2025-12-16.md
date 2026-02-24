# Daily Summary - 2025-12-16

## Syfte

Fokus idag var att stärka **korrekthet** och **reproducerbarhet** i Genesis-Core genom att:

- eliminera "config drift" mellan Optuna-trial-configs och backtest-resultat
- göra drift detekterbar och CI-vänlig (sanity-check med exit code)
- säkra backtest-korrekthet i metadata (särskilt `entry_reasons`)
- hålla repo:t grönt via pre-commit + full `pytest`

## Genomfört

### 1) Reproducerbarhet och drift-detektion

- Säkrade att "effective config" (`merged_config`) + `runtime_version` alltid kan spåras.
- Implementerade verktyg för att verifiera ekvivalens mellan:
  - trial config ("complete" config) och
  - sparad backtest-json (`results/backtests/*.json` eller direkt under run-dir)

Nya/centrala komponenter:

- `src/core/utils/diffing/config_equivalence.py`
  - canonicalisering (float-rounding) + fingerprint + deep diff med dot-paths
  - kontrollerar även `config_provenance`-invarianter
- `scripts/check_trial_config_equivalence.py`
  - CLI som scannar `run_*` och skriver `[OK]/[SKIP]/[MISMATCH]`
  - CI-vänliga exit codes
- `config/optimizer/config_equivalence_smoke.yaml`
  - minimal konfig för att kunna producera en konkret `[OK]` i loggen

### 2) Backtest-korrekthet

- `src/core/backtest/engine.py`
  - **HTF exit config appliceras per run** (engine init sker innan configs är kända)
  - **`entry_reasons`**: säkerställt att pending reasons sätts **före** entry exekveras och rensas om entry inte sker

Regressionstester (snabba, deterministiska):

- `tests/test_backtest_determinism_smoke.py`
  - determinism 2× run
  - determinism med exakt 1 trade
  - determinism med explicit exit reason
- `tests/test_backtest_entry_reasons.py`
  - verifierar att trade får rätt `entry_reasons` från entry-baren
- `tests/test_backtest_applies_htf_exit_config.py`
  - verifierar att `htf_exit_config` faktiskt påverkar engine/exit-motorn

### 3) API-säkerhet (paper trading)

- `tests/test_ui_endpoints.py`
  - hardar testet så att icke-TEST symbol måste klampas till TEST-par
- `src/core/server.py`
  - docstring uppdaterad så den matchar verkligt beteende (whitelist + fallback)

### 4) Observability / logging

- `src/core/strategy/fib_logging.py`
  - fib-flow logging (opt-in via env) respekterar processens log level; fall back till WARNING när INFO filtreras

### 5) Git-hygien och verifieringar

- Verifierade att `.env` ignoreras:
  - `git check-ignore -v .env` → `.gitignore:76:.env`
- Delade upp arbetet i 4 logiska commits och pushade till `origin/Phase-7d`.

## Resultat och observationer

### Teststatus

- ✅ `pre-commit run --all-files` (exit 0)
- ✅ Full `pytest`:
  - **487 passed, 1 skipped**
  - Noterade warnings:
    - flera test instansierar `BacktestEngine(... fast_window=False)` samtidigt som `GENESIS_PRECOMPUTE_FEATURES=1` är satt → varning om inkonsistenta exekveringsvägar (men inga failures).

### E2E-bevis: drift-check på färsk run

- Minimal optimizer-smoke körd med:
  - `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_MAX_CONCURRENT=1`
  - konfig: `config/optimizer/config_equivalence_smoke.yaml`
- Run-dir: `results/hparam_search/run_20251216_152114`
- Drift-check:
  - `scripts/check_trial_config_equivalence.py --run-dir ... --all` →
    - **`[OK] trial_001 (tBTCUSD_1h_trial_001.json)`**

### PR-status (ingen merge)

- Försök att skapa PR `Phase-7d` → `master` misslyckades:
  - GitHub API returnerade **422**: "**no history in common with master**"
  - Slutsats: `master` och `Phase-7d` är två separata historiker; PR kräver en "bridge"-branch.
- GitHub CLI (`gh`) finns inte installerad i miljön.

### Workspace status

- `git status --porcelain` är rent för tracked filer.
- Kvar lokalt: tre **untracked** experimentfiler (tas inte med i PR om man inte add:ar dem):
  - `config/tmp/champion_current_as_cfg_no_partials.json`
  - `config/tmp/champion_current_as_cfg_sa_up1.json`
  - `config/tmp/champion_current_as_cfg_sa_up2.json`

## Rekommenderade nästa steg

1. **Skapa bridge-branch från `master`** och merge:a in `Phase-7d` med `--allow-unrelated-histories`, pusha och skapa PR.
   - Detta är det minst riskabla sättet att få en granskbar PR när historikerna är separata.
2. (Valfritt) **Minska warnings i tests**:
   - antingen instansiera `BacktestEngine(... fast_window=True)` i de tester som inte bryr sig om fast_window,
   - eller temporärt se till att `GENESIS_PRECOMPUTE_FEATURES` inte påverkar unit tests.

## Mini-logg (kommandon / körningar)

- `pre-commit run --all-files`
- `pytest`
- optimizer smoke: `run_optimizer(config/optimizer/config_equivalence_smoke.yaml)`
- drift-check: `scripts/check_trial_config_equivalence.py --run-dir results/hparam_search/run_20251216_152114 --all`
