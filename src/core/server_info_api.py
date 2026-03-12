from __future__ import annotations

import sys

from core.api import info as _api_module

sys.modules[__name__] = _api_module
