# Risk logg: Pipeline-illusioner & spöken

> Levande logg för dold påverkan som kan ge tysta beteendeskiften mellan backtest/Optuna/manuella körningar.
> Fokus: korrekthet, determinism och jämförbarhet.

## Principer

- Stabilisering först: små, testade diffar.
- Varje riskpost ska ha: (1) evidens, (2) konsekvens, (3) fix-princip, (4) verifiering.

---

## Statusöversikt

- R10 Case/whitespace-sensitiv env-parsning (GENESIS_OPTIMIZER_JSON_CACHE): FIXAD ✅

---

## R10 — `GENESIS_OPTIMIZER_JSON_CACHE` är case/whitespace-sensitiv och kan ge förvirrande opt-in

**Status:** FIXED ✅

**Problem / risk**

- Optimizer-JSON-cache (mtime-baserad) var aktiverad endast vid exakt match i `{"1","true","True"}`.
- Det gjorde att t.ex. `GENESIS_OPTIMIZER_JSON_CACHE=TRUE` (vanligt i `.env`) eller `true ` inte aktiverade cache.

**Konsekvens**

- Förvirrande beteende och svårare reproducera “perf knobs” mellan körmiljöer.

**Fix-princip**

- Normalisera med `.strip().lower()` och tolka `"1"`/`"true"` case-insensitivt.

**Artefakter**

- Kod: `src/core/optimizer/runner.py` (`_read_json_cached`)
- Test: `tests/test_optimizer_json_cache_env_flag.py`

**Verifiering / acceptanskriterier**

- [x] Regressiontest: `GENESIS_OPTIMIZER_JSON_CACHE="TRUE"` aktiverar cache
- [x] Regressiontest: `GENESIS_OPTIMIZER_JSON_CACHE=""` och `"0"` aktiverar inte cache
