#!/usr/bin/env python3
"""
Migrate flat model structure to multi-timeframe structure.

Converts:
  {"schema": [...], "buy": {...}, "sell": {...}}

To:
  {
    "1m": {"schema": [...], "buy": {...}, "sell": {...}},
    "5m": {"schema": [...], "buy": {...}, "sell": {...}},
    ...
  }
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1D"]

# Symbols that need migration (exclude BTC and ETH which already have structure)
SYMBOLS_TO_MIGRATE = [
    "tALGOUSD",
    "tDOGEUSD",
    "tSOLUSD",
    "tADAUSD",
    "tAVAXUSD",
    "tDOTUSD",
    "tLTCUSD",
    "tAPTUSD",
    "tEOSUSD",
    "tFILUSD",
    "tNEARUSD",
    "tXAUTUSD",
    "tXTZUSD",
]


def is_flat_structure(data: dict) -> bool:
    """Check if model file has flat structure (needs migration)."""
    # Flat structure has schema/buy/sell at root
    if "schema" in data and "buy" in data and "sell" in data:
        return True
    # Multi-timeframe structure has timeframes as keys
    if any(tf in data for tf in TIMEFRAMES):
        return False
    return False


def migrate_file(file_path: Path, dry_run: bool = False) -> bool:
    """Migrate a single model file from flat to multi-timeframe structure.

    Returns True if migrated, False if skipped.
    """
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Processing: {file_path.name}")

    # Read current content
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [ERROR] Error reading file: {e}")
        return False

    # Check if already migrated
    if not is_flat_structure(data):
        print("  [SKIP] Already has multi-timeframe structure, skipping")
        return False

    print("  [FLAT] Flat structure detected:")
    print(f"     Schema: {data.get('schema', [])}")
    print(f"     Buy weights: {data.get('buy', {}).get('w', [])}")
    print(f"     Sell weights: {data.get('sell', {}).get('w', [])}")

    # Create multi-timeframe structure
    migrated = {}
    for tf in TIMEFRAMES:
        # Copy the flat structure for each timeframe
        migrated[tf] = {
            "schema": data["schema"],
            "buy": data["buy"],
            "sell": data["sell"],
        }

    print(f"  [OK] Created structure with {len(TIMEFRAMES)} timeframes")

    if not dry_run:
        # Write back to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(migrated, f, indent=2)
            print(f"  [SAVED] Saved to {file_path.name}")
        except Exception as e:
            print(f"  [ERROR] Error writing file: {e}")
            return False
    else:
        print(f"  [DRY-RUN] Would save to {file_path.name}")

    return True


def main():
    """Main migration function."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate model files to multi-timeframe structure")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all symbols that need migration",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        help="Migrate specific symbol (e.g., tADAUSD)",
    )

    args = parser.parse_args()

    # Determine which symbols to process
    if args.symbol:
        symbols = [args.symbol]
    elif args.all:
        symbols = SYMBOLS_TO_MIGRATE
    else:
        print("Error: Specify either --all or --symbol SYMBOL")
        parser.print_help()
        return 1

    print("=" * 60)
    print("Genesis-Core Model Structure Migration")
    print("=" * 60)
    if args.dry_run:
        print("[DRY-RUN] MODE: No files will be modified")
    print(f"Symbols to process: {len(symbols)}")
    print(f"Timeframes per symbol: {len(TIMEFRAMES)}")

    # Get models directory
    root = Path(__file__).resolve().parents[1]
    models_dir = root / "config" / "models"

    if not models_dir.exists():
        print(f"\n[ERROR] Models directory not found: {models_dir}")
        return 1

    # Process each symbol
    migrated_count = 0
    skipped_count = 0

    for symbol in symbols:
        file_path = models_dir / f"{symbol}.json"

        if not file_path.exists():
            print(f"\n[WARN] File not found: {file_path.name}")
            skipped_count += 1
            continue

        if migrate_file(file_path, dry_run=args.dry_run):
            migrated_count += 1
        else:
            skipped_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"[OK] Migrated: {migrated_count} files")
    print(f"[SKIP] Skipped: {skipped_count} files")
    print(f"Total processed: {len(symbols)} files")

    if args.dry_run:
        print("\n[DRY-RUN] This was a DRY-RUN. Run without --dry-run to apply changes.")
        return 0

    if migrated_count > 0:
        print("\n[SUCCESS] Migration complete!")
        print("\nNext steps:")
        print("   1. Run tests: pytest tests/")
        print("   2. Verify models load correctly")
        print(
            "   3. Git commit: git add config/models/ && git commit -m 'feat: migrate models to multi-timeframe structure'"
        )
    else:
        print("\n[OK] All files already migrated!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
