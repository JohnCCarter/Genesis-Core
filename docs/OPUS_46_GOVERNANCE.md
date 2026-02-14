# Opus 4.6 — Governance Framework for Genesis-Core

**Last update: 2026-02-14**

## Overview

Opus 4.6 är ett governance-lager som säkerställar kod-kvalitet och risk-styrning genom **3 obligatoriska gating-punkter**:

1. **Pre-Code Review** — Granska plan före implementering
2. **Diff Review** — Validera att ändringar inte introducerar oavsiktlig beteendeförändring
3. **Smoke Gates** — Köra kritisk test-delmängd före merge

Denna process gäller för:

- Alla **strategistiska beslut** (features, refactorings, config-förändringar)
- **Optuna-körningar** och resultat-analyser
- **Systeminställningar** och deployment-ändringar

Kanonisk referens är `.github/copilot-instructions.md`. Detta dokument är en utbyggd arbetsmanual och får inte stå i konflikt med den filen.

---

## Codex 5.3 — Agent + Plan + Doer

Codex 5.3 är exekveringsmotorn som tar en **commit-brief** och levererar ändringarna end-to-end.

### Codex ansvar

1. **Tar commit-brief**
   - Tolkar mål, acceptance criteria och scope (IN/OUT).
   - Identifierar berörda filer, risker och testbehov.

2. **Producerar plan/todos (planläge/agentläge)**
   - Skapar en konkret todo-lista före kodning.
   - Uppdaterar todo-status kontinuerligt under arbetet.
   - Markerar blockerad/skip med tydlig motivering.

3. **Gör ändringar strikt inom scope**
   - Ändrar endast filer/funktioner som ingår i commit-brief.
   - Flaggar scope-drift direkt om orelaterade ändringar krävs.
   - Undviker beteendeförändring utanför definierad del av systemet.

4. **Uppdaterar imports och flyttar filer säkert**
   - Vid filflytt: uppdaterar importvägar i samtliga användare.
   - Validerar referenser efter flytt (definitioner/usages/tester).
   - Säkerställer att gamla paths inte lämnar brutna beroenden.

5. **Statusmärker beslut korrekt i kommunikation**
   - Använder `föreslagen` för processförändringar som inte är implementerade.
   - Använder `införd` endast när ändringen är implementerad och verifierad i repot.
   - Får inte påstå att blockerande CI/pre-commit redan finns om den inte är införd.

### Commit-brief format (input till Codex)

```text
Title:
Goal:
Scope IN:
Scope OUT:
Acceptance criteria:
Required tests (smoke subset):
File move/import notes:
Risk notes:
```

### Gated commit-protokoll (obligatoriskt per commit)

#### 1) Commit-kontrakt (skrivs före arbete)

- **Kategori (en per commit):** `security | docs | tooling | refactor(server) | api | obs`
- **Scope IN:** exakt tillåten fillista
- **Scope OUT:** explicit exkluderad fillista
- **Förbud / Constraints (default = NO BEHAVIOR CHANGE):**
  - Ändra inte defaults, sortering, numerik, seeds, caching keys
  - Ändra inte endpoint paths/statuskoder/response shapes (om inte explicit)
  - Inga opportunistiska städningar utanför scope
- **Done-kriterier:** konkreta gates (kommandon/tester) + manuell check när relevant

**Hård regel:** Codex får inte börja implementera innan Opus har godkänt kontrakt + plan.

#### 2) Opus: Plan review (innan kod)

Opus ska:

- Bekräfta att scope är tillräckligt tight
- Peka ut riskzoner (init-ordning, config/env, determinism, API-kontrakt)
- Föreslå minsta gates som säkrar committen
- Godkänna eller stoppa

#### 3) Codex: Agent/Plan/Do (implementera)

Codex ska:

- Följa kontraktet strikt
- Göra minsta möjliga diff
- Inte förbättra logik om det inte är uttryckligen beställt
- Lämna kort filnivå-sammanfattning av ändringar

