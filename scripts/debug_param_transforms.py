from core.optimizer.param_transforms import transform_parameters

params = {
    "thresholds.entry_conf_overall": 0.22,
    "thresholds.min_edge": 0.008,
    "exit.exit_conf_threshold": 0.48,
    "exit.max_hold_bars": 8,
    "exit.trailing_stop_pct": 0.02,
    "multi_timeframe.ltf_override_threshold": 0.43,
    "multi_timeframe.ltf_override_adaptive.percentile": 0.81,
    "htf_fib.entry.tolerance_atr": 4.25,
    "ltf_fib.entry.tolerance_atr": 1.2,
    "risk.risk_map_deltas.conf_0": -0.05,
    "risk.risk_map_deltas.size_0": 0.0,
    "risk.risk_map_deltas.conf_1": 0.01,
    "risk.risk_map_deltas.size_1": 0.001,
    "risk.risk_map_deltas.conf_2": -0.02,
    "risk.risk_map_deltas.size_2": 0.0,
}

try:
    transformed, derived = transform_parameters(params)
    print("Success!")
    print(derived)
except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
