# Champion Reproducibility - Complete Config Storage

## Problem

Champions created in one time period could produce different results when tested later if `runtime.json` changed between creation and testing.

**Example:**

```
October 2025:
  runtime.json v1: ltf_override_threshold = 0.85
  aggressive.json: entry_conf_overall = 0.38
  Merge → Test → 938 trades, -20% return

February 2026:
  runtime.json v2: ltf_override_threshold = 0.70  ← CHANGED
  aggressive.json: entry_conf_overall = 0.38  ← UNCHANGED
  Merge → Test → 1200 trades, -35% return  ← DIFFERENT!
```

**Root Cause:** Champion files only stored trial parameter overrides (`cfg`), not the complete merged configuration. Testing required merging with whatever `runtime.json` existed at test time.

## Solution: Alternativ 1 - Complete Config Storage

Save the **entire merged configuration** (runtime + trial parameters) in both backtest results and champion files.

### Implementation

#### 1. Backtest Results (scripts/run_backtest.py)

```python
# Lines 182-206: Detect complete champions
override_payload = json.load(open(config_file))

if "merged_config" in override_payload:
    # Complete champion - use stored config
    logger.info("[CONFIG:champion] Using complete champion config (no runtime merge)")
    override_cfg = override_payload["merged_config"]
    is_complete_champion = True
else:
    # Regular config - merge with runtime
    override_cfg = override_payload.get("cfg", override_payload)
    cfg, _, runtime_version = ConfigAuthority.get()
    merged_cfg = _deep_merge(cfg, override_cfg)
    is_complete_champion = False

# Lines 210-212: Save merged_config to results
if not is_complete_champion:
    results["merged_config"] = merged_cfg
    results["runtime_version"] = runtime_version
```

#### 2. Optuna Runner (src/core/optimizer/runner.py)

```python
# Lines 708-747: Extract merged_config from results
results = json.load(open(results_path))
merged_config = results.get("merged_config")
runtime_version = results.get("runtime_version")

final_payload = {
    "cfg": trial_params,
    "merged_config": merged_config,
    "runtime_version": runtime_version,
    # ... metrics
}

# Line 1574: Pass runtime_version to write_champion
write_champion(
    champion_path,
    candidate,
    runtime_version=best_result.get("runtime_version")
)
```

#### 3. Champion Storage (src/core/optimizer/champion.py)

```python
@dataclass
class ChampionCandidate:
    cfg: JsonDict
    merged_config: JsonDict | None = None  # Complete merged config
    # ... other fields

@dataclass
class ChampionRecord:
    cfg: JsonDict
    merged_config: JsonDict | None = None  # Complete merged config
    runtime_version: int | None = None     # Runtime version at creation
    # ... other fields

def to_json(self) -> JsonDict:
    result = {
        "cfg": self.cfg,
        # ... other fields
    }
    if self.merged_config is not None:
        result["merged_config"] = self.merged_config
    if self.runtime_version is not None:
        result["runtime_version"] = self.runtime_version
    return result
```

## Usage

### Complete Champion (with merged_config)

**Champion file structure:**

```json
{
  "cfg": {
    "entry_conf_overall": 0.38,
    "exit_conf_threshold": 0.30
  },
  "merged_config": {
    "entry_conf_overall": 0.38,
    "exit_conf_threshold": 0.30,
    "multi_timeframe": {"ltf_override_threshold": 0.85},
    "ev": {"R_default": 1.8},
    "features": {...}
  },
  "runtime_version": 2,
  "metrics": {...}
}
```

**Testing:**

```bash
python scripts/run_backtest.py --config-file config/strategy/champions/champion.json
# → Uses merged_config directly
# → SKIPS runtime.json merge
# → Identical results every time ✅
```

**Log output:**

```
[CONFIG:champion] Using complete champion config (no runtime merge)
```

### Regular Config (without merged_config)

**Config file structure:**

```json
{
  "cfg": {
    "entry_conf_overall": 0.38,
    "exit_conf_threshold": 0.3
  }
}
```

**Testing:**

```bash
python scripts/run_backtest.py --config-file config/tmp/aggressive.json
# → Merges with current runtime.json
# → Results may vary if runtime changed ⚠️
```

## Data Flow

### Creation Flow (Optuna)

