#!/usr/bin/env python3
"""Preflight-kontroll för Optuna-körningar - säkerställer att allt är korrekt innan start."""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
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
            timeout_str = f"{timeout_seconds/3600:.1f}h" if timeout_seconds else "aldrig"
            issues.append(
                f"[WARN] max_trials={max_trials_int} - stoppar efter ~{est_hours:.1f}h "
                f"(eller timeout om {timeout_str} nås först)"
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


def check_duplicate_guard() -> tuple[bool, str]:
    env_value = os.getenv("OPTUNA_MAX_DUPLICATE_STREAK")
    if env_value is None:
        return True, "[OK] OPTUNA_MAX_DUPLICATE_STREAK ej satt (default 10)"
    try:
        streak = int(env_value)
    except ValueError:
        return False, f"[FAIL] OPTUNA_MAX_DUPLICATE_STREAK='{env_value}' är inte ett heltal"
    if streak <= 0:
        return False, f"[FAIL] OPTUNA_MAX_DUPLICATE_STREAK={streak} måste vara > 0"
    if streak < 5:
        return (
            True,
            f"[WARN] OPTUNA_MAX_DUPLICATE_STREAK={streak} är lågt – risk för tidigt avbrott",
        )
    return True, f"[OK] OPTUNA_MAX_DUPLICATE_STREAK={streak}"


def check_precompute_functionality(symbol: str, timeframe: str) -> tuple[bool, str]:
    """Testa att precompute-funktionalitet fungerar korrekt."""
    if not os.environ.get("GENESIS_PRECOMPUTE_FEATURES"):
        return True, "[SKIP] GENESIS_PRECOMPUTE_FEATURES inte satt"

    try:
        import sys
        from pathlib import Path

        # Add project root and src to path for imports
        project_root = Path(__file__).parent.parent
        src_path = project_root / "src"
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from src.core.backtest.engine import BacktestEngine

        # Ladda data
        data_path = ROOT / "data" / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet"
        if not data_path.exists():
            return False, f"[FAIL] Data saknas: {data_path}"

        # Skapa engine och testa precompute
        engine = BacktestEngine(
            symbol=symbol,
            timeframe=timeframe,
            initial_capital=10000,
            commission_rate=0.002,
            slippage_rate=0.001,
            warmup_bars=150,
            fast_window=True,  # Match production settings
        )
        engine.precompute_features = True

        # Load data (inga argument - använder self.symbol och self.timeframe)
        if not engine.load_data():
            return False, "[FAIL] Kunde inte ladda data"

        # Kolla antal bars
        total_bars = len(engine.candles_df)
        if total_bars < 150:
            return True, f"[WARN] För lite data ({total_bars} bars) - kan inte testa ordentligt"

        # Verifiera att precompute skapades
        if not hasattr(engine, "_precomputed_features") or not engine._precomputed_features:
            return False, "[FAIL] Precompute skapades inte trots precompute_features=True"

        precomp = engine._precomputed_features
        required = ["rsi_14", "atr_14", "ema_20", "ema_50"]
        missing = [k for k in required if k not in precomp]
        if missing:
            return False, f"[FAIL] Saknar features: {missing}"

        expected_len = total_bars
        actual_len = len(precomp["rsi_14"])
        if actual_len != expected_len:
            return False, f"[FAIL] Feature-längd {actual_len} != data-längd {expected_len}"

        return True, f"[OK] Precompute fungerar - {total_bars} bars, {len(precomp)} features"

    except ImportError as e:
        return True, f"[WARN] Import-fel (ignorerat): {e}"
    except Exception as e:
        return False, f"[FAIL] Precompute-fel: {e}"


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
    if len(parts) >= 4:
        try:
            # Vanlig konvention i projektet: ..._START_END[_V]
            start_date_str = parts[-3]
            end_date_str = parts[-2]
            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
        except (ValueError, IndexError):
            return False, f"[FAIL] snapshot_id saknar giltiga datumdelar: {snapshot_id}"
    else:
        return False, f"[FAIL] snapshot_id ogiltigt format: {snapshot_id}"

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


def check_date_source(meta: dict[str, Any], runs_cfg: dict[str, Any]) -> tuple[bool, str]:
    """
    Validera hur datumkälla bestäms i runnern:
    - Runnern läser use_sample_range från meta.runs (inte från meta).
    - Om use_sample_range=true i runs: krävs sample_start och sample_end i runs.
    - Om use_sample_range inte är true: krävs giltigt meta.snapshot_id som går att parsas.
    """
    issues: list[str] = []
    ok = True

    meta_usr = meta.get("use_sample_range", None)
    runs_usr = runs_cfg.get("use_sample_range", None)

    # Felplacering: flagga när use_sample_range ligger under meta istället för meta.runs
    if meta_usr is not None and runs_usr is None:
        ok = False
        issues.append(
            "[FAIL] use_sample_range är definierad under meta, men runner läser meta.runs.use_sample_range. "
            "Flytta den till meta.runs.use_sample_range."
        )

    # När runnern ska använda sample-range måste båda fält finnas i runs
    if runs_usr is True or (
        isinstance(runs_usr, str) and runs_usr.strip().lower() in {"1", "true", "yes", "y", "on"}
    ):
        start_raw = runs_cfg.get("sample_start")
        end_raw = runs_cfg.get("sample_end")
        if not start_raw or not end_raw:
            ok = False
            issues.append(
                "[FAIL] use_sample_range=true men runs.sample_start eller runs.sample_end saknas. "
                "Lägg till båda under meta.runs."
            )
        else:
            # Validera datumformat
            try:
                datetime.fromisoformat(str(start_raw).strip())
                datetime.fromisoformat(str(end_raw).strip())
                issues.append(f"[OK] sample_range: {start_raw} -> {end_raw}")
            except Exception:
                ok = False
                issues.append(
                    f"[FAIL] sample_start/sample_end har ogiltigt datumformat: {start_raw} / {end_raw}"
                )
    else:
        # Då måste snapshot_id vara giltig
        snap = meta.get("snapshot_id", "")
        if not isinstance(snap, str) or not snap.strip():
            ok = False
            issues.append(
                "[FAIL] use_sample_range=false (eller ej satt) och meta.snapshot_id saknas. "
                "Runner kommer krascha med 'trial snapshot_id saknas'."
            )

    if not issues:
        issues.append("[OK] Datumkälla validerad")
    return ok, " | ".join(issues)


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

    # 5. Duplicate guard (miljövariabel)
    ok, msg = check_duplicate_guard()
    print(f"5. Duplicate guard: {msg}")
    if not ok:
        all_ok = False
    print()

    # 6. Timeout/max_trials
    max_trials = runs_cfg.get("max_trials")
    timeout_seconds = optuna_cfg.get("timeout_seconds")
    ok, msg = check_timeout_config(max_trials, timeout_seconds)
    print(f"6. Timeout/max_trials: {msg}")
    print()

    # 7. Parametrar
    ok, msg = check_parameters_valid(parameters)
    print(f"7. Parametrar: {msg}")
    if not ok:
        all_ok = False
    print()

    # 8. Snapshot & Data
    snapshot_id = meta.get("snapshot_id")
    symbol = meta.get("symbol", "tBTCUSD")
    timeframe = meta.get("timeframe", "1h")
    ok, msg = check_snapshot_exists(snapshot_id, symbol, timeframe)
    print(f"8. Snapshot & Data: {msg}")
    if not ok:
        all_ok = False
    print()

    # 9. Datumkälla (runner-semantik)
    ok, msg = check_date_source(meta, runs_cfg)
    print(f"9. Datumkälla: {msg}")
    if not ok:
        all_ok = False
    print()

    # 10. Champion-validering
    print("10. Champion-validering:")
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

    # 11. Precompute-funktionalitet
    ok, msg = check_precompute_functionality(symbol, timeframe)
    print(f"11. Precompute: {msg}")
    if not ok:
        all_ok = False
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
