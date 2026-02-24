# README for AI Agents (Active Guide)

## Last update: 2026-02-24

Detta dokument är den **aktiva driftguiden** för agentarbete i Genesis-Core.

Historiska leverabler, långa körloggar och tidigare handoff-noteringar har flyttats till:

- `docs/history/AGENTS_HISTORY.md`

Om en regelkonflikt uppstår gäller denna prioritet:

1. Explicit user request för aktuell uppgift
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

## 0) Scope för instruktioner (viktigt)

- Använd repo-lokala styrdokument i detta repo.
- Använd **inte** global workstation-kontext som policykälla för repo-beslut.
- Repo-specifika regler har alltid företräde för implementation/review här.

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

## 3.1) Skills-first policy

- Invokera relevanta repo-skills för uppgiftens domän innan ad hoc-exekvering.
- Om lämplig skill saknas: skapa en `föreslagen` skill (JSON + docs + dev-manifest) innan process-coverage påstås.
- Skill-policy är normativ för både implementering och governance-review.

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

## 7) Repo-cleanup (komprimerad status)

Aktuell policy:

- `AGENTS.md` ska vara kort och operativ; historik och långa körloggar hör hemma i `docs/history/**` och `docs/ops/**`.
- Cleanup med destruktiv effekt kräver **separat commit-kontrakt**, explicit scope, och verifierad gate-körning.
- Nya cleanup-trancher ska inte dokumenteras som långa inline-listor här; länka i stället till kontrakt/rapport under `docs/ops/`.

Operativt läge (2026-02):

- Governance/docs-konsolidering genomförd.
- Historiska detaljer för tidigare trancher finns i `docs/ops/REPO_CLEANUP_*`.
- Aktiv backlogg för nästa steg finns i `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`.

Det här avsnittet är medvetet kort för att undvika dokumentdrift och duplicerad historik.

## 8) Referenser

- `.github/copilot-instructions.md`
- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`
- `.github/skills/repo_clean_refactor.json`
- `docs/OPUS_46_GOVERNANCE.md`
- `docs/history/AGENTS_HISTORY.md`
- `CLAUDE.md`
- `docs/ops/TERMINAL_TOOL_ACCESS_PLAYBOOK_2026-02-14.md`
