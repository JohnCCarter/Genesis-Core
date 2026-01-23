# Preflight Checklist - Canonical Optuna Körningar

**Status**: Active (2026-01-23)
**Related**: [Canonical Mode](./CANONICAL_MODE.md), P0.2

## Översikt

Denna checklista MÅSTE följas före alla canonical Optuna-körningar som tar >30 minuter. Syftet är att undvika dyra fel som upptäcks sent.

---

## Pre-Run Validation (OBLIGATORISKT)

### 1. Config Validation

```powershell
python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
```

**MÅSTE returnera 0** - fixar alla `[ERROR]` innan fortsättning.

**Kollar**:

- ✅ Champion-parametrar finns i sökrymd eller är korrekt fixerade
- ✅ `signal_adaptation` zones hanteras (ej fixerade till fel värden)
- ✅ Kritiska parametrar ej utelämnade (partial_1_pct, partial_2_pct, etc.)
- ✅ Search space kan reproducera champion

**Output vid fel**:

```
[ERROR] Champion parameter 'partial_1_pct' (0.6) not in search space
[ERROR] Fix: Add to search space or set as fixed value
```

---

### 2. Preflight Check

```powershell
python scripts/preflight_optuna_check.py config/optimizer/<config>.yaml
```

**MÅSTE returnera 0** - fixar alla kritiska varningar.

**Kollar**:

- ✅ Optuna installerat och importerbart
- ✅ Storage skrivbar
- ✅ Ingen tidigare DB-fil om `resume=false`
- ✅ Study resume fungerar om `resume=true`
- ✅ Sampler har `n_startup_trials >= 15`
- ✅ Timeout/max_trials korrekt konfigurerat
- ✅ Mode/miljö kompatibilitet (canonical 1/1)
- ✅ `GENESIS_FAST_HASH=0` i canonical mode (om strict=1)

**Output vid varning**:

```
[WARN] GENESIS_FAST_HASH=1 detected in canonical mode
[WARN] This may cause non-comparable results
[WARN] Set GENESIS_PREFLIGHT_FAST_HASH_STRICT=1 to fail instead
```

---

### 3. Baseline Smoke Test

```powershell
# Testa championens exakta parametrar på SAMMA period som Optuna kommer köra
python scripts/run_backtest.py \
  --config-file config/strategy/champions/tBTCUSD_1h.json \
  --start-date <explore_start> \
  --end-date <explore_end>
```

**Förväntat**:

- Minst 50+ trades på 6-månaders period
- PF >= 1.0
- No fatal errors

**Om <50 trades eller PF < 1.0**: Champion kan vara utdaterad för perioden, överväg att justera sökrymd.

---

## Environment Setup (OBLIGATORISKT)

### 4. Sätt Canonical Env Vars

```powershell
# PowerShell
$Env:GENESIS_FAST_WINDOW = '1'
$Env:GENESIS_PRECOMPUTE_FEATURES = '1'
$Env:GENESIS_RANDOM_SEED = '42'
$Env:GENESIS_FAST_HASH = '0'  # Explicit av

# Verifiera
echo "FAST_WINDOW: $Env:GENESIS_FAST_WINDOW"
echo "PRECOMPUTE: $Env:GENESIS_PRECOMPUTE_FEATURES"
echo "SEED: $Env:GENESIS_RANDOM_SEED"
echo "FAST_HASH: $Env:GENESIS_FAST_HASH"
```

**Förväntad output**:

```
FAST_WINDOW: 1
PRECOMPUTE: 1
SEED: 42
FAST_HASH: 0
```

---

### 5. Cache Management

```powershell
# Arkivera gamla _cache från tidigare runs
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
New-Item -Path "results/hparam_search/_archive/cache_$timestamp" -ItemType Directory -Force

# Flytta alla _cache kataloger
Get-ChildItem -Path "results/hparam_search/run_*/_cache" -Recurse |
  Move-Item -Destination "results/hparam_search/_archive/cache_$timestamp/"
```

**Varför**: Gamla cacher kan återanvändas felaktigt om parameter-hash kolliderar.

---

### 6. Database Management

**Om `resume=false` i config**:

```powershell
# Flytta/radera gammal DB-fil
$db_path = "results/hparam_search/storage/<study_name>.db"
if (Test-Path $db_path) {
    Move-Item $db_path "results/hparam_search/storage/_archive/<study_name>_$timestamp.db"
}
```

**Om `resume=true` i config**:

```powershell
# Verifiera att DB-fil finns
$db_path = "results/hparam_search/storage/<study_name>.db"
if (-not (Test-Path $db_path)) {
    Write-Error "Resume=true but DB file not found: $db_path"
    exit 1
}
```

---

## Search Space Validation

### 7. Champion Reproducibility Check

```powershell
python scripts/verify_champion_in_search_space.py \
  --champion config/strategy/champions/tBTCUSD_1h.json \
  --optuna-config config/optimizer/<config>.yaml
```

**Förväntat output**:

```
[OK] All champion parameters can be reproduced in search space
[OK] partial_1_pct: 0.6 in range [0.4, 0.8]
[OK] partial_2_pct: 0.5 in range [0.3, 0.7]
...
```

**Om FAIL**: Justera sökrymd eller fixa champion-parametrar i Optuna-config.

---

### 8. Search Space Breadth Check

```powershell
# Kör smoke med 3-5 trials och verifiera variation
python scripts/run_optuna_smoke.py config/optimizer/<config>.yaml --trials 5
```

