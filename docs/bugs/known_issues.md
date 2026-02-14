# Known Issues

This document tracks known issues, workarounds, and deferred fixes in Genesis-Core.

**Last Updated:** 2026-02-03

---

## Phase 3 Paper Trading Issues

### Issue #1: Champion Promotion Script Creates Wrong Structure

**Discovered:** 2026-02-03 (pre-flight blocker)

**Symptom:**

- Champion file created by promotion script lacks `merged_config` top-level key
- ChampionLoader expects `merged_config` but file only has `cfg`
- Server falls back to baseline (baseline:fallback_1h) silently

**Root Cause:**

- Promotion tooling (manual or scripted) does not generate ChampionLoader-compatible structure
- No schema validation at promotion time

**Impact:**

- HIGH - Paper trading would run with wrong strategy (baseline instead of champion)
- Detection requires manual inspection of `/strategy/evaluate` response

**Workaround:**

- Manually add `merged_config` key to champion JSON (duplicate of `cfg` content)
- Verify champion loading via API before paper trading start

**Proper Fix (deferred to post-freeze):**

- Update promotion script to generate correct structure
- Add schema validation step to promotion workflow
- Add CI test that verifies champion files load successfully

**References:**

- Fix commit: b4603c6
- Champion file: `config/strategy/champions/tBTCUSD_1h.json`

---

### Issue #2: detect-secrets Flags git_commit Hash in Champion Files

**Discovered:** 2026-02-03 (CI blocker)

**Symptom:**

- `detect-secrets` pre-commit hook flags `git_commit` field in champion JSON
- Reports "Hex High Entropy String" as potential secret
- Blocks commits containing champion files

**Root Cause:**

- Champion metadata includes `git_commit` hash (legitimate metadata)
- detect-secrets entropy heuristic cannot distinguish commit hashes from secrets

**Impact:**

- MEDIUM - Blocks CI when champion files are modified
- Workaround is manual (update .secrets.baseline)

**Workaround:**

- Run `detect-secrets scan --baseline .secrets.baseline` to update allowlist
- Stage `.secrets.baseline` with champion file changes

**Proper Fix:**

- Add inline `pragma: allowlist secret` to champion file template (if detect-secrets supports JSON)
- OR: Exclude `config/strategy/champions/*.json` from detect-secrets scan
- OR: Configure detect-secrets to ignore fields named `git_commit`

**References:**

- Fix commit: 390984d
- `.secrets.baseline` updated

---

### Issue #3: EOF Newline Missing in Champion Files

**Discovered:** 2026-02-03 (CI blocker)

**Symptom:**

- `end-of-file-fixer` pre-commit hook fails for champion JSON files
- Files written without trailing newline

**Root Cause:**

- JSON serialization does not add EOF newline by default
- Pre-commit expects POSIX-compliant text files (trailing newline)

**Impact:**

- LOW - Auto-fixed by pre-commit, but creates noise in commits

**Workaround:**

- Let `end-of-file-fixer` auto-fix (stage changes)
- OR: Manually ensure champion files end with newline

**Proper Fix:**

- Update champion file write logic to append newline
- Update promotion script/tooling

**References:**

- Fix commit: 390984d (auto-fixed)

---

## Optimization / Optuna Issues

### Issue #4: Duplicate Trials When Search Space Too Narrow

**Status:** Known limitation

**Symptom:**

- Optuna reports "Duplicate trials" and cannot suggest new parameters
- Happens when parameter ranges are very narrow or discrete

**Workaround:**

- Widen search space (lower entry thresholds, expand ranges)
- Use `bootstrap_random_trials` for initial exploration
- Ensure all YAML leaf nodes have proper `type: fixed|grid|float|int|loguniform`

**References:**

- `docs/optuna/OPTUNA_BEST_PRACTICES.md`

---

## Feature Computation Issues

### Issue #5: Two Feature Computation Paths (Live vs Backtest)

**Status:** By design (different semantics)

**Description:**

