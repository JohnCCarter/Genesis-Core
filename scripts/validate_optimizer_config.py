#!/usr/bin/env python3
"""Validerar optimizer-konfiguration mot champion innan lång körning.

Detta skript jämför en optimizer-konfiguration (.yaml) mot den nuvarande
champion-konfigurationen för att säkerställa att:
1. Championens viktiga parametrar finns i sökrymden
2. Fixerade värden matchar championens värden (eller är rimliga)
3. Championen kan reproduceras i sökrymden
4. Kritiska parametrar inte är utelämnade

Användning:
    python scripts/validate_optimizer_config.py config/optimizer/tBTCUSD_1h_optuna_fib_tune.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def load_champion(symbol: str, timeframe: str) -> dict[str, Any]:
    """Ladda champion-konfiguration."""
    champ_path = Path(f"config/strategy/champions/{symbol}_{timeframe}.json")
    if not champ_path.exists():
        raise FileNotFoundError(f"Champion not found: {champ_path}")
    return json.loads(champ_path.read_text(encoding="utf-8"))


def load_optimizer_config(config_path: Path) -> dict[str, Any]:
    """Ladda optimizer-konfiguration."""
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def extract_param_value(params: dict[str, Any], path: str) -> Any | None:
    """Extrahera parameter-värde från nested dict med dot-notation."""
    keys = path.split(".")
    current = params
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def check_fixed_matches_champion(
    opt_cfg: dict[str, Any],
    champ_params: dict[str, Any],
    param_path: str,
    description: str,
) -> list[str]:
    """Kontrollera om fixerad parameter matchar champion."""
    errors = []
    params_spec = opt_cfg.get("parameters", {})

    # Navigera till parameter-specen
    keys = param_path.split(".")
    spec = params_spec
    for key in keys:
        if not isinstance(spec, dict) or key not in spec:
            return [f"[WARN] Parameter {param_path} finns inte i optimizer-konfig"]
        spec = spec[key]

    if spec.get("type") != "fixed":
        return []  # Inte fixerad, hoppa över

    fixed_value = spec.get("value")
    champ_value = extract_param_value(champ_params, param_path)

    if champ_value is None:
        errors.append(
            f"[WARN] {description}: Champion har ingen {param_path}, men optimizer har fixerat värde {fixed_value}"
        )
    elif fixed_value != champ_value:
        errors.append(
            f"[ERROR] {description}: Fixerat till {fixed_value}, men champion har {champ_value}"
        )

    return errors


def check_champion_in_range(
    opt_cfg: dict[str, Any],
    champ_params: dict[str, Any],
    param_path: str,
    description: str,
) -> list[str]:
    """Kontrollera om championens värde ligger i sökrymden."""
    errors = []
    params_spec = opt_cfg.get("parameters", {})

    # Navigera till parameter-specen
    keys = param_path.split(".")
    spec = params_spec
    for key in keys:
        if not isinstance(spec, dict) or key not in spec:
            return [f"[WARN] Parameter {param_path} finns inte i optimizer-konfig"]

        spec = spec[key]

    champ_value = extract_param_value(champ_params, param_path)
    if champ_value is None:
        return []  # Champion har inte denna parameter

    param_type = spec.get("type")

    if param_type == "fixed":
        fixed_value = spec.get("value")
        if fixed_value != champ_value:
            errors.append(
                f"[ERROR] {description}: Fixerat till {fixed_value}, men champion har {champ_value}"
            )
    elif param_type == "float":
        low = spec.get("low")
        high = spec.get("high")
        if low is not None and champ_value < low:
            errors.append(
                f"[ERROR] {description}: Champion ({champ_value}) ligger under sökrymden (low={low})"
            )
        if high is not None and champ_value > high:
            errors.append(
                f"[ERROR] {description}: Champion ({champ_value}) ligger över sökrymden (high={high})"
            )
    elif param_type == "grid":
        grid_values = spec.get("values", [])
        if champ_value not in grid_values:
            errors.append(
                f"[ERROR] {description}: Champion ({champ_value}) finns inte i grid {grid_values}"
            )

    return errors


def validate_config(opt_config_path: Path) -> int:
    """Validera optimizer-konfiguration mot champion."""
    print(f"[VAL] Validerar {opt_config_path.name} mot champion...\n")

    opt_cfg = load_optimizer_config(opt_config_path)
    meta = opt_cfg.get("meta", {})
    symbol = meta.get("symbol", "tBTCUSD")
    timeframe = meta.get("timeframe", "1h")

    try:
        champ = load_champion(symbol, timeframe)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1

    champ_params = champ.get("parameters", {})
    errors: list[str] = []
    warnings: list[str] = []

    # Kontrollera max_trials vs timeout
    runs_cfg = opt_cfg.get("meta", {}).get("runs", {})
    max_trials = runs_cfg.get("max_trials")
    timeout = runs_cfg.get("optuna", {}).get("timeout_seconds")
    if max_trials is not None and timeout is not None:
        # Beräkna ungefärlig tid per trial (baserat på tidigare körningar: ~138s per trial)
        est_trials_in_timeout = int(timeout / 138) if timeout else None
        warnings.append(
            f"[INFO] max_trials={max_trials} och timeout={timeout}s ({timeout/3600:.1f}h) är båda satta. "
            f"Optuna stoppar när första gränsen nås. Ungefär {est_trials_in_timeout} trials kan köras inom timeout."
        )
    elif max_trials is None and timeout:
        warnings.append(
            f"[INFO] max_trials=null, timeout={timeout}s ({timeout/3600:.1f}h). Optuna kommer köra tills timeout nås."
        )

    # Kritiska parametrar att kontrollera
    critical_checks = [
        ("htf_exit_config.partial_1_pct", "Partial 1%"),
        ("htf_exit_config.partial_2_pct", "Partial 2%"),
        ("htf_exit_config.fib_threshold_atr", "HTF Fib threshold ATR"),
        ("htf_exit_config.trail_atr_multiplier", "Trail ATR multiplier"),
        ("thresholds.entry_conf_overall", "Entry conf overall"),
        ("exit.exit_conf_threshold", "Exit conf threshold"),
        ("exit.max_hold_bars", "Max hold bars"),
        ("risk.risk_map", "Risk map"),
    ]

    print("=== Fixerade parametrar ===")
    for param_path, description in critical_checks:
        check_results = check_fixed_matches_champion(opt_cfg, champ_params, param_path, description)
        for result in check_results:
            if result.startswith("[ERROR]"):
                errors.append(result)
            else:
                warnings.append(result)

    print("=== Sökrymmor (optuna/grid) ===")
    for param_path, description in critical_checks:
        check_results = check_champion_in_range(opt_cfg, champ_params, param_path, description)
        for result in check_results:
            if result.startswith("[ERROR]"):
                errors.append(result)
            else:
                warnings.append(result)

    # Kontrollera att championens parametrar kan reproduceras
    print("\n=== Champion-reproduktibilitet ===")
    champ_entry_conf = extract_param_value(champ_params, "thresholds.entry_conf_overall")
    champ_exit_conf = extract_param_value(champ_params, "exit.exit_conf_threshold")
    champ_max_hold = extract_param_value(champ_params, "exit.max_hold_bars")
    champ_partial_1 = extract_param_value(champ_params, "htf_exit_config.partial_1_pct")
    champ_partial_2 = extract_param_value(champ_params, "htf_exit_config.partial_2_pct")

    print(f"Champion entry_conf_overall: {champ_entry_conf}")
    print(f"Champion exit_conf_threshold: {champ_exit_conf}")
    print(f"Champion max_hold_bars: {champ_max_hold}")
    print(f"Champion partial_1_pct: {champ_partial_1}")
    print(f"Champion partial_2_pct: {champ_partial_2}")

    # Kontrollera signal_adaptation (saknas ofta i Optuna-konfigs)
    champ_signal_adapt = extract_param_value(champ_params, "thresholds.signal_adaptation")
    opt_params = opt_cfg.get("parameters", {})
    opt_signal_adapt = extract_param_value(opt_params, "thresholds.signal_adaptation")

    if champ_signal_adapt and not opt_signal_adapt:
        warnings.append(
            "[WARN] Champion har 'signal_adaptation' men den saknas i optimizer-konfig (kommer använda defaults)"
        )

    # Sammanfatta
    print("\n" + "=" * 60)
    if errors:
        print(f"[ERROR] {len(errors)} KRITISKA FEL:")
        for err in errors:
            if err.startswith("[ERROR]"):
                print(f"  {err}")
            else:
                errors.remove(err)
                warnings.append(err)
        print()
    if warnings:
        print(f"[WARN] {len(warnings)} VARNINGAR:")
        for warn in warnings:
            print(f"  {warn}")
        print()

    critical_errors = [e for e in errors if e.startswith("[ERROR]")]
    if critical_errors:
        print("[FAIL] VALIDERING MISSLYCKADES - Fixa felen innan körning!")
        return 1
    elif warnings:
        print("[WARN] VALIDERING MED VARNINGAR - Granska innan körning.")
        return 0
    else:
        print("[OK] VALIDERING OK - Konfiguration ser korrekt ut.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validera optimizer-konfiguration mot champion")
    parser.add_argument("config", type=Path, help="Path till optimizer .yaml-fil")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"[ERROR] Konfigfil hittades inte: {args.config}")
        return 1

    return validate_config(args.config)


if __name__ == "__main__":
    sys.exit(main())
