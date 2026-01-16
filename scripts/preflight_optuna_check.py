#!/usr/bin/env python3
"""Preflight-kontroll för Optuna-körningar - säkerställer att allt är korrekt innan start."""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def maybe_load_dotenv() -> tuple[bool, str]:
    """Ladda .env om den finns, utan att skriva över redan satta env vars.

    Preflight körs ofta i ett "rent" skal där användaren förväntar sig att .env ska gälla.
    För att spegla faktiska körningar (pipeline laddar också .env) försöker vi läsa den här.
    """

    dotenv_path = ROOT / ".env"
    if not dotenv_path.exists():
        return True, "[SKIP] .env saknas"

    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return (
            True,
            "[WARN] .env finns men python-dotenv saknas; preflight kan missa GENESIS_* variabler",
        )

    try:
        load_dotenv(dotenv_path=dotenv_path, override=False)
    except Exception as e:
        return False, f"[FAIL] Kunde inte ladda .env ({dotenv_path}): {e}"
    return True, f"[OK] Laddade .env ({dotenv_path})"


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


def check_timeout_config(max_trials: Any, timeout_seconds: Any, end_at: Any) -> tuple[bool, str]:
    """Kontrollera timeout, max_trials och ev. absolut stopptid (end_at)."""

    issues: list[str] = []

    def _parse_end_at(value: Any) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            dt = value
        else:
            s = str(value).strip()
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
        return dt

    try:
        end_at_dt = _parse_end_at(end_at)
    except Exception as e:
        return False, f"[FAIL] end_at kunde inte parsas: {e}"

    effective_timeout_seconds: float | None = None

    if timeout_seconds is not None:
        timeout_seconds_f = float(timeout_seconds)
        issues.append(
            f"[OK] timeout_seconds={int(timeout_seconds_f)}s ({timeout_seconds_f/3600:.1f}h)"
        )
        effective_timeout_seconds = timeout_seconds_f
    else:
        if end_at_dt is None:
            issues.append("[WARN] timeout_seconds är inte satt")
        else:
            issues.append("[OK] timeout_seconds ej satt (styr via end_at)")

    if end_at_dt is not None:
        now = datetime.now(tz=end_at_dt.tzinfo)
        remaining = (end_at_dt - now).total_seconds()
        if remaining <= 0:
            return False, f"[FAIL] end_at={end_at_dt.isoformat()} ligger i dåtiden"
        issues.append(
            f"[OK] end_at={end_at_dt.isoformat()} (återstår {remaining/3600:.2f}h från nu)"
        )
        effective_timeout_seconds = (
            remaining
            if effective_timeout_seconds is None
            else min(effective_timeout_seconds, remaining)
        )

    if effective_timeout_seconds is None:
        issues.append(
            "[WARN] Ingen effektiv time budget (timeout_seconds/end_at) - Optuna kan köra oändligt"
        )

    if max_trials is None:
        issues.append("[OK] max_trials=null - kör tills timeout/end_at")
    else:
        max_trials_int = int(max_trials)
        if max_trials_int > 0:
            est_hours = (max_trials_int * 170) / 3600  # ~170s per trial
            timeout_str = (
                "aldrig"
                if effective_timeout_seconds is None
                else f"{effective_timeout_seconds/3600:.1f}h"
            )
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


def check_mode_flags_consistency() -> tuple[bool, str]:
    """Validera canonical mode-flaggor så körningen inte kraschar eller blir icke-deterministisk."""

    explicit_mode = os.environ.get("GENESIS_MODE_EXPLICIT") == "1"
    fast_window = os.environ.get("GENESIS_FAST_WINDOW") == "1"
    precompute = os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1"

    fast_hash_raw = os.environ.get("GENESIS_FAST_HASH")
    fast_hash_enabled = False
    if fast_hash_raw is not None:
        fast_hash_enabled = str(fast_hash_raw).strip().lower() in {"1", "true", "yes", "on"}

    fast_hash_strict = os.environ.get("GENESIS_PREFLIGHT_FAST_HASH_STRICT") == "1"

    if explicit_mode:
        # Explicit mode används som debug-escape hatch. Vi informerar men blockerar inte.
        msg = "[WARN] GENESIS_MODE_EXPLICIT=1 (debug) – säkerställ att du vet varför"
        if fast_hash_enabled:
            msg += " | [WARN] GENESIS_FAST_HASH=1 (debug/perf) – kan ändra utfall, undvik för jämförbara runs"
        return True, msg

    if fast_window and not precompute:
        return (
            False,
            "[FAIL] GENESIS_FAST_WINDOW=1 kräver GENESIS_PRECOMPUTE_FEATURES=1 (annars kraschar engine)",
        )

    if precompute and not fast_window:
        return (
            True,
            "[WARN] GENESIS_PRECOMPUTE_FEATURES=1 men GENESIS_FAST_WINDOW!=1 – mixed-mode kan ge oväntat beteende",
        )

    if fast_hash_enabled:
        # FAST_HASH har empiriskt visat sig kunna påverka utfall. Canonical runs ska därför inte använda den.
        msg = "[FAIL]" if fast_hash_strict else "[WARN]"
        msg += (
            " GENESIS_FAST_HASH=1 i canonical mode – kan ge icke-jämförbara resultat (debug/perf knob). "
            "Sätt GENESIS_FAST_HASH=0 eller kör explicit mode om du verkligen vill."
        )
        return (False, msg) if fast_hash_strict else (True, msg)

    return (
        True,
        f"[OK] Mode flags: fast_window={int(fast_window)}, precompute={int(precompute)}, fast_hash={int(fast_hash_enabled)}",
    )