#### 4) Opus: Diff-audit (efter kod)

Opus ska verifiera:

- Ingen oavsiktlig beteendeförändring (defaults, sortering, numerik, timeouts)
- Inga ändrade env-tolkningar eller config-paths
- Inga API-ändringar utanför kontrakt
- Ingen ny risk i paper/live-flöden

Vid problem ska Opus ange exakt vad som ska revertas/justeras (minimalt).

#### 5) Gates körs → Commit

- Kör definierade gates (pre-commit/pytest/smoke subset)
- Commit tillåts endast när gates är gröna
- Commit message ska innehålla kategori + varför + vad + gates

### Viktig policy

- Små, kategoriska commits (en kategori per commit)
- `refactor(server)` innebär endast flytt/struktur/import (ingen logikförbättring)
- Trading/paper-känsliga delar granskas extra strikt:
  - `src/core/strategy/*`
  - `src/core/backtest/*`
  - `src/core/optimizer/*`
  - runtime/config authority paths
  - paper/live execution och API edges

## Source of truth vid konflikt

1. Explicit user request för aktuell uppgift
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

## Reference activation i chatten

För att referenser ska vara aktiva i en specifik chattförfrågan måste de ligga i listan "Used references" för den prompten.

Minimikontext för governance-uppgifter:

1. `.github/copilot-instructions.md`
2. `docs/OPUS_46_GOVERNANCE.md`
3. `AGENTS.md`

Vid rollspecifik granskning/implementering bör även inkluderas:

- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`

## Operativ fallback: terminalverktyg i chatten otillgängligt

Om terminalverktyg tillfälligt är otillgängligt i chattsessionen, följ playbook:

- `docs/ops/TERMINAL_TOOL_ACCESS_PLAYBOOK_2026-02-14.md`

Denna fallback är ett operativt arbetssätt och ändrar inte source-of-truth eller
gated commit-krav. Prioriteringsordningen i detta dokument och
`.github/copilot-instructions.md` gäller oförändrad.

### Codex leverabler (output)

- Uppdaterad todo-lista (från start till slutförd)
- Scope-låsta kodändringar
- Import-/filflytt-uppdateringar (om tillämpligt)
- Verifiering via definierade smoke gates
- Kort slutrapport: vad ändrades, hur verifierat, kvarvarande risker

---

## 1. Role: Opus 4.6 (Subagent + Reviewer)

Opus 4.6 är en **specialist-agent** som arbetar tillsammans med Codex 5.3 i två-agentsmodellen. Opus fokuserar på **kvalitet genom governance**, fungerar som risk-auditor och har veto vid kontraktsbrott.

### Ansvar

| Gate         | Timing                | Aktivitet                                    |
| ------------ | --------------------- | -------------------------------------------- |
| **Pre-Code** | Before implementation | Risk assessment, scope check, doc review     |
| **Diff**     | After code change     | Behavior change detection, side-effect audit |
| **Smoke**    | Before merge/commit   | Regression tests, critical path validation   |

### Verktyg & Output

- Risk assessment checklista (`OPUS_AUDIT_PLAN.md`)
- Automated diff analyzer (git-baserad)
- Smoke test orchestrator
- Gap/risk-logg

---

## 2. Gate 1: Pre-Code Review (Before Implementation)

### Purpose

Granska **planen** — inte koden — för att fånga risker, scope-drift och dokumentation-luckror innan arbetet börjar.

### Input

- Task description / issue link
- Proposed changes (feature, refactor, config tweak, etc.)
- Agent plan (if from subagent)

### Proces

1. **Document the plan** → Create `OPUS_AUDIT_PLAN_<task_id>.md` with sections:
   - Task summary
   - Acceptance criteria
   - Affected modules (code paths, configs, tests)
   - Risk inventory (regression, performance, drift)
   - Config dependencies (runtime.json, defaults, champions)
   - Scope boundaries (what's IN, what's OUT)

2. **Risk audit checklist**:
   - [ ] Scope är clearly defined och bounded
   - [ ] Acceptance criteria är testable
   - [ ] Risk exposure identified (entry/exit logic, features, backtest, optimizer)
   - [ ] Config dependencies mapped
   - [ ] Backward compat: en breaking change? Documented?
   - [ ] Feature-gate plan (A/B, temporary config, flag)?
   - [ ] Performance impact estimated?
   - [ ] Data/state cleanup needed?

3. **Sign-off**
   - If risks are acceptable → **OPUS_APPROVED_PRE**
   - If scope is fuzzy/unacceptable → Return to requester with questions

### Output

```
✅ OPUS_APPROVED_PRE: <task_id>
   Risk level: [LOW|MEDIUM|HIGH]
   Gate-required tests: [list of smoke tests]
   Config snapshots needed: [files]
   Estimated diff size: [lines]
