# Genesis-Core – Delningsbar översikt

## Syfte

Minimal, modulär kärna för tradingbot med tydlig separation av ansvar: config/runtime-SSOT, observability, IO (Bitfinex), strategi (rena funktioner) och risk (rena funktioner).

## Snabbstart (Windows PowerShell)

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

## Struktur (hög nivå)

```text
src/core/
  config/         # runtime config + schema/validering + audit
  observability/  # metrics + dashboard
  io/bitfinex/    # rest_public, rest_auth, ws_public, ws_auth
  risk/           # sizing.py, guards.py (ingen IO)
  strategy/       # strategi/pipeline (deterministiska funktioner)
  server.py       # FastAPI-app
```

## Viktiga endpoints

- GET `/health`
- GET `/observability/dashboard`
- GET `/ui`
- POST `/strategy/evaluate`
- GET `/public/candles`
- GET `/auth/check`
- GET `/account/wallets`
- GET `/account/positions`
- GET `/account/orders`
- GET `/paper/whitelist`
- GET `/paper/estimate`
- POST `/paper/submit`
- GET `/debug/auth`
- POST `/models/reload`
- GET `/config/runtime`
- POST `/config/runtime/validate`
- POST `/config/runtime/propose`

Exempel:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/observability/dashboard
curl -s http://127.0.0.1:8000/config/runtime
curl -s -X POST http://127.0.0.1:8000/strategy/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"policy":{"symbol":"tBTCUSD","timeframe":"1h"}}'
```

## Test & kvalitet

```powershell
pwsh -File scripts/ci.ps1  # black --check, ruff, pytest, bandit
```

Tester (exempel):

```bash
python scripts/test_rest_public.py
python scripts/test_ws_public.py
```

## Konfiguration (SSOT)

- `.env` (skapa från `.env.example`, inga hemligheter i repo)
- Runtime SSOT: `config/runtime.json`
- Append-only audit: `logs/config_audit.jsonl`

## Säkerhet & praxis

- Inga hemligheter i repo
- Pre-commit: black, ruff, bandit
- CI: lint/test/security på PR och push

## Licens & ägarskap

Intern utveckling. Kontakta ägaren innan extern delning.
