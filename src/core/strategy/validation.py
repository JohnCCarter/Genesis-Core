from __future__ import annotations

import math
from typing import Iterable, Tuple


def brier_score(probs: Iterable[Tuple[float, float, float]], labels: Iterable[str]) -> float:
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


def psi(
    expected: Iterable[float],
    actual: Iterable[float],
    bins: int = 10,
    eps: float = 1e-9,
) -> float:
    """Population Stability Index mellan två distributioner (1D), enkel lika-bredd-binning.

    expected/actual: listor av observationer i [0,1].
    """
    exp = list(expected)
    act = list(actual)
    if not exp or not act:
        return 0.0
    lo, hi = 0.0, 1.0
    w = (hi - lo) / max(1, bins)
    psi_val = 0.0
    for i in range(bins):
        a = lo + i * w
        b = a + w if i < bins - 1 else hi
        e_c = sum(1 for x in exp if (a <= x < b) or (i == bins - 1 and x == hi)) / len(exp)
        a_c = sum(1 for x in act if (a <= x < b) or (i == bins - 1 and x == hi)) / len(act)
        e_c = max(eps, e_c)
        a_c = max(eps, a_c)
        psi_val += (a_c - e_c) * math.log(a_c / e_c)
    return psi_val


def ks_statistic(expected: Iterable[float], actual: Iterable[float]) -> float:
    """Enkel KS‑statistik (max absolut skillnad mellan kumulativa distributioner)."""
    e = sorted(expected)
    a = sorted(actual)
    if not e or not a:
        return 0.0
    i = j = 0
    d_max = 0.0
    while i < len(e) or j < len(a):
        x = min(e[i] if i < len(e) else 1.0, a[j] if j < len(a) else 1.0)
        while i < len(e) and e[i] <= x:
            i += 1
        while j < len(a) and a[j] <= x:
            j += 1
        d_e = i / len(e)
        d_a = j / len(a)
        d_max = max(d_max, abs(d_e - d_a))
        if x == 1.0 and (i == len(e) and j == len(a)):
            break
    return d_max
