from __future__ import annotations

import logging
import os
import random

import numpy as np

LOGGER = logging.getLogger(__name__)


def set_global_seeds(seed: int = 42) -> None:
    """Set deterministic seeds for Python and NumPy.

    Note:
        Setting ``PYTHONHASHSEED`` here does *not* change hash randomization for the
        current Python interpreter (that is decided at process start). It *does*
        affect child processes spawned after this call (they inherit the env var).
    """
    random.seed(seed)
    np.random.seed(seed)
    # Only effective for child processes started after this point.
    os.environ["PYTHONHASHSEED"] = str(seed)
    # Torch (optional). Some Windows environments raise OSError (WinError 1114)
    # even when torch is installed; seeding should still continue for Python/NumPy.
    try:  # pragma: no cover
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except (ImportError, OSError) as exc:
        LOGGER.debug("PyTorch unavailable (%s); skipping torch seed setup", exc)
