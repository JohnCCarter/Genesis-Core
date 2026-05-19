# Arkitektur

- src/core/config: schema_v1.json + helpers (`validator.py`), samt runtime-SSOT via `ConfigAuthority` (atomic write + append-only audit)
- src/core/observability: metrics + /observability/dashboard
- src/core/io/bitfinex: rest_public/ws_public + rest_auth/ws_auth + ExchangeClient
- src/core/strategy: rena funktionsstrategier (ingen IO)
- src/core/risk: sizing/guards (ingen IO)
- FastAPI-server (urval): /health, /observability/dashboard, /ui, /strategy/evaluate, /public/candles, /paper/submit, /auth/check
- API-layout: `src/core/server.py` är canonical entrypoint/assembler medan route-implementationer ligger i `src/core/api/*` (`config`, `info`, `status`, `models`, `account`, `ui`, `public`, `paper`, `strategy`).

## API-ytor

- Observability: `GET /observability/dashboard` returnerar counters/gauges/events.
- Config:
  - `GET /config/runtime` – läser runtime snapshot (`cfg`, `hash`, `version`).
  - `POST /config/runtime/validate` – validerar en föreslagen runtime-config mot runtime-schemat (returnerar `valid` + felkod), men `valid=true` innebär inte i sig live-write-authority.
  - `POST /config/runtime/propose` – patchar whitelistade live-update-fält, kräver bearer + `expected_version`, skriver atomiskt till `config/runtime.json` och loggar append-only audit till `logs/config_audit.jsonl`; schema-valida men live-blockade patchar returnerar det grova publika felet `non_whitelisted_field`.
  - Not: `core.config.validator` exposes only the legacy/test-only helpers `LEGACY_SCHEMA_PATH`, `validate_legacy_config`, and `diff_legacy_config`; runtime config authority and API endpoint behavior do not depend on this module.
  - Current-state-matris för schema-valid vs live-skrivbar runtime-config finns i `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`.

### NonceManager

- Per-nyckel µs-nonce med beständig lagring och låsning för REST.
- WS-auth använder samma källa men konverterar µs→ms.
- Signerade REST-anrop använder strukturerad felmarkör-extraktion och bounded retry upp till tre försök för nonce-fel (`10114` / `nonce`-markörer), `429`/`5xx`, och transienta request-fel; nonce-specifika retries använder `bump_nonce()` och bounded jitter-backoff.

### WS reconnect (skelett)

- Exponential backoff med säker jitter (secrets‑baserad), övervakar ping/pong.
- Vid avbrott: stänger sessionen och låter ytterloopen reconnecta; efter anslutning skickas auth‑event igen.
- Håller WS‑lagret litet och tydligt; ingen topic‑hantering i core.

Separation of concerns: ingen nätverkslogik i strategy/risk; IO i core/io.

Se även `ARCHITECTURE_VISUAL.md` för evidence-baserade diagram med kodankare och reproducerbara `rg -n`-kommandon.
