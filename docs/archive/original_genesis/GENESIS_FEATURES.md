# Genesis (original) – Funktionsöversikt

Detta dokument sammanfattar de viktigaste funktionerna i original‑Genesis, som referens när vi mappar/porterar till Genesis‑Core.

## API‑yta (REST)

- Router prefix `/api/v2` med endpoints för:
  - Orderläggning, avbokning, historik (se `rest/routes.py`)
  - Wallets och funding (`rest/wallet.py`, `rest/funding.py`)
  - Positioner och positionshistorik (`rest/positions.py`, `rest/positions_history.py`)
  - Margin‑information (`rest/margin.py`)
  - Symboltjänster, watchlist, mallar, strategiinställningar (`services/*` via `routes.py`)
- Unified Config API (`rest/unified_config_api.py`):
  - Nyckelregister, schema, RBAC‑kontroller
  - Preview/apply‑flöde, audit logging och filtrering

## WebSocket/Socket.IO

- Socket.IO‑bridge för subscribes/unsubscribes (`ws/subscription_events.py`):
  - Kanaler: `ticker`, `trades`, `candles:trade:<tf>:<sym>`
  - Hjälper UI att konsumera WS utan REST‑wrap
- WebbSocket‑manager (`ws/manager.py`):
  - Privata Bitfinex‑strömmar: order (os/on/ou/oc), trades (te/tu)
  - Emit till UI‑events: `order_snapshot`, `order_new`, `order_update`, `order_cancel`, `trade_executed`
  - Wallet/Position handlers (`ws/wallet_handler.py`, `ws/position_handler.py`)

## Riskhantering

- Globala riskvakter (`services/risk_guards.py`, `services/unified_risk_service.py`):
  - Max daily loss, kill‑switch (max drawdown), exposure limits
  - Dagliga trade‑limits, cooldowns, trading windows
  - Circuit breaker: felräkning per tidsfönster, timeout/stängning, notifieringar
  - Guards‑konfig: `config/risk_guards.json`
- Risk Manager (`services/risk_manager.py`): pre‑trade checks mot policy + guards
- Policy Engine (`services/risk_policy_engine.py`): constraints/policybeslut

## Indikatorer

- `indicators/`:
  - `rsi.py`: RSI‑beräkning
  - `ema.py`: EMA + ema_z hjälpare
  - `adx.py`: ADX (TA‑Lib om finns, annars fallback)
  - `atr.py`: ATR
  - `regime.py`: Regimdetektion via ADX och EMA‑slope

## Strategier & Signal

- Enhetlig signalservice (`services/signal_service.py`, `services/unified_signal_service.py`)
- Realtime strategi‑integration i Bitfinex WS‑service
- Viktad strategiutvärdering (`services/strategy.py`, `strategy/weights.py`)

## Order & Exekvering

- TradingService med lägen: standard (REST), enhanced, realtime
- Idempotent orderläggning (client_id), DRY_RUN‑läge
- Post‑Only/Reduce‑Only stöd
- Bracket/OCO (`services/bracket_manager.py`):
  - Kopplar ihop entry/SL/TP via grupp‑ID, hanterar fills och auto‑cancel

## Konfiguration & Settings

- Pydantic settings med `.env`, fallback till v1/v2 (`config/settings.py`)
- Key registry + priority profiles (`config/key_registry.py`, `config/priority_profiles.py`)
- Startup‑konfiguration/aktivering av komponenter (`config/startup_config.py`)

## Observability & Rate Limiting

- Prometheus‑text (legacy) via services/metrics
- Avancerad rate limiter (`utils/advanced_rate_limiter.py`), request throttle/debouncer
- Loggning med sampling/dedup, latency‑trösklar

## Övrigt

- Backtest‑service, notifieringar, performance‑mätning, probabilistisk modell/validering
- MCP/Supabase integrationer (valbara)

---

### Portnings‑karta till Genesis‑Core (förslag)

- REST endpoints: börja med minsta nödvändiga (health/observability/config) och lägg till order/wallet/positions efter behov.
- WS: introducera publika kanaler (ticker/trades/candles) först, därefter privata event (os/on/ou/oc/te/tu) med tydliga callback‑interfaces.
- Risk: mappa globala guards och policy till `core/risk`, IO‑fritt. Circuit breaker som separat modul.
- Indikatorer/strategi: rena funktioner i `core/indicators` och `core/strategy` (ingen IO), håll signalgränssnitt stabilt.
- Observability: Prometheus‑exporter och händelsekategorisering på sikt.

## Nonce‑hantering (Bitfinex v2)

- REST v2
  - Nonce måste vara ett strikt växande heltal per API‑nyckel. Vanlig praxis: tidsstämpel i mikrosekunder (µs).
  - Signatur: HMAC‑SHA384 över strängen: "/api/v2/{endpoint}{nonce}{body-json}" med API‑hemligheten.
  - Headers: `bfx-apikey`, `bfx-nonce`, `bfx-signature`, `Content-Type: application/json`.

- WebSocket v2 (auth event)
  - `authNonce` ska vara millisekunder (ms). `authPayload` är `"AUTH{nonce_ms}"`. `authSig` är HMAC‑SHA384 av payload.
  - Meddelande: `{ event: "auth", apiKey, authNonce, authPayload, authSig }`.

- Felhantering
  - Vid t.ex. `10114` ("nonce too small"): bumpa lokalt nonce (≥ +1e6 µs), uppdatera cache och gör en engångs‑retry.
  - Spåra nonce per nyckel med persistens och låsning för process-/tråd‑säkerhet.

- Praxis i original‑Genesis
  - `NonceManager`: per‑nyckel, µs, filpersistens, `Lock`; WS återanvänder och konverterar µs→ms.
  - Engångs‑retry med `bump_nonce()` vid nonce‑fel.

- Rekommenderad portning till Genesis‑Core
  - Lägg till `NonceManager` och uppdatera REST/WS‑klienterna att använda den, inkl. engångs‑retry på 10114.
