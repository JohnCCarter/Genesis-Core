### Strategy Probability and Regime – Spec

- Moduler (pure): features, prob_model (wrapper), confidence, regime, decision
- Orkestrering: `core/strategy/evaluate.py`
- Observability: pure‑moduler returnerar `meta={versions,reasons}`; logging/counters sker i orkestrering

#### Validation & Reliability (P2)

- Reliability‑plots: bucket [0.5–0.6/…/0.9–1.0] per klass, tolerans ±7 pp
- Script: `scripts/reliability.py --input samples.jsonl --class buy`
- Drift (PSI/KS): jämför train vs live features (skala [0,1])
- Helpers: `core/strategy/validation.py` (psi, ks_statistic)

#### Features
- Tidsrättning: endast stängda barer
- Percentiler p10–p90 fryses via `config/strategy/defaults.json`

#### Probability (wrapper)
- Läser vikter/kalibrering från ModelRegistry
- Säkerställ kalibrering alltid appliceras efter `predict_proba`

#### Confidence
- Monoton skalning och clamp [0,1]

#### Regime (HTF)
- Input: `{adx_norm, atr_pct, ema_slope}` över 4h/Daily
- Hysteresis‑state returneras separat

#### Decision
- Gate‑ordning: EV → risk caps → regim‑riktning → proba‑tröskel → tie‑break → confidence → hysteresis → cooldown → sizing
- Fail‑safe: saknas data ⇒ NONE

### Strategy: Regim + Sannolikhetsmodell – Ansvarsfördelning och flöde

Syfte: Säkerställa strikt Separation of Concerns (SoC) mellan Probability, Confidence och Regim för att undvika överlappning, göra systemet transparent och lätt att testa.

---

### Översikt

- Probability: Statistikern – beräknar rå sannolikhet från historik/simulering.
- Confidence: Riskanalytikern – justerar sannolikhet utifrån nuvarande marknadsförhållanden.
- Regim: Spelplanen – klassificerar marknadsläge och styr vilka signaltyper/policys som gäller.

Beslut sker genom att kombinera dessa tre lager på ett deterministiskt sätt, följt av risk‑gating.

---

### 1) Probability – Statistikern 🧮

- Ansvar: Beräkna rå sannolikhet för buy/sell/hold baserat på historik, backtest eller Monte Carlo.
- Ska inte: Justera för volatilitet, likviditet, spread, regim, momentum eller intradagsbrus.
- Input (ex): Normaliserade features (ema_spread, rsi_norm, atr_pct, adx_norm) och modellmeta (vikter, bias, ev. kalibrering).
- Output: Probas dict {buy, sell, hold} där summan = 1.0.
- Exempel‑text: “Denna setup har 62% sannolikhet att lyckas baserat på data.”

I/O‑kontrakt (ex):

- In: features: dict[str, float]
- Ut: probas: dict[str, float] (sum=1)

---

### 2) Confidence – Riskanalytikern 📊

- Ansvar: Mappa probas till en praktiskt användbar confidence här och nu.
- Faktorer: ATR% (volatilitet), spread/slippage (bp), candle‑styrka, volym, datakvalitet (t.ex. saknade ticks).
- Ska inte: Klassificera regim (trend/range) eller besluta om en setup‑typ är tillåten.
- Input (ex): probas, atr_pct, spread_bp, volume_score, data_quality.
- Output: confidence ∈ [0, 1].
- Exempel‑text: “Givet nuvarande marknad är confidence 58%.”

I/O‑kontrakt (ex):

- In: probas, atr_pct, spread_bp, volume_score, data_quality
- Ut: confidence: float

Sizing‑princip (förslag):

- Kelly‑inspirerad skala med cap (t.ex. 0.5) och blandning: size_weight = (1−w)*kelly_norm + w*confidence.

---

### 3) Regim – Spelplanen 🌍

- Ansvar: Klassificera marknadsläget (trending, ranging, balanced; vol: high/normal) och definiera policy för vilka signaltyper som är tillåtna samt vilka trösklar som gäller.
- Ska inte: Beräkna sannolikheter eller justera för ATR/spread på mikronivå.
- Input (ex): adx_norm, atr_pct, ema_slope, enkel FSM‑state (accumulate/ride/distribute) om aktiverat.
- Output: regime (trend/range/balanced) + volatility (high/normal) + policy (tillåtna signaltyper, trösklar, ev. hysteresis/cooldown).
- Exempel‑text: “Regim = Trend → trend‑signaler tillåts; range‑signaler blockeras.”

I/O‑kontrakt (ex):

- In: adx_norm, atr_pct, ema_slope, state
- Ut: regime: {trending|ranging|balanced}, volatility: {high|normal}, policy: dict

Baslinjeregler (förslag):

- trending: ADX ≥ 25
- ranging: ADX < 20
- balanced: 20 ≤ ADX < 25
- high_vol: atr_pct ≥ 0.02 (2%)

