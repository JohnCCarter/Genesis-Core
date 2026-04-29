# RI bucket sample-expansion — B1 findings (2018–2025)

Date: 2026-04-21
Mode: RESEARCH
Branch: feature/ri-role-map-implementation-2026-03-24
Status: föreslagen exploratory research-evidens — non-authoritative.

## Purpose

Sammanfatta de empiriska fynden från B1 sample-expansion (utökning av
routing_trace från 146 → 715 matched positions över 2018–2025) för
RI-bucket-policyarbete.

## Scope

- Exploratory research under RESEARCH mode.
- Återanvänder fryst evidence-bundle read-only (bundle-hash oförändrad).
- Ingen runtime-kodändring. Inga labels, scores eller
  decision-authority-ändringar.

## Pipeline

1. `tmp/ri_bucket_extended_capture_2018_2025_20260421.py`
   — genererar `entry_rows.ndjson` per år via `GenesisPipeline` med
   evaluation-hook och evidence-bundle-config.
2. `tmp/scpe_ri_v1_router_replay_extended_20260421.py`
   — replayar router över extended entry_rows → `routing_trace.ndjson`.
3. `tmp/ri_bucket_signal_zone_extended_20260421.py`
   — kollapsar `clarity × edge → signal_strength`, producerar
   bucket-fördelning och per-år-stabilitet.

## Governance-invariants (verifierade)

| Invariant                          | Utfall                          |
| ---------------------------------- | ------------------------------- |
| Evidence-bundle hash före == efter | PASS (oförändrad i båda runsen) |
| Containment (approved output only) | PASS                            |
| Runtime-kod oförändrad             | PASS (ingen `src/**`-ändring)   |
| Shadow regime mismatches           | 0 / 715 rader                   |
| Transition guard rows (<1.0 mult)  | 0 / 715 rader                   |

## Dataexpansion

| Baseline (2024–2025) | Extended (2018–2025) | Faktor |
| -------------------- | -------------------- | ------ |
| 146 matched          | **715 matched**      | 4.9×   |

Per år: 2018 (124), 2019 (93), 2020 (78), 2021 (121), 2022 (106), 2023 (47),
2024 (72), 2025 (74).

## Bucket-fördelning (signal × zone)

Samma 3-nivå kollaps av `clarity × edge → signal_strength` som
146-baselinen. 11 av 27 möjliga buckets populerade — clarity och edge förblir
starkt korrelerade även över 8 år.

| signal     | zone | n   | long% |
| ---------- | ---- | --- | ----- |
| strong     | mid  | 136 | 86.8% |
| mid        | mid  | 122 | 77.9% |
| strong     | low  | 95  | 87.4% |
| mid        | low  | 88  | 72.7% |
| weak       | low  | 76  | 1.3%  |
| weak       | mid  | 75  | 6.7%  |
| strong     | high | 72  | 86.1% |
| mid_strong | mid  | 24  | 87.5% |
| mid_strong | low  | 12  | 100%  |
| mid_weak   | mid  | 9   | 77.8% |
| mid_weak   | low  | 6   | 50.0% |

## Per-år-stabilitet (Δmax LONG% över 8 år)

| signal     | zone | n   | Δmax   | Tolkning                |
| ---------- | ---- | --- | ------ | ----------------------- |
| weak       | low  | 76  | 10 pp  | **stabil NO-LONG**      |
| strong     | mid  | 136 | 24 pp  | stabil LONG             |
| mid        | low  | 88  | 33 pp  | måttligt stabil LONG    |
| strong     | low  | 95  | 35 pp  | LONG-dominant men noisy |
| mid        | mid  | 122 | 37 pp  | LONG-dominant, noisy    |
| weak       | mid  | 75  | 50 pp  | NO-LONG med outlier år  |
| strong     | high | 72  | 50 pp  | **instabil**            |
| mid_strong | mid  | 24  | 100 pp | för tunt samplad        |
| mid_weak   | mid  | 9   | 100 pp | för tunt samplad        |
| mid_weak   | low  | 6   | 100 pp | för tunt samplad        |
| mid_strong | low  | 12  | 0 pp   | för tunt samplad        |

## Viktigaste insikter

1. **`weak/low` är den mest stabila bucketen** (n=76, Δmax 10 pp, LONG% 1.3 %)
   — stark kandidat för hög-förtroende NO-LONG-filter.
2. **`strong/high` bekräftas instabil** över 8 år (Δmax 50 pp, 75–100 %
   2018–2019 men 50 % 2025). Tidigare 2-års-baseline (Δ36pp) underskattade
   variationen.
3. **`strong/mid` är den stabilaste LONG-bucketen** (Δmax 24 pp).
4. **Tunt samplade buckets** (`mid_strong`, `mid_weak`) förblir under n=25
   även med 4.9× expansion — indikerar att `clarity × edge`-korrelationen
   är strukturell, inte sample-driven.

## Kända begränsningar

- **HTF-regim är `"unknown"`** i alla 715 rader pga
  [HTF_ALLOWLIST_MISSING_3H_20260421](../bugs/HTF_ALLOWLIST_MISSING_3H_20260421.md).
  Extended-sampelet bekräftar att bugget har varit tyst under hela
  2018–2025. Zone-dimensionen (`low/mid/high`) fungerar dock och ger
  diskriminerande signal.
- **Retroaktiv champion-tillämpning**: `phased_v3` tränades på senare data;
  att applicera den på 2018–2023 är inte in-sample performance och utfallet
  ska inte tolkas som historisk live-edge.
- **Exploratory only**: inga labels, scores eller beslutsauktoritets-ändringar
  har införts. Promotion till runtime kräver separat governance-cykel.

## Artefakter

### Skript (tmp/)

- [tmp/ri_bucket_extended_capture_2018_2025_20260421.py](../../tmp/ri_bucket_extended_capture_2018_2025_20260421.py)
- [tmp/scpe_ri_v1_router_replay_extended_20260421.py](../../tmp/scpe_ri_v1_router_replay_extended_20260421.py)
- [tmp/ri_bucket_signal_zone_extended_20260421.py](../../tmp/ri_bucket_signal_zone_extended_20260421.py)

### Evidens-output (results/research/)

- `results/research/ri_advisory_environment_fit/bucket_extended_capture_2018_2025_20260421/pilot_2023/` (4 filer)
- `results/research/ri_advisory_environment_fit/bucket_extended_capture_2018_2025_20260421/full/` (4 filer)
- `results/research/scpe_v1_ri_extended_20260421/full/` (8 filer)
- [tmp/ri_bucket_signal_zone_extended_20260421.json](../../tmp/ri_bucket_signal_zone_extended_20260421.json)

### Relaterade docs

- [docs/bugs/RI_BUCKET_SAMPLE_EXPANSION_B1_20260421.md](../bugs/RI_BUCKET_SAMPLE_EXPANSION_B1_20260421.md)
  — scope-doc.
- [docs/bugs/HTF_ALLOWLIST_MISSING_3H_20260421.md](../bugs/HTF_ALLOWLIST_MISSING_3H_20260421.md)
  — HTF-buggen som gör att `htf_regime` saknas i alla rader.
- `docs/analysis/scpe_ri_v1_router_replay_plan_2026-04-20.md` — router-replay-plan.

## Next admissible step

- Spår B (HTF-fix) — separat commit-contract med Opus pre-code review.
- RI-bucket-policy-design kan fortsätta på signal×zone-dimensionerna som nu
  har ~4.9× mer sample-underlag; `weak/low` och `strong/mid` är de mest
  robusta kandidat-bucketen att börja från.
