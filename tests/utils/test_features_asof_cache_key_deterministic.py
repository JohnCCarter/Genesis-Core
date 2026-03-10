from __future__ import annotations

import os
import subprocess
import sys


def _compute_key_in_subprocess(*, pyhashseed: str) -> str:
    # NOTE: PYTHONHASHSEED must be set *before* interpreter starts.
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = pyhashseed
    env.pop("GENESIS_FAST_HASH", None)  # default-path only

    code = (
        "from core.strategy.features_asof import _compute_candles_hash;"
        "candles={'open':[1.0,1.0],'high':[2.0,2.0],'low':[0.5,0.5],'close':[100.0,101.0],'volume':[1.0,1.0]};"
        "print(_compute_candles_hash(candles, 1))"
    )

    proc = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.stdout.strip()


def test_compute_candles_hash_is_deterministic_across_pyhashseed() -> None:
    # Regression guard: built-in hash() is salted per process; cache keys must not depend on it.
    k1 = _compute_key_in_subprocess(pyhashseed="123")
    k2 = _compute_key_in_subprocess(pyhashseed="456")

    assert k1 == k2
    assert len(k1) == 32  # blake2b digest_size=16 -> 32 hex chars
