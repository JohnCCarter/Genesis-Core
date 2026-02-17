from __future__ import annotations

import argparse
import json
from collections.abc import Iterable


def bucket_edges(
    start: float = 0.5, stop: float = 1.0, step: float = 0.1
) -> list[tuple[float, float]]:
    edges: list[tuple[float, float]] = []
    x = start
    while x < stop:
        edges.append((x, min(stop, x + step)))
        x += step
    return edges


def reliability_by_bins(
    probs: Iterable[float],
    labels: Iterable[int],
    bins: list[tuple[float, float]] | None = None,
) -> list[dict]:
    bins = bins or bucket_edges(0.5, 1.0, 0.1)
    counts = [0 for _ in bins]
    pos = [0 for _ in bins]
    for p, y in zip(probs, labels, strict=False):
        for i, (lo, hi) in enumerate(bins):
            if lo <= p < hi or (hi == 1.0 and p == 1.0):
                counts[i] += 1
                if y == 1:
                    pos[i] += 1
                break
    out: list[dict] = []
    for (lo, hi), n, k in zip(bins, counts, pos, strict=False):
        acc = (k / n) if n else 0.0
        mid = (lo + hi) / 2.0
        out.append({"bin": f"[{lo:.2f},{hi:.2f})", "n": n, "acc": acc, "expected": mid})
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Reliability buckets for class probability")
    parser.add_argument(
        "--input", type=str, help="Path to JSONL with {probas:{buy,sell,hold}, label}"
    )
    parser.add_argument(
        "--class", dest="klass", type=str, default="buy", help="Class key to evaluate"
    )
    args = parser.parse_args()

    probs: list[float] = []
    labels: list[int] = []
    with open(args.input, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            p = float(((obj.get("probas") or {}).get(args.klass)) or 0.0)
            probs.append(p)
            lab = str(obj.get("label") or "hold")
            labels.append(1 if lab == args.klass else 0)

    buckets = reliability_by_bins(probs, labels)
    print(json.dumps(buckets, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
