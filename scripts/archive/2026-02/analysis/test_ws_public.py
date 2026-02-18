from __future__ import annotations

import asyncio
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


def _bootstrap_src_on_path() -> None:
    """Make `import core` work when running without editable install."""

    try:
        import core  # noqa: F401

        return
    except Exception:
        repo_root = _find_repo_root(Path(__file__).resolve())
        src_dir = repo_root / "src"
        if src_dir.is_dir() and str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.io.bitfinex.ws_public import one_message_ticker


async def main() -> None:
    res = await one_message_ticker()
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
