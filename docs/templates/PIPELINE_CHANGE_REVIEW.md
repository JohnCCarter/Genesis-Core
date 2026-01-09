# 🛡️ Pipeline Integrity Review (PIR)

**Change ID/Commit:** [e.g., feat/optimize-fib-calc]
**Date:** YYYY-MM-DD
**Reviewer:** [Name/Agent]
**Scope:** [e.g., BacktestEngine, Indicators, Data Loading]

---

## 1. Change Summary

_Short description of technical changes._

- [ ] Refactoring
- [ ] Bug fix
- [ ] Performance optimization
- [ ] New feature

**Description:**

> [Write here...]

---

## 2. Determinism Check (The "Chaos Test")

_Run the same config twice. Is the result IDENTICAL?_

- **Config:** `config/backtest_defaults.yaml` (or specific test config)
- **Seed:** 42
- **Run 1 Hash/Trades:** [e.g., 386 trades, MD5: abc...]
- **Run 2 Hash/Trades:** [e.g., 386 trades, MD5: abc...]

- [ ] **PASS** (Exact same result)
- [ ] **FAIL** (Results differ -> STOP & DEBUG)

---

## 3. Mode Parity Check (Fast vs Streaming)

_If changing indicators or execution: Does vectorized code (Fast) match iterative code (Streaming)?_

- **Fast Mode Trades:** [Count]
- **Streaming Mode Trades:** [Count]
- **Diff:** [Describe any differences and if acceptable]

- [ ] **PASS** (Identical or negligible diff due to float precision)
- [ ] **WARN** (Small differences, explained)
- [ ] **FAIL** (Logic error, different signals)
- [ ] **N/A** (Change does not affect execution logic)

---

## 4. State Management & Leakage

_Have we introduced variables that persist between runs?_

- [ ] Are all class variables reset in `__init__` or `reset()`?
- [ ] Are global caches (e.g., `_htf_context_cache`) handled/cleared?
- [ ] Is `PositionTracker` reset correctly?

---

## 5. Regression Testing (Champion Check)

_Does the change negatively affect our current Champion (unintentionally)?_

- **Champion:** [e.g., tBTCUSD_1h]
- **Previous Score/PF:** [e.g., PF 1.25]
- **New Score/PF:** [e.g., PF 1.25]

- [ ] **NEUTRAL** (No change, expected for refactoring)
- [ ] **IMPROVED** (Expected for bug fix)
- [ ] **DEGRADED** (Warning: Did we change logic unintentionally?)

---

## 6. Performance Impact

_Did it get faster or slower?_

- **Execution Time (1 year 1h):** [e.g., 4.2s]
- **Memory Usage:** [Normal/High]

---

## 7. Verdict

_Final assessment._

- [ ] ✅ **APPROVED** - Ready for merge/main.
- [ ] ⚠️ **CONDITIONAL** - Approved with notes (e.g., document new diff).
- [ ] 🛑 **REJECTED** - Must be fixed before merge.

**Next Steps:**

1. [e.g., Update unit tests]
2. [e.g., Run full Optuna-smoke test]
