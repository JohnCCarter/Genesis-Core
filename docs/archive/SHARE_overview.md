# Genesis-Core – Delningsbar översikt

## Syfte

Minimal, modulär kärna för tradingbot med tydlig separation av ansvar: config, observability, IO (Bitfinex), strategi (rena funktioner) och risk (rena funktioner).

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

## Struktur

```text
src/core/
  config/         # schema + validator + diff + audit
  observability/  # metrics + dashboard
  io/bitfinex/    # rest_public, rest_auth, ws_public, ws_auth
  risk/           # sizing.py, guards.py (ingen IO)
  strategy/       # rena funktionsstrategier (ingen IO)
  server.py       # FastAPI-app
```

## Endpoints

- GET `/health`
- GET `/observability/dashboard`
- GET `/account/wallets`
- GET `/account/positions`
- GET `/account/orders`
- SSOT Config: GET `/config/runtime`, POST `/config/runtime/validate`, POST `/config/runtime/propose`

Exempel:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/observability/dashboard
curl -s http://127.0.0.1:8000/account/wallets
```

## Test & Kvalitet

```powershell
pwsh -File scripts/ci.ps1  # black --check, ruff, pytest, bandit
```

Tester (exempel):

```bash
python scripts/test_rest_public.py
python scripts/test_ws_public.py
```

## Konfiguration

- `.env` (skapa från `.env.example`, inga hemligheter i repo)
- JSON-schema: `src/core/config/schema_v1.json`
- Append-only audit: `logs/config_audit.log`

## Säkerhet & Praxis

- Inga hemligheter i repo
- Pre-commit: black, ruff, bandit
- CI: Lint/Test/Security på PR och push

## Bitfinex IO

- Public: `rest_public.py`, `ws_public.py`
- Auth: `rest_auth.py`, `ws_auth.py` (kräver API‑nycklar i `.env`)

## Licens & Ägarskap

Intern utveckling. Kontakta ägaren innan extern delning.
