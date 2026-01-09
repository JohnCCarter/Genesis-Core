# Arkitektur

- src/core/config: schema_v1.json, validator + diff och append-only audit
- src/core/observability: metrics + /observability/dashboard
- src/core/io/bitfinex: rest_public/ws_public (auth-klienter tillkommer)
- src/core/strategy: rena funktionsstrategier (ingen IO)
- src/core/risk: sizing/guards (ingen IO)
- Minimal FastAPI-server: /health och /observability/dashboard

## API-ytor

- Observability: `GET /observability/dashboard` returnerar counters/gauges/events.
- Config (SSOT):
  - `GET /config/runtime` → `{ cfg, version, hash }`
  - `POST /config/runtime/validate` → `{ valid, errors, cfg? }`
  - `POST /config/runtime/propose` (kräver Bearer) – föreslår och auditar ändringar i `logs/config_audit.jsonl`.

### NonceManager

- Per-nyckel µs-nonce med beständig lagring och låsning för REST.
- WS-auth använder samma källa men konverterar µs→ms.
- Engångs-retry vid "nonce too small" (10114) med `bump_nonce()`.

### WS reconnect (skelett)

- Exponential backoff med säker jitter (secrets‑baserad), övervakar ping/pong.
- Vid avbrott: stänger sessionen och låter ytterloopen reconnecta; efter anslutning skickas auth‑event igen.
- Håller WS‑lagret litet och tydligt; ingen topic‑hantering i core.

Separation of concerns: ingen nätverkslogik i strategy/risk; IO i core/io.
