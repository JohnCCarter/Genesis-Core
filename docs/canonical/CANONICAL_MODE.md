# Canonical Mode - SSOT för reproducerbara backtests och optimeringar

**Status**: Active (2026-01-23)
**Owner**: P0 Determinism Lockdown
**Related**: P0.1, P0.2, P0.3

## Översikt

**Canonical Mode** är Genesis-Core's deterministiska exekveringsmiljö för alla kvalitetsbeslut:

- Optuna-optimeringar
- Champion-validering
- Walk-forward-analys
- Produktionsbeslut

**Varför**: Garanterar att samma konfiguration ger exakt samma resultat varje gång, vilket är kritiskt för reproducerbarhet och fair jämförelser.

---

## Canonical Contract

### ✅ Tillåtna Environment Variables

```powershell
# Canonical mode MÅSTE använda dessa
$Env:GENESIS_FAST_WINDOW = '1'            # Batch-läge (ej streaming)
$Env:GENESIS_PRECOMPUTE_FEATURES = '1'    # Preberäknade features
$Env:GENESIS_RANDOM_SEED = '42'           # Deterministisk seed (runner sätter default)
```

**Motivering**:

- `FAST_WINDOW=1` + `PRECOMPUTE_FEATURES=1` = 100% deterministisk code path
- Streaming mode har timing-beroenden som kan ge olika resultat
- Seed 42 är standard men kan ändras för sensitivity-analys

### ⛔ Förbjudna Environment Variables (i canonical mode)

```powershell
# DEBUG/PERF-ONLY - ej tillåtet i canonical mode
$Env:GENESIS_FAST_HASH = '1'              # ❌ Kan ändra utfall (perf knob)
$Env:GENESIS_MODE_EXPLICIT = '0,0'        # ❌ Manuell override (debug only)
```

**Motivering**:

- `GENESIS_FAST_HASH=1` är bevisat att ge annorlunda resultat (2026-01-15)
- `MODE_EXPLICIT` bryter pipeline's automatiska mode-val och riskerar mixed-mode

### 🔴 Fail-Fast Conditions

Canonical mode **FAILAR omedelbart** vid:

1. **Mixed mode detection**:

   ```
   ValueError: GENESIS_FAST_WINDOW=1 requires GENESIS_PRECOMPUTE_FEATURES=1
   ```

2. **Fast hash in canonical mode**:

   ```
   RuntimeError: Canonical mode requires GENESIS_FAST_HASH=0 (currently: 1)
   ```

3. **Preflight timeout miss** (Optuna):

   ```
   ValueError: Optuna timeout check failed (smoke test timed out)
   ```

4. **Champion parameter mismatch** (validation):
   ```
   ValueError: Champion parameter X not in search space or fixed to wrong value
   ```

---

## Canonical Optuna-körning

### Preflight (OBLIGATORISKT)

```powershell
# Steg 1: Verifiera config
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml

# Steg 2: Preflight-check (MÅSTE returnera 0)
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml

# Steg 3: Sätt canonical env
$Env:GENESIS_FAST_WINDOW = '1'
$Env:GENESIS_PRECOMPUTE_FEATURES = '1'
$Env:GENESIS_RANDOM_SEED = '42'
$Env:GENESIS_FAST_HASH = '0'  # Explicit av

# Steg 4: Starta körning
python -c "from core.optimizer.runner import run_optimizer; from pathlib import Path; run_optimizer(Path('config/optimizer/<config>.yaml'))"
```

### Checklista före start

- [ ] `validate_optimizer_config.py` returnerade 0
- [ ] `preflight_optuna_check.py` returnerade 0
- [ ] Champion-parametrar verifierade i sökrymd
- [ ] Gamla `_cache/` arkiverade
- [ ] DB-fil flyttad (om `resume=false`)
- [ ] Canonical env-vars satta
- [ ] `GENESIS_FAST_HASH=0` bekräftad

### Verifiera canonical mode

```powershell
# Dubbelkörning för att verifiera determinism
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start-date 2024-06-01 --end-date 2024-08-01
# Spara resultatet

python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start-date 2024-06-01 --end-date 2024-08-01
# Jämför med första körningen - ska vara identiska
```

**Förväntad output**: Exakt samma antal trades, PF, return, score (15+ decimaler).

---

## Non-Canonical Mode (Explicit Debug)

### När det är OK

Non-canonical mode är **endast tillåtet** för:

- ✅ **Performance profiling**: `GENESIS_FAST_HASH=1` för att mäta speedup
- ✅ **Debug/development**: `MODE_EXPLICIT=0,0` för att testa streaming-logik
- ✅ **Feature experiments**: Nya features som inte finns i precompute ännu

