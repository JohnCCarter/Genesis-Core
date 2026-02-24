#!/usr/bin/env python3

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> int:
    target = (
        Path(__file__).resolve().parent / "archive/2026-02/analysis/verify_mcp_installation.py"
    ).resolve()
    print(
        "[DEPRECATED] scripts/verify_mcp_installation.py moved to scripts/archive/2026-02/analysis/verify_mcp_installation.py.",
        file=sys.stderr,
    )
    argv = sys.argv[:]
    sys.argv = [str(target), *argv[1:]]
    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
