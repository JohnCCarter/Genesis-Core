# A/B-runbook: Quality v2 (Phase-7e)

## Syfte

Vi vill rulla ut **Quality v2** (”context/market quality”) på ett kontrollerat sätt och verifiera att vi får:

- bättre _netto_-kvalitet (PF net-of-commission, d.v.s. `pf_net`), och/eller
- bättre riskprofil (mindre netto-förlust från stora förlust-exits som t.ex. `EMERGENCY_SL`),

utan att skapa exit-churn eller ändra trade-set oväntat.

Den här runbooken beskriver exakt vilka configs som är **control/treatment** och hur vi reproducerar jämförelsen.

## Vad som testas

### Control (A)

- Champion (befintlig): `config/strategy/champions/tBTCUSD_1h.json`

### Treatment (B) – primär rekommendation

- Scoped strict: `config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped.json`
  - `data_quality` + `spread` scope = `both`
  - `atr` + `volume` scope = `sizing`

### Treatment (C) – valfri extra arm

- Scoped relaxed size: `config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped_relaxed_size.json`

## Nyckelprinciper (viktigt)

- Vi utvärderar **netto**: `net_pnl = pnl - commission` och rapporterar `pf_net`.
- I flera jämförelser har exit-reason-counts varit identiska mellan varianter → skillnaden kommer ofta från **position sizing** (inte entry/exit-beslut). Det är förväntat för scoped-upplägget.
- Kör i **canonical mode** (deterministiskt): fast_window + precompute.

## Reproducerbar körning

### Miljö

Säkerställ canonical mode:

- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_RANDOM_SEED=42`

### Backtest (control vs treatment)

Kör samma symbol/timeframe och samma tidsfönster för både A och B.

- A: `--config-file config/strategy/champions/tBTCUSD_1h.json`
- B: `--config-file config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped.json`

Om du kör C också:

- C: `--config-file config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped_relaxed_size.json`

## Spikade fönster + artifacts (Phase-7e körning 2025-12-25)

Fönsterdefinitionerna nedan är hämtade från sparade backtest-resultat i `results/backtests/` (canonical mode, seed=42).

- **W1**: `2024-04-18 23:00:00` → `2024-09-30 00:00:00`
- **W2**: `2024-10-01 00:00:00` → `2025-03-31 00:00:00`
- **W3**: `2025-04-01 00:00:00` → `2025-10-10 00:00:00`

### Exakta filer (A/B/C)

Notera: ibland skiljer trades-CSV och backtest-JSON med 1 sekund i timestamp (CSV skrivs efter körning).

#### W1

- A (Champion)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_194941.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_194940.json`
- B (Scoped strict)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_195023.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_195022.json`
- C (Relaxed size)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_195342.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_195342.json`

#### W2

- A (Champion)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_193150.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_193150.json`
- B (Scoped strict)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_193230.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_193230.json`
- C (Relaxed size)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_193934.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_193934.json`

#### W3

- A (Champion)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_193519.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_193518.json`
- B (Scoped strict)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_193601.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_193601.json`
- C (Relaxed size)
  - Trades: `results/trades/tBTCUSD_1h_trades_20251225_194026.csv`
  - Backtest: `results/backtests/tBTCUSD_1h_20251225_194026.json`

### Analys (pf_net + exit breakdown)

Använd:

- `scripts/analyze_w2_exit_breakdown.py`

Den tar en eller flera trades-CSV och skriver:

- `pf_net`
- exit reason counts
- net PnL per exit reason
- top winners/losers

Exempel (ersätt med dina CSV-paths):

- `results/trades/<...A...>.csv`
- `results/trades/<...B...>.csv`
- `results/trades/<...C...>.csv`

### Resultatsammanfattning (pf_net)

`pf_net = sum(net wins) / sum(|net losses|)` där `net_pnl = pnl - commission` (från `scripts/analyze_w2_exit_breakdown.py`).

| Fönster | A (Champion) pf_net | B (Scoped strict) pf_net | C (Relaxed size) pf_net |
| ------- | ------------------: | -----------------------: | ----------------------: |
| W1      |              0.6539 |                   0.6735 |                  0.6606 |
| W2      |              0.7926 |                   0.8176 |                  0.8009 |
| W3      |              1.0643 |                   1.0373 |                  1.0551 |

Observation (kort): i dessa körningar är exit-reason-counts identiska per fönster mellan A/B/C, så skillnaden i `pf_net` kommer primärt från sizing-effekten (vilket är förväntat i scoped-upplägget).

## Rollout i praktik (canary)

Rekommenderad canary-policy (hög nivå):

1. **Phase 1**: liten kapital-allokering (t.ex. 10%) i 3 dagar
2. **Phase 2**: 50% i 7 dagar
3. Full rollout om kriterier uppfylls

Se `config/validation_config.json -> canary_deployment` för exakta default-trösklar.

## Snabb “done”-check

Innan vi kallar treatment “vinnare”, verifiera:

- `pf_net` inte sämre än control på _viktiga_ fönster
- drawdown/”tail losses” inte sämre (t.ex. `EMERGENCY_SL` net-loss)
- inga nya exit-churn-mönster (t.ex. CONF-drop exit p.g.a. quality)
