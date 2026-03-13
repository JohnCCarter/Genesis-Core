from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from core.utils.env_flags import env_flag_enabled
from core.utils.optuna_helpers import set_global_seeds

if TYPE_CHECKING:
    from core.optimizer.runner import TrialConfig


def _trial_requests_htf_exits(effective_cfg: dict[str, Any]) -> bool:
    """Return True if the trial config implies HTF exits should be enabled."""

    htf_exit_cfg = effective_cfg.get("htf_exit_config")
    return isinstance(htf_exit_cfg, dict) and bool(htf_exit_cfg)


def _run_backtest_direct(
    trial: TrialConfig,
    config_path: Path,
    optuna_context: dict[str, Any] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[int, str, dict[str, Any] | None]:
    did_set_htf_exits = False
    prior_htf_exits = os.environ.get("GENESIS_HTF_EXITS")

    try:
        from core.optimizer import runner as runner_module
        from core.pipeline import GenesisPipeline

        pipeline = GenesisPipeline()
        os.environ["GENESIS_MODE_EXPLICIT"] = "0"
        try:
            seed_value = int(os.environ.get("GENESIS_RANDOM_SEED", "42"))
        except ValueError:
            seed_value = 42

        setup_env = getattr(pipeline, "setup_environment", None)
        if callable(setup_env):
            setup_env(seed=seed_value)
        else:  # pragma: no cover
            set_global_seeds(seed_value)

        payload = json.loads(config_path.read_text(encoding="utf-8"))
        cfg = payload["cfg"]
        effective_cfg = payload.get("merged_config")
        if not isinstance(effective_cfg, dict):
            effective_cfg = cfg

        if _trial_requests_htf_exits(effective_cfg) and "GENESIS_HTF_EXITS" not in os.environ:
            os.environ["GENESIS_HTF_EXITS"] = "1"
            did_set_htf_exits = True
        runtime_version_used = payload.get("runtime_version")
        runtime_version_current = runner_module._get_default_runtime_version()
        config_provenance: dict[str, object] = {
            "used_runtime_merge": False,
            "runtime_version_current": runtime_version_current,
            "runtime_version_used": runtime_version_used,
            "config_file": str(config_path),
            "config_file_is_complete": isinstance(payload.get("merged_config"), dict),
        }
        overrides = payload.get("overrides", {})

        mode_sig = (
            f"fw{os.environ.get('GENESIS_FAST_WINDOW','')}"
            f"pc{os.environ.get('GENESIS_PRECOMPUTE_FEATURES','')}"
            f"htf{os.environ.get('GENESIS_HTF_EXITS','')}"
        )
        cache_key = (
            f"{trial.symbol}_{trial.timeframe}_{trial.start_date}_{trial.end_date}_{mode_sig}"
        )
        with runner_module._DATA_LOCK:
            if cache_key not in runner_module._DATA_CACHE:
                try:
                    engine_loader = pipeline.create_engine(
                        symbol=trial.symbol,
                        timeframe=trial.timeframe,
                        start_date=trial.start_date,
                        end_date=trial.end_date,
                        warmup_bars=trial.warmup_bars,
                        fast_window=True,
                    )
                except TypeError:
                    engine_loader = pipeline.create_engine(
                        symbol=trial.symbol,
                        timeframe=trial.timeframe,
                        start_date=trial.start_date,
                        end_date=trial.end_date,
                        warmup_bars=trial.warmup_bars,
                    )

                if env_flag_enabled(os.getenv("GENESIS_PRECOMPUTE_FEATURES"), default=False):
                    engine_loader.precompute_features = True
                if engine_loader.load_data():
                    if (
                        os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1"
                        and hasattr(engine_loader, "_precomputed_features")
                        and not getattr(engine_loader, "_precomputed_features", None)
                    ):
                        runner_module._DATA_CACHE[cache_key] = None
                    else:
                        runner_module._DATA_CACHE[cache_key] = engine_loader
                else:
                    runner_module._DATA_CACHE[cache_key] = None

            engine = runner_module._DATA_CACHE[cache_key]

        if engine is None:
            if os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1":
                return (1, "Failed to load data or precompute features in canonical mode", None)
            return 1, "Failed to load data", None

        engine.warmup_bars = trial.warmup_bars

        if "commission" in overrides:
            engine.position_tracker.commission_rate = float(overrides["commission"])
        if "slippage" in overrides:
            engine.position_tracker.slippage_rate = float(overrides["slippage"])

        pruning_callback = None
        if optuna_context:
            storage = optuna_context.get("storage")
            study_name = optuna_context.get("study_name")
            trial_id = optuna_context.get("trial_id")
            if storage and study_name and trial_id is not None:
                try:
                    import optuna

                    pruner_cfg = optuna_context.get("pruner")
                    if isinstance(pruner_cfg, dict):
                        pruner_obj = runner_module._select_optuna_pruner(
                            pruner_cfg.get("name"), pruner_cfg.get("kwargs")
                        )
                    elif isinstance(pruner_cfg, str):
                        pruner_obj = runner_module._select_optuna_pruner(pruner_cfg, None)
                    else:
                        pruner_obj = runner_module._select_optuna_pruner(None, None)

                    study = optuna.load_study(
                        study_name=str(study_name),
                        storage=storage,
                        pruner=pruner_obj,
                    )

                    def _cb(step, value):
                        try:
                            t = optuna.trial.Trial(study, int(trial_id))
                            t.report(value, step)
                            return t.should_prune()
                        except Exception:
                            return False

                    pruning_callback = _cb
                except KeyError as err:  # pragma: no cover
                    runner_module.logger.warning(
                        "Optuna pruning disabled (study not found): %s", err
                    )
                except Exception as err:  # pragma: no cover
                    runner_module.logger.warning(
                        "Optuna pruning disabled due to setup failure: %s",
                        err,
                        exc_info=True,
                    )
        effective_cfg_for_run: dict[str, Any] | Any = effective_cfg
        if isinstance(effective_cfg, dict):
            effective_cfg_for_run = dict(effective_cfg)
            meta_for_run = dict(effective_cfg.get("meta") or {})
            meta_for_run["skip_champion_merge"] = True
            effective_cfg_for_run["meta"] = meta_for_run

        results = engine.run(
            policy={"symbol": trial.symbol, "timeframe": trial.timeframe},
            configs=effective_cfg_for_run,
            verbose=False,
            pruning_callback=pruning_callback,
        )

        if isinstance(results, dict):
            results.setdefault("config_provenance", config_provenance)
            results.setdefault("merged_config", effective_cfg)
            if runtime_version_used is not None:
                results.setdefault("runtime_version", runtime_version_used)
            if runtime_version_current is not None:
                results.setdefault("runtime_version_current", runtime_version_current)

        return 0, "", results

    except Exception as e:
        import traceback

        return 1, f"{e}\n{traceback.format_exc()}", None

    finally:
        if did_set_htf_exits:
            if prior_htf_exits is None:
                os.environ.pop("GENESIS_HTF_EXITS", None)
            else:
                os.environ["GENESIS_HTF_EXITS"] = str(prior_htf_exits)


def _build_backtest_cmd(
    trial: TrialConfig,
    *,
    start_date: str,
    end_date: str,
    capital_default: float,
    commission_default: float,
    slippage_default: float,
    config_file: Path | None,
    optuna_context: dict[str, Any] | None,
) -> list[str]:
    """Build the subprocess command for running a backtest."""

    cmd = [
        sys.executable,
        "-m",
        "scripts.run.run_backtest",
        "--symbol",
        trial.symbol,
        "--timeframe",
        trial.timeframe,
        "--start",
        start_date,
        "--end",
        end_date,
        "--warmup",
        str(trial.warmup_bars),
        "--capital",
        str(capital_default),
        "--commission",
        str(commission_default),
        "--slippage",
        str(slippage_default),
        "--fast-window",
        "--precompute-features",
    ]

    if config_file is not None:
        cmd.extend(["--config-file", str(config_file)])

    if optuna_context:
        storage = optuna_context.get("storage")
        study_name = optuna_context.get("study_name")
        trial_id = optuna_context.get("trial_id")
        if storage and study_name and trial_id is not None:
            pruner_cfg = optuna_context.get("pruner")
            pruner_name: str | None = None
            pruner_kwargs: dict[str, Any] | None = None
            if isinstance(pruner_cfg, dict):
                pruner_name = (
                    pruner_cfg.get("name")
                    or pruner_cfg.get("type")
                    or pruner_cfg.get("pruner")
                    or pruner_cfg.get("kind")
                )
                if isinstance(pruner_cfg.get("kwargs"), dict):
                    pruner_kwargs = pruner_cfg.get("kwargs")
            elif isinstance(pruner_cfg, str):
                pruner_name = pruner_cfg

            cmd.extend(
                [
                    "--optuna-trial-id",
                    str(trial_id),
                    "--optuna-storage",
                    str(storage),
                    "--optuna-study-name",
                    str(study_name),
                ]
            )

            if pruner_name:
                cmd.extend(["--optuna-pruner", str(pruner_name)])
            if pruner_kwargs:
                cmd.extend(
                    [
                        "--optuna-pruner-kwargs",
                        json.dumps(pruner_kwargs, separators=(",", ":")),
                    ]
                )

    return cmd
