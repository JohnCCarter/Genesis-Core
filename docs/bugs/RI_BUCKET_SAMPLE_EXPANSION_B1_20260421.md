# RI Bucket Sample Expansion — B1 Extended Phase C capture (2018–2025)

Date: 2026-04-21
Mode: RESEARCH
Branch: feature/ri-role-map-implementation-2026-03-24
Status: föreslagen research-evidens (exploratory, non-authoritative)

## Purpose

Utöka routing_trace-samplet från 146 matched positions (2024–2025) till ett
historiskt bredare underlag för signal×zone bucket-stabilitetsanalys. Underlaget
ska räcka för robust policy-design utan att kompromissa fryst evidence-bundle.

## Scope IN

- `tmp/ri_bucket_extended_capture_2018_2025_20260421.py` — kopia av
  `tmp/ri_advisory_environment_fit_capture_v2_20260417.py` med
  utökad `YEAR_WINDOWS` och ny `DEFAULT_OUTPUT_DIR`.
- `tmp/scpe_ri_v1_router_replay_extended_20260421.py` — kopia av
  `tmp/scpe_ri_v1_router_replay_20260420.py` med ny input/output-path.
- Ny output-katalog:
  `results/research/ri_advisory_environment_fit/bucket_extended_capture_2018_2025_20260421/`.

## Scope OUT

- Ingen runtime-kodändring (ingen förändring av `src/core/**`).
- Ingen ändring av fryst evidence-bundle
  (`artifacts/bundles/ri_advisory_environment_fit/phase3_phasec_evidence_freeze_2026-04-17/**`).
- Ingen ändring av fryst output-katalog
  `phase3_phasec_evidence_capture_v2_2026-04-17/**`.
- Ingen HTF-allowlist-fix (deferred till Spår B under separat Opus-review).

## Constraints

- NO RUNTIME BEHAVIOR CHANGE.
- Återanvänder fryst evidence-bundle read-only (hash före/efter ska vara
  identisk).
- HTF-context förblir `HTF_NOT_APPLICABLE` i alla 3h-rader (känt och
  dokumenterat i `docs/bugs/HTF_ALLOWLIST_MISSING_3H_20260421.md`).
- Resultatet är exploratory research-evidens, inte runtime-validity, och får
  inte användas som promotion-evidens utan separat governance-cykel.

## Procedure

1. Pilot 2023: kör extended capture enbart för år 2023 för att verifiera att
   pipeline fungerar på icke-2024/2025-data och skatta körtid.
2. Om pilot passerar: kör 2018–2025 (8 år) i en fortsättning och producera
   `entry_rows.ndjson` samt `capture_summary.json`.
3. Replay router på extended entry_rows → `routing_trace.ndjson`.
4. Kör `tmp/ri_bucket_signal_zone_20260421.py` på extended trace och jämför
   bucket-distribution och LONG%-stabilitet mot 2024/2025-baseline.

## Evidence

- Freeze-bundle hash verifieras före/efter varje körning i
  `capture_summary.json`.
- Ny output-katalog hålls scope-lockad via `_ensure_output_scope`.

## Known limitations

- HTF-context saknas för hela 3h-historiken tills Spår B adressas — detta
  begränsar zone-dimensionens informationsvärde men påverkar inte
  signal-dimensionen (clarity×edge).
- Evidensbundlens champion-modell har tränats på data före 2024–2025; att
  applicera den på 2018–2023 är en **retroaktiv tillämpning** och ska inte
  tolkas som in-sample performance.
