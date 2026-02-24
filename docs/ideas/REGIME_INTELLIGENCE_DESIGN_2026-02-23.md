# Genesis – Regime Intelligence & Adaptive Risk Curve

**Version:** v0.1 (Design Proposal)
**Datum:** 2026-02-23
**Författare:** Chamoun
**Status:** Design / Brainstorm – ej godkänd för implementation
**Scope:** Multi-dimensionell regime-klassificering + adaptiv riskkurva

---

## 1. Syfte

Uppgradera Genesis från:

> Binär regime-gate (vol percentile-baserad)

till:

> Multi-dimensionell regime-klassificering med clarity score och adaptiv riskkurva

Utan att:
- Bryta determinism
- Röra core execution invarianter
- Öka arkitektonisk fragibilitet
- Bryta freeze-constraints

---

## 2. Pre-design Audit – Vad Finns i Koden Idag

Innan implementationsbeslut genomfördes en fullständig read-only genomgång av
`src/core/strategy/`, `src/core/indicators/`, `src/core/risk/` och `src/core/backtest/`.

Nedan dokumenteras fyra kritiska fynd som påverkar design-valet.

---

### Fynd 1 – Två parallella regime-implementationer (divergens)

**Filer:**
- `src/core/strategy/regime.py` (184 rader) – ADX-baserad, 4 labels, hysteresis-logik
- `src/core/strategy/regime_unified.py` (112 rader) – EMA ±2%-baserad, 4 labels

**Problemet:**

Den ADX-baserade implementationen (`regime.py`) är mer sofistikerad:
- Använder ADX (>25 = trending, <20 = ranging)
- Har inbyggd hysteresis (`hysteresis_steps`-parameter)
- Spårar kandidat-regim och kräver N konsekutiva bekräftelser

Den EMA-baserade implementationen (`regime_unified.py`) är enklare:
- Klassificerar enbart baserat på pris vs EMA ±2%
- Saknar hysteresis
- **Är den som faktiskt används i produktion** (`evaluate.py:250`)

**Konsekvens:**
Den bättre implementationen är inte i mainline. Systemet kör på den svagare.
Detta måste adresseras innan en ny clarity score byggs ovanpå fel bas.

**Direkt åtgärd (förutsättning för Phase 1):**
Bestäm vilken implementation som är SSOT. Konvergera till en fil.
Kandidat: `regime.py` utökas med EMA-fallback + används i `evaluate.py`.

---

### Fynd 2 – "Clarity score" existerar redan, under fel namn

**Fil:** `src/core/strategy/confidence.py:69–218`

Systemet beräknar redan ett `quality_factor` med fyra komponenter:

| Komponent | Mäter | Scope |
|-----------|-------|-------|
| `data_quality` | Datakvalitet / stale ticks | gate + sizing |
| `spread` | Bid-ask spread (bp) | gate + sizing |
| `atr` | Volatilitetsnivå (ATR%) | gate + sizing |
| `volume` | Volymkvalitet | gate + sizing |

**Problemet:**
`quality_factor` mäter **datakvalitet och marknadsmikrostruktur** – inte **regimklarhet**.

En `clarity_score` i den föreslagna designen ska mäta:
- Hur tydlig trenden är (ADX-styrka, EMA-lutning)
- Hur konsistent strukturen är (candle overlap, volatilitetsstabilitet)
- Hur persistent regimet är (antal stabila bars)

Dessa är **ortogonala** mätningar. Om de slås ihop uppstår begreppsförvirring och
framtida debuggbarhet försämras.

**Direkt åtgärd:**
`clarity_score` ska vara en separat beräkning. Den ska **inte** ersätta `quality_factor`
utan komplettera det. I `decision.py` kombineras de separat i sizing-logiken.

---

### Fynd 3 – Sizing är redan multi-dimensionell, men osynlig

**Fil:** `src/core/strategy/decision.py:1097–1221`

Systemet gör redan:

```python
size = base_size
     * quality_scale          # confidence-baserad skalning
     * regime_mult            # LTF regime-multiplikator
     * htf_regime_mult        # HTF Fibonacci-position (bull/bear)
     * vol_mult               # ATR-percentil-multiplikator
```

