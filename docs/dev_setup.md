# Dev setup (Windows) + editor-baslinje

**Senast uppdaterad:** 2026-01-08

Detta dokument är en praktisk “kontinuitets-SSOT” för hur man får Genesis-Core att köra lokalt utan överraskningar.

- Projektsetup (venv, dependencies, QA) ska vara editor-agnostisk.
- Editor-baslinjen (VS Code/Cursor) finns här för att säkerställa samma beteende vid handoff.

## 1) Projektsetup (Python/venv)

Utgå från `README.md` för komplett onboarding. Minsta fungerande flöde:

1. Skapa och aktivera venv (`.venv`).
2. Installera projektet editable med dev-extras.
3. Kör QA: `pre-commit` och `pytest`.

Viktigt:

- Lägg **aldrig** hemligheter i repo. Använd `.env` lokalt (ignored) och `.env.example` som mall.
- Om du kör backtests/Optuna: canonical mode är **1/1** (fast_window + precompute).
  `scripts/run_backtest.py` och `core.pipeline.GenesisPipeline` hanterar detta och markerar
  icke-canonical mode explicit via `GENESIS_MODE_EXPLICIT=1`.

Obs (scripts + src-layout):

- Scripts ska lägga `<repo>/src` på `sys.path` och sedan importera via `core.*`.
- Undvik `src.core.*` i aktiva scripts; detta fångas av guardrail-testet
  `tests/test_no_src_core_imports_in_scripts.py`.
  (Historiska scripts under `scripts/archive/**` är medvetet undantagna tills vidare.)

## 2) Kör API lokalt (FastAPI)

API:t körs som ASGI-app: `core.server:app`.

- Rekommenderat under dev: starta med `uvicorn` (se `README.md`).
- Om du ser auth-relaterade fel: verifiera `.env` och kör `/debug/auth` + `/auth/check`.

## 3) Editor-baslinje (VS Code / Cursor)

### Grundläggande inställningar

Settings-path (Windows):

- VS Code: `%APPDATA%/Code/User/settings.json`
- Cursor: `%APPDATA%/Cursor/User/settings.json`

Rekommenderade nycklar:

- `github.copilot.enable`: `"*": true`, `"scminput": false` – Copilot i kod men inte i commit-meddelanden.
- `editor.formatOnSave`: `true` – nyttjar formatterare (Black/Prettier).
- `editor.unicodeHighlight.invisibleCharacters`: `true` och `editor.unicodeHighlight.ambiguousCharacters`: `true` – fångar osynliga tecken i Python/YAML.
- `update.releaseTrack`: `stable` – undviker prerelease-regressioner under stabiliseringsfasen.
- `files.exclude` och `search.exclude`: inkludera `**/.venv`, `**/__pycache__`, `**/.mypy_cache`, `**/.log` för renare sökningar.

### Obligatoriska extensioner

Verifiera med `code --list-extensions`:

- `ms-python.python`, `ms-python.debugpy`, `ms-python.black-formatter`
- `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`
- `github.copilot`, `github.copilot-chat`, `ms-vscode.vscode-copilot-data-analysis`, `ms-vscode.vscode-copilot-vision`, `ms-vscode.vscode-websearchforcopilot`
- `ms-vscode.powershell` (Windows-shell workflow)
- `bar.python-import-helper`, `kevinrose.vsc-python-indent`, `njpwerner.autodocstring`
- `mechatroner.rainbow-csv`, `ms-toolsai.datawrangler`
- `github.codespaces`, `github.vscode-pull-request-github`, `github.vscode-github-actions`
- `openai.chatgpt` (explicit önskemål att behålla)

## 4) Verifiering (snabb check)

1. Öppna en Python-fil och kontrollera att format-on-save triggar Black.
2. Kör `pre-commit run --all-files` i venv.
3. Kör `python -m pytest`.

## 5) Handoff-påminnelser

- Dokumentera avvikelser i `docs/daily_summaries/daily_summary_YYYY-MM-DD.md`.
- Vid nya verktyg/policies: uppdatera detta dokument och relevanta instruktioner i `.github/copilot-instructions.md`.
- Starta inte långa Optuna-körningar innan `scripts/validate_optimizer_config.py` returnerar 0.
