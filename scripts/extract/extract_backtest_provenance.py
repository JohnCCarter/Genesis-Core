"""Extract provenance details from a saved backtest artifact.

Why this exists
--------------
Backtest artifacts in `results/backtests/*.json` can be very large. This script extracts a small,
report-friendly provenance summary (period, execution mode, config source, runtime versions, etc.)
so audit reports can cite reproducible evidence without manual scrolling.

Usage
-----
python scripts/extract_backtest_provenance.py results/backtests/tBTCUSD_1h_20260112_142153.json
python scripts/extract_backtest_provenance.py --format md results/backtests/*.json

Notes
-----
- This script is intentionally read-only.
- It does not try to interpret performance; it only extracts provenance metadata.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _get(d: dict[str, Any], path: str, default: Any = None) -> Any:
    """Best-effort dotted-path lookup into nested dicts."""

    cur: Any = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def extract_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract a compact provenance summary from a backtest JSON payload."""

    backtest_info = payload.get("backtest_info") or {}
    execution_mode = backtest_info.get("execution_mode") or {}
    config_prov = payload.get("config_provenance") or {}

    # Prefer the top-level runtime fields if present (they are explicit), else fall back to config_provenance.
    runtime_version_used = payload.get("runtime_version")
    runtime_version_current = payload.get("runtime_version_current")

    if runtime_version_used is None:
        runtime_version_used = config_prov.get("runtime_version_used")
    if runtime_version_current is None:
        runtime_version_current = config_prov.get("runtime_version_current")

    out: dict[str, Any] = {
        "artifact": str(payload.get("backtest_path") or ""),
        "symbol": backtest_info.get("symbol"),
        "timeframe": backtest_info.get("timeframe"),
        "period": {
            "start_date": backtest_info.get("start_date"),
            "end_date": backtest_info.get("end_date"),
        },
        "execution_mode": {
            "fast_window": execution_mode.get("fast_window"),
            "env_precompute_features": execution_mode.get("env_precompute_features"),
            "precomputed_ready": execution_mode.get("precomputed_ready"),
            "mode_explicit": execution_mode.get("mode_explicit"),
            "env_htf_exits": execution_mode.get("env_htf_exits"),
        },
        "provenance": {
            "config_file": config_prov.get("config_file"),
            "runtime_version_used": runtime_version_used,
            "runtime_version_current": runtime_version_current,
            "has_merged_config": isinstance(payload.get("merged_config"), dict),
        },
        "build": {
            "git_hash": backtest_info.get("git_hash"),
            "seed": backtest_info.get("seed"),
            "timestamp": backtest_info.get("timestamp"),
        },
    }

    # Some artifacts store these fields under slightly different paths; include best-effort fallbacks.
    if out["symbol"] is None:
        out["symbol"] = _get(payload, "symbol")
    if out["timeframe"] is None:
        out["timeframe"] = _get(payload, "timeframe")

    return out


def _to_markdown_summary(path: Path, prov: dict[str, Any]) -> str:
    period = prov["period"]
    mode = prov["execution_mode"]
    p = prov["provenance"]
    b = prov["build"]

    lines = [
        f"- `{path.as_posix()}`",
        f"  - period: `{period.get('start_date')}` → `{period.get('end_date')}`",
        "  - execution_mode: "
        f"`fast_window={mode.get('fast_window')}`, "
        f"`env_precompute_features={json.dumps(mode.get('env_precompute_features'))}`, "
        f"`mode_explicit={json.dumps(mode.get('mode_explicit'))}`",
        "  - provenance:",
        f"    - `config_provenance.config_file`: `{p.get('config_file')}`",
        f"    - `runtime_version_used`: `{p.get('runtime_version_used')}`, "
        f"`runtime_version_current`: `{p.get('runtime_version_current')}`",
        f"    - `merged_config`: `{bool(p.get('has_merged_config'))}`",
        "  - build:",
        f"    - `git_hash`: `{b.get('git_hash')}`, `seed`: `{b.get('seed')}`, `timestamp`: `{b.get('timestamp')}`",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract provenance from backtest JSON artifacts")
    parser.add_argument("paths", nargs="+", help="Path(s) to results/backtests/*.json")
    parser.add_argument(
        "--format",
        choices=["json", "md"],
        default="md",
        help="Output format (default: md)",
    )

    args = parser.parse_args()

    paths = [Path(p) for p in args.paths]

    all_out: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        prov = extract_provenance(payload)
        prov["artifact"] = str(path)
        all_out.append(prov)

    if args.format == "json":
        print(json.dumps(all_out, indent=2, sort_keys=True))
        return 0

    # markdown
    for prov in all_out:
        print(_to_markdown_summary(Path(prov["artifact"]), prov))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
