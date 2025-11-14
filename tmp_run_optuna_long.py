from pathlib import Path

from core.optimizer.runner import run_optimizer


if __name__ == "__main__":
    run_optimizer(
        Path("config/optimizer/tBTCUSD_1h_optuna_remodel_v1.yaml"),
        run_id="run_20251114_long",
    )

