#!/usr/bin/env python3
"""Verify MCP Server Installation.

This script verifies that the MCP server is properly installed and configured.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path


def _bootstrap_repo_root_on_path() -> Path:
    """Ensure repo root is importable so `mcp_server` can be imported."""

    # scripts/<this file> -> parents[1] == repo root
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""

    print("Checking dependencies...")
    missing: list[str] = []

    def _check_module(name: str, display_name: str | None = None) -> bool:
        if importlib.util.find_spec(name) is None:
            return False
        # Import to validate that import doesn't explode at runtime.
        mod = importlib.import_module(name)
        shown = display_name or mod.__name__
        version = getattr(mod, "__version__", None)
        suffix = f" ({version})" if isinstance(version, str) and version else ""
        print(f"  [OK] {shown} installed{suffix}")
        return True

    if not _check_module("mcp"):
        print("  [MISSING] mcp")
        missing.append("mcp")

    if not _check_module("aiofiles"):
        print("  [MISSING] aiofiles")
        missing.append("aiofiles")

    if not _check_module("git", display_name="gitpython"):
        print("  [MISSING] gitpython")
        missing.append("gitpython")

    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install -e '.[mcp]'")
        return False

    print("\nAll dependencies installed")
    return True


def check_file_structure(repo_root: Path) -> bool:
    """Check if required files exist."""

    print("\nChecking file structure...")
    required_files = [
        "mcp_server/__init__.py",
        "mcp_server/server.py",
        "mcp_server/tools.py",
        "mcp_server/resources.py",
        "mcp_server/config.py",
        "mcp_server/utils.py",
        "config/mcp_settings.json",
        ".vscode/mcp.json",
        "docs/mcp_server_guide.md",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = repo_root / file_path
        if full_path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [MISSING] {file_path}")
            all_exist = False

    if all_exist:
        print("\nAll required files exist")
        return True

    print("\nSome files are missing")
    return False


def check_server_import() -> bool:
    """Check if the MCP server can be imported."""

    print("\nChecking server import...")
    modules = [
        "mcp_server.config",
        "mcp_server.tools",
        "mcp_server.resources",
        "mcp_server.utils",
        "mcp_server.server",
    ]

    try:
        for name in modules:
            mod = importlib.import_module(name)
            print(f"  [OK] {mod.__name__}")
        print("\nServer modules can be imported")
        return True
    except ImportError as e:
        print(f"\nImport error: {e}")
        return False


def check_configuration() -> bool:
    """Check if configuration is valid."""

    print("\nChecking configuration...")
    try:
        from mcp_server.config import load_config

        config = load_config()
        print(f"  [OK] Server name: {config.server_name}")
        print(f"  [OK] Version: {config.version}")
        print(f"  [OK] Log level: {config.log_level}")
        print(
            f"  [OK] File operations: {'enabled' if config.features.file_operations else 'disabled'}"
        )
        print(
            f"  [OK] Code execution: {'enabled' if config.features.code_execution else 'disabled'}"
        )
        print(
            f"  [OK] Git integration: {'enabled' if config.features.git_integration else 'disabled'}"
        )
        print("\nConfiguration is valid")
        return True
    except Exception as e:
        print(f"\nConfiguration error: {e}")
        return False


def main() -> int:
    """Run all verification checks."""

    repo_root = _bootstrap_repo_root_on_path()

    print("=" * 60)
    print("Genesis-Core MCP Server Installation Verification")
    print("=" * 60)
    print()

    checks = [
        check_dependencies(),
        check_file_structure(repo_root),
        check_server_import(),
        check_configuration(),
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("MCP Server installation verified successfully")
        print("\nNext steps:")
        print("1. Start the server: python -m mcp_server.server")
        print("2. Configure VSCode (see docs/mcp_server_guide.md)")
        return 0

    print("Installation verification failed")
    print("\nPlease fix the issues above and run this script again.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
