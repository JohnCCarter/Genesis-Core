#!/usr/bin/env python3
"""Snabbtest för att mäta tid per trial."""

import time
from pathlib import Path

from core.optimizer.runner import run_optimizer


def main():
    config_path = Path("config/optimizer/tBTCUSD_1h_optuna_fib_tune_quick.yaml")

    start_time = time.time()
    print(f"[START] {time.strftime('%H:%M:%S')}")

    try:
        results = run_optimizer(config_path)
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    elapsed = time.time() - start_time
    print(f"\n[DONE] {time.strftime('%H:%M:%S')}")
    print(f"Total tid: {elapsed:.1f}s ({elapsed/60:.1f} min)")

    completed_trials = [r for r in results if not r.get("skipped") and not r.get("error")]
    if completed_trials:
        avg_time = elapsed / len(completed_trials)
        print(f"Antal trials: {len(completed_trials)}")
        print(f"Genomsnitt per trial: {avg_time:.1f}s ({avg_time/60:.2f} min)")
        print(f"\nI 12h kan vi köra ungefär: {int(43200 / avg_time)} trials")
    else:
        print("[WARN] Inga completed trials")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
