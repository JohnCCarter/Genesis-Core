### TODO – Genesis‑Core (V1-spec, modulärt och testbart)

**Status:** ✅ Phase 1 & 2 KLART | Phase 3 (ML Training) pågår

---

## Phase 1 & 2: Core System ✅ KLART

Prioritet P1 (strategi-pipeline)

- [x] Probability: `predict_proba_for(symbol, timeframe, features)` – koppla `model_registry` (ingen extra logik)
- [x] Features: `extract_features(candles)` enligt definitionssektionen (tidsrättat, p10–p90‑klippning)
- [x] Confidence: `compute_confidence(probas, atr_pct, spread_bp, volume_score, data_quality)` – monoton skalning
- [x] Regim (HTF): `classify_regime(adx_norm, atr_pct, ema_slope)` med hysteresis (2–3 HTF‑barer)
- [x] Decision: `decide(policy, probas, confidence, state, risk_ctx, cfg)` – EV‑filter, hysteresis, cooldown, risk‑gating
- [x] Enhetstester per modul + en E2E med dummy‑vikter

Prioritet P2 (validering & observability)

- [x] Reliability‑plots (bucket 0.5–0.6/…/0.7–0.8); tolerans ±7 pp (documents/scripts only)
- [x] Driftkontroller: PSI/KS mellan train och live features (docs + placeholder helpers)
- [x] Observability: counters/gauges/events + versionsstämplar (features/prob_model/calibration/policy)

Prioritet P3 (modell & policy)

- [x] Exempelpolicy per regim: thresholds (trending 0.55, ranging 0.60, balanced 0.58), N=2 hysteresis, cooldown=120s
- [x] Kalibrering: specificera isotonic/logistic per symbol/TF och versionering (docs + filformat)
- [x] Champion‑process: dokumentera uppdateringsflöde och rollbackkriterier

Regler (ska efterlevas i kod)

- [x] No overlap: Probability/Confidence/Regim/Decision har skarpa ansvar
- [x] Fail‑safe: saknas data/NaN ⇒ Decision = NONE
- [x] Latensbudget: ≤ 20 ms/modul (LTF) - Verifierat: avg 0.6ms total
- [x] Inga hemligheter i logg; reasons som maskinläsbara koder

Noteringar

- Starta inga implementationer utan uttryckligt godkännande.
- Håll moduler rena (pure), deterministiska och väl testade.

- Framtida Autotune
