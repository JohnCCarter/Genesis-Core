# Optimizer Runner & Rapportering (Phase-7a)

Senast uppdaterad: 2025-10-21

## 1. Översikt
Phase-7a introducerar en engångsoptimering med grid/serial-runner och champion-hantering. Detta dokument beskriver hur man kör optimeringar och sammanfattar resultat med det nya CLI:t.

## 2. Run-struktur
När `run_optimizer` körs skapas en katalog under `results/hparam_search/<run_id>/` med:
- `run_meta.json`: metadata (run_id, symbol, timeframe, snapshot_id, git_commit, starttid).
- `trial_<n>.json`: resultat per försök (score, constraints, logfil, attempts).
- `trial_<n>.log`: samlad stdout/err från `scripts/run_backtest.py`.

Champion-uppdatering sker när en trial utan hard failures överträffar tidigare champion. Fil skrivs till `config/strategy/champions/<symbol_tf>.json` och backup hamnar i `config/strategy/champions/backup/`.

## 3. CLI – `scripts/optimizer.py`

### 3.1 Kommandon
- `python scripts/optimizer.py summarize <run_id>`
  - Läser `run_meta.json` och alla `trial_*.json` i run-katalogen.
  - Skriver antal försök, skip, fail samt visar bästa trial (score + grundläggande metrics).

### 3.2 Exempel
```bash
python scripts/optimizer.py summarize run_20251021_101500
```
Utdata (exempel):
```
== Optimizer Summary ==
Run dir: .../results/hparam_search/run_20251021_101500
Meta:
  run_id: run_20251021_101500
  symbol: tBTCUSD
  timeframe: 1h
  snapshot_id: tBTCUSD_1h_2024-10-22_2025-10-01_v1
  git_commit: abc123
Counts:
  total=120 completed=118 skipped=2 failed=0
Best trial:
  id: trial_034
  file: trial_034.json
  score: 145.20
  num_trades: 72
  sharpe_ratio: 0.48
  total_return: 18.5%
  profit_factor: 2.1
```

### 3.3 Felhantering
- Om run-katalog saknas: `FileNotFoundError`.
- Ogiltig JSON i trial/meta: ignoreras per fil och loggas inte i CLI.

## 4. Tester
- `tests/test_optimizer_cli.py` säkerställer att CLI summerar metadata och identifierar bästa trial.
- `tests/test_optimizer_runner.py` verifierar att champion uppdateras och att resultaten returneras från runnern.

## 5. Att göra (nästa steg)
- Utökning av CLI med topp N-lista och statistik (percentiler, medelvärden).
- Integrera CLI-rapport i README och eventuellt automatiserade rapporter.
- Walk-forward och rapportering för validering (Plan steg 6).
