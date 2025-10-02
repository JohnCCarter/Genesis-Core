from __future__ import annotations

import math
from typing import Iterable, Tuple


def brier_score(
    probs: Iterable[Tuple[float, float, float]], labels: Iterable[str]
) -> float:
    """Brier score för multi-class {buy,sell,hold}.

    probs: iterable av (p_buy, p_sell, p_hold) där varje element summerar ≈ 1
    labels: iterable av sanna etiketter {"buy","sell","hold"}
    Returnerar medelvärde av kvadratiska fel.
    """
    total = 0.0
    n = 0
    mapping = {"buy": (1.0, 0.0, 0.0), "sell": (0.0, 1.0, 0.0), "hold": (0.0, 0.0, 1.0)}
    for (pb, ps, ph), lab in zip(probs, labels):
        yb, ys, yh = mapping.get(lab, (0.0, 0.0, 1.0))
        total += (pb - yb) ** 2 + (ps - ys) ** 2 + (ph - yh) ** 2
        n += 1
    return total / n if n else 0.0


def log_loss(
    probs: Iterable[Tuple[float, float, float]],
    labels: Iterable[str],
    eps: float = 1e-12,
) -> float:
    """Log loss (cross-entropy) för {buy,sell,hold} med numerisk stabilitet.

    eps klipper sannolikheter bort från 0/1 för att undvika -inf.
    """
    total = 0.0
    n = 0
    for (pb, ps, ph), lab in zip(probs, labels):
        pb = min(1.0 - eps, max(eps, pb))
        ps = min(1.0 - eps, max(eps, ps))
        ph = min(1.0 - eps, max(eps, ph))
        if lab == "buy":
            total += -math.log(pb)
        elif lab == "sell":
            total += -math.log(ps)
        else:
            total += -math.log(ph)
        n += 1
    return total / n if n else 0.0