**Förväntat**:

- Minst 3 olika trade counts (ej alla identiska)
- Score-variation > 0.1
- Ingen trial med 0 trades (om inte explore-fas)

**Om alla identiska**: Sökrymd för smal eller champion-merge aktiv (sätt `skip_champion_merge=true`).

---

## Concurrency & Resources

### 9. System Resources Check

```powershell
# Kontrollera ledigt diskutrymme (minst 10 GB)
Get-PSDrive C | Select-Object Used, Free

# Kontrollera CPU/RAM
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5

# Stäng av Windows Update (viktigt!)
# Manuellt: Settings > Windows Update > Pause for 7 days
```

**Minimum requirements**:

- 10 GB ledigt diskutrymme
- <80% RAM-användning innan start
- Windows Update pausad

---

### 10. Concurrency Settings

**Rekommenderat**:

```yaml
# I optimizer config
optuna:
  max_concurrent: 4 # För CPU-bound backtests (fast mode)
```

**Varför inte högre**:

- SQLite DB kan ge `disk I/O error` vid >4 concurrent writers
- Precompute-cache är thread-safe men mer workers = mer RAM

**Om SQLite-fel uppstår**:

1. Sänk `max_concurrent` till 2
2. Eller byt till PostgreSQL storage (se Optuna docs)

---

## Final Pre-Launch Checklist

**Innan `run_optimizer()` startas**:

- [ ] `validate_optimizer_config.py` returnerade 0
- [ ] `preflight_optuna_check.py` returnerade 0
- [ ] Champion smoke test kördes framgångsrikt (>50 trades)
- [ ] Canonical env-vars satta och verifierade
- [ ] `GENESIS_FAST_HASH=0` bekräftad
- [ ] Gamla `_cache/` arkiverade
- [ ] DB-fil hanterad (flyttad om resume=false, verifierad om resume=true)
- [ ] Champion-parametrar verifierade i sökrymd
- [ ] Smoke test visar variation (ej alla identiska)
- [ ] Diskutrymme >= 10 GB
- [ ] Windows Update pausad
- [ ] `max_concurrent` sätt till säkert värde (2-4)

---

## During Run Monitoring

### Real-time Checks

```powershell
# Kolla DB-storlek (ska växa)
Get-ChildItem "results/hparam_search/storage/*.db" | Select-Object Name, Length

# Kolla senaste trial-log
Get-Content "results/hparam_search/run_*/trial_*.log" -Tail 50

# Kolla cache-träffar (bör vara låg för ny körning)
Select-String -Path "results/hparam_search/run_*/trial_*.log" -Pattern "from_cache=True" | Measure-Object
```

**Red flags**:

- DB-storleken växer inte på 10+ minuter
- Många `disk I/O error` i loggar → sänk concurrency
- > 80% cache hits på nya trials → arkivera cache och starta om

---

## Post-Run Validation

### Efter körning slutfört

```powershell
# Sammanfatta resultat
python scripts/optimizer.py summarize <run_id> --top 10

# Verifiera trial-diversity
python scripts/analyze_optuna_db.py results/hparam_search/storage/<study>.db

# Exportera för analys
python scripts/export_optuna_trials.py results/hparam_search/storage/<study>.db
```

**Förväntat**:

- Top-10 trials har variation i parametrar
- Best trial score >= champion baseline
- <20% duplicat-ratio (om högre, bredda sökrymd)

---

## Emergency Abort Procedure

**Om körningen måste stoppas**:

1. **Ctrl+C i terminal** (avslutar pågående trials gracefully)
2. **Vänta 30s** tills alla workers stängt DB-connections
3. **Backup DB-fil**:
   ```powershell
   Copy-Item "results/hparam_search/storage/<study>.db" `
             "results/hparam_search/storage/<study>_backup_$timestamp.db"
   ```
4. **Analysera vad som hände**:
   ```powershell
   python scripts/optimizer.py summarize <run_id>
   ```

**Resume efter abort**:

- Sätt `resume: true` i config
- Kör preflight igen (verifiera DB-integritet)
- Starta om med `run_optimizer()`

---

## Troubleshooting Common Issues

### Issue: "DB locked" eller "disk I/O error"

**Lösning**:

1. Stoppa körningen (Ctrl+C)
2. Sänk `max_concurrent` till 2
3. Starta om med `resume: true`

### Issue: Alla trials får samma score

**Lösning**:

1. Kolla `backtest_info.champion_status.champion_merged` i resultat
2. Om `true`: Sätt `meta.skip_champion_merge: true` i config
3. Rensa cache och kör om

### Issue: 0 trades i explore-fas

**Lösning**:

1. Bredda sökrymd (särskilt `entry_conf`, `signal_adaptation.zones`)
2. Sänk constraints (`min_trades: 1` istället för 50)
3. Kör smoke igen för att verifiera

---

## Related Documentation

- [Canonical Mode](./CANONICAL_MODE.md)
- [Optuna Best Practices](../optuna/OPTUNA_BEST_PRACTICES.md)
- [P0.2 Preflight Implementation](../roadmap/STABILIZATION_PLAN_9_STEPS.md#p02)

---

## Change Log

| Date       | Change                      | Reason                                        |
| ---------- | --------------------------- | --------------------------------------------- |
| 2026-01-23 | Initial creation            | P1.1 task - operator checklist                |
| 2026-01-20 | Resume signature guardrails | Optuna resume safety (2026-01-20 deliverable) |