def check_storage_resume_sanity(
    storage: Any, allow_resume: Any, n_jobs: Any, max_concurrent: Any
) -> tuple[bool, str]:
    """Extra sanity för run-konfiguration som annars ger tysta/överraskande resultat."""

    msgs: list[str] = []
    ok = True

    allow_resume_bool = bool(allow_resume)
    if storage in (None, "") and allow_resume_bool:
        msgs.append(
            "[WARN] resume=true men storage=null – inga trials persistieras (inget att resume:a)"
        )
    elif storage in (None, "") and not allow_resume_bool:
        msgs.append("[OK] storage=null + resume=false (in-memory/engångskörning)")

    try:
        if n_jobs is not None and max_concurrent is not None:
            if int(n_jobs) != int(max_concurrent):
                msgs.append(
                    f"[WARN] optuna.n_jobs={n_jobs} matchar inte meta.runs.max_concurrent={max_concurrent} – "
                    "risk för förvirring kring parallellism"
                )
    except Exception:
        pass

    if not msgs:
        msgs.append("[OK] Storage/resume sanity OK")
    return ok, " | ".join(msgs)


def check_htf_requirements(meta: dict[str, Any], parameters: dict[str, Any]) -> tuple[bool, str]:
    """Faila tidigt om HTF-exits efterfrågas men nödvändiga 1D candles saknas."""

    symbol = meta.get("symbol", "tBTCUSD")
    htf_spec = parameters.get("htf_exit_config")
    wants_htf = isinstance(htf_spec, dict) and len(htf_spec) > 0
    if not wants_htf:
        return True, "[SKIP] Ingen htf_exit_config i parameters"

    htf_data = _pick_data_file(symbol, "1D")
    if htf_data is None:
        return (
            False,
            f"[FAIL] htf_exit_config kräver 1D candles men ingen datafil hittades för {symbol} 1D",
        )

    env_htf = os.environ.get("GENESIS_HTF_EXITS")
    if env_htf != "1":
        return (
            True,
            f"[WARN] htf_exit_config finns och 1D-data hittades ({htf_data.name}) men GENESIS_HTF_EXITS!=1. "
            "Optimizer-runnern kan auto-enabla per trial, men manuella backtests behöver env/.env.",
        )

    return True, f"[OK] HTF: GENESIS_HTF_EXITS=1 och 1D-data finns ({htf_data.name})"


def _parse_snapshot_date_range(snapshot_id: str) -> tuple[datetime, datetime] | None:
    """Parse (start, end) från snapshot_id av typen ..._<YYYY-MM-DD>_<YYYY-MM-DD>_vX.

    Returns:
        (start_dt, end_dt) med tider 00:00:00, eller None om parsing misslyckas.
    """

    if not snapshot_id or not isinstance(snapshot_id, str):
        return None

    parts = snapshot_id.split("_")
    if len(parts) < 4:
        return None

    start_raw = parts[-3]
    end_raw = parts[-2]
    try:
        start_dt = datetime.fromisoformat(str(start_raw).strip())
        end_dt = datetime.fromisoformat(str(end_raw).strip())
    except Exception:
        return None

    if end_dt < start_dt:
        return None

    return start_dt, end_dt


def _champion_path(symbol: str, timeframe: str) -> Path:
    return ROOT / "config" / "strategy" / "champions" / f"{symbol}_{timeframe}.json"


