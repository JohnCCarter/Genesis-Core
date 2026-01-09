"""DEPRECATED (temporary one-off).

This script was a quick analysis helper hardcoded to a specific run directory and is no longer
maintained.

If you need this again, re-create it locally from git history or write a new analysis script that takes
the run_id/path as an argument.
"""

from __future__ import annotations


def main() -> int:
    print(
        "[DEPRECATED] scripts/analyze_failures_temp.py was a one-off helper and is intentionally "
        "kept as a stub. Use a parameterized script instead."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
