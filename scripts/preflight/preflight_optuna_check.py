from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent.parent / "archive/2026-02/analysis/preflight_optuna_check.py"
).resolve()


def _load_target_exports() -> None:
    """Load target code into this module namespace for monkeypatch compatibility."""

    source = _TARGET.read_text(encoding="utf-8")
    code = compile(source, str(_TARGET), "exec")
    exec(code, globals())


if __name__ != "__main__":
    _load_target_exports()


def _run_deprecated_cli() -> int:
    print(
        "[DEPRECATED] scripts/preflight_optuna_check.py moved to scripts/archive/2026-02/analysis/preflight_optuna_check.py.",
        file=sys.stderr,
    )
    argv = sys.argv[:]
    sys.argv = [str(_TARGET), *argv[1:]]
    runpy.run_path(str(_TARGET), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(_run_deprecated_cli())
