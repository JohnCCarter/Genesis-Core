from pathlib import Path

import pandas as pd


def resample_1h_to_6h():
    input_path = Path("data/raw/tBTCUSD_1h_frozen.parquet")
    output_path = Path("data/raw/tBTCUSD_6h_frozen.parquet")

    if not input_path.exists():
        print(f"Error: Input file {input_path} not found.")
        return

    print(f"Reading {input_path}...")
    df = pd.read_parquet(input_path)

    # Ensure timestamp is datetime and set as index
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    print("Resampling to 6h...")
    # Resample logic for OHLCV
    ohlcv_dict = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}

    df_6h = df.resample("6h").agg(ohlcv_dict)

    # Drop incomplete bins (NaNs) if any
    df_6h.dropna(inplace=True)

    # Reset index to make timestamp a column again
    df_6h.reset_index(inplace=True)

    print(f"Saving {len(df_6h)} rows to {output_path}...")
    df_6h.to_parquet(output_path)
    print("Done.")


if __name__ == "__main__":
    resample_1h_to_6h()