```
1. Optuna trial
   ↓
2. Merge: runtime.json + trial_params → merged_config
   ↓
3. Run backtest with merged_config
   ↓
4. Save to results JSON:
   - cfg: trial_params (override values only)
   - merged_config: complete merged config
   - runtime_version: 2
   ↓
5. Write champion file:
   - cfg: trial_params
   - merged_config: complete merged config
   - runtime_version: 2
```

### Testing Flow (Backtest)

```
Load config file
   ↓
Check: "merged_config" in file?
   ↓
YES → Use merged_config directly (skip runtime merge)
NO  → Merge with current runtime.json
   ↓
Run backtest
```

## Merge Behavior

### Deep Merge Example

**runtime.json (base):**

```json
{
  "thresholds": {"entry_conf_overall": 0.35},
  "exit": {"exit_conf_threshold": 0.40},
  "risk": {"risk_map": [[0.45, 0.015], [0.55, 0.025]]},
  "multi_timeframe": {"ltf_override_threshold": 0.85},
  "ev": {"R_default": 2.0},
  "features": {...}
}
```

**aggressive.json (overrides):**

```json
{
  "thresholds": { "entry_conf_overall": 0.38 },
  "exit": { "exit_conf_threshold": 0.3 },
  "risk": {
    "risk_map": [
      [0.3, 0.015],
      [0.4, 0.022]
    ]
  }
}
```

**merged_config (result):**

```json
{
  "thresholds": {"entry_conf_overall": 0.38},      // from aggressive
  "exit": {"exit_conf_threshold": 0.30},           // from aggressive
  "risk": {"risk_map": [[0.3, 0.015], [0.4, 0.022]]},  // from aggressive
  "multi_timeframe": {"ltf_override_threshold": 0.85}, // from runtime ✓
  "ev": {"R_default": 2.0},                        // from runtime ✓
  "features": {...}                                // from runtime ✓
}
```

Fields present in `aggressive.json` override runtime values.
Fields missing from `aggressive.json` are filled from runtime.

## Benefits

### Reproducibility

- Champions produce identical results regardless of when tested
- Complete configuration stored prevents drift from runtime changes
- `runtime_version` tracking enables forensics and debugging

### Flexibility

- Regular config files still merge with current runtime (dynamic)
- Champions use frozen config (static)
- Choose behavior by including/excluding `merged_config`

### Transparency

- Full configuration visible in champion files
- No hidden dependencies on runtime state
- Clear documentation of what was actually tested

### Scientific Rigor

- Results can be validated months later
- No "works on my machine" issues from runtime drift
- Proper experiment reproducibility

## Backward Compatibility

**Old champions without merged_config:**

```json
{
  "cfg": { "entry_conf_overall": 0.38 }
}
```

- Still work via runtime merge
- Produce results based on current runtime.json
- Not reproducible across runtime versions

**New champions with merged_config:**

```json
{
  "cfg": {"entry_conf_overall": 0.38},
  "merged_config": {...}
}
```

- Reproducible across time
- Independent of runtime.json changes
- Recommended for all production champions

## Migration

To convert old champions to complete champions:

```python
import json
from core.config.config_authority import ConfigAuthority

# Load old champion
champion = json.load(open("old_champion.json"))

# Get current runtime
runtime, _, version = ConfigAuthority.get()

# Recreate merge
from scripts.run_backtest import _deep_merge
merged = _deep_merge(runtime, champion["cfg"])

# Add to champion
champion["merged_config"] = merged
champion["runtime_version"] = version

# Save
json.dump(champion, open("old_champion.json", "w"), indent=2)
```

**Note:** Merged config will reflect current runtime state. For true historical accuracy, you'd need the exact runtime.json version from when the champion was created.

## Verification

Check if backtest results contain merged_config:

```bash
python -c "import json; r = json.loads(open('results/backtests/result.json').read()); print('merged_config:', 'merged_config' in r); print('runtime_version:', r.get('runtime_version'))"
```

Expected output:

```
merged_config: True
runtime_version: 2
```

## File Locations

- **Results:** `results/backtests/tBTCUSD_1h_YYYYMMDD_HHMMSS.json`
- **Champions:** `config/strategy/champions/{symbol}_{timeframe}.json`
- **Runtime:** `config/runtime.json` (active), `config/runtime.seed.json` (template)

## Related Documentation

- `docs/runtime/RUNTIME_PATCH_WORKFLOW.md` - Runtime configuration updates
- `docs/optimizer.md` - Optuna optimization workflow
- `AGENTS.md` - Agent handoff and project status
