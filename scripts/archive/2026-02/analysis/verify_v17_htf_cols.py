#!/usr/bin/env python3
"""Verifiera att v17-featurefiler innehåller HTF-Fibonacci-kolumner."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "htf_fib_0382",
    "htf_fib_05",
    "htf_fib_0618",
    "htf_fib_0786",
    "htf_swing_high",
    "htf_swing_low",
}

OPTIONAL_COLUMNS = {"htf_swing_age_bars", "htf_timestamp"}


def iter_feature_files(base_dir: Path, symbol: str | None, timeframe: str | None) -> list[Path]:
    """Returnera lista över featurefiler att kontrollera."""

    base_dir = base_dir.resolve()
    if not base_dir.exists():
        raise FileNotFoundError(f"Base directory does not exist: {base_dir}")

    candidates: list[Path] = []

    if symbol and timeframe:
        # Curated struktur (symbol/timeframe/…)
        candidates.extend(sorted(base_dir.glob(f"{symbol}/{timeframe}/**/*_v17*.feather")))
        candidates.extend(sorted(base_dir.glob(f"{symbol}/{timeframe}/**/*_v17*.parquet")))
        candidates.extend(sorted(base_dir.glob(f"{symbol}/{timeframe}/*features_v17*.feather")))
        candidates.extend(sorted(base_dir.glob(f"{symbol}/{timeframe}/*features_v17*.parquet")))

        # Flat struktur (t.ex. data/archive/features)
        candidates.extend(sorted(base_dir.glob(f"{symbol}_{timeframe}_features_v17*.feather")))
        candidates.extend(sorted(base_dir.glob(f"{symbol}_{timeframe}_features_v17*.parquet")))
    else:
        candidates.extend(sorted(base_dir.glob("**/*features_v17*.feather")))
        candidates.extend(sorted(base_dir.glob("**/*features_v17*.parquet")))

    return [path for path in candidates if path.exists()]


def load_columns(path: Path) -> pd.Series:
    """Läs endast de kolumner som behövs från filen."""

    try:
        if path.suffix == ".feather":
            df = pd.read_feather(path, columns=list(REQUIRED_COLUMNS | OPTIONAL_COLUMNS))
        elif path.suffix == ".parquet":
            df = pd.read_parquet(path, columns=list(REQUIRED_COLUMNS | OPTIONAL_COLUMNS))
        else:
            raise ValueError(f"Unsupported file extension: {path.suffix}")
        return df
    except Exception as exc:  # pragma: no cover - diagnostic output
        raise RuntimeError(f"Failed to read {path}: {exc}") from exc


def check_file(path: Path) -> tuple[bool, list[str]]:
    """Kontrollera en enskild fil. Returnerar (ok, list med fel)."""

    errors: list[str] = []
    try:
        df = load_columns(path)
    except Exception as exc:  # pragma: no cover - diagnostic output
        return False, [str(exc)]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Saknar kolumner: {sorted(missing)}")
        return False, errors

    nan_counts = df[list(REQUIRED_COLUMNS)].isna().sum()
    nan_cols = nan_counts[nan_counts > 0]
    if not nan_cols.empty:
        issues = [f"{col}: {int(count)} NaN" for col, count in nan_cols.items()]
        errors.append("NaN-värden: " + ", ".join(issues))

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data/curated/v1/features"),
        help="Basdirectory för v17-featurefiler",
    )
    parser.add_argument("--symbol", help="Filtrera på symbol", default=None)
    parser.add_argument("--timeframe", help="Filtrera på timeframe", default=None)

    args = parser.parse_args()

    files = iter_feature_files(args.base_dir, args.symbol, args.timeframe)
    if not files:
        print("[WARN] Hittade inga v17-filer att kontrollera.")
        return 0

    any_errors = False
    for path in files:
        ok, messages = check_file(path)
        if ok:
            print(f"[OK] {path}")
        else:
            any_errors = True
            print(f"[FAIL] {path}")
            for msg in messages:
                print(f"        - {msg}")

    if any_errors:
        print("\n[SUMMARY] HTF-kolumnkontrollen misslyckades.")
        return 1

    print("\n[SUMMARY] Alla kontroller passerade.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
