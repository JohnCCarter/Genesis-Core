# Genesis-Core
Denna kodbas är under aktiv utveckling (WIP).

<!--
>
> - Paper only: boten körs enbart mot Bitfinex Paper‑account. Livehandel aktiveras först när utvecklaren uttryckligen beslutar det.
> - Single‑user: endast repoägaren/utvecklaren utvecklar och använder boten.  

Minimal kärna med FastAPI, config-validering, observability och Bitfinex IO.

## Setup (Python 3.11)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
uvicorn core.server:app --reload --app-dir src
```

Hälsa:

```bash
curl http://127.0.0.1:8000/health
```

## Testskript (Bitfinex)

Kräver ifylld `.env` (baserat på `.env.example`) för auth-test (auth-klienter tillkommer).

```bash
python scripts/test_rest_public.py
python scripts/test_ws_public.py
```

## Endpoints

- `GET /health` – enkel hälsokontroll.
- `GET /observability/dashboard` – counters/gauges/events.
- `POST /config/validate` – body: JSON-config, svar: `{valid, errors}`.
- `POST /config/diff` – body: `{old, new}`, svar: `{changes}`.
- `POST /config/audit` – body: `{changes, user}`, append-only logg i `logs/config_audit.log`.

Exempel:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/observability/dashboard
curl -s -X POST http://127.0.0.1:8000/config/validate -H 'Content-Type: application/json' -d '{"dry_run":true}'
curl -s -X POST http://127.0.0.1:8000/config/diff -H 'Content-Type: application/json' -d '{"old":{"x":1},"new":{"x":2}}'
curl -s -X POST http://127.0.0.1:8000/config/audit -H 'Content-Type: application/json' -d '{"changes":[{"key":"x","old":1,"new":2}],"user":"local"}'
```

### NonceManager

- Per-nyckel nonce i mikrosekunder (µs) med persistens och låsning.
- REST signerar strängen "/api/v2/{endpoint}{nonce}{body-json}" (HMAC-SHA384).
- WS använder millisekunder (ms) i `authNonce` med payload `AUTH{nonce_ms}`.
- Vid "nonce too small" (10114) görs engångs-retry efter `bump_nonce()`.

Auth-REST (curl-exempel – beräkna `bfx-nonce` och `bfx-signature` enligt `core/io/bitfinex/rest_auth.py`):

```bash
curl -s -X POST "https://api.bitfinex.com/v2/auth/r/alerts" \
  -H "Content-Type: application/json" \
  -H "bfx-apikey: <BITFINEX_API_KEY>" \
  -H "bfx-nonce: <NONCE_US>" \
  -H "bfx-signature: <HMAC_SHA384('/api/v2/auth/r/alerts' + NONCE_US + '{}')>" \
  -d '{}'
```

### Curl + PowerShell piping

Generera headers och använd dem direkt i curl (Windows PowerShell):

```powershell
$h = python scripts/build_auth_headers.py auth/r/alerts --body '{}' | ConvertFrom-Json
curl -s -X POST "https://api.bitfinex.com/v2/auth/r/alerts" `
  -H "Content-Type: application/json" `
  -H ("bfx-apikey: " + $h."bfx-apikey") `
  -H ("bfx-nonce: " + $h."bfx-nonce") `
  -H ("bfx-signature: " + $h."bfx-signature") `
  -d '{}'
```

### API‑nycklar (Paper account)

- Utveckling: Boten är en singel-user och används/utvecklas endast av utvecklaren för paper account och är för utveckling och testning, API nycklarna som används nu är API keys för paper account (Simulerad läge) Ingen rädsla att köp/sälj verkligen händer då detta är ett fullt ut paper account.
- Produktion: Boten kommer inte att användas i produktion/live trading tills utvecklaren säger annat.
- Endast nycklar behövs – REST/WS‑URL:er är hårdkodade mot Bitfinex v2. `.env` ska aldrig committas.
- Snabbverifiering:
  - `python scripts/test_ws_public.py` → `{ "ok": true }`
  - `python scripts/test_ws_auth.py` → `{ "ok": true }`
  - `python scripts/test_rest_auth.py` → `{ "status": 200 }`

### WS reconnect – snabbstart

Kör en minimal reconnect‑loop med ping/pong och åter‑auth:

```python
# scripts/run_ws_reconnect.py
import asyncio
from core.io.bitfinex.ws_reconnect import get_ws_reconnect_client

async def main():
    client = get_ws_reconnect_client()
    await client.run()

asyncio.run(main())
```

```powershell
python -c "import asyncio; from core.io.bitfinex.ws_reconnect import get_ws_reconnect_client; asyncio.run(get_ws_reconnect_client().run())"
```

## Pre-commit

```bash
pip install pre-commit
pre-commit install
```

## CI lokalt

```powershell
pwsh -File scripts/ci.ps1
```
-->

## Konfiguration (SSOT)

- Runtime config lagras i `config/runtime.json` (SSOT). Filen ignoreras av git; `config/runtime.seed.json` används som seed.
- API:
  - `GET /config/runtime` → `{ cfg, version, hash }`
  - `POST /config/runtime/validate` → `{ valid, errors, cfg? }`
  - `POST /config/runtime/propose` (kräver Bearer) → `{ cfg, version, hash }`
- Bearer‑auth: sätt env `BEARER_TOKEN` i backend. Skicka `Authorization: Bearer <token>` i UI/klient.
- Audit: ändringar loggas i `logs/config_audit.jsonl` (rotation vid ~5MB). Innehåller `actor`, `paths`, `hash_before/after`.

## UI‑noter
- UI laddar alltid `/config/runtime` vid start och visar `config_version/hash` i status.
- Knappen “Föreslå ändring” POST:ar `/config/runtime/propose` och uppdaterar status.
- Sätt bearer‑token i UI‑fältet (sparas i `localStorage.ui_bearer`).

## SymbolMapper
- `SymbolMode`: `realistic|synthetic` (env `SYMBOL_MODE`, CI sätter `synthetic`).
- Strategier använder mänskliga symboler (t.ex. `BTCUSD`); I/O mappar:
  - Realistic: `BTCUSD` → `tBTCUSD`
  - Synthetic: `BTCUSD` → `tTESTBTC:TESTUSD`
- Explicit TEST‑symboler (`tTEST...:TESTUSD`) bypassas oförändrade.