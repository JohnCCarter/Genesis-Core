"""
Provenance tracking för reproducerbarhet av ML models.

Skapar hashar av data och konfiguration för att säkerställa
att model training kan reproduceras exakt.
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


def hash_dataframe(df: pd.DataFrame) -> str:
    """
    Skapa deterministisk hash av DataFrame.

    Args:
        df: DataFrame att hasha

    Returns:
        16-char hex hash
    """
    # Sort för konsistens
    df_sorted = df.sort_index(axis=1).sort_index(axis=0)

    # Convert till bytes
    data_bytes = df_sorted.to_csv(index=False).encode("utf-8")

    # SHA256 hash (trunc till 16 chars)
    return hashlib.sha256(data_bytes).hexdigest()[:16]


def hash_config(config: dict) -> str:
    """
    Hash av konfiguration.

    Args:
        config: Configuration dict

    Returns:
        16-char hex hash
    """
    # Sort keys för deterministic output
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:16]


def hash_list(items: list) -> str:
    """Hash av list (för labels, etc)."""
    items_str = json.dumps(items, sort_keys=True)
    return hashlib.sha256(items_str.encode("utf-8")).hexdigest()[:16]


def create_provenance_record(
    features_df: pd.DataFrame, labels: list, config: dict, model_path: Path
) -> dict:
    """
    Skapa komplett provenance record.

    Args:
        features_df: Features DataFrame
        labels: Labels list
        config: Training configuration
        model_path: Path till model

    Returns:
        Provenance dict med all information för reproducering
    """
    try:
        import sklearn

        sklearn_version = sklearn.__version__
    except ImportError:
        sklearn_version = "unknown"

    return {
        "timestamp": datetime.now().isoformat(),
        "data_hash": hash_dataframe(features_df),
        "labels_hash": hash_list([label if label is not None else -1 for label in labels]),
        "config_hash": hash_config(config),
        "model_path": str(model_path),
        "data_info": {
            "n_samples": len(features_df),
            "n_features": len(features_df.columns),
            "date_range": {
                "start": (
                    features_df["timestamp"].min().isoformat()
                    if "timestamp" in features_df.columns
                    else "unknown"
                ),
                "end": (
                    features_df["timestamp"].max().isoformat()
                    if "timestamp" in features_df.columns
                    else "unknown"
                ),
            },
            "feature_names": list(features_df.columns),
        },
        "config": config,
        "environment": {
            "python_version": sys.version,
            "sklearn_version": sklearn_version,
            "pandas_version": pd.__version__,
        },
    }


def save_provenance(provenance: dict, model_path: Path):
    """Spara provenance record."""
    provenance_path = model_path.parent / f"{model_path.stem}_provenance.json"
    with open(provenance_path, "w") as f:
        json.dump(provenance, f, indent=2)

    return provenance_path


def verify_reproducibility(model_path: Path, current_features_df: pd.DataFrame) -> bool:
    """
    Verifiera att nuvarande data matchar training data.

    Args:
        model_path: Path till modell
        current_features_df: Nuvarande features

    Returns:
        True om data matchar, False annars
    """
    provenance_path = model_path.parent / f"{model_path.stem}_provenance.json"

    if not provenance_path.exists():
        print("⚠ WARNING: No provenance record found")
        return False

    with open(provenance_path) as f:
        original_provenance = json.load(f)

    current_hash = hash_dataframe(current_features_df)

    if current_hash != original_provenance["data_hash"]:
        print("⚠ WARNING: Data has changed since training!")
        print(f"Original hash: {original_provenance['data_hash']}")
        print(f"Current hash:  {current_hash}")
        print("Results may not be reproducible")
        return False

    print("✓ Data verified - identical to training data")
    return True
