"""
Ensure `Genesis-Core/src` is on sys.path for tests executed from monorepo root.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_SCRIPTS = _ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


# Keep unit tests deterministic and independent of the developer's shell.
# Many parts of the system use GENESIS_* env flags; if a developer has these set
# locally (e.g. GENESIS_PRECOMPUTE_FEATURES=1), it can change code paths and
# produce noisy warnings. Tests that need specific values should set them
# explicitly via monkeypatch.
_ENV_VARS_TO_CLEAR = (
    "GENESIS_FAST_WINDOW",
    "GENESIS_PRECOMPUTE_FEATURES",
    "GENESIS_MODE_EXPLICIT",
    "GENESIS_FAST_HASH",
    "GENESIS_DISABLE_INDICATOR_CACHE",
    "GENESIS_DISABLE_METRICS",
    "GENESIS_OPTIMIZER_JSON_CACHE",
    "GENESIS_FEATURE_CACHE_SIZE",
)


@pytest.fixture(autouse=True)
def _clear_genesis_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ENV_VARS_TO_CLEAR:
        if name in os.environ:
            monkeypatch.delenv(name, raising=False)