def check_champion_drift_smoke(symbol: str, timeframe: str) -> tuple[bool, str]:
    """Snabb drift-check: verifiera att nuvarande champion fortfarande gör trades.

    Bakgrund:
        När schema/defaults eller decision-semantik ändras kan äldre champions bli 'no-trade'
        utan att validering (Pydantic) failar. Denna check fångar det tidigt.

    Policy:
        - Default: WARN om 0 trades (för att undvika falska negativa på korta fönster).
        - Om GENESIS_PREFLIGHT_CHAMPION_SMOKE_STRICT=1: FAIL på 0 trades.
        - Om GENESIS_PREFLIGHT_CHAMPION_SMOKE=0: SKIP.
    """

    if os.environ.get("GENESIS_PREFLIGHT_CHAMPION_SMOKE", "1") == "0":
        return True, "[SKIP] Champion drift smoke disabled (GENESIS_PREFLIGHT_CHAMPION_SMOKE=0)"

    strict = os.environ.get("GENESIS_PREFLIGHT_CHAMPION_SMOKE_STRICT") == "1"
    days_raw = os.environ.get("GENESIS_PREFLIGHT_CHAMPION_SMOKE_DAYS", "60")
    try:
        days = max(7, int(days_raw))
    except ValueError:
        days = 60

    champion_file = _champion_path(symbol, timeframe)
    if not champion_file.exists():
        return True, f"[WARN] Ingen champion-fil hittades: {champion_file}"

    try:
        import json

        champion = json.loads(champion_file.read_text(encoding="utf-8"))
    except Exception as e:
        return (False, f"[FAIL] Kunde inte läsa champion-fil ({champion_file.name}): {e}")

    snapshot_id = champion.get("snapshot_id")
    dr = _parse_snapshot_date_range(snapshot_id) if isinstance(snapshot_id, str) else None
    if dr is None:
        return True, f"[WARN] Champion saknar/har ogiltig snapshot_id: {snapshot_id}"
    snap_start, snap_end = dr

    start_dt = snap_start
    end_dt = min(snap_end, snap_start + timedelta(days=days))

    merged_cfg = champion.get("merged_config") or champion.get("cfg")
    if not isinstance(merged_cfg, dict):
        return False, "[FAIL] Champion saknar merged_config/cfg (kan inte smoke-testa)"

    prev_env = {
        "GENESIS_FAST_WINDOW": os.environ.get("GENESIS_FAST_WINDOW"),
        "GENESIS_PRECOMPUTE_FEATURES": os.environ.get("GENESIS_PRECOMPUTE_FEATURES"),
        "GENESIS_MODE_EXPLICIT": os.environ.get("GENESIS_MODE_EXPLICIT"),
        "GENESIS_HTF_EXITS": os.environ.get("GENESIS_HTF_EXITS"),
    }

    try:
        # Smoke-test ska spegla canonical 1/1.
        os.environ["GENESIS_FAST_WINDOW"] = "1"
        os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
        os.environ["GENESIS_MODE_EXPLICIT"] = "0"

        # Mimic runner: om htf_exit_config finns ska HTF vara på.
        if isinstance(merged_cfg.get("htf_exit_config"), dict) and merged_cfg.get(
            "htf_exit_config"
        ):
            os.environ["GENESIS_HTF_EXITS"] = "1"

        from core.backtest.metrics import calculate_metrics
        from core.pipeline import GenesisPipeline

        pipe = GenesisPipeline()
        pipe.setup_environment(seed=int(os.environ.get("GENESIS_RANDOM_SEED", "42")))

        # Warmup: använd championens warmup om satt, annars 150 (canonical i våra runs).
        warmup = merged_cfg.get("warmup_bars")
        try:
            warmup_bars = 150 if warmup is None else int(warmup)
        except Exception:
            warmup_bars = 150

        engine = pipe.create_engine(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_dt.date().isoformat(),
            end_date=end_dt.date().isoformat(),
            capital=10000.0,
            commission=0.002,
            slippage=0.0005,
            warmup_bars=warmup_bars,
        )
        if not engine.load_data():
            return False, f"[FAIL] Champion smoke: kunde inte ladda data för {symbol} {timeframe}"

        results = engine.run(
            policy={"symbol": symbol, "timeframe": timeframe},
            configs=merged_cfg,
            verbose=False,
            pruning_callback=None,
        )
        if "error" in results:
            return False, f"[FAIL] Champion smoke: backtest error: {results.get('error')}"

        metrics = calculate_metrics(results, prefer_summary=False)
        trades = int(metrics.get("total_trades") or 0)

        if trades == 0:
            msg = (
                f"[WARN] Champion drift smoke: 0 trades i {days}d fönster "
                f"({start_dt.date()}..{end_dt.date()}). "
                "Indikerar möjlig drift/regression eller för strikt konfig."
            )
            if strict:
                return False, msg.replace("[WARN]", "[FAIL]")
            return True, msg

        return True, (
            f"[OK] Champion drift smoke: {trades} trades i {days}d fönster "
            f"({start_dt.date()}..{end_dt.date()})"
        )
    except Exception as e:
        return (False if strict else True, f"[WARN] Champion drift smoke: kunde inte köras: {e}")
    finally:
        for k, v in prev_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


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

        from core.backtest.engine import BacktestEngine

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
        # Check for section key OR dot notation (e.g. "thresholds.entry_conf")
        has_section = section in parameters or any(
            k.startswith(f"{section}.") for k in parameters.keys()
        )
        if not has_section:
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
    data_file_frozen = base_dir / "raw" / f"{symbol}_{timeframe}_frozen.parquet"
    data_file_curated = base_dir / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet"
    data_file_legacy = base_dir / "candles" / f"{symbol}_{timeframe}.parquet"

    if data_file_frozen.exists():
        try:
            import pandas as pd

            df = pd.read_parquet(data_file_frozen, columns=["timestamp"])
            if len(df) == 0:
                return False, f"[FAIL] Datafil är tom: {data_file_frozen}"
            n_rows = len(df)
            return (
                True,
                f"[OK] snapshot_id: {snapshot_id} | Datafil: {data_file_frozen} ({n_rows:,} rader)",
            )
        except Exception as e:
            return False, f"[FAIL] Kan inte läsa datafil {data_file_frozen}: {e}"
    if data_file_curated.exists():
        try:
            import pandas as pd

            df = pd.read_parquet(data_file_curated, columns=["timestamp"])
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

            df = pd.read_parquet(data_file_legacy, columns=["timestamp"])
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
            f"[FAIL] Datafil saknas för {symbol} {timeframe}:\n  Försökte: {data_file_frozen}\n  Försökte: {data_file_curated}\n  Försökte: {data_file_legacy}",
        )


