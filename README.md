# Genesis-Core

Denna kodbas är under aktiv utveckling (WIP).

## MCP Server (AI Assistant Integration)

Genesis-Core includes a full-featured MCP (Model Context Protocol) server for seamless integration with VSCode, GitHub Copilot, and other AI coding assistants.

### Quick Start

```bash
# Install MCP dependencies
pip install -e ".[mcp]"

# Start the server
python -m mcp_server.server
```

**Features:**

- 🔧 7 powerful tools (read/write files, execute code, search, Git status)
- 📚 4 resource types (docs, structure, Git, config)
- 🔒 Security-first design with path validation and timeouts
- 📝 Comprehensive logging and error handling

**Documentation:** See [`docs/mcp_server_guide.md`](docs/mcp_server_guide.md) for complete setup and usage guide.

## Cloudflare Worker gateway (legal.\*) → FastAPI backend 2025-12-23

If you are using a Cloudflare Worker as an edge gateway (e.g. `legal.genesiscoremcp.com`), the worker must forward requests to a
publicly reachable FastAPI base URL (the Genesis-Core HTTP API).

- The worker cannot call `localhost` on your machine.
- `BACKEND_ORIGIN` must point to the FastAPI backend base URL (not the worker domain, and not the MCP server).
- In local development, FastAPI typically runs on `http://127.0.0.1:8000` (see the commented setup section below).
- To make it reachable from the worker, expose FastAPI via Cloudflare Tunnel (recommended) or host it externally.

Recommended pattern:

- Public backend hostname: `https://api.genesiscoremcp.com`
- Tunnel origin service: `http://127.0.0.1:8000`
- Worker config: `BACKEND_ORIGIN=https://api.genesiscoremcp.com`

Important: if you want to prevent bypassing the worker, protect the backend hostname (e.g. Cloudflare Access service token, or a
shared secret header validated by the backend).

## Execution mode policy (canonical for quality decisions) 2025-12-18

Genesis-Core har två prestandaväxlar som också påverkar exekveringsvägen i backtestmotorn:

- `GENESIS_FAST_WINDOW=1` (zero-copy windows)
- `GENESIS_PRECOMPUTE_FEATURES=1` (precompute + on-disk cache)

Policy (2025-12): **1/1 är canonical** för alla "quality decisions" (Optuna, Validate, champion-jämförelser, rapportering).

- Standardflöden kommer därför att köra 1/1 även om ditt shell råkat ha gamla env-flaggor.
- För debug/felsökning kan du köra 0/0, men det är **debug-only** och ska inte jämföras mot Optuna/Validate.

Se [`docs/features/FEATURE_COMPUTATION_MODES.md`](docs/features/FEATURE_COMPUTATION_MODES.md) för detaljer, inkl.
`GENESIS_MODE_EXPLICIT` och hur du explicit väljer 0/0 via CLI.

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

- `GET /ui` – Minimal dashboard
- `POST /strategy/evaluate` – Kör strategi‑pipeline
- `GET /public/candles` – Publika candles (Bitfinex)
- `GET /auth/check` – Snabb auth‑hälsokontroll
- `POST /paper/submit` – Skicka paper‑order (TEST‑symboler)
- `GET /paper/estimate` – Beräkna min/max ordersize (wallet-aware)
- `GET /debug/auth` – Maskerad vy av laddade nycklar
- `POST /models/reload` – Force reload model cache (efter ML training)
- `GET /health` – Hälsa
- `GET /observability/dashboard` – Counters/gauges/events
- `GET /account/wallets` – Exchange‑wallets (proxy)
- `GET /account/positions` – Aktiva positioner (proxy, TEST)
- `GET /account/orders` – Öppna ordrar (proxy, TEST)
- `GET /paper/whitelist` – Lista TEST-symboler
- SSOT Config:
  - `GET /config/runtime` → `{ cfg, version, hash }`
  - `POST /config/runtime/validate` → `{ valid, errors, cfg? }`
  - `POST /config/runtime/propose` (kräver Bearer)

Exempel:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/observability/dashboard
curl -s http://127.0.0.1:8000/account/wallets
curl -s http://127.0.0.1:8000/config/runtime
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

## Performance Optimizations

Genesis-Core includes several optimizations for faster backtesting and model training:

### Quick Start

```bash
# Fast backtest with all optimizations
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h \
  --fast-window --precompute-features

# Optuna hyperparameter optimization with performance flags
export GENESIS_FAST_WINDOW=1
export GENESIS_PRECOMPUTE_FEATURES=1
python scripts/run_optuna_optimization.py --config config/optuna/study.yaml

# Benchmark performance improvements
python scripts/benchmark_backtest.py --symbol tBTCUSD --timeframe 1h --bars 1000
python scripts/benchmark_optuna_performance.py
```

### Key Optimizations

1. **Feature Caching** - LRU cache reduces repeated calculations (5-10x speedup)
2. **Zero-Copy Windows** - NumPy array views eliminate list conversions
3. **Precomputed Indicators** - One-time computation for entire dataset (2-3x speedup)
4. **Optimizer Caching** - Cached trial summaries for faster analysis
5. **Optuna Integration** - Parameter signature caching, batch SQLite ops, optimized trial loading

### Performance Impact

**Backtesting**:
- **Hash computation**: 0.0007ms (10x faster)
- **Feature extraction**: 4.78ms per bar
- **Full backtest**: 2-3x faster with all optimizations
- **Zero memory overhead**: Uses NumPy views, not copies

**Optuna Optimization (100 trials)**:
- **Without optimizations**: ~100 minutes
- **With optimizations**: ~35 minutes
- **Speedup**: 2.8x faster

See [`docs/PERFORMANCE_GUIDE.md`](docs/PERFORMANCE_GUIDE.md) and [`docs/OPTUNA_OPTIMIZATIONS.md`](docs/OPTUNA_OPTIMIZATIONS.md) for detailed documentation.

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
