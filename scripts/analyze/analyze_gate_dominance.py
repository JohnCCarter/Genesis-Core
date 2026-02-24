from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent.parent / "archive/2026-02/analysis/analyze_gate_dominance.py"
).resolve()


def _load_target_exports() -> None:
    """Load and expose target module symbols when imported as a module.

    This preserves existing import semantics, e.g.:
    `from scripts.analyze.analyze_gate_dominance import _percentile`.
    """

    namespace = runpy.run_path(
        str(_TARGET), run_name="scripts.archive_compat.analyze_gate_dominance"
    )
    skip = {"__name__", "__file__", "__package__", "__spec__", "__cached__", "__builtins__"}
    for key, value in namespace.items():
        if key not in skip:
            globals()[key] = value


if __name__ != "__main__":
    _load_target_exports()


def main() -> int:
    print(
        "[DEPRECATED] scripts/analyze_gate_dominance.py moved to scripts/archive/2026-02/analysis/analyze_gate_dominance.py.",
        file=sys.stderr,
    )
    argv = sys.argv[:]
    sys.argv = [str(_TARGET), *argv[1:]]
    runpy.run_path(str(_TARGET), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
