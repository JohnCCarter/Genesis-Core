# RI vs legacy — 1h fib-gate binding diagnostic

Datum: 2026-03-30
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: research-diagnostik / measurement only / ingen runtime-ändring

## Syfte

Detta är den minimala uppföljningen efter att den bounded 1h fib-gate-slicen gav plateau.

Frågan här var inte längre tuning, utan bindning:

> Är HTF/LTF fib-gates faktiskt aktiva som beslutspåverkande gates, eller är de strukturellt inaktiva i den nuvarande beslutsytan?

Ingen kod i `src/core/**` ändrades. Ingen sökrymd expanderades. Ingen optimization kördes.

## Diagnostiskt underlag

- Script: `tmp/ri_fib_gate_binding_diagnostic.py`
- JSON-artifact: `artifacts/diagnostics/ri_fib_gate_binding_1h_20260330.json`
- Fixed input surface: candidate-posturen från `config/optimizer/1h/phased_v1/tBTCUSD_1h_phased_v1_fib_gate_matrix.yaml`
- Baseline parity source: `results/hparam_search/ri_role_map_slice3_fib_gate_1h_20260330/tBTCUSD_1h_trial_004.json`
- Window: `2024-01-01 .. 2024-12-31`

Diagnostiken mätte per bar som nådde fib-lagret:

- HTF status: `PASS / BLOCK / UNAVAILABLE`
- LTF status: `PASS / BLOCK / UNAVAILABLE`
- om fib ändrade kandidaten mellan pre-gating och post-gating

## Distribution

Totalt processade bars: `8759`

Bars som faktiskt nådde fib-lagret: `6691` (`76.8286%` av alla bars)

### HTF fib status

- `PASS`: `3750` (`56.0454%` av fib-layer bars)
- `BLOCK`: `0` (`0.0000%`)
- `UNAVAILABLE`: `2941` (`43.9546%`)

### LTF fib status

- `PASS`: `6691` (`100.0000%` av fib-layer bars)
- `BLOCK`: `0` (`0.0000%`)
- `UNAVAILABLE`: `0` (`0.0000%`)

## Beslutspåverkan

- Fib-changed decisions: `0`
- Andel av fib-layer bars med beslutsdelta: `0.0000%`
- Andel av alla bars med beslutsdelta: `0.0000%`

Det observerades alltså **ingen enda bar** där fib-gating ändrade kandidaten mellan före och efter gating.

## Parity-kontroll för instrumenteringen

Instrumenteringen verifierades mot tidigare fixed candidate-artifact:

- baseline trade hash: `b6baa95baaa258f3`
- instrumented trade hash: `b6baa95baaa258f3`
- `trade_path_equal = true`

Metrikerna matchade också exakt, vilket betyder att diagnostikpatchen fungerade som observatör och inte ändrade utfallet.

## Slutsats

Klassning:

> **inactive**

Tolkning:

- fib-lagret **nås ofta** på 1h (`6691` bars)
- HTF är ibland otillgänglig (`UNAVAILABLE`) och ibland utvärderad som `PASS`
- LTF är konsekvent `PASS`
- varken HTF eller LTF producerade något observerat `BLOCK`
- fib-gating gav **0** beslutspåverkande deltan

Den rimliga research-domen blir därför:

> I den nuvarande 1h decision-surface är fib-gating **strukturellt inaktiv som beslutsgate**. Den är observerbar i state/debug, men den binder inte och ändrar inte beslut.
