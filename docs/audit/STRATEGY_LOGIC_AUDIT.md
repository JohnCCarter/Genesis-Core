# Auditrapport: Strategilogik (Genesis-Core)

Datum: 2026-02-21
Branch: feature/composable-strategy-phase2
Scope (kärnflöde):
- `src/core/strategy/evaluate.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/confidence.py`

Fokus: korrekthet, fail-safety, determinism/reproducerbarhet i backtest vs live, samt risk för drift-/konfigrelaterade krascher.

## Sammanfattning
Jag har identifierat **4 prioriterade risk-/felklasser** i strategilogiken:

1) **Osäkra `float(...)`-konverteringar** på sannolikheter/konfigfält kan krascha pipeline om input innehåller `None`/strängar (trots att det finns `safe_float` i delar av koden). Detta är extra känsligt eftersom en crash i `decide()` stoppar all handel.
2) **Config-kontrakt glider mellan “validerad runtime-config” och “rå champion/config dict”**: flera ställen antar att config redan är canonical/typad (floats), men `evaluate_pipeline()` mergar in champion + overrides som kan innehålla icke-coercade värden.
3) **`decide()` är monolitisk (mycket stor)** och blandar gating, override-logik, fib-checkar, hysteresis, cooldown och sizing i en funktion → hög risk för regressions och svårtestade edge cases.
4) **Override/diagnostik-state växer och kan bli dyrt** (historylistor, debugpayloads) och kan påverka backtest/optuna prestanda om debug råkar bli på.

Utöver detta finns mindre förbättringspunkter kring regimdetektion, kvalitetsskalning och robusthet i state-hantering.

---

## Detaljfynd

### Fynd A — Kritisk: `float(None)` kan fortfarande krascha (probas & thresholds)
**Filer:**
- `src/core/strategy/decision.py`
- `src/core/strategy/confidence.py`

**Observation**
- `decision.safe_float()` finns och är skapad för att undvika `float(None)`-crash (referens i docstring).
- Trots det finns flera direkta `float(...)` på fält som i praktiken kan vara `None` eller sträng:
  - `decision.py`: `p_buy = float(probas.get("buy", 0.0))`, `p_sell = float(probas.get("sell", 0.0))`
  - `confidence.py`: `p_buy = float(probas.get("buy", 0.0)) if probas else 0.0` (samma mönster)
  - `decision.py`: `thr = float(thresholds.get(regime_str, default_thr))` om thresholds dict innehåller `None`
  - `decision.py`: `multiplier = float((adaptive_cfg.get("regime_multipliers") or {}).get(regime_str, 1.0))` (kan vara str/None)

**Risk**
- En enda `None` i probas/config kan krascha `decide()` → stoppar hela pipeline (och i live kan det stoppa trading).

**Rekommenderad åtgärd**
- Ersätt dessa med `safe_float(..., default=...)`/lokal `_safe_float` och logga/flagga när coercion sker.
- Alternativt: validera & canonicalisera `probas` direkt efter `predict_proba_for()` och innan `compute_confidence/decide()`.

**Severity:** High

---

### Fynd B — Konfig- och typkontrakt är implicit: champion+override merge kan föra in "råa" värden
**Fil:** `src/core/strategy/evaluate.py`

**Observation**
- `evaluate_pipeline()` mergar champion-config och runtime overrides via `_deep_merge()`.
- Därefter skickas `configs` (rå dict) rakt in i `compute_confidence()` och `decide()`.
- `ConfigAuthority`/`RuntimeConfig` kan producera canonical floats, men det finns inget som garanterar att champion-filer/overrides alltid följer samma typkontrakt.

**Risk**
- "Osynliga" typfel (strängar, None) smyger in och kan krascha eller ge subtilt ändrat beteende.
- Reproducerbarhet: samma kod kan bete sig olika beroende på champion-filens format.

**Rekommenderad åtgärd**
- Inför ett enda tydligt steg i pipeline: `configs = RuntimeConfig(**configs).model_dump_canonical()` (eller motsvarande) innan beslutslogiken.
- Om det inte är möjligt p.g.a. extra-fält: överväg en explicit `normalize_configs(configs)` som coerces kritiska fält (thresholds/risk/mtf).

**Severity:** Medium–High

---

### Fynd C — Monolitisk `decide()` gör logiken svårtestad och riskerar regressions
**Fil:** `src/core/strategy/decision.py`

