import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from core.ml.labeling import align_features_with_labels, generate_labels
from core.utils import get_candles_path
from core.utils.data_loader import load_features
from scripts.evaluate_model import create_model_from_json, load_trained_model

# Ensure project paths
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def evaluate_model(model_path: Path) -> dict[str, float]:
    model_json = load_trained_model(model_path)
    schema: list[str] = model_json.get("schema", [])
    if not schema:
        raise ValueError(f"Model {model_path.name} saknar schema")

    parts = model_path.stem.split("_")
    if len(parts) < 3:
        raise ValueError(f"Kan inte tolka symbol/tidsram ur {model_path.name}")
    symbol = parts[0]
    timeframe = parts[1]

    # Ladda features och candles
    features_df = load_features(symbol, timeframe, version="v18")
    if "timestamp" in features_df.columns:
        cols = ["timestamp"] + schema
    else:
        cols = schema
    missing = [col for col in schema if col not in features_df.columns]
    if missing:
        raise ValueError(f"Saknade features {missing} i datasetet för {model_path.name}")
    features_df = features_df[cols]

    candles_path = get_candles_path(symbol, timeframe)
    candles_df = pd.read_parquet(candles_path)
    close_prices = candles_df["close"].tolist()

    lookahead_bars = 10
    threshold_pct = 0.0

    labels = generate_labels(close_prices, lookahead_bars, threshold_pct)
    start_idx, end_idx = align_features_with_labels(len(features_df), labels)
    if end_idx <= start_idx:
        raise ValueError("Inga giltiga labels efter alignment")

    aligned_features = features_df.iloc[start_idx:end_idx]
    aligned_labels = np.array(labels[start_idx:end_idx])
    feature_columns = [col for col in aligned_features.columns if col != "timestamp"]
    X = aligned_features[feature_columns].values
    nan_mask = np.isnan(X).any(axis=1)
    if nan_mask.any():
        X = X[~nan_mask]
        aligned_labels = aligned_labels[~nan_mask]

    buy_model, sell_model = create_model_from_json(model_json)
    buy_pred = buy_model.predict_proba(X)[:, 1]
    sell_pred = sell_model.predict_proba(X)[:, 1]

    buy_auc = roc_auc_score(aligned_labels, buy_pred)
    sell_auc = roc_auc_score(1 - aligned_labels, sell_pred)
    score = float((buy_auc + sell_auc) / 2.0)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "buy_auc": float(buy_auc),
        "sell_auc": float(sell_auc),
        "score": score,
        "samples": int(len(X)),
        "features": feature_columns,
    }


def main() -> None:
    models_dir = ROOT / "results" / "models"
    evaluation_dir = ROOT / "results" / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)

    model_paths = [
        p
        for p in models_dir.glob("*.json")
        if all(
            pattern not in p.stem for pattern in ["holdout", "metrics", "calibrated", "provenance"]
        )
    ]

    results: dict[str, dict[str, float]] = {}
    for model_path in sorted(model_paths):
        print(f"[EVAL] {model_path.name}")
        metrics = evaluate_model(model_path)
        results[model_path.stem] = metrics

        out_path = evaluation_dir / f"{model_path.stem}_evaluation.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {"model": model_path.name, "metrics": metrics}, f, indent=2, ensure_ascii=False
            )

    scoreboard_path = evaluation_dir / "model_scoreboard.json"
    with open(scoreboard_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[DONE] Result sparat till {scoreboard_path}")


if __name__ == "__main__":
    main()
