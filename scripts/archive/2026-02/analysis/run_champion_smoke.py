import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


REPO_ROOT = _find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(REPO_ROOT / "src"))

from core.optimizer.runner import run_optimizer  # noqa: E402


def main():
    config_path = REPO_ROOT / "config" / "optimizer" / "tBTCUSD_1h_champion_centered_smoke.yaml"

    print("=" * 80)
    print("Champion-Centered Optimization - Smoke Test")
    print("=" * 80)
    print(f"Config: {config_path.name}")
    print("Strategy: Small intervals around validated champion (2-year PF 1.10)")
    print("Duration: ~10-15 minutes (5 trials on 3 months)")
    print("=" * 80)

    run_optimizer(config_path)


if __name__ == "__main__":
    main()
