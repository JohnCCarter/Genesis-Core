### README för AI‑agenter (lokal utveckling)

Denna fil beskriver hur AI‑agenter ska arbeta lokalt med projektet.

#### Regler
- Följ Separation of concerns: `core/strategy/*` är rena, deterministiska funktioner.
- Inga hemligheter i loggar; använd `core.utils.logging_redaction` vid behov.
- Pausa vid osäkerhet, verifiera med tester innan du fortsätter.
- Skriv alltid enhetstester när du lägger till logik. Håll latens per modul < 20 ms.
- Använd `metrics` endast i orkestreringslager (`core/strategy/evaluate.py`), inte i pure‑moduler.

#### Setup (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
```

#### CI lokalt
```powershell
pwsh -File scripts/ci.ps1
```

#### Kör FastAPI lokalt
```powershell
uvicorn core.server:app --reload --app-dir src
```

#### URL:er
```
UI: http://127.0.0.1:8000/ui
Health: http://127.0.0.1:8000/health
```

#### Strategy‑pipeline lokalt
Se exempel i `README.md` (GitHub‑läsare) eller kör tester:
```powershell
python -m pytest -q
```

#### Konfiguration (SSOT)
- Runtime: `config/runtime.json` är SSOT; seedas från `config/runtime.seed.json` om saknas. Filen är git‑ignorerad.
- API:
  - `GET /config/runtime` → `{ cfg, version, hash }`
  - `POST /config/runtime/validate` → `{ valid, errors, cfg? }`
  - `POST /config/runtime/propose` → kräver `Authorization: Bearer <token>` (env `BEARER_TOKEN`).
- UI:
  - Sätt bearer‑token i UI‑fältet (sparas i `localStorage.ui_bearer`).
  - “Föreslå ändring” POST:ar `/config/runtime/propose` och uppdaterar statuspanel (version/hash).
- Audit: ändringar loggas i `logs/config_audit.jsonl` (rotation ~5 MB) med `actor`, `paths`, `hash_before/after`.

#### SymbolMapper
- `SYMBOL_MODE=realistic|synthetic` (CI sätter `synthetic`).
- Strategi använder mänskliga symboler (`BTCUSD`); I/O mappar till Bitfinex (`tBTCUSD`) eller TEST (`tTESTBTC:TESTUSD`).
- TEST‑symboler bypassas (skickas oförändrade).

#### Filstruktur (kärna)
- `