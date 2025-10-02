# Genesis‑Core – Funktionsöversikt

## Nuvarande funktioner

- Server

  - GET `/health` – hälsokontroll
  - GET `/observability/dashboard` – counters/gauges/events
  - POST `/config/validate` – validerar config mot schema v1
  - POST `/config/diff` – diffar `{old,new}` och returnerar `changes`
  - POST `/config/audit` – skriver append-only logg till `logs/config_audit.log`

- Konfiguration

  - Pydantic Settings (`.env`, inga hemligheter i repo)
  - JSON Schema v1 (`schema_v1.json`)
  - Validering, diff och audit-append

- Observability

  - Inbyggda counters/gauges/events via `core/observability/metrics.py`
  - Dashboard-endpoint

- Bitfinex IO (v2)

  - Public REST: `rest_public.py`
  - Public WS: `ws_public.py`
    - Handshake: `ticker` och `candles` väntar på `subscribed` eller `error`, timeout ger fail-fast
  - Auth REST: `rest_auth.py` (HMAC-SHA384 signering med NonceManager)
  - Auth WS: `ws_auth.py` (auth payload, µs→ms nonce)
    - Metrics: `ws_auth_request/success/error/maintenance/timeout`
    - Hanterar `info` maintenance (20051/20060) som tydlig reconnect‑signal
  - Central REST‑klient: `exchange_client.py` (NonceManager + enkel jitter‑retry)

- NonceManager

  - Per‑nyckel µs‑nonce med persistens och låsning (`core/utils/nonce_manager.py`)
  - Engångs‑retry vid "nonce too small" (10114) via `bump_nonce()` i REST
  - Skript för header‑generering: `scripts/build_auth_headers.py`

- WS reconnect

  - `ws_reconnect.py`: exponential backoff (secrets‑jitter), ping/pong‑watchdog, åter‑auth
  - `core/utils/backoff.py`: liten util för konsekvent backoff i IO‑lagret

- Logging (redaction)

  - `core/utils/logging_redaction.py`: maskerar API‑nycklar/signaturer i loggar

- Privata läs‑helpers (auth, ej endpoints)

  - `read_helpers.py`: `get_wallets()`, `get_positions()`

- Risk (rena funktioner, ingen IO)

  - `sizing.capped_position_size`
  - `guards.breached_max_drawdown`, `guards.within_daily_loss_limit`

- Strategi (rena funktioner)

  - Indikatorer (rena): `indicators/ema.py`, `indicators/atr.py`, `indicators/rsi.py`, `indicators/adx.py`
  - EMA-cross mini i `strategy/ema_cross.py`
  - Exempelstrategi i `strategy/example.py`

- Kvalitet & CI

  - Pre-commit: black, ruff, bandit
  - CI (GitHub Actions): lint, test, security
  - Lokalt CI-script: `scripts/ci.ps1`

- Tester
  - `tests/test_health.py`, `tests/test_observability.py`, `tests/test_config_endpoints.py`, `tests/test_nonce.py`
  - `tests/test_exchange_client.py`, `tests/test_logging_redaction.py`, `tests/test_ws_reconnect.py`, `tests/test_read_helpers.py`
  - Körbara exempel: `scripts/test_rest_public.py`, `scripts/test_ws_public.py`, `scripts/test_rest_auth.py`, `scripts/test_ws_auth.py`

## Roadmap (förslag)

- Risk & Portfölj

  - Trailing max drawdown per strategi
  - Dynamisk riskbudget per vol/regim
  - Max samtidiga positioner och exposure caps per instrument

- Strategier

  - Modulär feature‑pipeline (EMA, RSI, ADX, Regime)
  - Signal‑ensembler och viktning
  - Slippage‑ och avgiftsmodell i sim

- Exekvering

  - Orderrouter‑abstraktion (IO‑agnostisk)
  - Simulerad börs (backtest) och Replay
  - Rate limit och circuit breaker‑policy

- Observability

  - Prometheus‑exporter
  - Event‑kategorisering och sampling
  - Latency/throughput‑mått per IO‑klient

- Säkerhet & Driftsäkerhet

  - Secure secrets hantering (Key Vault/1Password)
  - Backoff/retry‑policy med jitter
  - Hårdare lint‑regler och typer (mypy)

- DevEx
  - Makefile/Invoke‑kommandon
  - Dockerfile + docker‑compose för lokal körning
  - Mer exempel i README och docs
