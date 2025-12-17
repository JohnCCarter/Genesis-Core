#!/usr/bin/env python3
"""
Run backtest on historical data.

Usage:
    python scripts/run_backtest.py --symbol tBTCUSD --timeframe 15m
    python scripts/run_backtest.py --symbol tETHUSD --timeframe 1h --capital 20000
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover - numpy optional in some envs
    np = None

try:  # pragma: no cover - torch optional
    import torch
except ImportError:
    torch = None

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Ensure config package resolvable
CONFIG_DIR = ROOT_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)
(CONFIG_DIR / "__init__.py").touch(exist_ok=True)

from core.backtest.metrics import calculate_metrics, print_metrics_report  # noqa: E402
from core.backtest.trade_logger import TradeLogger  # noqa: E402
from core.config.authority import ConfigAuthority  # noqa: E402
from core.optimizer.scoring import score_backtest  # noqa: E402
from core.pipeline import GenesisPipeline  # noqa: E402
from core.utils.diffing import diff_metrics, summarize_metric_deltas  # noqa: E402


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _summarize_runtime(label: str, cfg: dict) -> None:
    thresholds = cfg.get("thresholds", {})
    entry_conf = thresholds.get("entry_conf_overall")
    adaptation = (thresholds.get("signal_adaptation") or {}).get("zones") or {}
    zones = {
        name: (zone or {}).get("entry_conf_overall")
        for name, zone in adaptation.items()
        if isinstance(zone, dict)
    }
    mtf = cfg.get("multi_timeframe", {})
    allow_override = mtf.get("allow_ltf_override")
    override_thr = mtf.get("ltf_override_threshold")
    print(
        f"[CONFIG:{label}] entry_conf={entry_conf} "
        f"zones(low/mid/high)={zones.get('low')}/{zones.get('mid')}/{zones.get('high')} "
        f"allow_ltf_override={allow_override} override_thr={override_thr}"
    )


def main():
    """CLI entry point."""
    pipeline = GenesisPipeline()
    defaults = pipeline.defaults

    parser = argparse.ArgumentParser(description="Run backtest on historical data")
    parser.add_argument("--symbol", type=str, required=True, help="Trading symbol (e.g., tBTCUSD)")
    parser.add_argument(
        "--timeframe",
        type=str,
        required=True,
        help="Candle timeframe (e.g., 15m, 1h)",
    )
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)", default=None)
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)", default=None)
    parser.add_argument(
        "--capital",
        type=float,
        default=defaults.get("capital", 10000.0),
        help=f"Initial capital (default: {defaults.get('capital', 10000.0)})",
    )
    parser.add_argument(
        "--commission",
        type=float,
        default=defaults.get("commission", 0.002),
        help=f"Commission rate (default: {defaults.get('commission', 0.002)} = {defaults.get('commission', 0.002)*100:.1f}%%)",
    )
    parser.add_argument(
        "--slippage",
        type=float,
        default=defaults.get("slippage", 0.0005),
        help=f"Slippage rate (default: {defaults.get('slippage', 0.0005)} = {defaults.get('slippage', 0.0005)*100:.2f}%%)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=defaults.get("warmup", 120),
        help=f"Warmup bars for indicators (default: {defaults.get('warmup', 120)})",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print trade details")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to files")
    parser.add_argument(
        "--config-file",
        type=Path,
        help="Optional JSON-fil med override av runtime-config",
    )
    parser.add_argument(
        "--fast-window",
        action="store_true",
        help="Use precomputed column arrays for faster window building",
    )
    parser.add_argument(
        "--precompute-features",
        action="store_true",
        help="Precompute common features (ATR/EMA) for performance",
    )
    parser.add_argument(
        "--compare",
        type=Path,
        help="Path to baseline backtest JSON to compare against",
    )
    parser.add_argument("--optuna-trial-id", type=int, help="Optuna trial ID for pruning")
    parser.add_argument("--optuna-storage", type=str, help="Optuna storage URL")
    parser.add_argument("--optuna-study-name", type=str, help="Optuna study name")

    args = parser.parse_args()

    print("=" * 70)
    print("Genesis-Core Backtest Runner")
    print("=" * 70)

    try:
        seed_value = int(os.environ.get("GENESIS_RANDOM_SEED", "42"))
    except ValueError:
        seed_value = 42

    # Setup environment via pipeline
    pipeline.setup_environment(seed=seed_value)

    try:
        # Initialize engine via pipeline
        engine = pipeline.create_engine(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=args.start,
            end_date=args.end,
            capital=args.capital,
            commission=args.commission,
            slippage=args.slippage,
            warmup_bars=args.warmup,
        )

        # Load data
        if not engine.load_data():
            return 1

        # Load runtime config
        authority = ConfigAuthority()
        cfg_obj, _, runtime_version = authority.get()
        cfg = cfg_obj.model_dump()
        is_complete_champion = False
        config_provenance: dict[str, object] = {
            "used_runtime_merge": True,
            "runtime_version_current": runtime_version,
            "runtime_version_used": runtime_version,
            "config_file": str(args.config_file) if args.config_file else None,
            "config_file_is_complete": False,
        }

        if args.config_file:
            override_payload = json.loads(args.config_file.read_text(encoding="utf-8"))
            if not isinstance(override_payload, dict):
                raise ValueError("config-file must be a JSON object")

            # Backwards-compat: some files use 'parameters' instead of 'cfg'.
            override_cfg = override_payload.get("cfg")
            if override_cfg is None:
                override_cfg = override_payload.get("parameters")
            if not isinstance(override_cfg, dict):
                raise ValueError("config-file must contain a 'cfg' (or 'parameters') dictionary")

            # Check if this is a complete champion (has merged_config)
            merged_config_from_file = override_payload.get("merged_config")
            if merged_config_from_file is not None:
                # Complete champion - use merged_config directly, no runtime merge
                is_complete_champion = True
                print("[CONFIG:champion] Using complete champion config (no runtime merge)")
                champion_runtime_version = override_payload.get("runtime_version")
                config_provenance["used_runtime_merge"] = False
                config_provenance["config_file_is_complete"] = True
                if champion_runtime_version and champion_runtime_version != runtime_version:
                    print(
                        f"[CONFIG:champion] WARNING: Champion created with runtime v{champion_runtime_version}, "
                        f"current runtime is v{runtime_version}"
                    )
                if champion_runtime_version is not None:
                    try:
                        config_provenance["runtime_version_used"] = int(champion_runtime_version)
                    except (TypeError, ValueError):
                        # Keep current runtime_version_used as fallback
                        pass
                merged_cfg = merged_config_from_file
            else:
                # Regular test file - merge with runtime
                _summarize_runtime("runtime", cfg)
                merged_cfg = _deep_merge(cfg, override_cfg)

            try:
                cfg_obj = authority.validate(merged_cfg)
            except Exception as exc:  # ValidationError from Pydantic
                print(f"\n[FAILED] Ogiltig override-config: {exc}")
                return 1
            cfg = cfg_obj.model_dump()
            if not is_complete_champion:
                _summarize_runtime("runtime+override", cfg)
        else:
            _summarize_runtime("runtime", cfg)
            merged_cfg = cfg

        # Prepare policy
        policy = {"symbol": args.symbol, "timeframe": args.timeframe}

        # Setup Optuna pruning if requested
        pruning_callback = None
        if args.optuna_trial_id is not None and args.optuna_storage and args.optuna_study_name:
            try:
                import optuna

                # Suppress Optuna logging in subprocess
                optuna.logging.set_verbosity(optuna.logging.WARNING)

                study = optuna.load_study(
                    study_name=args.optuna_study_name,
                    storage=args.optuna_storage,
                )

                def _optuna_callback(step, value):
                    try:
                        trial = optuna.trial.Trial(study, args.optuna_trial_id)
                        trial.report(value, step)
                        if trial.should_prune():
                            return True
                    except Exception:
                        pass
                    return False

                pruning_callback = _optuna_callback
                print(f"[Optuna] Pruning enabled for trial {args.optuna_trial_id}")
            except ImportError:
                print("[WARN] Optuna not installed, pruning disabled")
            except Exception as e:
                print(f"[WARN] Failed to setup Optuna pruning: {e}")

        # Run backtest
        results = engine.run(
            policy=policy,
            configs=merged_cfg,
            verbose=args.verbose,
            pruning_callback=pruning_callback,
        )

        # Always attach config provenance & merged_config for reproducibility.
        # Note: even for "complete champion" inputs we still include merged_config in results so that
        # optimizer tooling (and humans) can inspect the effective config without chasing inputs.
        results["config_provenance"] = config_provenance
        results["merged_config"] = merged_cfg
        results["runtime_version"] = config_provenance.get("runtime_version_used", runtime_version)
        results["runtime_version_current"] = runtime_version

        if "error" in results:
            print(f"\n[ERROR] Backtest failed: {results['error']}")
            return 1

        # Calculate metrics
        metrics = calculate_metrics(results)

        # Calculate score (same as Optuna uses)
        score_result = score_backtest(results)
        score_value = score_result.get("score", 0.0)
        score_metrics = score_result.get("metrics", {})
        score_baseline = score_result.get("baseline", {}) if isinstance(score_result, dict) else {}
        score_version = None
        if isinstance(score_baseline, dict):
            score_version = score_baseline.get("score_version")

        # Add score to results for saving
        results["score"] = {
            "score": score_value,
            "metrics": score_metrics,
            "hard_failures": score_result.get("hard_failures", []),
            "score_version": score_version,
        }

        # Print report
        print_metrics_report(metrics, results.get("backtest_info"))
        print(f"\nScore: {score_value:.4f}")

        # Save results
        saved_files: dict[str, Path] | None = None
        if not args.no_save:
            logger = TradeLogger()
            saved_files = logger.save_all(results)
            print("\n[OK] Results saved:")
            for key, path in saved_files.items():
                print(f"  {key}: {path}")

        # Diff mot baseline om begärt
        if args.compare:
            comparison_path = args.compare
            if not comparison_path.exists():
                print(f"\n[WARN] Compare file saknas: {comparison_path}")
            else:
                try:
                    baseline = json.loads(comparison_path.read_text(encoding="utf-8"))
                    baseline_metrics = (
                        (baseline.get("summary") or {}).get("metrics")
                        or baseline.get("metrics")
                        or {}
                    )
                    result_metrics = (
                        (results.get("summary") or {}).get("metrics")
                        or results.get("metrics")
                        or {}
                    )
                    metrics_diff = diff_metrics(baseline_metrics, result_metrics)
                    trades_old = len(baseline.get("trades") or [])
                    trades_new = len(results.get("trades") or [])
                    print("\n[DIFF] Metrics delta:")
                    print(summarize_metric_deltas(metrics_diff) or "  (no differences)")
                    trade_delta = trades_new - trades_old
                    print(f"[DIFF] Trades: old={trades_old} new={trades_new} delta={trade_delta:+}")
                except json.JSONDecodeError as exc:
                    print(f"\n[WARN] Kunde inte läsa compare-fil ({comparison_path}): {exc}")

        print("\n[SUCCESS] Backtest complete!")
        return 0

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Backtest interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[FAILED] {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
