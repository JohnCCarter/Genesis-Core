# Genesis-Core

Genesis-Core är en Python 3.11+ kodbas för **deterministisk backtest/optimering** och en **FastAPI-tjänst** runt en trading-strategi.

Viktiga principer:

- **Paper / TEST-symboler**: paper-orderflöden är hårt begränsade till whitelistade TEST-spotpar.
- **Reproducerbarhet**: samma config + samma data ska ge samma resultat (stabiliseringsfokus).
- **SSOT config**: runtime-konfig styrs via `config/runtime.json` och config-API.

## Snabbstart (Windows PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Starta API (lokalt):

```powershell
uvicorn core.server:app --reload --app-dir src
```

Verifiera tooling & tester:

```powershell
pre-commit run --all-files
python -m pytest
```

## Secrets / .env

- Lägg **aldrig** `.env` i git.
- Utgå från `.env.example` för lokala nycklar/inställningar.
- Säkerhet: API:t ska inte returnera råa exception-meddelanden till klienter; felsök via loggar (och `error_id` när det finns).

## MCP Server (AI Assistant Integration)

Repo:t innehåller en MCP-server (Model Context Protocol) för integration med VS Code / Copilot och andra assistenter.

```powershell
python -m pip install -e ".[mcp]"
python -m mcp_server.server
```

Se:

- `mcp_server/README.md` (operativ guide)
- `docs/mcp_server_guide.md` (projekt-specifik guide)

## Execution mode policy (canonical för quality decisions) 2025-12-18

Genesis-Core har två prestandaväxlar som också påverkar exekveringsvägen i backtestmotorn:

- `GENESIS_FAST_WINDOW=1` (zero-copy windows)
- `GENESIS_PRECOMPUTE_FEATURES=1` (precompute + on-disk cache)

Policy (2025-12): **1/1 är canonical** för alla "quality decisions" (Optuna, Validate, champion-jämförelser, rapportering).

- Standardflöden kommer därför att köra 1/1 även om ditt shell råkat ha gamla env-flaggor.
- För debug/felsökning kan du köra 0/0, men det är **debug-only** och ska inte jämföras mot Optuna/Validate.

Se `docs/features/FEATURE_COMPUTATION_MODES.md` för detaljer, inkl. `GENESIS_MODE_EXPLICIT`.

## Konfiguration (SSOT)

- Runtime config lagras i `config/runtime.json` (SSOT). Filen ignoreras av git; `config/runtime.seed.json` används som seed.
- API:
  - `GET /config/runtime` → `{ cfg, version, hash }`
  - `POST /config/runtime/validate` → `{ valid, errors, cfg? }`
  - `POST /config/runtime/propose` (kräver Bearer) → `{ cfg, version, hash }`
- Bearer‑auth: sätt env `BEARER_TOKEN` i backend. Skicka `Authorization: Bearer <token>` i UI/klient.
- Audit: ändringar loggas i `logs/config_audit.jsonl` (rotation vid ~5MB). Innehåller `actor`, `paths`, `hash_before/after`.

## Registry governance (skills/compacts) – repo som SSOT

Genesis-Core använder en enkel governance-modell där "skills" och "compacts" är **versionerade i repo:t**
och används som SSOT för agent-/processregler.

- Registry-data ligger under `registry/`.
  - `.github/skills/*.json` (versionerade skills)
  - `registry/compacts/*.json` (versionerade compacts)
  - `registry/manifests/dev.json` och `registry/manifests/stable.json` (vilka versioner som är aktiva)
  - `registry/schemas/*.schema.json` (JSON Schema)
- CI gate: `python scripts/validate_registry.py` validerar schema + korsreferenser.
- Break-glass / audit: om `registry/manifests/stable.json` ändras i en PR kräver CI även att
  `registry/audit/break_glass.jsonl` uppdateras med en audit-entry som refererar committen som ändrade
  `registry/manifests/stable.json` (via `commit_sha`).
- Review-disciplin: `.github/CODEOWNERS` kan kräva review för ändringar under `registry/`.

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
