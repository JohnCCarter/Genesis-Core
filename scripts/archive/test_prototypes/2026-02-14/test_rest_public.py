from __future__ import annotations

import asyncio
import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    """Make `import core` work when running without editable install."""

    try:
        import core  # noqa: F401

        return
    except Exception:
        repo_root = Path(__file__).resolve().parents[1]
        src_dir = repo_root / "src"
        if src_dir.is_dir() and str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.io.bitfinex.rest_public import get_platform_status


async def main() -> None:
    st = await get_platform_status()
    print({"platform_status": st})


if __name__ == "__main__":
    asyncio.run(main())
