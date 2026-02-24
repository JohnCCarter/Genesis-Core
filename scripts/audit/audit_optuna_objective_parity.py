from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent.parent
    / "archive/deprecated_2026-02/audit_optuna_objective_parity.py"
).resolve()


def _load_target_exports() -> None:
    """Expose archived target symbols when this wrapper is imported as module."""

    namespace = runpy.run_path(
        str(_TARGET), run_name="scripts.archive_compat.audit_optuna_objective_parity"
    )
    skip = {"__name__", "__file__", "__package__", "__spec__", "__cached__", "__builtins__"}
    for key, value in namespace.items():
        if key not in skip:
            globals()[key] = value


if __name__ != "__main__":
    _load_target_exports()


def main() -> int:
    print(
        "[DEPRECATED] scripts/audit_optuna_objective_parity.py moved to scripts/archive/deprecated_2026-02/audit_optuna_objective_parity.py.",
        file=sys.stderr,
    )
    argv = sys.argv[:]
    sys.argv = [str(_TARGET), *argv[1:]]
    runpy.run_path(str(_TARGET), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
