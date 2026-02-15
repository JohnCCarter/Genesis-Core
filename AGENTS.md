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

## 7) Pågående repo-cleanup (P0/P1/P2/P3/D1/D2/D3/D3A/D3B/D3C/D3D/D3E/D3F/D3G/D3H/D3I/D3J/D3K/D3L/D4A/D4B/D5/D6/D7/D8/D9/D10/D11/D12/D13/D14/D15/D16/D17/D18/D19/D20/D21/D22/D23/D24/D25/D26/D27/D28/D29/D30)

Status per 2026-02-15:

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
- D3J diagnose move-only: införd (1 diagnose-script)
- D3K diagnose move-only: införd (1 diagnose-script + 1 scopead .github-referensfil)
- D3L diagnose move-only: införd (1 diagnose-script)
- D4A results trackability blocker: införd (docs-only, execution fortsatt föreslagen)
- D4B results policy options: införd (docs-only, policyändring fortsatt föreslagen)
- D5 results out-of-band guide: införd (docs-only, execution fortsatt föreslagen)
- D6 results policy-tranche: införd (tooling/docs-only, begränsad allowlist för `archive/_orphaned/results/**`, ingen execution)
- D7 results minimal execution pilot: införd (move-only, exakt 1 fil till `archive/_orphaned/results/**`, ingen övrig execution)
- D8 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, ingen övrig execution)
- D9 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, plus scopead newline/format-normalisering för 3 orphaned filer)
- D10 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, ingen övrig execution)
- D11 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, plus scopead newline-normalisering för 6 orphaned filer)
- D12 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, plus scopead newline-normalisering för 3 orphaned filer)
- D13 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, plus scopead newline-normalisering för 3 orphaned filer)
- D14 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, plus scopead newline-normalisering för 3 orphaned filer)
- D15 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, plus scopead newline-normalisering för 3 orphaned filer)
- D16 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, ingen övrig execution)
- D17 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, ingen övrig execution)
- D18 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, plus scopead newline-normalisering för 5 carry-forward filer)
- D19 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, ingen övrig execution)
- D20 results minimal execution tranche: införd (move-only, exakt 3 filer till `archive/_orphaned/results/**`, ingen övrig execution)
- D21 results minimal delete execution tranche: införd (delete-only, exakt 1 mapp `results/hparam_search/phase7b_grid_3months/**`)
- D22 results minimal delete execution tranche: införd (delete-only, exakt 3 filer `results/backtests/tBTCUSD_1h_20251022_152515/152517/152519.json`)
- D23 results minimal delete execution tranche: införd (delete-only, exakt 10 filer `results/backtests/tBTCUSD_1h_20251022_153336..160723.json`)
- D24 results minimal delete execution tranche: införd (delete-only, exakt 10 filer `results/backtests/tBTCUSD_1h_20251022_160814..162341.json`)
- D25 results minimal delete execution tranche: införd (delete-only, exakt 10 filer `results/backtests/tBTCUSD_1h_20251022_164122..171912.json`)
- D26 results minimal delete execution tranche: införd (delete-only, exakt 7 filer `results/backtests/tBTCUSD_1h_20251022_172222..180346.json`)
- D27 results minimal delete execution tranche: införd (delete-only, exakt 10 filer `results/backtests/tBTCUSD_1h_20251026_205559..20251027_230343.json`)
- D28 results minimal delete execution tranche: införd (delete-only, exakt 10 filer `results/backtests/tBTCUSD_1h_20251225_171516..180544.json`)
- D29 results minimal delete execution tranche: införd (delete-only, exakt 10 filer `results/backtests/tBTCUSD_1h_20251225_180629..182253.json`)
- D30 results minimal delete execution tranche: införd (delete-only, exakt 10 filer `results/backtests/tBTCUSD_1h_20251225_182338..185329.json`)

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
- `docs/ops/REPO_CLEANUP_D3J_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3J_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3K_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3K_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3L_EXEC_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D3L_EXEC_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D4A_TRACKABILITY_CONTRACT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D4A_TRACKABILITY_REPORT_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D4B_POLICY_OPTIONS_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D5_OOB_EXECUTION_GUIDE_2026-02-14.md`
- `docs/ops/REPO_CLEANUP_D6_POLICY_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D6_POLICY_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D7_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D7_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D8_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D8_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D9_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D9_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D10_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D10_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D11_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D11_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D12_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D12_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D13_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D13_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D14_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D14_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D15_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D15_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D16_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D16_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D17_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D17_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D18_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D18_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D19_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D19_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D20_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D20_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D21_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D21_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D22_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D22_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D23_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D23_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D24_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D24_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D25_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D25_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D26_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D26_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D27_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D27_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D28_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D28_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D29_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D29_EXEC_REPORT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D30_EXEC_CONTRACT_2026-02-15.md`
- `docs/ops/REPO_CLEANUP_D30_EXEC_REPORT_2026-02-15.md`

## 8) Referenser

- `.github/copilot-instructions.md`
- `docs/OPUS_46_GOVERNANCE.md`
- `docs/history/AGENTS_HISTORY.md`
- `CLAUDE.md`
- `docs/ops/TERMINAL_TOOL_ACCESS_PLAYBOOK_2026-02-14.md`
