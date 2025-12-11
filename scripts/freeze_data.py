from pathlib import Path

import pandas as pd


def freeze_data():
    base_dir = Path("data/raw/bitfinex/candles")
    dest_dir = Path("data/raw")

    files_to_freeze = [
        ("tBTCUSD_1h_2025-12-11.parquet", "BTCUSD_1h_frozen.parquet"),
        ("tBTCUSD_1m_2025-12-11.parquet", "BTCUSD_1m_frozen.parquet"),
    ]

    for src_name, dest_name in files_to_freeze:
        src_path = base_dir / src_name
        dest_path = dest_dir / dest_name

        print(f"Freezing {src_name} -> {dest_name}...")

        if not src_path.exists():
            print(f"Error: Source file {src_path} does not exist.")
            continue

        try:
            # Read with pandas to force download if cloud-tiered
            df = pd.read_parquet(src_path)
            print(f"  Loaded {len(df)} rows.")

            # Save to new location
            df.to_parquet(dest_path, index=False)
            print(f"  Saved to {dest_path}")

        except Exception as e:
            print(f"  Failed to freeze {src_name}: {e}")


if __name__ == "__main__":
    freeze_data()
