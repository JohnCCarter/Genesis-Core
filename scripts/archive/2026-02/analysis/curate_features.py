#!/usr/bin/env python3
"""
Curate precomputed features by moving them from data/archive/features to
data/curated/v1/features with timestamped metadata.

Usage:
    python scripts/curate_features.py --symbol tBTCUSD --timeframe 1h --version v17
    python scripts/curate_features.py --all
"""

import argparse
import json
import shutil
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

CURATED_DIR = Path("data/curated/v1/features")
ARCHIVE_DIR = Path("data/archive/features")


def iter_archive_files(
    symbol: str | None = None, timeframe: str | None = None, version: str | None = None
) -> Iterable[Path]:
    if not ARCHIVE_DIR.exists():
        return []

    for feather in ARCHIVE_DIR.glob("*.feather"):
        parts = feather.stem.split("_")
        if len(parts) < 2:
            continue
        sym = parts[0]
        tf = parts[1]
        ver = "_".join(parts[2:]) if len(parts) > 2 else ""

        if symbol and sym != symbol:
            continue
        if timeframe and tf != timeframe:
            continue
        if version and version not in ver:
            continue

        yield feather


def curate_file(
    feather_path: Path, *, subdir: str, version: str, dry_run: bool = False
) -> dict[str, str]:
    if not feather_path.exists():
        raise FileNotFoundError(feather_path)

    symbol, timeframe, *version_parts = feather_path.stem.split("_")
    version = "_".join(version_parts) if version_parts else ""

    curated_dir = CURATED_DIR / symbol / timeframe / subdir
    curated_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    curated_feather = (
        curated_dir / f"{symbol}_{timeframe}_{version or 'features'}_{timestamp}.feather"
    )
    curated_parquet = curated_feather.with_suffix(".parquet")

    archive_parquet = feather_path.with_suffix(".parquet")

    if dry_run:
        return {
            "feather": str(curated_feather),
            "parquet": str(curated_parquet),
        }

    shutil.copy2(feather_path, curated_feather)

    if archive_parquet.exists():
        shutil.copy2(archive_parquet, curated_parquet)

    metadata = {
        "symbol": symbol,
        "timeframe": timeframe,
        "version": version,
        "source": str(feather_path),
        "created_at": timestamp,
    }
    metadata_path = curated_dir / f"{symbol}_{timeframe}_{version or 'features'}_{timestamp}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    return {
        "feather": str(curated_feather),
        "parquet": str(curated_parquet),
        "metadata": str(metadata_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Curate features from archive into curated store")
    parser.add_argument("--symbol", help="Symbol, e.g. tBTCUSD")
    parser.add_argument("--timeframe", help="Timeframe, e.g. 1h")
    parser.add_argument(
        "--version", choices=["v17", "v18"], required=True, help="Feature version to curate"
    )
    parser.add_argument("--dry-run", action="store_true", help="List actions without copying")

    args = parser.parse_args()

    CURATED_DIR.mkdir(parents=True, exist_ok=True)

    targets = list(
        iter_archive_files(
            symbol=args.symbol,
            timeframe=args.timeframe,
            version=args.version,
        )
    )

    if not targets:
        print("[INFO] No matching features found in archive.")
        return 0

    for feather in targets:
        result = curate_file(
            feather, subdir=args.version, version=args.version, dry_run=args.dry_run
        )
        print(f"[CURATE] {feather.name} -> {result['feather']}")

    print(f"[DONE] Curated {len(targets)} feature file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
