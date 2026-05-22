# Genesis-Core Documentation

Status: `historical archive-era documentation index / retained for traceability / not current documentation status`

> Current status note (2026-05-22, `feature/genesis-topology-lifecycle-authority-map`): this
> README is retained as historical archive-era documentation context from `Phase-6c`. It is
> not the current project documentation index, current onboarding route, or current system
> readiness statement. For current entry points, use the repo root `README.md`, `docs/README.md`,
> and `docs/CURRENT_AUTHORITY_INDEX.md`.

**Last Updated:** 2025-10-10 (Phase-6c)

---

Historical reading note: the `ACTIVE`, `CURRENT`, and readiness labels below are preserved
as part of the archived Phase-6c snapshot and do not describe the current repository state.

## 📚 ACTIVE DOCUMENTATION

These documents are CURRENT and actively maintained:

### **Validation & Production (Phase-5/6)**

| Document | Purpose | Lines | Status |
|----------|---------|-------|--------|
| **ADVANCED_VALIDATION_PRODUCTION.md** | Comprehensive validation guide (Purged WFCV, PBO, PSI/KS, Regime Gates) | 2,045 | ✅ ACTIVE |
| **VALIDATION_CHECKLIST.md** | Concrete checklist for model validation | 471 | ✅ ACTIVE |
| **INDICATORS_REFERENCE.md** | Technical indicators reference guide | 847 | ✅ ACTIVE |
| **FEATURE_COMPUTATION_MODES.md** | Live vs Backtest feature semantics (AS-OF) | 175 | ✅ CRITICAL |

---

## 🗂️ ARCHIVED DOCUMENTATION

Historical documents moved to `archive/` for reference:

### **Phase 1-4 Documents (Superseded)**

| Document | Original Purpose | Archived As | Reason |
|----------|------------------|-------------|--------|
| ARCHITECTURE.md | Phase 1-2 system architecture | `ARCHITECTURE_phase1-2.md` | Superseded by current implementation |
| GENESIS_FEATURES.md | Original Genesis (legacy) features | `GENESIS_FEATURES_legacy.md` | Different system |
| GENESIS-CORE_FEATURES.md | Phase 1-4 feature list | `GENESIS-CORE_FEATURES_phase1-4.md` | Outdated feature set |
| STRATEGY_PROBABILITY_AND_REGIME.md | Phase 3 strategy spec | `STRATEGY_SPEC_phase3.md` | Design evolved significantly |
| SHARE.md | Basic overview | `SHARE_overview.md` | Superseded by README.md |

### **Other Archived Documents**

- `ROBUSTNESS_IMPLEMENTATION_GUIDE_superseded.md` - Superseded by ADVANCED_VALIDATION_PRODUCTION.md
- Phase 3 conflict docs, pre-phase3 README/TODO versions
- Historical granskning documents

---

## 💡 EXPERIMENTAL IDEAS

Documents in `ideas/` are FUTURE experiments, not current implementation:

| Document | Type | Status |
|----------|------|--------|
| **fvg-fib.md** | FFCI (Fair Value Gap + Fibonacci Confluence Index) feature design | 📝 Design ready, awaiting testing |

---

## 📖 HOW TO USE THIS DOCUMENTATION

### **For New Developers:**

1. **START HERE:** `README.md` (project root) - Overview and quick start
2. **THEN:** `README.agents.md` - Detailed agent workflow and Phase status
3. **VALIDATION:** `VALIDATION_CHECKLIST.md` - What needs to pass before production
4. **INDICATORS:** `INDICATORS_REFERENCE.md` - Technical indicator reference

### **For ML Work:**

1. **CRITICAL:** `FEATURE_COMPUTATION_MODES.md` - Understand AS-OF semantics
2. **VALIDATION:** `ADVANCED_VALIDATION_PRODUCTION.md` - Production ML practices
3. **REFERENCE:** `INDICATORS_REFERENCE.md` - Available indicators

### **For Historical Context:**

Check `archive/` for how the system evolved through Phase 1-4.

---

## 🧪 Benchmarkskript

- `scripts/benchmark_performance.py` kan köras direkt i Windows-terminalen utan att sätta `PYTHONIOENCODING`; all utdata är ASCII efter uppdatering 2025-11-10.

---

## 🎯 CURRENT PHASE STATUS

**Phase-6c:** REGIME-AWARE CALIBRATION (Complete)

- ML-Regime synchronization implemented
- All indicators validated
- System production-ready

**Key Files:**

- `src/core/strategy/regime_unified.py` - Regime detection
- `src/core/strategy/prob_model.py` - Regime-aware ML inference
- `config/models/tBTCUSD_1h.json` - Model with regime calibration

---

## 🔄 DOCUMENT LIFECYCLE

**Active** → Used daily, frequently updated
**Archived** → Historical reference, no longer updated
**Ideas** → Future experiments, not yet implemented

**Maintainer:** Keep this README updated when documents are added/archived.