---

### Beslutsflöde (logikskiss)

1. probas = Probability(features)
2. regime, policy = Regim(indicators/state)
3. Tie‑break: om |p_long − p_short| < 0.02 ⇒ NONE
4. Kalibrering: applicera isotonic/logistic per symbol/TF
5. Regim‑tröskel på kalibrerad p: p_regime_gate = max(p_long, p_short) (efter kalibrering)
6. confidence = Confidence(probas_kalibrerad, market_state)
7. Confidence‑gate: conf_overall ≥ entry_conf_overall
8. Hysteresis: kräver över tröskel två beslut i rad (entry‑TF)
9. Cooldown: blockera nya entries i N bars efter exekvering (entry‑TF)
10. decision = Decision(policy, probas_kalibrerad, confidence, risk_gates) → {buy|sell|hold}, size
11. risk‑gating: om `breached_daily_loss` eller `breached_max_drawdown` → force `hold`

Trösklar per regim (ex):

- trending: buy/sell ≥ 0.55
- ranging: buy/sell ≥ 0.60 (striktare mot whipsaw)
- balanced: buy/sell ≥ 0.58
- Hysteresis: kräver över tröskel två beslut i rad. Cooldown: 60–180s efter exekvering.

---

### Konfiguration (nycklar, exempel – inga hemligheter i repo)

- thresholds: {trending: 0.55, ranging: 0.60, balanced: 0.58}
- hysteresis_steps: 2
- cooldown_seconds: 120
- kelly_cap: 0.5
- confidence_weight: 0.5
- regime_rules: {adx_trend_min: 25, adx_range_max: 20, atr_vol_pct: 0.02}
- model_registry: champion/challenger per `symbol:timeframe` (ev. även per regim i nästa steg)

---

### Observability

- Counters: `model_eval_count`, `decision_buy/sell/hold`, `decision_overridden_by_risk`
- Gauges: `confidence`, `atr_pct`, `spread_bp`, `adx_norm`
- Events: snapshot av {features, top_proba, regime, decision} med redaktion av känsliga fält

---

### Policy per regim (P3)

- Thresholds (ex):
  - trending: 0.55
  - range: 0.60
  - balanced: 0.58
- Hysteresis: N = 2 beslut i rad över tröskel innan skifte
- Cooldown: 120 sekunder (notera: implementeringen använder bars; mappa sekunder → bars via TF vid orkestrering)
- Repo‑defaults är konservativa (prod‑lika). Använd lokala overrides för dev/snabbtest.

Nycklar i `config/strategy/defaults.json`:
- `thresholds.regime_proba`
- `gates.hysteresis_steps`
- `gates.cooldown_bars` (optionellt även `gates.cooldown_seconds` för dokumentationssyfte)

---

### Kalibrering (P3)

- Stöd för logistisk kalibrering via `buy.calib={a,b}` och `sell.calib={a,b}` i modellfilen (redan i bruk)
- Isotonic/logistic per symbol/TF kan versioneras separat (rekommenderat format):

Exempel (logistic, i modellmeta):
```json
{
  "schema": ["ema_delta_pct","rsi"],
  "buy":  { "w": [1.0, 0.2],  "b": 0.0, "calib": { "a": 1.0, "b": 0.0 } },
  "sell": { "w": [-1.0, 0.1], "b": 0.0, "calib": { "a": 1.0, "b": 0.0 } },
  "calibration_version": "v1"
}
```

Exempel (isotonic, separat fil):
```json
// calibration/tBTCUSD_1m.buy.isotonic.json
{ "version": "v1", "knots": [[0.50,0.49],[0.60,0.58],[0.70,0.69],[0.80,0.79],[0.90,0.88]] }
```

Policy:
- Logistic: använd `a,b` i modellen (snabbt, enkelt)
- Isotonic: referera via fil + version i meta; wrappern kan applicera vid behov

---

### Champion‑process (P3)

- Källor: `config/models/registry.json` (champion/challenger per `symbol:timeframe`)
- Flöde:
  1. Utvärdera kandidater (log loss primärt, Brier sekundärt) + robusthetskrav (reliability/PSI/KS)
  2. Välj champion per `symbol:timeframe` (ev. även per regim framöver)
  3. Skriv registry och versions‑tagga kalibrering/vikter
  4. Rollback‑kriterier: degradationslarm (log loss ↑, PSI/KS ↑) över tröskel → återställ föregående champion
- Dokumentation: spara beslut, datum, orsak och versionsinfo

### Definitioner (exakta)

- atr_pct = ATR / Close
  - ATR beräknas enligt Wilder (period P); Close = senaste stängningspris
  - Range: [0, +∞); ofta tolkat i procentenheter (multiplicera med 100 vid behov)
- adx_norm = ADX / 100
  - ADX i [0, 100]; normaliseras till [0, 1] för features och regler
