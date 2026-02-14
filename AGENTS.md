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

## 7) Pågående repo-cleanup (P0/P1/P2/P3/D1/D2/D3/D3A/D3B/D3C/D3D/D3E/D3F/D3G/D3H/D3I)

Status per 2026-02-14:

- Fokus: governance/docs-konsolidering
- `results/**`: ingen flytt/radering i P0
- Root-artefakter: inventeras, ingen destruktiv åtgärd i P0
- `AGENTS.md`: delad i aktiv guide + historikfil
- P1 tooling-inventering: införd (icke-destruktiv)
- P2 destruktiv cleanup: föreslagen (kräver separat kontrakt + retention policy + dry-run + explicit godkännande)
- P3 dry-run-scope: införd (icke-destruktiv, docs-only)
- P3 dry-run-rapport: införd (icke-destruktiv, docs-only)
- D1 root-artefaktflytt: införd (destruktiv, move-only, 3 filer)
- D2 root-output hardening: införd (tooling, styrd output-path för burnin_summary)
- D3 större destruktiva scope (results/scripts): föreslagen (högre risk, kräver kandidatvis kontrakt)
- D3A debug-script move-only: införd (6 lågkopplade script)
- D3B debug-script move-only: införd (3 refererade script, docs-impact dokumenterad)
- D3C test-script move-only: införd (7 lågkopplade testprototyper)
- D3D mixad low-ref move-only: införd (2 diagnose + 1 test-script)
- D3E mixad low-ref move-only: införd (3 diagnose + 2 test-script)
- D3F test low-ref move-only: införd (3 test-script)
- D3G test low-ref move-only: införd (2 test-script)
- D3H test move-only: införd (1 test-script)
- D3I test move-only: införd (3 test-script)

Detaljer:

- `docs/ops/REPO_CLEANUP_P0_CONTRACT_2026-02-14.md`
- `docs/ops/ROOT_ARTIFACT_INVENTORY_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P1_TOOLING_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P2_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_RETENTION_POLICY_DRAFT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P3_DRYRUN_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P3_DRYRUN_SCOPE_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_P3_DRYRUN_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D1_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D1_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D2_HARDEN_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D2_HARDEN_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_NEXT_BACKLOG_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3A_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3A_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3B_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3B_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3C_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3C_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3D_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3D_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3E_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3E_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3F_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3F_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3G_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3G_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3H_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3H_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3I_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3I_EXEC_REPORT_2026-02-14.md`

## 8) Referenser

- `.github/copilot-instructions.md`
- `docs/OPUS_46_GOVERNANCE.md`
- `docs/history/AGENTS_HISTORY.md`
- `CLAUDE.md`
- `docs/ops/TERMINAL_TOOL_ACCESS_PLAYBOOK_2026-02-14.md`
