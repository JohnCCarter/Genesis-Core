# Genesis-Core — Project Instructions

## Frontend

- **Typ**: Embedded single-page HTML med inline CSS och vanilla JavaScript
- **Plats**: `src/core/api/ui.py` (23KB inline HTML)
- **Inga externa ramverk**: Ingen React, Vue, Tailwind eller npm-beroenden
- **Typsnitt**: `system-ui, -apple-system, Segoe UI, Roboto` / `ui-monospace` för kod
- **Färgpalett**: Tailwind-inspirerade neutrala grå (#374151, #6b7280, #e5e7eb)
- **Layout**: CSS Grid för formulär
- **JavaScript**: Fetch API, localStorage, auto-refresh var 5:e sekund, Bearer token-auth
- **Symbol-konvertering**: TEST↔real (`tTESTBTC:TESTUSD` ↔ `tBTCUSD`)

## Backend

- **Språk**: Python 3.11+
- **Framework**: FastAPI + Uvicorn (ASGI)
- **Källkod**: `src/core/`
- **Routers**: `/config`, `/strategy`, `/account`, `/paper`, `/public`, `/ui`
- **Auth**: Bearer token (`BEARER_TOKEN` env-variabel)
- **Körning**: `uvicorn core.server:app --app-dir src`
- **Exchange**: Bitfinex REST + WebSocket (`src/core/io/bitfinex/`)
- **Nyckelbibliotek**: Pandas, NumPy, Pydantic v2, Optuna, WebSockets, PyArrow

## Database

- **Ingen traditionell databas** — filbaserad SSOT
- **Runtime-config**: `config/runtime.json` (atomic writes)
- **Audit-logg**: `logs/config_audit.jsonl` (append-only)
- **Feature-cache**: PyArrow-columnar data på disk (schema_version=1)
- **Modell-registry**: `config/models/registry.json`
- **Champion-configs**: `config/strategy/champions/*.json`
- **Optimizer search spaces**: `config/optimizer/<timeframe>/**/*.yaml`

## Folder Structure

```
Genesis-Core/
├── src/
│   └── core/
│       ├── api/          # FastAPI routers + embedded UI
│       ├── backtest/     # BacktestEngine, PositionTracker, metrics
│       ├── strategy/     # Pure functions: features, models, confidence, decision
│       ├── indicators/   # ATR, EMA, RSI, Bollinger, Fibonacci
│       ├── intelligence/ # Regime detection, HTF analysis
│       ├── config/       # ConfigAuthority (SSOT), schema, validator
│       ├── optimizer/    # Optuna runner, scoring, param_transforms
│       ├── io/           # Bitfinex REST + WebSocket clients
│       └── risk/         # Position guards, P&L checks
├── config/               # Runtime JSON, champions, optimizer YAML
├── logs/                 # Audit logs (append-only)
├── tests/                # pytest: backtest, core, integration, governance
├── scripts/              # CLI-entrypoints (canonical subfolder)
├── docs/                 # Governance docs, templates, layout policy
├── .github/
│   ├── skills/           # Skills-registry (JSON, SPEC only)
│   ├── agents/           # Codex53.agent.md, Opus46.agent.md
│   └── copilot-instructions.md
├── .claude/
│   └── agents/           # Lokala agent-kopior för Claude Code
└── AGENTS.md             # Constitutional governance
```

## Deployment Strategy

- **Lokal körning**: `uvicorn core.server:app --app-dir src`
- **Backtesting**: `python -m scripts.run_backtest`
- **Optimering**: `python -m core.optimizer.runner <config.yaml>`
- **MCP-server**: `python -m mcp_server.server`
- **Inga containers** konfigurerade — direkt Python-process
- **Miljövariabler**:
  - `BEARER_TOKEN` — API-auth
  - `GENESIS_RANDOM_SEED` (default 42) — reproducibilitet
  - `GENESIS_FAST_WINDOW` (canonical 1)
  - `GENESIS_PRECOMPUTE_FEATURES` (canonical 1)
  - `SYMBOL_MODE` (realistic/synthetic, CI=synthetic)
  - `GENESIS_MODE_EXPLICIT` — explicit governance-läge

## Agents

- **Codex 5.3** (`.claude/agents/Codex53.agent.md`): Implementeringsagent
- **Opus 4.6** (`.claude/agents/Opus46.agent.md`): Governance-reviewer

Governance SSOT: `docs/governance_mode.md`