- ema_spread = (EMA_fast − EMA_slow) / Close
  - Normaliserad spread (dimensionslös); positiv när momentum uppåt
- ema_slope = (EMA_slow(t) − EMA_slow(t−1)) / Close
  - En enkel lutningsapproximation, normaliserad med Close
- rsi_norm = RSI / 100
  - RSI i [0, 100]; normaliseras till [0, 1]
- spread_bp = (Ask − Bid) / MidPrice × 10_000 (basis points; 1 bp = 0.01%)
- candle_body_ratio = |Close − Open| / max(High − Low, ε); om High == Low ⇒ 0
- vol_jump_z: z‑score på daglig förändring i atr_pct (winsorized), fönster = 60 (konfigurerbart)
- data_quality: “stale” om age > 3×TF; sänk confidence vid stale eller volym=0 på senaste bar

---

### Feature‑skalning (policy)

- Klippning: clamp varje feature till säkra band för robusthet
  - atr_pct ∈ [0, 0.2] (20%)
  - adx_norm ∈ [0, 1]
  - ema_spread ∈ [−0.1, 0.1]
  - ema_slope ∈ [−0.05, 0.05]
  - rsi_norm ∈ [0, 1]
- Saknade värden: ersätt med 0.0 (eller senaste giltiga) – dokumentera valet
- Ordning: följ `schema` i modellens meta exakt (t.ex. ["ema_spread", "rsi_norm", "atr_pct", "adx_norm"]).

---

### Valideringsprotokoll (v1)

- Delning: rullande fönster per symbol/tidram (t.ex. 6M backtest → 4M train, 2M val)
- Stratifiering: utvärdera per regim (trending/ranging/balanced; high/normal vol)
- Metrik: log loss (primär), Brier score, accuracy, buy/sell precision/recall, churn
- Drift: spåra metrik över tid (glidande fönster) och larma vid försämring > X%
- Pass/fail‑kriterier: log loss ≤ baseline×(1+δ) och stabilitet inom toleranser; annars underkänt
- Reproducerbarhet: frys seeds, versions‑tagga data/parametrar

---

### Champion‑regler (model selection)

- Kandidater: minst två (t.ex. baseline A och softmax B) på samma feature‑set
- Urval: lägsta log loss som klarar robusthetskrav → champion per symbol:timeframe (ev. per regim senare)
- Registry: skriv `config/models/registry.json` med champion‑vägen
- Override: manuell override tillåten (dokumentera orsak och tidsstämpel)
- Rollback: om prod‑drift försämras över tröskel → återställ föregående champion
- Kadens: omvärdera schemalagt (t.ex. veckovis), inte kontinuerligt

---

### Ej‑överlappningsregler (sammanfattning)

- Probability rör inte volatilitet/spread/regim; Confidence/Regim rör inte sannolikhetsinlärning.
- Regim bestämmer policy/trösklar och tillåtna signaltyper – inte sannolikheten i sig.
- Confidence mappas till sizing och kortsiktig acceptans, inte modellval.

---

### Nästa steg (på godkännande)

- Implementera minimal Regim‑detektor (ADX/ATR%) och `decide()` med trösklar + hysteresis + cooldown.
- Koppla `model_registry` till probas via `predict_proba_for(symbol, timeframe, features)`.

---

### Baslinjeparametrar (konfigurerbara)

- thresholds:
  - regime_proba: { trending: 0.55, range: 0.60, balanced: 0.58 }
  - fallback_regime_proba_delta: +0.02 (HTF‑fallback; reason=FALLBACK_HTF)
  - entry_conf_overall: 0.70 (confidence‑gate efter kalibrerad p‑gate)
- EV:
  - R_default: 1.8
- gates:
  - hysteresis_steps: 2 (entry‑TF)
  - cooldown_bars: 5 (entry‑TF)
- TF‑vikter för sammanslagning av confidence:
  - tf_weights: { "15m": 0.8, "1h": 1.2, "4h": 1.5 } (normaliseras till sum=1)
- Event‑regler (volatilitet):
  - paus vid atr_pct ≥ p97 (Daily), återuppta vid < p95
- Quality‑parametrar:
  - stale_threshold_factor: 3.0 (× TF)
  - vol_jump_window: 60
  - clip_percentiles: [10, 90]
- Risk‑mapping:
  - risk_map: [[0.60,0.005],[0.70,0.008],[0.80,0.010],[0.90,0.012]]
  - risk_cap_pct: 0.012
  - symbol_portfolio_cap_pct: 0.025
- Reasons (koder, ej fria texter):
  - R_EVENT_BLOCK, R_TREND_ONLY_LONG, R_TREND_ONLY_SHORT, P_TIE_BREAK, Q_SPREAD_BAD,
    Q_VOL_SPIKE, HYST_WAIT, COOLDOWN_ACTIVE, EV_NEG, FAIL_SAFE_NULL, FALLBACK_HTF
