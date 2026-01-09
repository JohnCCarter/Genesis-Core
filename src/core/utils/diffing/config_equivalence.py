from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canonical import canonicalize_config, fingerprint_config


@dataclass(slots=True)
class ConfigDiffItem:
    path: str
    trial: Any
    results: Any


def _format_path(parts: tuple[str, ...]) -> str:
    return ".".join(parts)


def _deep_diff(a: Any, b: Any, *, path: tuple[str, ...] = (), out: list[ConfigDiffItem]) -> None:
    if type(a) is not type(b):
        out.append(ConfigDiffItem(path=_format_path(path), trial=a, results=b))
        return

    if isinstance(a, dict):
        keys = set(a.keys()) | set(b.keys())
        for key in sorted(keys):
            if key not in a:
                out.append(
                    ConfigDiffItem(
                        path=_format_path(path + (key,)),
                        trial=None,
                        results=b[key],
                    )
                )
            elif key not in b:
                out.append(
                    ConfigDiffItem(
                        path=_format_path(path + (key,)),
                        trial=a[key],
                        results=None,
                    )
                )
            else:
                _deep_diff(a[key], b[key], path=path + (key,), out=out)
        return

    if isinstance(a, list):
        max_len = max(len(a), len(b))
        for idx in range(max_len):
            key = str(idx)
            if idx >= len(a):
                out.append(
                    ConfigDiffItem(
                        path=_format_path(path + (key,)),
                        trial=None,
                        results=b[idx],
                    )
                )
            elif idx >= len(b):
                out.append(
                    ConfigDiffItem(
                        path=_format_path(path + (key,)),
                        trial=a[idx],
                        results=None,
                    )
                )
            else:
                _deep_diff(a[idx], b[idx], path=path + (key,), out=out)
        return

    if a != b:
        out.append(ConfigDiffItem(path=_format_path(path), trial=a, results=b))


def _extract_effective_config(payload: dict[str, Any]) -> dict[str, Any] | None:
    merged = payload.get("merged_config")
    if isinstance(merged, dict):
        return merged

    cfg = payload.get("cfg")
    if isinstance(cfg, dict):
        return cfg

    return None


def compare_trial_config_to_results(
    trial_config_payload: dict[str, Any],
    backtest_results_payload: dict[str, Any],
    *,
    precision: int = 6,
    max_diffs: int = 50,
) -> tuple[bool, dict[str, Any]]:
    """Compare effective config between a trial config file and a backtest result JSON.

    This is intended as a drift detector: if optimizer trial configs (written as complete configs)
    do not match the effective config recorded in backtest results, something is wrong.

    Returns:
        (ok, report)
    """

    issues: list[str] = []

    trial_effective = _extract_effective_config(trial_config_payload)
    results_effective = _extract_effective_config(backtest_results_payload)

    if trial_effective is None:
        return False, {
            "ok": False,
            "issues": ["Trial config saknar merged_config/cfg."],
            "diffs": [],
        }

    if results_effective is None:
        return False, {
            "ok": False,
            "issues": ["Backtest-resultat saknar merged_config."],
            "diffs": [],
        }

    # Runtime version consistency (best-effort; older results may not have this)
    trial_runtime_version = trial_config_payload.get("runtime_version")
    results_runtime_version = backtest_results_payload.get("runtime_version")
    if trial_runtime_version is not None and results_runtime_version is not None:
        if int(trial_runtime_version) != int(results_runtime_version):
            issues.append(
                f"runtime_version mismatch: trial={trial_runtime_version} results={results_runtime_version}"
            )

    # Provenance expectations when trial config is "complete" (has merged_config)
    if isinstance(trial_config_payload.get("merged_config"), dict):
        provenance = backtest_results_payload.get("config_provenance") or {}
        used_runtime_merge = provenance.get("used_runtime_merge")
        if used_runtime_merge is not None and used_runtime_merge is not False:
            issues.append(
                "config_provenance.used_runtime_merge är inte False trots att trial_config har merged_config"
            )

        config_file_is_complete = provenance.get("config_file_is_complete")
        if config_file_is_complete is not None and config_file_is_complete is not True:
            issues.append(
                "config_provenance.config_file_is_complete är inte True trots att trial_config har merged_config"
            )

    canon_trial = canonicalize_config(trial_effective, precision=precision)
    canon_results = canonicalize_config(results_effective, precision=precision)

    if canon_trial != canon_results:
        issues.append("merged_config mismatch")

    diffs: list[ConfigDiffItem] = []
    if canon_trial != canon_results:
        _deep_diff(canon_trial, canon_results, path=(), out=diffs)

    report = {
        "ok": len(issues) == 0,
        "issues": issues,
        "fingerprints": {
            "trial": fingerprint_config(trial_effective, precision=precision),
            "results": fingerprint_config(results_effective, precision=precision),
        },
        "diffs": [
            {"path": d.path, "trial": d.trial, "results": d.results} for d in diffs[:max_diffs]
        ],
        "diffs_truncated": len(diffs) > max_diffs,
    }

    return report["ok"], report
