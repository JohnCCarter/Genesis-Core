#!/usr/bin/env python3
"""
Apply a runtime configuration patch from a JSON file.

The input file may either contain the flattened structure expected by
ConfigAuthority (e.g. {"thresholds": {...}}) or be wrapped in {"cfg": {...}},
matching the tmp profiles under config/tmp/.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.config.authority import ConfigAuthority  # noqa: E402


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _diff_paths(a: object, b: object, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a) | set(b)
        for key in keys:
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            if key not in a or key not in b:
                paths.append(next_prefix)
            else:
                paths.extend(_diff_paths(a[key], b[key], next_prefix))
    elif isinstance(a, list) and isinstance(b, list):
        if a != b:
            paths.append(prefix or "(list)")
    else:
        if a != b:
            paths.append(prefix or "(value)")
    return paths


ALLOWED_ROOT_KEYS = {
    "thresholds",
    "gates",
    "risk",
    "ev",
    "multi_timeframe",
    "htf_fib",
    "ltf_fib",
    "htf_exit_config",
    "exit",
    "warmup_bars",
}
ALLOWED_RISK_KEYS = {"risk_map"}
ALLOWED_MTF_KEYS = {
    "use_htf_block",
    "allow_ltf_override",
    "ltf_override_threshold",
    "ltf_override_adaptive",
}


def _unwrap_payload(payload: dict) -> dict:
    if "cfg" in payload and isinstance(payload["cfg"], dict):
        cfg_inner = payload["cfg"]
        if "parameters" in cfg_inner and isinstance(cfg_inner["parameters"], dict):
            return dict(cfg_inner["parameters"])
        return dict(cfg_inner)
    if "parameters" in payload and isinstance(payload["parameters"], dict):
        return dict(payload["parameters"])
    return payload


def _sanitize_patch(patch: dict) -> dict:
    sanitized: dict[str, Any] = {}
    for key in ALLOWED_ROOT_KEYS:
        if key not in patch:
            continue
        value = patch[key]
        if not isinstance(value, dict):
            sanitized[key] = value
            continue
        if key == "risk":
            filtered = {rk: value[rk] for rk in ALLOWED_RISK_KEYS if rk in value}
            if filtered:
                sanitized[key] = filtered
            continue
        if key == "multi_timeframe":
            filtered = {mk: value[mk] for mk in ALLOWED_MTF_KEYS if mk in value}
            if filtered:
                sanitized[key] = filtered
            continue
        sanitized[key] = value
    return sanitized


def _load_patch(path: Path, full_mode: bool = False) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Patch file must contain a JSON object")
    unwrapped = _unwrap_payload(payload)
    if full_mode:
        return unwrapped  # Skip whitelist filter in full mode
    sanitized = _sanitize_patch(unwrapped)
    if not sanitized:
        raise ValueError(
            "Patch did not include any runtime fields "
            "(allowed: thresholds, gates, risk.risk_map, ev, multi_timeframe)"
        )
    return sanitized


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply runtime config patch")
    parser.add_argument("patch_file", type=Path, help="Path to JSON file with overrides")
    parser.add_argument("--actor", type=str, default="cli", help="Actor to record in audit log")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and show diff without writing runtime.json",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Apply ALL fields from patch (skip whitelist filter) - USE WITH CAUTION for experimentation only",
    )
    args = parser.parse_args()

    authority = ConfigAuthority()
    cfg_obj, _, version = authority.get()
    baseline = cfg_obj.model_dump_canonical()

    patch = _load_patch(args.patch_file, full_mode=args.full)
    if args.full:
        print("[WARNING] Running in FULL mode - all fields will be applied (whitelist bypassed)")
    merged = _deep_merge(baseline, patch)
    try:
        authority.validate(merged)
    except Exception as exc:  # pragma: no cover - validation errors bubble up
        print(f"[FAILED] Patch validation error: {exc}")
        return 1

    diff = _diff_paths(baseline, merged)
    if args.dry_run:
        print("[DRY-RUN] Patch validated successfully.")
        if diff:
            print("Changed paths:")
            for path in diff:
                print(f"  - {path}")
        else:
            print("No differences detected.")
        return 0

    if args.full:
        # In full mode, write directly to runtime.json bypassing whitelist check
        import json

        runtime_path = ROOT_DIR / "config" / "runtime.json"
        try:
            runtime_data = json.loads(runtime_path.read_text(encoding="utf-8"))
            new_version = runtime_data.get("version", 0) + 1
            runtime_data["version"] = new_version
            runtime_data["cfg"] = merged
            runtime_path.write_text(json.dumps(runtime_data, indent=2), encoding="utf-8")
            print("[OK] Runtime config updated (FULL mode - direct write).")
            print(f"  Version: {new_version}")
            print(f"  Actor:   {args.actor}")
        except Exception as exc:
            print(f"[FAILED] Could not write runtime.json: {exc}")
            return 1
    else:
        # Normal mode: use ConfigAuthority with whitelist
        try:
            snap = authority.propose_update(patch, actor=args.actor, expected_version=version)
            print("[OK] Runtime config updated.")
            print(f"  Version: {snap.version}")
            print(f"  Hash:    {snap.hash}")
        except Exception as exc:
            print(f"[FAILED] Could not persist patch: {exc}")
            return 1

    if diff:
        print("  Paths:")
        for path in diff:
            print(f"    - {path}")
    else:
        print("  (no field changes detected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
