# PORTING

Denna fil beskriver läget för portningen från gamla Genesis till nya `Genesis-Core` och hålls kort och uppdaterad.

## Status

- Under utveckling: minimal, inkrementell portning pågår.
- Paper only & single‑user: inga live‑nycklar används.
- CI (black, ruff, pytest, bandit): grönt i nuläget.

## Klart porterat (minimalistiskt)

- ExchangeClient (REST, central): signering (HMAC‑SHA384), NonceManager, engångs‑retry/backoff, delad AsyncClient.
- NonceManager: monoton, persistent, tråd/process‑säker; `bump_nonce` vid 10114.
- WS public/auth (minimalt härdat): ACK/ERROR/timeout, maintenance (20051/20060).
- WS reconnect‑skelett: backoff + jitter, ping/pong‑watchdog, åter‑auth.
- Logging‑redaction: maskerar `bfx-apikey`/signature i loggar.
- Privata read‑helpers: `get_wallets()`, `get_positions()`.
- Observability: counters/gauges/events + `/observability/dashboard`.
- Risk guards (rena): `breached_max_drawdown`, `within_daily_loss_limit` + minimala tester.
- Risk PnL-helper: `risk/pnl.py` (`daily_pnl_usd`, `breached_daily_loss`) + små tester.

## Pågående

- (tomt)

## Nästa steg (förslag)

1. Latens‑metrics i REST/WS och exponera i dashboard.
2. Fler privata read‑helpers (t.ex. historik/ledger) + tester (mock).
3. Uppdatera `docs/GENESIS-CORE_FEATURES.md` och `docs/SHARE.md` vid behov.

## Policy

- Minimal yta, små PR:er, separation of concerns.
- Enhetstester och observability för varje portning.
