# Genesis DevOps Command Team — Hybrid v1.1 (Operational Contract)

Status: **införd (repo-dokumentation)**

Detta dokument är en operativ arbetsmodell som kompletterar governance-flödet.
Det är **inte** en ersättare för SSOT-källor och får inte överstyra dem.

## 0) Primära källor (SSOT)

1. `AGENTS.md` (Constitution)
2. `docs/governance_mode.md` (Mode SSOT)
3. `.github/copilot-instructions.md` (Operational contract)
4. Agentprofiler: `Codex53.agent` (Execution), `Opus46.agent` (Governance/Veto)
5. Judge: CI + Freeze Guard

**Regel:** vid konflikt följs ordningen ovan.

---

## 1) Riskklassificering (deterministisk)

### LOW

- `docs/**`
- `tests/**` (test-only)
- kommentarer/formattering
- PR-templates/metadata

### MED

- tooling/scripts (ej core paths)
- CI/workflows
- observability/logging
- server/CLI-refactor utanför core strategy/backtest/optimizer

### HIGH

- `src/core/strategy/**`
- `src/core/backtest/**`
- `src/core/optimizer/**`
- config authority / merge-semantics
- `config/strategy/champions/**`
- freeze guard-relaterat

**Default:** osäkerhet klassas som **HIGH**.

---

## 2) Mode-regel (STRICT / RESEARCH / SANDBOX)

Mode löses **alltid deterministiskt** via `docs/governance_mode.md`
(inkl. branch mapping/freeze escalation/fallback).

Ingen manuell fallback till RESEARCH om SSOT inte uttryckligen säger det.

**Hård regel:** `STRICT`-krav kan aldrig nedgraderas av riskklass.

---

## 3) Required Path

### Quick Path (LOW)

- Plan kan hoppas över endast för trivial ändring
- Opus valfri om 100% LOW + ingen tvekan
- PR merge endast via skyddade checks (ingen bypass)

### Lite Path (MED)

- Plan krävs
- Opus lite: pre-plan sanity + post-diff notes
- CI måste vara grön

### Full Gated Path (HIGH eller mode=STRICT)

- Plan krävs
- Opus obligatorisk: pre-plan + post-diff
- Stop-on-drift strikt
- CI/freeze guard måste vara gröna innan merge

---

## 4) Autonomi-policy (Codex/Opus)

### Codex (Execution)

- Implementerar endast inom Scope IN
- Producerar commit-bunden evidens + Implementation Report
- Får inte märka READY utan gate-evidens

### Opus (Governance/Veto)

- Pre-code verdict: `APPROVED | APPROVED_WITH_NOTES | BLOCKED`
- Post-diff audit med blockerande authority i HIGH/STRICT
- Kan kräva minsta rollback/remediation

### Merge authority

- LOW: Codex-förslag möjligt, men branch protection gäller alltid
- MED: Opus OK + CI green före merge
- HIGH/STRICT: Opus pre+post OK + alla required gates PASS

---

## 5) Safety rails (obligatoriska)

### A) Forbidden touches auto-check

- Om HIGH-zon berörs i LOW/MED-task ⇒ `STOP_CONDITION`
- Om `config/strategy/champions/**` eller freeze guard berörs ⇒ alltid HIGH + Full/STRICT

### B) One-candidate rule

- Gäller audit/removal: **en kandidat per PR**, ingen parallell kandidatbranch
- Rapportera först när status = `READY_FOR_REVIEW`

### C) Evidence completeness gate

- `READY_FOR_REVIEW` tillåts endast om alla obligatoriska evidensfält är ifyllda

---

## 6) Command Packet v1.1 (copy/paste per task)

`COMMAND PACKET`

- Mode: (STRICT/RESEARCH/SANDBOX) — source: `docs/governance_mode.md`
- Risk: (LOW/MED/HIGH) — why:
- Required Path: (Quick/Lite/Full)
- Objective: (1–2 meningar)
- Candidate: (om relevant)
- Base SHA: (obligatorisk)
- Scope IN: (exakta filer/paths)
- Scope OUT: (explicit lista)
- Expected changed files: (obligatorisk lista)
- Max files touched: (heltal)
- Gates required:
  - `pre-commit run --all-files`
  - `pytest -q`
  - selectors: determinism / pipeline hash / freeze guard (om relevant)
- Stop Conditions:
  - scope drift
  - behavior change utan godkänt undantag
  - hash/determinism regression
  - forbidden paths touched
- Output required:
  - Implementation Report
  - PR evidence template

---

## 7) Implementation Report (obligatorisk)

- PR link + commit SHA + branch
- Diffstat + changed files
- Gate matrix (PASS/FAIL per gate)
- Explicit: `Zero behavior change` (när relevant)
- Notes: risker / edge cases / öppna frågor
- `STOP_CONDITION` (om triggat) + evidens

---

## 8) Command Team run-loop (sekventiell)

1. Fastställ mode från SSOT.
2. Klassificera risk deterministiskt.
3. Välj path (Quick/Lite/Full) enligt mode + risk.
4. Lås Scope IN/OUT + Expected changed files.
5. Kör implementation i minsta möjliga diff.
6. Kör gates och samla commit-bunden evidens.
7. Opus post-diff audit (när required).
8. Rapportera `READY_FOR_REVIEW` eller `STOP_CONDITION` med evidens.
