## 2026-01-14

You are a senior system architect and critical reviewer for Genesis-Core.
Goal: Produce a read-only, evidence-based analysis of which indicators/features are used, flag overlaps/risks, and map them to Optuna/scorer/champion selection.

NON-NEGOTIABLE:

- Do not guess. Only report what you can verify from the code/configs.
- No lookahead bias. Respect strict as-of semantics.
- Prefer explicit behavior over implicit behavior.
- If context is missing, fail explicitly and list what’s missing.
- No behavior change unless explicitly requested. If you propose changes, include tests.

TASK (B + C):

1. Identify the Single Source of Truth for feature computation:

   - Find the module(s) that compute features "as-of" (likely something like features_asof.py).
   - List every computed feature key, and for each, the upstream indicators used (RSI/ATR/BB/ADX/FIB/etc), and the input columns required.
   - Note any env flags that affect feature computation (e.g., GENESIS_PRECOMPUTE_FEATURES, FAST_WINDOW, FAST_HASH, DISABLE_METRICS).

2. Inventory all indicator implementations:

   - Locate where RSI/ATR/BB/ADX/EMA/MACD/Fib swing detection etc. are computed.
   - Cross-check which indicators are computed but never used downstream (dead/unused compute).
   - Produce a concise table: indicator -> file -> where used (feature keys / strategy / exits / guards).

3. Flag overlaps / risks (B):

   - Identify redundant or highly correlated features (e.g., fib05_x_rsi_inv vs fib05_prox_atr + rsi_inv_lag1).
   - Identify duplicated computations of the same indicator in multiple places (vectorized vs asof vs precompute).
   - Identify potential mismatches between precomputed feature keys and runtime lookup keys.
   - Identify any implicit fallbacks (slow-path) that might make Optuna trials non-comparable across runs.
   - Identify any places where missing precompute data changes behavior silently; if found, propose explicit failure or explicit logging.

4. Map features to model schema + Optuna + scorer + champion (C):
   - Find where model schema / selected feature set is defined (likely JSON configs).
   - For each model config (or at least for tBTCUSD_1h and any other active symbols), list:
     - schema features used by the model
     - which computed features are NOT in schema (computed but unused by model)
   - Trace how model output feeds into scorer and decision:
     - locate scorer versioning (GENESIS_SCORE_VERSION) and how score is computed
     - identify what Optuna optimizes (objective) and which params affect features vs only decision thresholds
   - Trace champion selection / loading:
     - where champion config is loaded
     - how it is merged/overridden in backtest/optimizer vs live
     - verify determinism guards (e.g., global_index / explicit config)
   - Deliver a diagram-like chain:
     Raw candles -> indicators -> features -> model(schema) -> proba/confidence -> scorer -> decision -> backtest metrics.

DELIVERABLES:
A) A structured report (markdown) with:

- SSOT feature list (feature_key -> formula/inputs -> source file/line ref)
- Indicator inventory (indicator -> implementation -> used by which feature keys)
- Overlap/risk section with concrete evidence and impact
- Optuna/scorer/champion mapping with file references
  B) A list of “actionable recommendations” (no code changes unless asked), prioritised by:

1.  correctness/determinism
2.  testability/traceability
3.  performance (only if safe)

OPTIONAL (only if trivial and safe):

- Add a small script or test that asserts:
  - all model schema feature names exist in SSOT output
  - no unused computed features unless explicitly justified
    But do NOT implement unless requested; just propose.

Start by printing the repo paths you will inspect and the grep/search terms you will use.
Then proceed step-by-step and cite exact files/definitions.

1. Reproducerbar Optuna (slutar jämföra äpplen och päron)

Om vissa trials kör precompute-path och andra kör slow-path (p.g.a. saknade keys/flags) så blir resultaten inte jämförbara även om seed är samma.
➡️ Vinsten: Optuna hittar bättre parametrar snabbare eftersom objective blir stabilt.

2. Snabbare körningar (utan att offra korrekthet)

När ni vet exakt:

vilka indikatorer/features som faktiskt används av modellen (schema)

vilka som bara räknas “för säkerhets skull”
…kan ni kapa onödig beräkning eller åtminstone undvika att precomputea sådant som ändå inte används.
➡️ Vinsten: kortare backtest/trial-tider och lägre CPU-kostnad, men med bibehållen SSOT.

3. Mindre feature-creep och mindre “spagetti”

En explicit karta:
candles → indicators → features → schema → scorer → decision
gör att nya idéer (t.ex. likviditet, fib/htf-filter) kan läggas in på rätt ställe utan att skapa dubbla sanningar.
➡️ Vinsten: lättare att ersätta/modulera utan att riskera lookahead eller implicit fallback.

4. Korrelation/överlapp blir synligt (och kan hanteras)

Om flera features i praktiken säger samma sak (t.ex. fib-prox \* rsi vs fib-prox + rsi) så kan modellen ändå funka, men:

Optuna kan överanpassa

viktning/kalibrering blir instabil mellan regimer
➡️ Vinsten: ni kan medvetet välja “en representation” eller behålla båda men veta konsekvensen.

5. Färre “mystery bugs” i live

När champion laddas/mergas olika i live vs backtest kan ni få:

“varför beter den sig annorlunda live?”

“varför blir 2025 så dåligt fast 2024 är bra?”
➡️ Vinsten: ni kan spåra exakt vilka variabler/features/paths som skiljer — och eliminera skillnaden.

6. Bättre observability: ni kan logga rätt saker

När ni vet vilka 10 features som faktiskt driver modellen kan ni logga:

feature values (as-of)

proba/confidence

scorer input/output
➡️ Vinsten: snabbare felsökning och enklare “post-mortem” på dåliga trades.

Bottom line (vad ni “vinner” i pengar/resultat)

Detta är en multiplikator:

Optuna blir mer pålitligt → bättre parametrar → bättre generalisering

Mindre drift mellan backtest och live → färre obehagliga överraskningar

Mindre slöseri på onödiga features → fler trials på samma tid
