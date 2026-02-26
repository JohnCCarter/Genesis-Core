# Arkitektur

- src/core/config: schema_v1.json + helpers (`validator.py`), samt runtime-SSOT via `ConfigAuthority` (atomic write + append-only audit)
- src/core/observability: metrics + /observability/dashboard
- src/core/io/bitfinex: rest_public/ws_public + rest_auth/ws_auth + ExchangeClient
- src/core/strategy: rena funktionsstrategier (ingen IO)
- src/core/risk: sizing/guards (ingen IO)
- FastAPI-server (urval): /health, /observability/dashboard, /ui, /strategy/evaluate, /public/candles, /paper/submit, /auth/check

## API-ytor

- Observability: `GET /observability/dashboard` returnerar counters/gauges/events.
- Config:
  - `GET /config/runtime` – läser runtime snapshot (`cfg`, `hash`, `version`).
  - `POST /config/runtime/validate` – validerar en föreslagen runtime-config (returnerar `valid` + felkod).
  - `POST /config/runtime/propose` – patchar whitelistade fält, skriver atomiskt till `config/runtime.json` och loggar append-only audit till `logs/config_audit.jsonl`.
  - Not: JSON Schema v1 helpers finns som funktioner (`core.config.validator.validate_config`, `core.config.validator.diff_config`).

### NonceManager

- Per-nyckel µs-nonce med beständig lagring och låsning för REST.
- WS-auth använder samma källa men konverterar µs→ms.
- Engångs-retry vid "nonce too small" (10114) med `bump_nonce()`.

### WS reconnect (skelett)

- Exponential backoff med säker jitter (secrets‑baserad), övervakar ping/pong.
- Vid avbrott: stänger sessionen och låter ytterloopen reconnecta; efter anslutning skickas auth‑event igen.
- Håller WS‑lagret litet och tydligt; ingen topic‑hantering i core.

Separation of concerns: ingen nätverkslogik i strategy/risk; IO i core/io.

Se även `ARCHITECTURE_VISUAL.md` för evidence-baserade diagram med kodankare och reproducerbara `rg -n`-kommandon.
