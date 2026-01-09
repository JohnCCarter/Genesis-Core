# Optuna Hardening Spec (Genesis-Core)

Syfte: Förhindra att Optuna förstärker degenerata/extrema beteenden (0 trades, NaN, guard-block, loss clusters) och göra sökningen stabil, reproducerbar och informationsrik.

## Status (implementerat 2025-12-18)

- **Explore→Validate** (tvåstegsflöde) finns nu i `src/core/optimizer/runner.py`:
  - Explore kör Optuna på kort fönster.
  - Validate kör om top-N kandidater på längre fönster med striktare constraints.
- **Promotion safety** är konfigstyrd via `promotion.enabled` samt extra spärr `promotion.min_improvement`.
- Referenskonfig + resultat:
  - `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v7_smoke_explore_validate.yaml`
  - `docs/daily_summaries/daily_summary_2025-12-18.md`

## 1) Klassificera trial-outcome (måste finnas i payload)

Varje trial ska klassas i exakt en av följande kategorier:

- `VALID`: metrics finns och är numeriskt stabila
- `INVALID_NUMERIC`: NaN/Inf i features, equity, metrics eller score
- `ZERO_TRADES_SIGNAL_DEAD`: `signals_generated == 0` (eller motsv.) efter warmup
- `ZERO_TRADES_BLOCKED`: `signals_generated > 0` men `trades == 0`
- `EXECUTION_BLOCKED`: orders aldrig skickas eller alltid rejectas p.g.a. guards/validering
- `DUPLICATE_WITHIN_RUN`: identisk parameter-signatur som tidigare trial i samma run

Minsta fält i trial-payload (för att stödja ovan):

- `bars_total`, `warmup_bars`
- `signals_generated`, `candidates`
- `blocked_by_reason: dict[str,int]` (minst topporsaker)
- `risk_rejects`, `orders_submitted`, `orders_rejected`, `fills`
- `trades_opened`, `trades_closed` (eller `trades`)
- `nan_count_features` (eller bool `has_nan_features`)
- `metrics`: `total_return_net`, `profit_factor`, `max_drawdown`, `max_loss_streak`, `avg_hold_bars`

## 2) Degenerata outcomes måste vara dyrast (gäller båda faser)

Returnera aldrig 0.0 för degenerata outcomes.

Föreslagna fasta penalties (maximera score):

- `INVALID_NUMERIC`: `score = -5000`
- `DUPLICATE_WITHIN_RUN`: `score = -300`
  (OBS: gäller inte legitima cache-hits med återrapporterad riktig score; bara duplicat inom samma run)
- `ZERO_TRADES_SIGNAL_DEAD`: `score = -1500`
- `ZERO_TRADES_BLOCKED`: `score = -2000`
- `EXECUTION_BLOCKED`: `score = -2200`

## 3) Two-phase objective (Feasibility-first)

### Fas 1: Feasible trading (första N trials)

Mål: snabbt hitta regioner som _faktiskt handlar_ utan att riskera katastrof.

Definitioner:

- Effektiva bars: `B = max(1, bars_total - warmup_bars)`
- Trade-rate: `r = trades / B`
- Target-range: `[r_lo, r_hi]` (ex: 0.002–0.02)

Penalties:

- `p_rate = 0` om `r_lo <= r <= r_hi`, annars:
  - `p_rate = min(5.0, min(abs(r - r_lo), abs(r - r_hi)) / max(1e-9, 0.5*(r_lo + r_hi)))`
- `p_dd = max(0.0, (dd - dd_target) / dd_target)`
- `p_hold = max(0.0, (hold_min - avg_hold_bars) / hold_min)`

Feasibility score (maximera):

`score = 1.0 - 1.0*p_rate - 1.5*p_dd - 0.5*p_hold`

Rekommenderade defaultvärden:

- `dd_target = 0.15`
- `hold_min = 2` bars
- `N = 25–50` (eller tidsbaserat)

### Fas 2: Production score (resten av trials)

Mål: optimera riskjusterad avkastning utan att belöna loss clusters eller övertrading.

Normaliserade termer:

- `R = total_return_net` (andel, ex 0.08)
- `DD = max_drawdown` (andel)
- `PFc = clip(profit_factor, 0.0, 5.0)`
- `p_streak = max(0.0, (max_loss_streak - streak_target) / streak_target)`
- `p_rate_hi = max(0.0, (r - r_hi) / r_hi)`

Production score (maximera):

`score = 100*R - 60*DD + 10*log1p(PFc) - 15*p_streak - 10*p_rate_hi`

Rekommenderade defaultvärden:

- `streak_target = 6`

## 4) Pruning (tidigt stopp på extrema symptom)

Efter warmup + `audit_window` (ex 200 bars), prune om någon gäller:

- `trades == 0` och `signals_generated == 0` → prune
- `trades == 0` och `signals_generated > 0` → prune
- `max_drawdown > dd_max_early` → prune (ex 0.25)
- `max_loss_streak >= loss_streak_early` → prune (ex 10)

## 5) Minska diskontinuiteter i sökrymden

- Föredra kontinuerliga thresholds framför boolska on/off.
- Om bools måste finnas: behandla dem som fas-2-parametrar (inte fas-1), eller lås dem under fas-1.

## 6) Minimal outputstandard (Decision Trace)

Varje trial ska spara en kompakt sammanfattning (JSON) med:

- `signals_generated`, `candidates`
- `blocked_by_reason`
- `risk_rejects`, `orders_submitted`, `orders_rejected`, `fills`
- `trades_opened`, `trades_closed`
- `nan_count_features`, `merge_row_drops`, `first_valid_bar_index`