**Problemet:**
Dessa multiplicatorer är separata, oklart kalibrerade och producerar ingen
loggbar sammanfattning. Det är i praktiken redan en kurva – men ingen vet om det,
och den är inte designad som en kurva.

Den föreslagna `risk_multiplier = f(clarity_score)` är en förenkling och formalisering
av vad som redan finns, inte en ny idé från scratch.

**Direkt åtgärd:**
Phase 1 ersätter inte hela sizing-logiken. Den lägger till `clarity_score` som
en ny explicit input och gör kurvan synlig och loggbar.

---

### Fynd 4 – Oanvänd regime-persistence funktion

**Fil:** `src/core/indicators/derived_features.py`

`calculate_regime_persistence()` är implementerad men inte integrerad i
något pipeline-steg. Funktionen mäter hur stabilt ett regime har varit
de senaste N barsen – exakt vad som behövs för clarity score.

**Direkt åtgärd:**
Integrera i `regime_clarity.py` (ny fil) som en av clarity-komponenterna.

---

## 3. Design-principer

1. Deterministisk core förblir orörd.
2. Regime är inte binär.
3. ML är valfritt overlay – aldrig en handelsbeslutare.
4. Alla regime-outputs måste vara fullt loggbara och reproducerbara.
5. Risk anpassar sig mjukt (kurva), inte via hårda hopp.
6. Fail-closed logik förblir på plats.
7. **Ny princip (från audit):** En SSOT för regime-detektion. Två parallella
   implementationer tillåts inte existera utan explicit motivering.

---

## 4. Systemarkitektur

```
Market Data (OHLCV)
   │
   ├─ HTF candles (4H / 1D)
   │      │
   │      └─ [EXISTERANDE] HTF Fibonacci context (htf_fibonacci.py)
   │
   └─ LTF candles (1H / 15m)
          │
          └─ Feature Layer (features_asof.py) ──────[EXISTERANDE]
                 │
                 ├─ EMA, ADX, ATR, RSI              [EXISTERANDE]
                 ├─ Fibonacci levels                 [EXISTERANDE]
                 └─ volatility_shift                 [EXISTERANDE, ej integrerad]

                 ↓
         regime_clarity.py                           [NY FIL]
                 │
                 ├─ Rule-based signals
                 │      ├─ trend_strength   (ADX + EMA separation)
                 │      ├─ chop_score       (candle overlap ratio)
                 │      ├─ vol_state        (ATR expansion/contraction)
                 │      └─ persistence      (calculate_regime_persistence ← integreras)
                 │
                 ├─ (Phase 2) ML clarity modifier
                 │
                 └─ Output: RegimeOutput
                        ├─ label: RegimeLabel
                        └─ clarity_score: float (0–100)

                 ↓
         Policy Mapper (utökning av befintlig sizing-sektion)
                 │
                 └─ risk_multiplier = f(clarity_score)  [NY KURVA]

                 ↓
         Existerande Decision Engine (decision.py)       [ORÖRD]
                 │
                 └─ size = base * quality_scale * clarity_mult * htf_mult * vol_mult
```

---

## 5. Regime Model

### 5.1 Regime Labels

Fast uppsättning. Ingen dynamisk expansion.

| Label | Beskrivning |
|-------|-------------|
| `TREND_UP` | Tydlig upptrend (ADX högt, pris > EMA, positiv slope) |
| `TREND_DOWN` | Tydlig nedtrend (ADX högt, pris < EMA, negativ slope) |
| `RANGE` | Sidrörelse (ADX lågt, låg volatilitet, hög candle overlap) |
| `TRANSITION` | Osäkert läge – varken tydlig trend eller range |
| `CHAOS` | Hög volatilitet + hög chop (marknad utan struktur) |

**Notering om TRANSITION:**
TRANSITION är inte en catch-all. Den kräver positiv definition:
- `20 ≤ ADX ≤ 25` OCH
- `volatility_shift` ∈ [0.8, 1.2] (varken expanderande eller kontraherande)

Om inget av ovanstående matchar → fallback till RANGE, inte TRANSITION.