**Observation**
- `decide()` implementerar 10+ steg (EV, event/risk caps, regime, thresholds, tie-break, fib HTF/LTF gates, confidence gate, edge gate, hysteresis, cooldown, sizing + multipliers).
- Funktionen har många inre closures och stora debug-payloads.

**Risk**
- Hög risk att en ändring i en del (t.ex. fib override) påverkar andra steg.
- Svårt att skriva minimala unit tests för specifika gates.

**Rekommenderad åtgärd**
- Bryt ut till små pure-funktioner med tydliga inputs/outputs:
  - `select_candidate(...)` (proba+regim)
  - `apply_fib_gates(...)` (HTF/LTF + override)
  - `apply_confidence_gate(...)`
  - `apply_hysteresis_and_cooldown(...)`
  - `compute_position_size(...)`
- Lägg till testmatriser per gate ("table-driven tests").

**Severity:** Medium

---

### Fynd D — Override-state och debug kan växa: risk för prestanda/IO
**Fil:** `src/core/strategy/decision.py`

**Observation**
- `ltf_override_state` lagrar historiklistor per riktning med fönster (default 120). Det är OK, men kopiering/serialisering kan bli tungt.
- Debug-strukturer (`htf_fib_entry_debug`, `ltf_fib_entry_debug`, `fib_gate_summary`, `ltf_override_debug`) kan bli stora (levels, targets, raw ctx).
- `_log_decision_event()` skriver endast vid DEBUG, vilket är bra, men state_out byggs ändå med debug-payloads oavsett log-level.

**Risk**
- Backtest/Optuna kan få onödigt stora meta/state objekt som ökar minne/CPU.

**Rekommenderad åtgärd**
- Gör debug-payloads "lazy": endast inkludera full debug om en flagga är på (`configs["debug"]["fib"]` el. env-flag).
- Deduplicera/trimma levels i debug (t.ex. max N levels).

**Severity:** Low–Medium

---

### Fynd E — Dubbel regimlogik (fast-path vs unified) kan ge inkonsekvenser
**Fil:** `src/core/strategy/evaluate.py`

**Observation**
- Regim beräknas antingen via precomputed EMA50 fast-path eller `detect_regime_unified()`.
- Trösklar i fast-path (±2%) kan skilja från unified-metoden, vilket kan ändra regime beroende på om `precomputed_features` finns.

**Risk**
- Samma candles kan få olika regime beroende på körläge → påverkar kalibrering och gating.

**Rekommenderad åtgärd**
- Säkerställ att fast-path använder exakt samma logik/thresholds som unified-regime (eller dokumentera skillnaden och varför).

**Severity:** Medium

---

## Rekommenderad prioritering
1) **A (float(None)-robusthet)**: eliminera återstående crash-vägar i `decide()` och `compute_confidence()`.
2) **B (config-normalisering)**: gör config-kontrakt explicit (validera/coerce en gång i pipeline).
3) **E (regime-konsistens)**: undvik divergerande regime mellan fast-path och unified.
4) **C/D (struktur/prestanda)**: refaktorera och gör debug lazy när riskerna ovan är stängda.

---

## Handoff till nästa agent
### Mål
Öka robusthet och determinism i strategipipelinen utan att ändra avsedd tradinglogik.

### Föreslagen arbetsordning
1) **Hårdna probas/confidence konvertering**
   - Byt `float(probas.get(...))` → `safe_float(...)` i `decision.py` och `confidence.py`.
   - Lägg till unit test: `probas={"buy": None, "sell": 0.7}` ska inte krascha och ska fail-safe:a till NONE (eller definierat beteende).

2) **Inför config-normalisering i `evaluate_pipeline()`**
   - Efter merge: validera/coerce relevanta delar (minst thresholds/risk/multi_timeframe/ev).
   - Lägg till test som visar att strängar i champion-config ("0.85") inte kraschar och blir float.

3) **Regime-konsistens**
   - Verifiera att fast-path och unified ger samma regime för samma input.
   - Om inte: antingen aligna thresholds eller disable fast-path.

4) (Valfritt) **Gör debug lazy**
   - Introducera `configs["debug"]["fib"]` (default False) och bara då inkludera full debug i state_out.

### Definition of Done
- `decide()` och `compute_confidence()` tolererar `None`/sträng i probas/config utan crash.
- Reproducerbar regim mellan fast-path och unified (eller dokumenterad och testad skillnad).
- Nya enhetstester täcker minst 2 crash-scenarier.
