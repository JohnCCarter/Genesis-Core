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

from core.config.settings import get_settings
from core.io.bitfinex.ws_auth import auth_ping


async def main() -> None:
    s = get_settings()
    if not ((s.BITFINEX_API_KEY or "").strip() and (s.BITFINEX_API_SECRET or "").strip()):
        print({"skip": "missing api keys"})
        return
    res = await auth_ping()
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