**Mappning från befintliga labels:**

| Befintligt | Nytt |
|------------|------|
| `bull` | `TREND_UP` |
| `bear` | `TREND_DOWN` |
| `ranging` | `RANGE` |
| `balanced` | `TRANSITION` |

### 5.2 Clarity Score (0–100)

Representerar strukturell konfidans i aktuellt regime.
Måste vara deterministisk givet identiska inputs.

**Beräkning (pseudo-kod):**

```python
trend_strength = normalize(adx, 0, 50) * 0.5
              + normalize(abs(ema_slope), 0, 0.01) * 0.3
              + normalize(abs(price_vs_ema_pct), 0, 0.05) * 0.2

chop_score = candle_overlap_ratio(last_n_bars, n=20)

vol_alignment = vol_state_consistent_with_label(label, atr_expansion_ratio)

persistence = calculate_regime_persistence(regime_history, window=10) / 10.0

clarity_score = clamp(
    trend_strength * 40
    + (1 - chop_score) * 25
    + vol_alignment * 20
    + persistence * 15,
    0, 100
)
```

Alla komponenter normaliserade 0–100. Vikter är konfigurerbara.

---

## 6. Adaptiv Riskkurva

### 6.1 Ersätt binär gate

**Gammalt:**
```python
if regime_ok:
    trade()
else:
    veto()
```

**Nytt:**
```python
risk_multiplier = risk_curve(clarity_score)
size = base_size * risk_multiplier  # (kombinerat med övriga multiplicatorer)
```

### 6.2 Riskkurva

Mjuk interpolation (linjär mellan bands, inga hårda hopp):

| Clarity | Risk Multiplier |
|---------|----------------|
| 0–20 | 0.3× (starkt reducerat) |
| 20–40 | 0.6× |
| 40–60 | 1.0× (baseline) |
| 60–75 | 1.4× |
| 75–85 | 1.8× |
| 85–100 | 2.2× |

**Implementation:** `numpy.interp(clarity_score, breakpoints, multipliers)`
Inga if-satser. Inga hårda band.

### 6.3 Interaction med quality_factor

`quality_factor` (datakvalitet) och `clarity_score` (regimklarhet) är separata:

```python
# I decision.py sizing-sektion:
clarity_mult  = risk_curve(clarity_score)           # regime-baserad
quality_scale = compute_quality_factor(...)         # data-baserad (befintlig)

size = base_size * quality_scale * clarity_mult * htf_mult * vol_mult
```

De multipliceras – de adderas inte. Låg datakvalitet kan trumfa hög clarity.

### 6.4 Guardrails (icke-förhandlingsbara)

Portfolio-nivå constraints överstyr alltid regime:

| Drawdown | Effekt |
|----------|--------|
| DD > 8% | Halvera alla clarity_mult (× 0.5) |
| DD > 12% | Cap clarity_mult till max 1.0 (stäng av boost-tiers) |
| DD > 15% | Kill switch – force HOLD oavsett signal |

Befintlig `risk/guards.py` används. Ny logik: koppla guard-output till clarity_mult cap.

---

## 7. Loggning & Attribution

Varje beslutspunkt måste logga:

```python
{
    "regime_label": "TREND_UP",
    "clarity_score": 72.4,
    "clarity_mult": 1.4,
    "risk_multiplier_final": 1.12,  # efter DD-guardrail
    "clarity_components": {
        "trend_strength": 0.81,
        "chop_score": 0.22,
        "vol_alignment": 1.0,
        "persistence": 0.70
    },
    "quality_factor": 0.88,
    "quality_components": { ... },  # befintlig
    "final_size": 0.0045,
    "blocker": null,  # eller "DD_GUARDRAIL_12PCT"
    "regime_source": "rule_based",  # eller "ml_overlay" i Phase 2
}
```

Mål: varje "0 trades men oklart varför" ska kunna spåras till exakt komponent.

---

## 8. Determinism-krav

