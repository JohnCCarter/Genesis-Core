# Research artifacts

Den här mappen är den framåtriktade ytan för reproducerbara experimentbundlar i Genesis-Core.
Den är **inte** governance-SSOT och den är **inte** i sig en authority-signal för runtime, readiness eller promotion.

## Syfte

Här ska researchmaterial leva som behöver vara:

- reproducerbart
- bundle-baserat
- nära sina manifest och artefakter
- tydligt separerat från beslutstexter och policy-SSOT

## Rekommenderad struktur

```text
results/research/
  <program>/
    phase_01_<name>/
      manifest.json
      artifacts.json
      summary.md
      tables/
      traces/
    phase_02_<name>/
      ...
  <program>_summary/
    ...
```

## Organisationsregler

- strukturera **program först**, **fas sedan**
- håll maskinläsbara artefakter nära den fas som skapade dem
- använd `summary.md` för kort bundlekontext, inte för att duplicera stora governance-resonemang
- använd `docs/analysis/` för längre mänskliga synteser
- använd `results/evaluation/` för små kuraterade summary-artefakter som andra dokument behöver referera till

## Viktig gräns

En research-bundle kan ge evidens eller observation, men den får inte läsas som policybeslut eller som SSOT bara för att den är välorganiserad.
Historiska mappar kan föregå denna taxonomi; README:n beskriver främst hur nya bundlar bör formas framåt.
