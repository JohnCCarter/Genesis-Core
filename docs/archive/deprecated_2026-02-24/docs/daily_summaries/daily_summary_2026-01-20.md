# Daily Summary - 2026-01-20

## Summary of Work

Dagens fokus var att **förhindra att långa Optuna-körningar råkar gå fel** (fel DB/study, tyst config-/kod-drift vid resume).
I stället för att starta en ny långkörning lades tyngdpunkten på _operational safety_ och uppdaterade runbooks.

## Key Changes

- **Optuna resume-säkerhet: study signature (`genesis_resume_signature`)**
  - Runnern sätter en Optuna `user_attr` som fingerprintar config + kod/runtime + viktiga mode-flaggor.
  - Vid mismatch failar resume fast med: "Optuna resume blocked: study signature mismatch".
  - Stop-policy-fälten `end_at` och `timeout_seconds` ingår inte i signaturen (så det går att förlänga en körning utan att bryta resume-säkerhet).
  - Overrides för kontrollerade undantag:
    - `GENESIS_BACKFILL_STUDY_SIGNATURE=1` (backfilla legacy-studier utan signature)
    - `GENESIS_ALLOW_STUDY_RESUME_MISMATCH=1` (tillåt mismatch; ej för canonical beslut)

- **Docs/runbook uppdaterade för long-run guardrails**
  - `docs/optuna/README.md` (inkl. `GENESIS_FAST_HASH=0` i canonical exempel + resume-sektion)
  - `docs/optuna/OPTUNA_BEST_PRACTICES.md` (ny sektion om resume safety)
  - `docs/optimization/optimizer.md` (felsökningsrad för signature-mismatch)

- **Long-run konfig för Explore→Validate (ej körd här)**
  - `config/optimizer/tBTCUSD_1h_optuna_ev_longrun_20260120_20260124.yaml`
  - Promotion är avstängt och `storage`/`study_name` är unika för att minska risk för återanvändning.

## Verification

- Dokumentationsändringar granskade för korrekt env-var-stavning och konsistens med runnern.

## Next Steps

- När en långkörning ska startas: kör alltid preflight + validator först och verifiera att canonical-flaggor är satta (inkl. `GENESIS_FAST_HASH=0`).
- Om en befintlig Optuna DB ska återupptas: säkerställ att `genesis_resume_signature` matchar, annars byt `study_name`/`storage` eller backfilla explicit (endast när du är säker).