```

---

## 3. Gate 2: Diff Review (After Code Changes)

### Purpose

Validera att **implementeringen matchar planen** och inte introducerar oavsiktliga bieffekter.

### Input

- Completed code changes (PR, commits, or branches)
- Pre-code plan (from Gate 1)

### Process

1. **Automated diff scan** (run from `scripts/opus_diff_analyzer.py`):

   ```powershell
   python scripts/opus_diff_analyzer.py --before <base> --after <head> --plan OPUS_AUDIT_PLAN_<task_id>.md
   ```

   Outputs:
   - Files changed (categorized: test, core, config, script)
   - Lines added/removed
   - Behavioral changes detected (imports, function signatures, defaults)
   - Risk flags (unexpected file touches, deletions, large deletions)

2. **Manual audit**:
   - [ ] Code changes align with pre-code plan?
   - [ ] New files follow repo structure (`src/core/...`, `scripts/...`, `tests/...`)?
   - [ ] No stray edits to unrelated files?
   - [ ] Tests added for new/changed behavior?
   - [ ] Logging/debug code removed (or intentional)?
   - [ ] No hardcoded values (numbers, paths, symbols)?
   - [ ] Config schema updated if needed?

3. **Behavioral change verification** (sample checks):
   - Decision logic: Does it affect entry/exit/risk decisions? ✓ Inteded?
   - Cache: New caches? Invalidation logic? ✓ Correct?
   - I/O: New file reads/writes? ✓ Path correct, side-effect tracked?
   - Optuna: Sampler/pruner changes? ✓ Reproducibility verified?

4. **Sign-off**
   - If diff matches plan → **OPUS_APPROVED_DIFF**
   - If unmatched changes → Return with delta notes (what to fix)

### Output

```
✅ OPUS_APPROVED_DIFF: <task_id>
   Diff size: XYZ lines across N files
   Risk changes detected: [none|LOW|MEDIUM|HIGH]
   Behavioral drifts: [list or none]
   Smoke gates ready: [test names]
```

---

## 4. Gate 3: Smoke Gates (Before Merge)

### Purpose

Köra en **kritisk delmängd av tester** för att validera att inga regressions snuck in och att core workflows fortfarande fungerar.

### Input

- Merged/integrated code changes
- Gate-required tests (from planning)

### Process

**Run the smoke suite** (or use CI/pre-commit hooks):

```powershell
# Core linting + security
black --check .
ruff check .
bandit -r src -c bandit.yaml

# Unit tests (critical paths only — subset, not full)
pytest tests/test_config_schema.py -q
pytest tests/test_backtest_engine.py::test_mode_enforcement -q
pytest tests/test_decision_logic.py -q
pytest tests/test_feature_pipeline.py -q
pytest tests/test_optimizer_runner.py -q

