#!/usr/bin/env python3
"""
Verify MCP Server Installation

This script verifies that the MCP server is properly installed and configured.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path so we can import mcp_server
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    missing = []

    try:
        import mcp

        print("  ✓ mcp installed")
    except ImportError:
        print("  ✗ mcp not installed")
        missing.append("mcp")

    try:
        import aiofiles

        print("  ✓ aiofiles installed")
    except ImportError:
        print("  ✗ aiofiles not installed")
        missing.append("aiofiles")

    try:
        import git

        print("  ✓ gitpython installed")
    except ImportError:
        print("  ✗ gitpython not installed")
        missing.append("gitpython")

    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -e '.[mcp]'")
        return False

    print("\n✅ All dependencies installed")
    return True


def check_file_structure():
    """Check if required files exist."""
    print("\nChecking file structure...")
    project_root = Path(__file__).parent.parent
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
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} missing")
            all_exist = False

    if all_exist:
        print("\n✅ All required files exist")
        return True
    else:
        print("\n❌ Some files are missing")
        return False


def check_server_import():
    """Check if the MCP server can be imported."""
    print("\nChecking server import...")
    try:
        from mcp_server import config, resources, server, tools, utils

        print("  ✓ mcp_server.config")
        print("  ✓ mcp_server.tools")
        print("  ✓ mcp_server.resources")
        print("  ✓ mcp_server.utils")
        print("  ✓ mcp_server.server")
        print("\n✅ Server modules can be imported")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False


def check_configuration():
    """Check if configuration is valid."""
    print("\nChecking configuration...")
    try:
        from mcp_server.config import load_config

        config = load_config()
        print(f"  ✓ Server name: {config.server_name}")
        print(f"  ✓ Version: {config.version}")
        print(f"  ✓ Log level: {config.log_level}")
        print(
            f"  ✓ File operations: {'enabled' if config.features.file_operations else 'disabled'}"
        )
        print(
            f"  ✓ Code execution: {'enabled' if config.features.code_execution else 'disabled'}"
        )
        print(
            f"  ✓ Git integration: {'enabled' if config.features.git_integration else 'disabled'}"
        )
        print("\n✅ Configuration is valid")
        return True
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Genesis-Core MCP Server Installation Verification")
    print("=" * 60)
    print()

    checks = [
        check_dependencies(),
        check_file_structure(),
        check_server_import(),
        check_configuration(),
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("✅ MCP Server installation verified successfully!")
        print("\nNext steps:")
        print("1. Start the server: python -m mcp_server.server")
        print("2. Configure VSCode (see docs/mcp_server_guide.md)")
        print("3. Run tests: pytest tests/test_mcp_*.py")
        return 0
    else:
        print("❌ Installation verification failed")
        print("\nPlease fix the issues above and run this script again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