1. Alla regime-inputs loggas per bar.
2. Alla regime-outputs loggas per bar.
3. `clarity_score` beräknas som ren funktion (inga globala side-effects).
4. Inga stokastiska runtime-beslut.
5. Samma input → samma beslut.
6. `candle_overlap_ratio` och `calculate_regime_persistence` måste ha explicit
   fönsterstorlek i config (inte hårdkodad).

---

## 9. Implementationsfaser

### Phase 1 – Regel-baserad Regime + Riskkurva

**Scope:**
- Ny fil: `src/core/strategy/regime_clarity.py`
  - `classify_regime_with_clarity(features, config) -> RegimeOutput`
  - Integrerar `calculate_regime_persistence()` från `derived_features.py`
  - Konvergerar med `regime.py` (ADX-logik) som SSOT
- Utökning av `decision.py:1142–1178` (sizing)
  - Lägger till `clarity_mult = risk_curve(clarity_score)`
  - Loggning av alla clarity-komponenter
- Koppla DD-guardrails (`risk/guards.py`) till clarity_mult cap
- Ingen ML

**Före Phase 1 startar (obligatoriskt):**
- Besluta om `regime.py` vs `regime_unified.py` som SSOT
- Ta bort eller deprecate den som inte väljs
- Säkerställ att `evaluate.py` pekar på rätt implementation

### Phase 2 – ML Confidence Overlay (valfri)

**Constraints:**
- Modell-version fryst
- Feature-set fryst
- Seed fixerad
- Inferens måste vara ren funktion
- Loggas per beslut
- ML modifierar **enbart** `clarity_score` inom definierade bounds (±15 poäng max)
- ML beslutar aldrig direkt om trade

### Phase 3 – Regime-Aware Strategy Routing (valfri)

- Olika policy per regime
- Utvärderas efter Phase 1 är validerad

---

## 10. Icke-mål

- Ingen sänkning av timeframe för att jaga aktivitet
- Ingen scalping-arkitektur
- Ingen borttagning av fail-closed invarianter
- Inga svarta lådor
- Ingen okontrollerad hävstång
- Ingen sammanslagning av `quality_factor` och `clarity_score`

---

## 11. Förväntad beteendeförändring

**Från:**
- Låg frekvens
- Binär gating
- Konservativt-only beteende

**Till:**
- Deltagande i alla klimat med proportionell risk
- Clarity-proportionell positionsstorlek
- Högre handelsfrekvens (målsättning: 150–250 trades/år)
- Kontrollerad aggressivitet i högt-clarity-regimer

---

## 12. Pre-implementation Checklista

Innan implementation påbörjas måste följande vara klart:

- [ ] Beslut: `regime.py` eller `regime_unified.py` som SSOT
- [ ] Konvergens-commit: ena implementationen tas bort
- [ ] Backtest-baseline: nuvarande trade-frekvens och DD dokumenterad
- [ ] Definition av `candle_overlap_ratio` specificerad (fönsterstorlek, normalisering)
- [ ] Riskkurva-breakpoints validerade mot historisk clarity-distribution
- [ ] Commit-kontrakt skrivet (Codex53-format) och godkänt av Opus46

---

## 13. Öppna frågor

1. **Vad blockerar trades idag?** Decision-loggen visar `EV_BLOCK`, `PROBA_BLOCK`,
   `HTF_FIB_BLOCK` etc. Är problemet regime-gating eller probability-trösklarna?
   Svar på denna fråga avgör om Phase 1 överhuvudtaget adresserar rätt problem.

2. **Hysteresis på clarity_score?** Om clarity oscillerar runt 59–61 fluktuerar
   risk_multiplier snabbt. Ska clarity-banden ha hysteresis liknande befintlig
   hysteresis i `decision.py:1059–1083`?

3. **Candle overlap ratio – definition?** Nuvarande `fib_prox_score` och `bb_position`
   finns. Behöver ett nytt `chop_index` beräknas eller kan befintliga features
   kombineras?

4. **Clarity_score i backtesting vs live?** Feature computation har olika semantik
   (se `docs/features/FEATURE_COMPUTATION_MODES.md`). Clarity-beräkningen måste
   vara korrekt i båda paths.

---

*Nästa steg: Besvara öppna frågor, fastställ SSOT-beslut, skriv minimal implementation-spec.*