def _is_truthy(value: Any) -> bool:
    if value is True:
        return True
    if value is False or value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return False


def _pick_data_file(symbol: str, timeframe: str) -> Path | None:
    base_dir = ROOT / "data"
    candidates = [
        base_dir / "raw" / f"{symbol}_{timeframe}_frozen.parquet",
        base_dir / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet",
        base_dir / "candles" / f"{symbol}_{timeframe}.parquet",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _get_time_range_from_parquet(path: Path) -> tuple[datetime, datetime] | None:
    """Returnera (min_ts, max_ts) för en candle-parquet via timestamp-kolumnen."""
    try:
        import pandas as pd

        df = pd.read_parquet(path, columns=["timestamp"], engine="pyarrow", memory_map=True)
    except Exception:
        try:
            import pandas as pd

            df = pd.read_parquet(path, columns=["timestamp"])
        except Exception:
            return None

    if df is None or len(df) == 0 or "timestamp" not in df.columns:
        return None

    ts = df["timestamp"]
    min_ts = ts.min()
    max_ts = ts.max()
    if pd.isna(min_ts) or pd.isna(max_ts):
        return None
    # Säkerställ python-datetime
    return (pd.Timestamp(min_ts).to_pydatetime(), pd.Timestamp(max_ts).to_pydatetime())


def check_requested_data_coverage(
    meta: dict[str, Any], runs_cfg: dict[str, Any]
) -> tuple[bool, str]:
    """Faila tidigt om önskat datumintervall inte täcks av tillgänglig candle-data."""
    symbol = meta.get("symbol", "tBTCUSD")
    timeframe = meta.get("timeframe", "1h")

    use_sample_range = _is_truthy(runs_cfg.get("use_sample_range"))

    start_raw: Any | None = None
    end_raw: Any | None = None
    source = ""

    if use_sample_range:
        start_raw = runs_cfg.get("sample_start")
        end_raw = runs_cfg.get("sample_end")
        source = "sample_range"
    else:
        snap = meta.get("snapshot_id")
        if isinstance(snap, str) and snap.strip():
            parts = snap.split("_")
            if len(parts) >= 4:
                start_raw = parts[-3]
                end_raw = parts[-2]
                source = "snapshot_id"

    if not start_raw or not end_raw:
        return (
            True,
            "[SKIP] Ingen datumintervall att täckningsvalidera (saknar sample_start/end eller snapshot_id)",
        )

    try:
        req_start = datetime.fromisoformat(str(start_raw).strip())
        req_end = datetime.fromisoformat(str(end_raw).strip())
    except Exception as e:
        return (
            False,
            f"[FAIL] Kunde inte tolka datumintervall ({source}): {start_raw} / {end_raw}: {e}",
        )

    if req_end < req_start:
        return (
            False,
            f"[FAIL] Ogiltigt datumintervall: start={req_start.date()} > end={req_end.date()}",
        )

    data_file = _pick_data_file(symbol, timeframe)
    if data_file is None:
        return False, f"[FAIL] Ingen datafil hittades för {symbol} {timeframe}"

    tr = _get_time_range_from_parquet(data_file)
    if tr is None:
        return False, f"[FAIL] Kunde inte läsa timestamp-range från {data_file}"

    data_start, data_end = tr

    if req_start > data_end or req_end < data_start:
        return (
            False,
            f"[FAIL] Datumintervall ({req_start.date()}..{req_end.date()}) ligger utanför data-range "
            f"({data_start.date()}..{data_end.date()}) i {data_file.name}",
        )

    if req_start < data_start or req_end > data_end:
        return (
            False,
            f"[FAIL] Data täcker inte hela intervallet ({req_start.date()}..{req_end.date()}). "
            f"Tillgängligt: {data_start.date()}..{data_end.date()} i {data_file.name}",
        )

    return (
        True,
        f"[OK] Data coverage: {req_start.date()}..{req_end.date()} inom {data_start.date()}..{data_end.date()} "
        f"({data_file.name})",
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
    if _is_truthy(runs_usr):
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

                # Informativt: snapshot_id används ofta bara som metadata när sample_range används.
                # Om snapshot_id ändå är satt men inte matchar sample_start/end är det lätt att bli förvirrad.
                snap = meta.get("snapshot_id")
                if isinstance(snap, str) and snap.strip():
                    parts = snap.split("_")
                    if len(parts) >= 4:
                        snap_start = parts[-3]
                        snap_end = parts[-2]
                        if str(snap_start) != str(start_raw) or str(snap_end) != str(end_raw):
                            issues.append(
                                "[WARN] meta.snapshot_id-datum matchar inte sample_range. "
                                f"snapshot_id={snap_start}->{snap_end}, sample_range={start_raw}->{end_raw}. "
                                "(Runnern använder sample_range när use_sample_range=true.)"
                            )
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

    # 0. .env (för att preflight ska spegla faktiska körningar)
    ok, msg = maybe_load_dotenv()
    print(f"0. Environment: {msg}")
    if not ok:
        all_ok = False
    print()

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
    end_at = optuna_cfg.get("end_at")
    ok, msg = check_timeout_config(max_trials, timeout_seconds, end_at)
    print(f"6. Timeout/max_trials: {msg}")
    if not ok:
        all_ok = False
    print()

    # 6b. Mode flags (canonical mode)
    ok, msg = check_mode_flags_consistency()
    print(f"6b. Mode flags: {msg}")
    if not ok:
        all_ok = False
    print()

    # 6c. Storage/resume/n_jobs sanity
    ok, msg = check_storage_resume_sanity(
        optuna_cfg.get("storage"),
        runs_cfg.get("resume", True),
        optuna_cfg.get("n_jobs"),
        runs_cfg.get("max_concurrent"),
    )
    print(f"6c. Storage/resume sanity: {msg}")
    if not ok:
        all_ok = False
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

    # 8b. HTF requirements (om HTF-exits efterfrågas av config)
    ok, msg = check_htf_requirements(meta, parameters)
    print(f"8b. HTF requirements: {msg}")
    if not ok:
        all_ok = False
    print()

    # 9. Datumkälla (runner-semantik)
    ok, msg = check_date_source(meta, runs_cfg)
    print(f"9. Datumkälla: {msg}")
    if not ok:
        all_ok = False
    print()

    # 10. Data coverage (matchar runnerns faktiska date-source + lokala candle-filer)
    ok, msg = check_requested_data_coverage(meta, runs_cfg)
    print(f"10. Data coverage: {msg}")
    if not ok:
        all_ok = False
    print()

    # 11. Champion-validering
    print("11. Champion-validering:")
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

    # 11b. Champion drift smoke (fångar no-trade regressioner)
    ok, msg = check_champion_drift_smoke(symbol, timeframe)
    print(f"11b. Champion drift smoke: {msg}")
    if not ok:
        all_ok = False
    print()

    # 12. Precompute-funktionalitet
    ok, msg = check_precompute_functionality(symbol, timeframe)
    print(f"12. Precompute: {msg}")
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