### Hur man markerar non-canonical

```python
# I backtest_info
backtest_info["canonical_mode"] = False
backtest_info["non_canonical_reason"] = "Performance profiling with FAST_HASH=1"
```

### Preflight strict mode (optional)

```powershell
# Fail-fast om FAST_HASH=1 i canonical mode
$Env:GENESIS_PREFLIGHT_FAST_HASH_STRICT = '1'
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
```

**Output om FAST_HASH=1**:

```
[ERROR] GENESIS_FAST_HASH=1 in canonical mode (set GENESIS_PREFLIGHT_FAST_HASH_STRICT=0 to warn only)
Exit code: 1
```

---

## Troubleshooting

### "Olika resultat trots samma config"

**Symptom**: Samma parametrar ger olika trade counts/scores mellan körningar.

**Debug-steg**:

1. Verifiera canonical env-vars:

   ```powershell
   echo $Env:GENESIS_FAST_WINDOW        # Ska vara '1'
   echo $Env:GENESIS_PRECOMPUTE_FEATURES # Ska vara '1'
   echo $Env:GENESIS_FAST_HASH          # Ska vara '0' eller tom
   ```

2. Kontrollera `backtest_info.effective_config_fingerprint`:

   ```python
   import json
   r1 = json.load(open("run1.json"))
   r2 = json.load(open("run2.json"))
   assert r1["backtest_info"]["effective_config_fingerprint"] == r2["backtest_info"]["effective_config_fingerprint"]
   ```

3. Kör feature parity test:
   ```powershell
   python -m pytest tests/test_feature_parity_fast_window.py -v
   ```

### "Optuna-trials har identiska scores"

**Symptom**: Många trials får exakt samma score trots olika parametrar.

**Troliga orsaker**:

1. **Champion auto-merge**: Runtime-config overridar trial-parametrar
   - Lösning: Sätt `meta.skip_champion_merge=true` i Optuna-config

2. **Sökrymd för smal**: Parameter inte aktivt styrande
   - Lösning: Kör `scripts/analyze_optuna_db.py` och bredda intervall

3. **Gate-dominans**: En gate blockerar alla trades innan parametern aktiveras
   - Lösning: Kör `scripts/analyze_gate_dominance.py` på sample

### "Preflight timeout-check failar"

**Symptom**: `preflight_optuna_check.py` rapporterar timeout-risk.

**Lösning**:

```yaml
# I optimizer config
optuna:
  timeout_seconds: null # Sätt till null om max_trials används
  max_trials: 100 # ELLER sätt trials till null om timeout används
```

**OBS**: Optuna stoppar vid **första** gränsen som nås.

---

## Best Practices

### 1. Alltid canonical mode för quality decisions

```python
# ✅ RÄTT - canonical mode för Optuna/validering
$Env:GENESIS_FAST_WINDOW = '1'
$Env:GENESIS_PRECOMPUTE_FEATURES = '1'
run_optimizer()

# ❌ FEL - non-canonical mode kan ge andra resultat
run_optimizer()  # utan env-vars
```

### 2. Dokumentera non-canonical runs

```python
# Om du MÅSTE köra non-canonical
backtest_info["canonical_mode"] = False
backtest_info["non_canonical_reason"] = "Testing new indicator X before precompute"
```

### 3. Arkivera resultat med canonical status

```
results/
  canonical/
    run_20260123_canonical_optuna/
  non_canonical/
    run_20260123_perf_test_fast_hash/
```

### 4. Verifiera determinism regelbundet

```powershell
# I pre-commit hooks eller CI
python -m pytest tests/test_canonical_determinism.py
```

---

## Related Documentation

- [P0.1 - Lazy Champion Loader](../roadmap/STABILIZATION_PLAN_9_STEPS.md#p01)
- [P0.2 - Canonical Mode Preflight](../roadmap/STABILIZATION_PLAN_9_STEPS.md#p02)
- [P0.3 - Feature Parity Test](../roadmap/STABILIZATION_PLAN_9_STEPS.md#p03)
- [Optuna Best Practices](../optuna/OPTUNA_BEST_PRACTICES.md)
- [Preflight Checklist](./PREFLIGHT_CHECKLIST.md)

---

## Change Log

| Date       | Change                    | Reason                          |
| ---------- | ------------------------- | ------------------------------- |
| 2026-01-23 | Initial creation          | P1.1 documentation task         |
| 2026-01-15 | FAST_HASH policy          | Proven non-determinism evidence |
| 2026-01-14 | Canonical contract locked | P0.1-P0.3 completion            |
