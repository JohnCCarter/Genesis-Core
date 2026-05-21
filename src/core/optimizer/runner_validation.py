from __future__ import annotations

from pathlib import Path
from typing import Any


def _parse_validation_top_n(validation_cfg: dict[str, Any]) -> int:
    try:
        top_n_raw = validation_cfg.get("top_n", 0)
        return int(top_n_raw) if top_n_raw is not None else 0
    except (TypeError, ValueError):
        return 0


def _select_validation_candidates(
    *,
    results: list[dict[str, Any]],
    top_n: int,
    strategy: str,
    optuna_strategy: str,
    run_meta: dict[str, Any],
    select_top_n_from_optuna_storage,
) -> list[dict[str, Any]]:
    ranked: list[tuple[float, dict[str, Any]]] = []
    for result in results:
        if result.get("error") or result.get("skipped"):
            continue
        score_block = result.get("score") or {}
        try:
            score_value = float(score_block.get("score"))
        except (TypeError, ValueError):
            continue
        ranked.append((score_value, result))

    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = [result for _score, result in ranked[:top_n]]
    if not selected and strategy == optuna_strategy:
        selected = select_top_n_from_optuna_storage(run_meta, top_n)
    return selected


def run_validation_stage_impl(
    *,
    validation_cfg: dict[str, Any] | None,
    results: list[dict[str, Any]],
    strategy: str,
    optuna_strategy: str,
    run_meta: dict[str, Any],
    run_meta_path: Path,
    run_dir: Path,
    run_id: str,
    allow_resume: bool,
    max_attempts: int,
    config_constraints: dict[str, Any] | None,
    snapshot_id: str,
    symbol: str,
    timeframe: str,
    warmup_bars: int,
    baseline_results: dict[str, Any] | None,
    baseline_label: str | None,
    as_bool,
    resolve_sample_range,
    select_top_n_from_optuna_storage,
    load_existing_trials,
    run_trial,
    trial_config_cls,
    write_serialized_run_meta,
) -> list[dict[str, Any]] | None:
    if not isinstance(validation_cfg, dict) or not as_bool(validation_cfg.get("enabled", True)):
        return None

    top_n = _parse_validation_top_n(validation_cfg)
    if top_n <= 0:
        return None

    selected = _select_validation_candidates(
        results=results,
        top_n=top_n,
        strategy=strategy,
        optuna_strategy=optuna_strategy,
        run_meta=run_meta,
        select_top_n_from_optuna_storage=select_top_n_from_optuna_storage,
    )
    if not selected:
        return None

    val_start: str | None = None
    val_end: str | None = None
    if as_bool(validation_cfg.get("use_sample_range")):
        val_start, val_end = resolve_sample_range(snapshot_id, validation_cfg)

    val_dir = (run_dir / "validation").resolve()
    val_dir.mkdir(parents=True, exist_ok=True)
    val_allow_resume = bool(validation_cfg.get("resume", allow_resume))
    val_existing_trials = {}
    if val_allow_resume and val_dir.exists():
        val_existing_trials = load_existing_trials(val_dir)

    val_constraints_cfg = validation_cfg.get("constraints")
    if val_constraints_cfg is None:
        val_constraints_cfg = config_constraints
    if not isinstance(val_constraints_cfg, dict):
        val_constraints_cfg = None

    validation_results: list[dict[str, Any]] = []
    for idx, base_result in enumerate(selected, start=1):
        params = dict(base_result.get("parameters") or {})
        trial_cfg = trial_config_cls(
            snapshot_id=snapshot_id,
            symbol=symbol,
            timeframe=timeframe,
            warmup_bars=warmup_bars,
            parameters=params,
            start_date=val_start,
            end_date=val_end,
        )
        payload = run_trial(
            trial_cfg,
            run_id=run_id,
            index=idx,
            run_dir=val_dir,
            allow_resume=val_allow_resume,
            existing_trials=val_existing_trials,
            max_attempts=max_attempts,
            constraints_cfg=val_constraints_cfg,
            cache_enabled=True,
            seen_param_keys=None,
            seen_param_lock=None,
            baseline_results=baseline_results,
            baseline_label=baseline_label,
            optuna_context=None,
        )
        if isinstance(payload, dict):
            payload.setdefault("stage", "validation")
        validation_results.append(payload)

    run_meta.setdefault("validation", {}).update(
        {
            "enabled": True,
            "top_n": top_n,
            "sample_start": val_start,
            "sample_end": val_end,
            "constraints": val_constraints_cfg,
            "validated": len(validation_results),
            "validation_dir": str(val_dir),
        }
    )
    write_serialized_run_meta(run_meta_path, run_meta)

    return validation_results
