#!/usr/bin/env python3
"""Preflight-kontroll för Optuna-körningar - säkerställer att allt är korrekt innan start."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def check_optuna_installed() -> tuple[bool, str]:
    """Kontrollera att Optuna är installerat."""
    try:
        import optuna

        return True, f"[OK] Optuna {optuna.__version__} installerat"
    except ImportError:
        return False, "[FAIL] Optuna är inte installerat - kör: pip install optuna"


def check_storage_writable(storage: str | None) -> tuple[bool, str]:
    """Kontrollera att Optuna-storage är skrivbart."""
    if not storage or not storage.startswith("sqlite:///"):
        return True, f"[WARN] Storage-format: {storage} (förväntar sqlite:///)"

    db_path = Path(storage.replace("sqlite:///", ""))
    try:
        # Försök skapa katalogen om den inte finns
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # Försök öppna/redigera databasen
        if db_path.exists():
            if not db_path.is_file():
                return False, f"✗ Storage-sökväg finns men är inte en fil: {db_path}"
            # Kontrollera skrivrättigheter
            test_path = db_path.parent / ".optuna_write_test"
            try:
                test_path.write_text("test")
                test_path.unlink()
            except Exception as e:
                return False, f"✗ Ingen skrivrättighet till {db_path.parent}: {e}"
        return True, f"[OK] Storage {db_path} är skrivbar"
    except Exception as e:
        return False, f"[FAIL] Kan inte skriva till storage: {e}"


def check_study_resume(
    storage: str | None, study_name: str | None, allow_resume: bool
) -> tuple[bool, str]:
    """Kontrollera study resume-konfiguration."""
    if not storage or not study_name:
        return True, "[WARN] Storage eller study_name saknas"

    if not allow_resume:
        if storage and storage.startswith("sqlite:///"):
            db_path = Path(storage.replace("sqlite:///", ""))
            if db_path.exists():
                return (
                    False,
                    f"[FAIL] Resume=false men storage-fil finns redan: {db_path}. "
                    "Byt filnamn eller ta bort den för att undvika återanvändning.",
                )
        return True, "[OK] Resume=false - ny study kommer skapas"

    try:
        import optuna

        db_path = Path(storage.replace("sqlite:///", ""))
        if db_path.exists():
            # Försök ladda study
            study = optuna.load_study(study_name=study_name, storage=storage)
            n_trials = len(study.trials)
            return (
                True,
                f"[OK] Study '{study_name}' finns med {n_trials} trials - resume kommer fungera",
            )
        else:
            return (
                True,
                f"[OK] Study '{study_name}' finns inte - ny study kommer skapas",
            )
    except Exception as e:
        return False, f"[FAIL] Kan inte ladda study för resume-kontroll: {e}"


def check_timeout_config(max_trials: Any, timeout_seconds: Any) -> tuple[bool, str]:
    """Kontrollera timeout och max_trials-konfiguration."""
    issues = []

    if timeout_seconds is None:
        issues.append("[WARN] timeout_seconds är inte satt - Optuna kan köra oändligt")
    else:
        hours = timeout_seconds / 3600
        issues.append(f"[OK] timeout_seconds={timeout_seconds}s ({hours:.1f}h)")

    if max_trials is None:
        issues.append("[OK] max_trials=null - kör tills timeout")
    else:
        max_trials_int = int(max_trials)
        if max_trials_int > 0:
            est_hours = (max_trials_int * 170) / 3600  # ~170s per trial
            issues.append(
                f"[WARN] max_trials={max_trials_int} - stoppar efter ~{est_hours:.1f}h "
                f"(eller timeout om {timeout_seconds/3600:.1f}h nås först)"
            )

    return True, " | ".join(issues)


def check_sampler_settings(optuna_cfg: dict[str, Any]) -> tuple[bool, str]:
    sampler = optuna_cfg.get("sampler") or {}
    kwargs = sampler.get("kwargs") or {}
    messages = []

    n_startup = kwargs.get("n_startup_trials")
    if n_startup is None:
        messages.append(
            "[WARN] n_startup_trials saknas i sampler.kwargs – TPE kan exploatera för tidigt"
        )
    elif int(n_startup) < 15:
        messages.append(
            f"[WARN] n_startup_trials={n_startup} är lågt – överväg >=15 för bättre exploration"
        )
    else:
        messages.append(f"[OK] n_startup_trials={n_startup}")

    if "n_ei_candidates" in kwargs:
        messages.append(f"[OK] n_ei_candidates={kwargs['n_ei_candidates']}")
    else:
        messages.append("[WARN] n_ei_candidates saknas – använder Optunas default")

    return True, " | ".join(messages)


def check_parameters_valid(parameters: dict[str, Any]) -> tuple[bool, str]:
    """Kontrollera att parametrarna är korrekta."""
    issues = []

    # Kontrollera att alla required-fält finns
    required_sections = ["thresholds", "risk", "exit"]
    for section in required_sections:
        if section not in parameters:
            issues.append(f"[FAIL] Saknar parameter-sektion: {section}")

    # Kontrollera att det finns minst en icke-fixerad parameter
    def count_searchable_params(spec: dict[str, Any], path: str = "") -> int:
        count = 0
        for key, value in spec.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, dict):
                param_type = value.get("type")
                if param_type in ("float", "grid"):
                    count += 1
                elif param_type == "fixed":
                    pass  # Ignorera fixerade
                else:
                    count += count_searchable_params(value, current_path)
        return count

    searchable = count_searchable_params(parameters)
    if searchable == 0:
        issues.append("[WARN] Alla parametrar är fixerade - ingen optimering kommer ske")
    else:
        issues.append(f"[OK] {searchable} sökbara parametrar hittade")

    has_errors = any("[FAIL]" in issue for issue in issues)
    return not has_errors, " | ".join(issues)


def check_snapshot_exists(snapshot_id: str, symbol: str, timeframe: str) -> tuple[bool, str]:
    """Kontrollera att snapshot-data finns och är läsbar."""
    if not snapshot_id:
        return False, "[FAIL] snapshot_id saknas i konfiguration"

    # Extrahera datum från snapshot_id (format: SYMBOL_TF_START_END_V)
    parts = snapshot_id.split("_")
    if len(parts) >= 5:
        try:
            start_date_str = parts[-3]  # 2024-10-22
            end_date_str = parts[-2]  # 2025-10-01
            # Validera datumformat
            from datetime import datetime

            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
        except (ValueError, IndexError):
            pass  # Ignorera om parsing misslyckas

    # Kontrollera att datafilen finns
    from pathlib import Path

    base_dir = Path(__file__).parent.parent / "data"
    data_file_curated = base_dir / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet"
    data_file_legacy = base_dir / "candles" / f"{symbol}_{timeframe}.parquet"

    if data_file_curated.exists():
        try:
            import pandas as pd

            df = pd.read_parquet(data_file_curated)
            if len(df) == 0:
                return False, f"[FAIL] Datafil är tom: {data_file_curated}"
            n_rows = len(df)
            return (
                True,
                f"[OK] snapshot_id: {snapshot_id} | Datafil: {data_file_curated} ({n_rows:,} rader)",
            )
        except Exception as e:
            return False, f"[FAIL] Kan inte läsa datafil {data_file_curated}: {e}"
    elif data_file_legacy.exists():
        try:
            import pandas as pd

            df = pd.read_parquet(data_file_legacy)
            if len(df) == 0:
                return False, f"[FAIL] Datafil är tom: {data_file_legacy}"
            n_rows = len(df)
            return (
                True,
                f"[OK] snapshot_id: {snapshot_id} | Datafil: {data_file_legacy} ({n_rows:,} rader)",
            )
        except Exception as e:
            return False, f"[FAIL] Kan inte läsa datafil {data_file_legacy}: {e}"
    else:
        return (
            False,
            f"[FAIL] Datafil saknas för {symbol} {timeframe}:\n  Försökte: {data_file_curated}\n  Försökte: {data_file_legacy}",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight-kontroll för Optuna-körningar")
    parser.add_argument("config", type=Path, help="Path till optimizer .yaml-fil")
    args = parser.parse_args()

    if not args.config.exists():
        print(f"[ERROR] Konfigfil hittades inte: {args.config}")
        return 1

    print("=" * 70)
    print("OPTUNA PREFLIGHT CHECK")
    print("=" * 70)
    print()

    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    meta = cfg.get("meta", {})
    runs_cfg = meta.get("runs", {})
    optuna_cfg = runs_cfg.get("optuna", {})
    parameters = cfg.get("parameters", {})

    all_ok = True

    # 1. Optuna installerat
    ok, msg = check_optuna_installed()
    print(f"1. Optuna installation: {msg}")
    if not ok:
        all_ok = False
    print()

    # 2. Storage skrivbart
    storage = optuna_cfg.get("storage")
    ok, msg = check_storage_writable(storage)
    print(f"2. Storage: {msg}")
    if not ok:
        all_ok = False
    print()

    # 3. Study resume
    study_name = optuna_cfg.get("study_name")
    allow_resume = runs_cfg.get("resume", True)
    ok, msg = check_study_resume(storage, study_name, allow_resume)
    print(f"3. Study resume: {msg}")
    if not ok:
        all_ok = False
    print()

    # 4. Sampler-inställningar
    ok, msg = check_sampler_settings(optuna_cfg)
    print(f"4. Sampler: {msg}")
    print()

    # 5. Timeout/max_trials
    max_trials = runs_cfg.get("max_trials")
    timeout_seconds = optuna_cfg.get("timeout_seconds")
    ok, msg = check_timeout_config(max_trials, timeout_seconds)
    print(f"5. Timeout/max_trials: {msg}")
    print()

    # 6. Parametrar
    ok, msg = check_parameters_valid(parameters)
    print(f"6. Parametrar: {msg}")
    if not ok:
        all_ok = False
    print()

    # 7. Snapshot & Data
    snapshot_id = meta.get("snapshot_id")
    symbol = meta.get("symbol", "tBTCUSD")
    timeframe = meta.get("timeframe", "1h")
    ok, msg = check_snapshot_exists(snapshot_id, symbol, timeframe)
    print(f"7. Snapshot & Data: {msg}")
    if not ok:
        all_ok = False
    print()

    # 8. Validering mot champion
    print("8. Champion-validering:")
    try:
        from scripts.validate_optimizer_config import validate_config

        val_result = validate_config(args.config)
        if val_result != 0:
            all_ok = False
            print(
                "   [WARN] Champion-validering misslyckades - kör validering separat för detaljer"
            )
        else:
            print("   [OK] Champion-validering OK")
    except Exception as e:
        print(f"   [WARN] Kunde inte köra champion-validering: {e}")
    print()

    # Sammanfattning
    print("=" * 70)
    if all_ok:
        print("[OK] Alla preflight-checkar passerade - Optuna bör kunna köras")
        return 0
    else:
        print("[FAIL] Några preflight-checkar misslyckades - fixa innan körning")
        return 1


if __name__ == "__main__":
    sys.exit(main())
