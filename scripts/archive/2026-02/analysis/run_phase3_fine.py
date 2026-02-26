import sys
from pathlib import Path


def _find_repo_root() -> Path:
    """Find repository root from current file location."""

    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "src").exists():
            return parent
    return Path(__file__).resolve().parent.parent


# Add src to path
repo_root = _find_repo_root()
sys.path.insert(0, str(repo_root / "src"))

from core.optimizer.runner import run_optimizer  # noqa: E402


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
