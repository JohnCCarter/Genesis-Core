### TODO – Genesis‑Core (V1-spec, modulärt och testbart)

Prioritet P1 (nästa session)

- [ ] Probability: `predict_proba_for(symbol, timeframe, features)` – koppla `model_registry` (ingen extra logik)
- [ ] Features: `extract_features(candles)` enligt definitionssektionen (tidsrättat, p10–p90‑klippning)
- [ ] Confidence: `compute_confidence(probas, atr_pct, spread_bp, volume_score, data_quality)` – monoton skalning
- [ ] Regim (HTF): `classify_regime(adx_norm, atr_pct, ema_slope)` med hysteresis (2–3 HTF‑barer)
- [ ] Decision: `decide(policy, probas, confidence, state, risk_ctx, cfg)` – EV‑filter, hysteresis, cooldown, risk‑gating
- [ ] Enhetstester per modul + en E2E med dummy‑vikter

Prioritet P2 (validering & observability)

- [ ] Reliability‑plots (bucket 0.5–0.6/…/0.7–0.8); tolerans ±7 pp (documents/scripts only)
- [ ] Driftkontroller: PSI/KS mellan train och live features (docs + placeholder helpers)
- [ ] Observability: counters/gauges/events + versionsstämplar (features/prob_model/calibration/policy)

Prioritet P3 (modell & policy)

- [ ] Exempelpolicy per regim: thresholds (trending 0.55, ranging 0.60, balanced 0.58), N=2 hysteresis, cooldown=120s
- [ ] Kalibrering: specificera isotonic/logistic per symbol/TF och versionering (docs + filformat)
- [ ] Champion‑process: dokumentera uppdateringsflöde och rollbackkriterier

Regler (ska efterlevas i kod)

- [ ] No overlap: Probability/Confidence/Regim/Decision har skarpa ansvar
- [ ] Fail‑safe: saknas data/NaN ⇒ Decision = NONE
- [ ] Latensbudget: ≤ 20 ms/modul (LTF)
- [ ] Inga hemligheter i logg; reasons som maskinläsbara koder

Noteringar

- Starta inga implementationer utan uttryckligt godkännande.
- Håll moduler rena (pure), deterministiska och väl testade.