- Live trading: Current bar forming (excludes `now_index`)
- Backtesting: All bars closed (includes current bar)
- Results NOT directly comparable between modes

**Impact:**

- Can cause confusion when debugging discrepancies
- Requires awareness of which mode is active

**Mitigation:**

- Documentation: `docs/features/FEATURE_COMPUTATION_MODES.md`
- Canonical mode enforced: `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`
- Debug mode requires `GENESIS_MODE_EXPLICIT=1`

**References:**

- `CLAUDE.md` (Feature Computation Modes section)

---

## CI / GitHub Actions Issues

### Issue #6: GitHub Actions Partial Outage (2026-02-03)

**Discovered:** 2026-02-03 16:10 UTC

**Symptom:**

- Workflows do not trigger or show in UI after push
- "Delays in UI updates for Actions Runs"
- API returns `total_count: 0` even after push confirmed

**Root Cause:**

- GitHub Actions service degradation
- Mitigation applied 16:51 UTC, monitoring ongoing

**Impact:**

- HIGH during outage - Cannot verify CI-green status
- Blocks paper trading pre-flight verification

**Workaround:**

- Wait for GitHub service recovery
- Trigger with empty commit after recovery
- Verify via GitHub UI directly

**Status:**

- 2026-02-03 18:07 UTC - Recovery in progress
- Commits 390984d and db8d547 in queue

**References:**

- GitHub Status: https://www.githubstatus.com
- Incident timeline: 16:10 UTC investigation → 16:51 UTC mitigation

---

## Script / Tooling Issues

### Issue #7: Lambda Expression in calculate_paper_trading_metrics.py

**Discovered:** 2026-02-03 (ruff E731)

**Symptom:**

- `status_emoji = lambda passed: "✅" if passed else "❌"`
- Ruff flags: "Do not assign a `lambda` expression, use a `def`"

**Impact:**

- LOW - Style issue, no behavior change

**Fix:**

- Changed to proper function definition
- Commit: 390984d

---

### Issue #8: Unused Variables in Validation Scripts

**Discovered:** 2026-02-03 (ruff F841)

**Symptom:**

- `bar_index` assigned but never used in `run_extended_validation_2024.py`
- `state_out` assigned but never used in `sanity_check_size_zero_reasons.py`

**Impact:**

- LOW - Dead code, no functional impact

**Fix:**

- Removed unused assignments
- Commit: 390984d

---

## Process / Workflow Issues

### Issue #9: ChampionLoader Structure Not Documented

**Discovered:** 2026-02-03

**Symptom:**

- No documentation specifying expected champion file structure
- Promotion guide does not mention `merged_config` requirement

**Impact:**

- MEDIUM - Leads to manual errors, pre-flight blockers

**Fix Needed:**

- Document ChampionLoader expected structure
- Add example champion file to docs
- Update promotion guide with structure requirements

**References:**

- `src/core/optimizer/champion.py` (ChampionLoader implementation)

---

## Template for New Issues

```markdown
### Issue #N: [Short Title]

**Discovered:** YYYY-MM-DD

**Symptom:**

- What happens
- Error messages or unexpected behavior

**Root Cause:**

- Why it happens

**Impact:**

- HIGH/MEDIUM/LOW
- Who/what is affected

**Workaround:**

- Immediate solution (if available)

**Proper Fix:**

- Long-term solution
- Deferred to: [milestone/date]

**References:**

- Commits, files, docs
```

---

## Resolution Process

1. **Discover** - Document symptom, impact, discovery date
2. **Diagnose** - Root cause analysis
3. **Workaround** - Immediate unblocking solution (if critical)
4. **Fix** - Proper solution (may be deferred)
5. **Verify** - Test fix, update docs
6. **Close** - Mark resolved, reference fix commit

---

## Issue Priorities

- **HIGH** - Blocks critical path (paper trading, production)
- **MEDIUM** - Causes friction, manual work, or confusion
- **LOW** - Style issues, minor annoyances
