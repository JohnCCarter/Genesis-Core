#!/usr/bin/env python3
"""Preflight-check for Genesis MCP remote session safety and readiness.

This script is intended to be run before ChatGPT/MCP work sessions. It validates
that MCP is running in the expected dev workspace (/home checkout), that remote
security/auth flags are sane, and that git object storage permissions look healthy.
"""

from __future__ import annotations

import json
import os
import pwd
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

SERVICE_NAME = "genesis-mcp.service"
DEFAULT_CONFIG_REL_PATH = Path("config/mcp_settings.remote_git.json")


@dataclass
class CheckResult:
    level: str  # PASS | WARN | FAIL
    name: str
    detail: str


def _parse_systemctl_show_output(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _iter_git_owner_anomalies(git_dir: Path, expected_uid: int, limit: int = 20) -> list[Path]:
    anomalies: list[Path] = []
    for root, dirs, files in os.walk(git_dir):
        root_path = Path(root)
        for entry_name in [*dirs, *files]:
            entry = root_path / entry_name
            try:
                if entry.lstat().st_uid != expected_uid:
                    anomalies.append(entry)
                    if len(anomalies) >= limit:
                        return anomalies
            except OSError:
                continue
    return anomalies


def _read_proc_environ(pid: int) -> dict[str, str]:
    env_path = Path(f"/proc/{pid}/environ")
    raw = env_path.read_bytes().split(b"\x00")
    env: dict[str, str] = {}
    for item in raw:
        if not item or b"=" not in item:
            continue
        key_b, value_b = item.split(b"=", 1)
        env[key_b.decode("utf-8", errors="ignore")] = value_b.decode("utf-8", errors="ignore")
    return env


def run_preflight(repo_root: Path) -> tuple[int, list[CheckResult]]:
    results: list[CheckResult] = []

    config_path = repo_root / DEFAULT_CONFIG_REL_PATH
    if not config_path.exists():
        results.append(CheckResult("FAIL", "config-file", f"Missing config file: {config_path}"))
        return 2, results

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            cfg = json.load(handle)
    except Exception as exc:  # noqa: BLE001
        results.append(CheckResult("FAIL", "config-json", f"Invalid JSON: {exc}"))
        return 2, results

    features = cfg.get("features") or {}
    for feature_key in ["file_operations", "git_integration", "code_execution"]:
        enabled = bool(features.get(feature_key))
        level = "PASS" if enabled else "FAIL"
        results.append(
            CheckResult(level, f"config-feature-{feature_key}", f"{feature_key}={enabled}")
        )

    security = cfg.get("security") or {}
    blocked = set(security.get("blocked_patterns") or [])
    for required in [".git", ".env", "config/runtime.json"]:
        level = "PASS" if required in blocked else "WARN"
        results.append(
            CheckResult(level, f"config-blocked-{required}", f"blocked={required in blocked}")
        )

    max_file_size = int(security.get("max_file_size_mb") or 0)
    if max_file_size >= 10:
        results.append(
            CheckResult("PASS", "config-max-file-size", f"max_file_size_mb={max_file_size}")
        )
    else:
        results.append(
            CheckResult("WARN", "config-max-file-size", f"max_file_size_mb={max_file_size}")
        )

    show = subprocess.run(
        [
            "systemctl",
            "--no-pager",
            "show",
            SERVICE_NAME,
            "-p",
            "ActiveState",
            "-p",
            "MainPID",
            "-p",
            "WorkingDirectory",
            "-p",
            "ExecStart",
        ],
        capture_output=True,
        text=True,
        check=False,
        stdin=subprocess.DEVNULL,
    )
    if show.returncode != 0:
        results.append(
            CheckResult("FAIL", "systemd-show", (show.stderr or show.stdout).strip() or "failed")
        )
        return 2, results

    svc = _parse_systemctl_show_output(show.stdout)
    active = svc.get("ActiveState") == "active"
    results.append(CheckResult("PASS" if active else "FAIL", "service-active", str(active)))

    expected_workdir = str(repo_root)
    workdir = svc.get("WorkingDirectory") or ""
    workdir_ok = workdir == expected_workdir
    results.append(
        CheckResult(
            "PASS" if workdir_ok else "FAIL",
            "service-workingdir",
            f"current={workdir} expected={expected_workdir}",
        )
    )

    exec_start = svc.get("ExecStart") or ""
    exec_ok = expected_workdir in exec_start
    results.append(
        CheckResult(
            "PASS" if exec_ok else "FAIL",
            "service-execstart",
            "contains expected repo path" if exec_ok else "unexpected ExecStart path",
        )
    )

    pid_raw = (svc.get("MainPID") or "0").strip()
    pid = int(pid_raw) if pid_raw.isdigit() else 0
    if pid <= 0:
        results.append(CheckResult("FAIL", "service-mainpid", f"invalid pid={pid_raw}"))
        return 2, results

    try:
        env = _read_proc_environ(pid)
    except Exception as exc:  # noqa: BLE001
        results.append(CheckResult("FAIL", "proc-environ", str(exc)))
        return 2, results

    env_expectations = {
        "GENESIS_MCP_CONFIG_PATH": str(DEFAULT_CONFIG_REL_PATH),
        "GENESIS_MCP_REMOTE_SAFE": "0",
        "GENESIS_MCP_REMOTE_ULTRA_SAFE": "0",
        "GENESIS_MCP_REMOTE_GIT_MODE": "1",
        "GENESIS_MCP_REMOTE_ALLOW_UNAUTH": "0",
    }
    for key, expected in env_expectations.items():
        actual = env.get(key)
        ok = actual == expected
        results.append(
            CheckResult(
                "PASS" if ok else "FAIL",
                f"env-{key}",
                f"current={actual!r} expected={expected!r}",
            )
        )

    bind_host = env.get("GENESIS_MCP_BIND_HOST")
    if bind_host == "127.0.0.1":
        results.append(CheckResult("PASS", "env-bind-host", "GENESIS_MCP_BIND_HOST=127.0.0.1"))
    else:
        results.append(
            CheckResult(
                "WARN",
                "env-bind-host",
                f"GENESIS_MCP_BIND_HOST={bind_host!r} (recommended '127.0.0.1')",
            )
        )

    token = env.get("GENESIS_MCP_REMOTE_TOKEN")
    token_ok = isinstance(token, str) and len(token) >= 20
    results.append(
        CheckResult(
            "PASS" if token_ok else "FAIL",
            "env-remote-token",
            (
                "<missing>"
                if not token
                else ("<set>" if len(token) <= 8 else f"<set len={len(token)}>")
            ),
        )
    )

    git_dir = repo_root / ".git"
    objects_dir = git_dir / "objects"
    if not objects_dir.exists():
        results.append(CheckResult("FAIL", "git-objects-exists", f"Missing {objects_dir}"))
    else:
        writable = os.access(objects_dir, os.W_OK)
        results.append(
            CheckResult("PASS" if writable else "FAIL", "git-objects-writable", str(writable))
        )

    current_uid = os.getuid()
    owner_name = pwd.getpwuid(current_uid).pw_name
    anomalies = _iter_git_owner_anomalies(git_dir, expected_uid=current_uid, limit=20)
    if anomalies:
        sample = ", ".join(str(p.relative_to(repo_root)) for p in anomalies[:5])
        results.append(
            CheckResult(
                "FAIL",
                "git-owner-anomalies",
                f"found={len(anomalies)} sample=[{sample}] expected_owner={owner_name}",
            )
        )
    else:
        results.append(CheckResult("PASS", "git-owner-anomalies", "none"))

    fail_count = sum(1 for r in results if r.level == "FAIL")
    warn_count = sum(1 for r in results if r.level == "WARN")

    if fail_count > 0:
        exit_code = 2
    elif warn_count > 0:
        exit_code = 1
    else:
        exit_code = 0

    return exit_code, results


def _print_results(results: Iterable[CheckResult], exit_code: int) -> None:
    print("=" * 72)
    print("Genesis MCP Session Preflight")
    print("=" * 72)
    for result in results:
        prefix = {
            "PASS": "[PASS]",
            "WARN": "[WARN]",
            "FAIL": "[FAIL]",
        }.get(result.level, "[INFO]")
        print(f"{prefix:<7} {result.name}: {result.detail}")

    print("-" * 72)
    if exit_code == 0:
        print("PRECHECK RESULT: READY (all critical checks passed)")
    elif exit_code == 1:
        print("PRECHECK RESULT: CAUTION (warnings found, no critical failures)")
    else:
        print("PRECHECK RESULT: BLOCKED (critical failures found)")
    print("=" * 72)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    exit_code, results = run_preflight(repo_root)
    _print_results(results, exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