# Smoke: Single backtest run (baseline config, 1 month sample)
python scripts/run_backtest.py \
  --symbol tBTCUSD \
  --timeframe 1h \
  --config-file config/strategy/champions/tBTCUSD_1h.json \
  --start-date 2024-01-01 \
  --end-date 2024-02-01 \
  --smoke

# Optuna smoke (if optimizer touched)
python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_optuna_smoke_htf_fix.yaml --max-trials 2
```

**Validation criteria**:

- [ ] black/ruff/bandit: 0 errors
- [ ] Unit tests: > 95% pass
- [ ] Smoke backtest: completes, non-zero trades, reasonable metrics
- [ ] Logs: No `[ERROR]` or `[CRITICAL]`
- [ ] Output files created (backtest JSON, optuna results)

### Output

```
✅ OPUS_APPROVED_SMOKE: <task_id>
   Linting: PASS (black+ruff+bandit)
   Unit tests: 47/47 pass
   Smoke backtest: 156 trades, PF 1.14, Return +2.34%
   Optuna smoke: 2/2 trials valid
   Clear to merge: YES
```

---

## 5. Workflow Integration

### Standard Flow (Code Contribution)

```
┌─────────────────────────────┐
│  Requester: Task Request    │ (Task, acceptance criteria)
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│ GATE 1: Opus Pre-Code       │ ← Risk audit, scope check
│ (Plan review)               │
└──────────────┬──────────────┘
               │
         APPROVED? ──NO──→ [Return to requester]
               │ YES
               ▼
┌─────────────────────────────┐
│  Codex 5.3: Plan + Do       │ (Todos + scoped code changes)
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│ GATE 2: Opus Diff Review    │ ← Behavior change audit
│ (Code review)               │
└──────────────┬──────────────┘
               │
         APPROVED? ──NO──→ [Return to author]
               │ YES
               ▼
┌─────────────────────────────┐
│ GATE 3: Opus Smoke Gates    │ ← Test suite, regressions
│ (Before merge)              │
└──────────────┬──────────────┘
               │
         PASSED? ──NO──→ [Debug, fix, re-test]
               │ YES
               ▼
┌─────────────────────────────┐
│  ✅ MERGE / COMMIT          │
└─────────────────────────────┘
```

### Parallel Agent Operation

```
Timeline (example: 2 agents working in parallel)

Day 1:       Codex: Tar commit-brief + producerar plan/todos
Day 1:       Opus: Plan review + gate-set (PRE_CODE done)
Day 2:       Codex: Implementerar inom Scope IN
Day 2:       Opus: Diff-audit av ändringar (DIFF done)
Day 3:       Codex: Kör definierade gates och rapporterar resultat
Day 3:       Opus: Slutlig smoke-verifiering (SMOKE done)
Day 3:       ✅ Commit enligt kontrakt
```

---

## 6. Opus Audit Documents (Template)

### `OPUS_AUDIT_PLAN_<task_id>.md` (Pre-Code)

```markdown
# Opus Audit Plan: <Task Title>

**Date**: <ISO date>
**Task ID**: <link to issue/request>
**Requester**: <Agent name>
**Opus Auditor**: <Opus-assigned agent>

## Summary

[1-2 sentence task description]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
      ...

## Affected Modules

- `src/core/strategy/decision.py` (entry logic)
- `config/runtime.json` (signal_adaptation zones)
- `tests/test_decision_logic.py` (new test coverage)

## Risk Inventory

| Risk                     | Type     | Mitigation                          |
| ------------------------ | -------- | ----------------------------------- |
| Entry/exit logic changes | Behavior | Smoke backtest with baseline config |
| Config schema change     | Compat   | Backward-compat test in preflight   |

## Config Dependencies

- `signal_adaptation.zones` (must be present in runtime.json)
- `runtime_version` (used to trigger reload in backtest)

## Scope (IN/OUT)

**IN**: Decision logic, signal_adaptation config
**OUT**: Indicator calculations, feature pipeline

