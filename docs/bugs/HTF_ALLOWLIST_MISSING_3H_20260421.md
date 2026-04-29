# HTF allowlist missing "3h" — silent HTF regime disable (2026-04-21)

## Status

**IMPLEMENTED / POST-AUDITED WITH NOTES** — 2026-04-22.
Två-seamsproblemet är verifierat och minimal fix-shape är implementerad och
validerad inom låst scope. Kvalificerande not: `python -m black --check src tests`
failade på två förhandsbefintliga filer utanför slicens scope, medan touchade filer
är black-clean och `python -m pre_commit run --all-files` passerade.

## Sammanfattning

3h-lanen blockeras i två separata seams:

1. HTF bundle-eligibility i
   [src/core/strategy/features_asof_parts/context_bundle_utils.py](../../src/core/strategy/features_asof_parts/context_bundle_utils.py#L8)
   saknar `"3h"` och hoppar därför över HTF-context-bygget helt för 3h.
2. HTF Fibonacci-contextens timeframe-allowlist i
   [src/core/indicators/htf_fibonacci_context.py](src/core/indicators/htf_fibonacci_context.py#L121-L128)
   saknar också `"3h"` och returnerar därför `HTF_NOT_APPLICABLE` även när
   runtime-ytan anropas direkt.

Resultatet: alla strategier som körs på 3h-timeframe får `htf_regime = "unknown"`
och **alla HTF-gate/sizing/veto-beslut baserade på HTF regime har varit tysta
no-ops** — inklusive champion `phased_v3` på 3h.

## Root cause

### A. Upstream bundle-gating saknar 3h

`build_fibonacci_context_bundle(...)` i
`src/core/strategy/features_asof_parts/context_bundle_utils.py` bygger idag både
HTF- och LTF-context endast för följande timeframes:

```python
_ELIGIBLE_TIMEFRAMES = {"1h", "30m", "6h", "15m"}
```

Det betyder att 3h inte ens försöker bygga HTF-context via feature-pipelinen.

### B. Runtime-allowlist saknar 3h

Hårdkodad allowlist i `_compute_htf_fibonacci_context`:

```python
# src/core/indicators/htf_fibonacci_context.py, rad 121-128
if tf_norm not in ["1h", "30m", "6h", "15m"]:
    return {
        "available": False,
        "reason": "HTF_NOT_APPLICABLE",
        "timeframe": tf_norm,
        "htf_timeframe": htf_timeframe,
    }
```

`"3h"` ingår inte i listan. Call chain som påverkas:

- `features_asof_parts/fibonacci_context_utils.py` →
- `src/core/strategy/evaluate.py` (`compute_htf_regime`, rad 427) →
- `src/core/intelligence/regime/htf.py` (returnerar `"unknown"` när
  `available != True`) →
- `src/core/strategy/components/context_builder.py` (rad 137) →
- `src/core/strategy/components/htf_gate.py` (rad 44) →
- `src/core/strategy/decision_sizing.py` (rad 434, `htf_regime_size_multipliers`
  aktiveras aldrig).

## Verifierad evidens

### 1. Statisk scan av evidens-korpus

Skript: `tmp/scan_htf_regime_20260421.py`

- Skannade 10 944 JSON/NDJSON/Parquet-filer under
  `artifacts/`, `results/`, `logs/`, `registry/`, `reports/`.
- **0 filer** innehåller `htf_regime` med annat värde än `"unknown"` eller null.

### 2. Runtime-verifiering på 3h-bars

Skript: `tmp/verify_htf_regime_runtime_20260421.py`

- Laddade 28 735 3h-bars från
  `data/curated/v1/candles/tBTCUSD_3h.parquet`.
- Samplade 51 timestamps från 2024 + 51 från 2025 (jämt fördelade).
- Anropade `get_htf_fibonacci_context(... timeframe="3h", htf_timeframe="1D")`
  direkt på runtime-ytan.
- **102 / 102** anrop returnerade:
  - `available = False`
  - `reason = "HTF_NOT_APPLICABLE"`
  - `swing_high = None`, `swing_low = None`
- `compute_htf_regime(...)` returnerade `"unknown"` i **102 / 102** fall.

### 3. Routing trace empirisk distribution

Källa: `routing_trace.ndjson` (146 rader, 2024+2025).

- `htf_regime`: **100 %** `"unknown"`.
- `transition_bucket`: **98 %** `"stable"`.
- `clarity_bucket`, `edge_bucket`, `zone`, `confidence_bucket` har balanserade
  distributioner.

### 4. Extended sample-verifiering (2018–2025)

Källa: extended routing_trace från B1 sample-expansion (715 rader,
2018–2025). Se
[docs/bugs/RI_BUCKET_SAMPLE_EXPANSION_B1_20260421.md](RI_BUCKET_SAMPLE_EXPANSION_B1_20260421.md).

- `htf_regime`: **100 %** `"unknown"` även över 8 historiska år — bekräftar
  att bugget inte är 2024/2025-specifikt utan har varit tyst under hela
  perioden 2018–2025.

## Konsekvenser

### Optimering

- Optuna-sökningar på 3h har optimerat HTF-relaterade parametrar
  (`htf_regime_size_multipliers`, HTF-gate-trösklar etc.) **mot brus**, eftersom
  deras kod-paths aldrig aktiverades.
- Champion `phased_v3` på 3h valdes utan HTF-aware beslutsfattande — den 2024
  edge som observerats är **inte** driven av HTF-signalen.

### RI (Regime Intelligence)

- RI-policyer som villkorar på `htf_regime` har inte kunnat differentiera
  beteende på 3h.
- Tidigare planerad bucket-taxonomi `regime × freshness × vol × side` ej
  användbar på 3h-evidens; pivoterar till `clarity × edge × zone` (dimensioner
  med verifierad signal).

### Backtests & paper

- Alla 3h-backtests i evidens-korpus har körts med HTF tyst avstängt. Resultaten
  är konsistenta med sig själva men **motsvarar inte** en config där HTF skulle
  vara aktiv.

## Föreslagen fix-shape

**Spår B** — föreslagen som minimal två-surface-fix:

```python
# Föreslagen minimal två-surface-fix
# 1) features_asof_parts/context_bundle_utils.py
_HTF_ELIGIBLE_TIMEFRAMES = {"15m", "30m", "1h", "3h", "6h"}

# 2) indicators/htf_fibonacci_context.py
if tf_norm not in ["15m", "30m", "1h", "3h", "6h"]:
```

- Tillägg: `"3h"` i HTF-pathen.
- Raffinering: LTF-context-semantiken hölls oförändrad för 3h i denna slice;
  upstream-bundle-gating ska delas i separat HTF- respektive LTF-eligibility i
  stället för att bredda båda samtidigt.
- Kosmetisk: sortering i stigande ordning (ingen behavior change för övriga TF).
- Övervägs parallellt: observability-förbättring (logga `HTF_NOT_APPLICABLE`
  med `tf_norm`-värde för att fånga framtida tysta träffar).

**Inte i scope för denna fix:**

- Dynamisk ratio-validering (`ltf_to_htf_ratio >= N`). Robustare men större
  surface; egen framtida cykel.
- Utvidgning till 4h/12h/andra TF som inte är i aktiv användning.

### Krav för fix-cykeln

- Commit-contract med explicit **behavior-change exception**.
- Opus pre-code review (hög-sensitivitets-zon).
- Parity-tester före/efter: för LTF ∉ `{3h}` måste befintligt beteende vara
  oförändrat.
- Ny smoke-test: 3h → `available = True` för bars där swing-bounds är giltiga.
- Re-evaluering av `phased_v3` champion på 3h med aktiv HTF (separat
  governance-beslut efter fix).

## Interrim-strategi (nu)

- **Spår A**: denna dokumentation låser fyndet i historiken.
- **Spår C**: RI-policy-arbete fortsätter på bucket-dimensioner som är
  verifierat populerade (`clarity × edge × zone`), utan att blockeras av spår B.
- Spår B lyfts som separat cykel när explicit pre-code approval finns.

## Referenser

### Kod

- [src/core/indicators/htf_fibonacci_context.py](../../src/core/indicators/htf_fibonacci_context.py#L121-L128)
  (allowlist, rot-orsak)
- [src/core/intelligence/regime/htf.py](../../src/core/intelligence/regime/htf.py)
  (returnerar `"unknown"` när `available != True`)
- [src/core/strategy/evaluate.py](../../src/core/strategy/evaluate.py#L427)
  (anrop `compute_htf_regime`)
- [src/core/strategy/decision_sizing.py](../../src/core/strategy/decision_sizing.py#L434)
  (`htf_regime_size_multipliers`)

### Evidens-skript (tmp/)

- [tmp/scan_htf_regime_20260421.py](../../tmp/scan_htf_regime_20260421.py)
- [tmp/verify_htf_regime_runtime_20260421.py](../../tmp/verify_htf_regime_runtime_20260421.py)
- [tmp/ri_bucket_empirical_extract_20260421.py](../../tmp/ri_bucket_empirical_extract_20260421.py)

### Relaterat

- [docs/bugs/HTF_INVALID_SWING_HARDENING_20251226.md](HTF_INVALID_SWING_HARDENING_20251226.md)
  — tidigare HTF-härdning (producer/consumer schema).
