from __future__ import annotations

import json
import runpy
import sys
from datetime import UTC, datetime
from pathlib import Path


def _log_deprecated_usage(wrapper: Path, target: Path) -> None:
    payload = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "wrapper_path": wrapper.as_posix(),
        "target_path": target.as_posix(),
    }
    log_path = wrapper.parent / "deprecated-usage.log"
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main() -> int:
    wrapper = Path(__file__).resolve()
    target = (wrapper.parent / "archive/analysis/compare_htf_exits.py").resolve()
    print(
        "[DEPRECATED] scripts/compare_htf_exits.py moved to scripts/archive/analysis/compare_htf_exits.py.",
        file=sys.stderr,
    )
    _log_deprecated_usage(wrapper, target)
    argv = sys.argv[:]
    sys.argv = [str(target), *argv[1:]]
    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