## Smoke Gates (Required)

1. `pytest tests/test_decision_logic.py -q`
2. `python scripts/run_backtest.py ... --smoke`

---

**Pre-Code Sign-off**: OPUS_APPROVED_PRE
**Risk Level**: [LOW|MEDIUM|HIGH]
```

### Commit Message Template (with Opus gates)

```
[Feature/Fix/Refactor] Short description

- Implementation detail 1
- Implementation detail 2

Opus Gates:
✅ PRE_CODE: <task_id>
✅ DIFF: <diff size>, <risk level>
✅ SMOKE: <test count passed>, <core metrics>

Related: #<issue>
```

---

## 7. Automation: `scripts/opus_diff_analyzer.py`

Kör Opus-auditen med commit-kontrakt direkt i CLI:

```powershell
python scripts/opus_diff_analyzer.py \
  --before <base_ref> \
  --after <head_ref> \
  --category docs \
  --scope-file AGENTS.md \
  --scope-file docs/OPUS_46_GOVERNANCE.md \
  --scope-file scripts/opus_diff_analyzer.py
```

Viktiga flaggor:

- `--category`: commit-kategori (`security|docs|tooling|refactor(server)|api|obs`)
- `--scope-file`: exakt tillåten fil (upprepa per fil)
- `--scope-prefix`: tillåten katalogprefix
- `--allow-behavior-change`: inaktiverar default-läget `NO_BEHAVIOR_CHANGE` för explicit godkända beteendeförändringar

Standardläge är strikt: kontraktsbrott eller out-of-scope ger `HIGH` och blockerar commit.

---

## 8. Checklist for Agents Using Opus 4.6

### Codex 5.3 execution checklist

- [ ] Commit-brief inläst och bekräftad
- [ ] Todos skapade innan första kodändring
- [ ] Scope-lås aktiverat (IN/OUT dokumenterat)
- [ ] Eventuella filflyttar utförda och imports uppdaterade
- [ ] Referenser verifierade efter flytt/import-ändringar
- [ ] Smoke subset körd enligt brief
- [ ] Slutlig todo-lista markerad komplett

### Before Starting Work

- [ ] Opus Pre-Code Review done? (Link: `OPUS_AUDIT_PLAN_*.md`)
- [ ] Risk level understood? (LOW/MEDIUM/HIGH)
- [ ] Smoke gate tests identified?
- [ ] Config snapshots noted?

### After Implementing

- [ ] Code matches pre-code plan?
- [ ] New tests added?
- [ ] Linting clean (black, ruff, bandit)?
- [ ] Ready for Opus Diff Review?

### Before Committing

- [ ] Opus Smoke Gates all pass?
- [ ] Backtest output reasonable?
- [ ] No unexpected log errors?
- [ ] Commit message includes Opus gate sign-offs?

---

## 9. FAQ

**Q: Can I skip Opus gates?**
A: Nej. Gated commit-protokollet gäller varje commit. För docs-only kan gate-setet reduceras enligt commit-kontraktet, men Opus-gates får inte hoppas över.

**Q: What if Smoke Gates fail?**
A: Fix the issue, re-run smoke gates, document the delta. No merge until gates pass.

**Q: How long does Opus review take?**
A: Pre-Code: 10–20 min. Diff: 10–30 min (depends on change size). Smoke: 5–30 min (parallel testing).

**Q: What if there's a conflict between Opus and Agent guidance?**
A: Opus gates are **mandatory** (risk governance). Agent guidance is contextual. Opus wins on safety; agents clarify intent.

---

## 10. Status & History

| Date       | Change                         | Gate | Outcome |
| ---------- | ------------------------------ | ---- | ------- |
| 2026-02-14 | Opus 4.6 framework established | —    | LIVE    |

---

**Next**: Integrate Opus gates into CI/pre-commit hooks and document in `.github/workflows` or local `.pre-commit-config.yaml`.
