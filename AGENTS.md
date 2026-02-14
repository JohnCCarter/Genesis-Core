# README for AI Agents (Active Guide)

## Last update: 2026-02-14

Detta dokument är den **aktiva driftguiden** för agentarbete i Genesis-Core.

Historiska leverabler, långa körloggar och tidigare handoff-noteringar har flyttats till:

- `docs/history/AGENTS_HISTORY.md`

Om en regelkonflikt uppstår gäller denna prioritet:

1. Explicit user request för aktuell uppgift
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

## 1) Aktiv arbetsmodell

Repo:t använder två-agentmodellen:

- **Codex 5.3** — Agent + Plan + Doer
- **Opus 4.6** — Subagent + Reviewer + Risk-auditor

Båda rollerna definieras i:

- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`

## 2) Obligatoriskt gated commit-protokoll

### Commit-kontrakt (före arbete)

Måste innehålla:

- Category: `security | docs | tooling | refactor(server) | api | obs`
- Scope IN: exakt tillåten fillista
- Scope OUT: explicit exkluderad fillista
- Constraints (default): `NO BEHAVIOR CHANGE`
- Done criteria: konkreta gates + manuell check när relevant

Default-förbud om inget annat anges:

- Ändra inte defaults, sortering, numerik, seeds, cache keys.
- Ändra inte endpoint paths, status codes eller response shapes.
- Ändra inte env/config-tolkning eller config authority paths.

### Gate-ordning (obligatorisk)

1. Opus plan review (pre-code)
2. Codex implementation (inom scope)
3. Opus diff-audit (post-code)
4. Gates gröna
5. Commit

Commitmeddelande ska inkludera:

- Category
- Why
- What changed
- Gate results

## 3) Kommunikationsdisciplin

- Använd `föreslagen` för process/tooling-idéer som inte är implementerade och verifierade.
- Använd `införd` först efter verifierad implementation i detta repo.
- Påstå inte att blockerande CI/pre-commit är aktiv om konfigurationen inte finns och är validerad.

## 4) High-sensitivity zones (extra strikt)

Ändringar i dessa zoner kräver striktare review och deterministisk verifiering:

- `src/core/strategy/*`
- `src/core/backtest/*`
- `src/core/optimizer/*`
- runtime/config authority paths
- paper/live execution och API edges

## 5) Baslinje för verifiering

Rekommenderad gate-stack för kodcommit:

1. `black --check .`
2. `ruff check .`
3. `bandit -r src -c bandit.yaml`
4. Relevant pytest-subset
5. Fokus-smoke för berört flöde (vid behov)

För docs-only commits används reducerat gate-set enligt kontraktet.

## 6) Snabbkommandon (operativt)

### Setup (Windows PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev,ml]
```

### Optuna preflight

```powershell
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

### Canonical mode (kvalitetsbeslut)

```powershell
$Env:GENESIS_FAST_WINDOW='1'
$Env:GENESIS_PRECOMPUTE_FEATURES='1'
$Env:GENESIS_RANDOM_SEED='42'
```

## 7) Pågående repo-cleanup (P0)

Status per 2026-02-14:

- Fokus: governance/docs-konsolidering
- `results/**`: ingen flytt/radering i P0
- Root-artefakter: inventeras, ingen destruktiv åtgärd i P0
- `AGENTS.md`: delad i aktiv guide + historikfil

Detaljer:

- `docs/ops/REPO_CLEANUP_P0_CONTRACT_2026-02-14.md`
- `docs/ops/ROOT_ARTIFACT_INVENTORY_2026-02-14.md`

## 8) Referenser

- `.github/copilot-instructions.md`
- `docs/OPUS_46_GOVERNANCE.md`
- `docs/history/AGENTS_HISTORY.md`
- `CLAUDE.md`
