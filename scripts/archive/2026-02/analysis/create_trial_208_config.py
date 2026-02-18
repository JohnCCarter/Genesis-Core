import json
from pathlib import Path

# Params from Trial 208
PARAMS = {
    "thresholds.entry_conf_overall": 0.28,
    "thresholds.min_edge": 0.01,
    "thresholds.signal_adaptation.zones.low.entry_conf_overall": 0.2,
    "thresholds.signal_adaptation.zones.low.regime_proba": 0.41,
    "thresholds.signal_adaptation.zones.mid.entry_conf_overall": 0.33,
    "thresholds.signal_adaptation.zones.mid.regime_proba": 0.44,
    "thresholds.signal_adaptation.zones.high.entry_conf_overall": 0.41000000000000003,
    "thresholds.signal_adaptation.zones.high.regime_proba": 0.6,
    "exit.exit_conf_threshold": 0.38,
    "exit.max_hold_bars": 22,
    "exit.trailing_stop_pct": 0.01,
    "htf_exit_config.enable_partials": True,
    "htf_exit_config.enable_trailing": False,
    "htf_exit_config.fib_threshold_atr": 0.8,
    "htf_exit_config.trail_atr_multiplier": 2.0,
    "multi_timeframe.ltf_override_threshold": 0.44999999999999996,
    "multi_timeframe.ltf_override_adaptive.percentile": 0.88,
    "htf_fib.entry.tolerance_atr": 3.5,
    "ltf_fib.entry.tolerance_atr": 1.4,
    "risk.risk_map_deltas.conf_0": 0.05,
    "risk.risk_map_deltas.size_0": -0.004,
    "risk.risk_map_deltas.conf_1": -0.06,
    "risk.risk_map_deltas.size_1": -0.003,
    "risk.risk_map_deltas.conf_2": 0.04000000000000001,
    "risk.risk_map_deltas.size_2": 0.01,
}

BASE_RISK_MAP = [
    (0.48, 0.01),
    (0.59, 0.015),
    (0.70, 0.07),
]


def _expand_dot_notation(params):
    expanded = {}
    for key, value in params.items():
        if "." in key:
            parts = key.split(".")
            current = expanded
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
                if not isinstance(current, dict):
                    continue
            current[parts[-1]] = value
        else:
            if key in expanded and isinstance(expanded[key], dict) and isinstance(value, dict):
                expanded[key].update(value)
            else:
                expanded[key] = value
    return expanded


def _build_risk_map_from_deltas(deltas):
    points = []
    for idx, (base_conf, base_size) in enumerate(BASE_RISK_MAP):
        conf_delta = float(deltas.get(f"conf_{idx}", 0.0))
        size_delta = float(deltas.get(f"size_{idx}", 0.0))
        conf = max(0.05, min(0.95, base_conf + conf_delta))
        size = max(0.0, base_size + size_delta)
        points.append((conf, size))

    points.sort(key=lambda item: item[0])
    result = []
    last_size = 0.0
    for conf, size in points:
        size = max(size, last_size)
        last_size = size
        result.append([round(conf, 6), round(size, 6)])
    return result


def deep_merge(target, source):
    for key, value in source.items():
        if isinstance(value, dict) and key in target and isinstance(target[key], dict):
            deep_merge(target[key], value)
        else:
            target[key] = value
    return target


def main():
    # Load base config
    base_path = Path("config/strategy/champions/tBTCUSD_1h.json")
    with open(base_path) as f:
        config = json.load(f)

    # Expand params
    expanded_params = _expand_dot_notation(PARAMS)

    # Handle risk map
    if "risk" in expanded_params and "risk_map_deltas" in expanded_params["risk"]:
        deltas = expanded_params["risk"].pop("risk_map_deltas")
        risk_map = _build_risk_map_from_deltas(deltas)
        expanded_params["risk"]["risk_map"] = risk_map

    # Merge into config['parameters']
    if "parameters" not in config:
        config["parameters"] = {}

    deep_merge(config["parameters"], expanded_params)

    # Save
    out_path = Path("config/tmp/trial_208_analysis.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Created {out_path}")


if __name__ == "__main__":
    main()
