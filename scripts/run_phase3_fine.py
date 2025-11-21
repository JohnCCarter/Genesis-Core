import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from core.optimizer.runner import run_optimizer


def main():
    config_path = repo_root / "config" / "optimizer" / "tBTCUSD_1h_optuna_phase3_fine.yaml"

    print("=" * 80)
    print("Phase 3: Fine Tuning Optimization")
    print("=" * 80)
    print(f"Config: {config_path.name}")
    print("Goal: Improve Profit Factor > 1.15 by refining exits and entries.")
    print("Based on: Phase 2d (v6) results (Trades Unlocked, PF ~1.04)")
    print("=" * 80)

    run_optimizer(config_path)


if __name__ == "__main__":
    main()
