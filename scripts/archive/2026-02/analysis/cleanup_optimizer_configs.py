import shutil
from pathlib import Path


def cleanup_configs():
    optimizer_dir = Path("config/optimizer")
    archive_dir = optimizer_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    # Files to KEEP (Base versions and references)
    keep_patterns = [
        "tBTCUSD_1h_optuna_phase3_fine_v7.yaml",
        "tBTCUSD_1h_optuna_phase3_wide_v7.yaml",
        "tBTCUSD_1h_coarse_grid.yaml",
        "archive",  # Don't move the archive folder itself
    ]

    print(f"Cleaning up {optimizer_dir}...")

    count = 0
    for file_path in optimizer_dir.iterdir():
        if file_path.is_dir():
            continue

        filename = file_path.name

        # Check if we should keep it
        if filename in keep_patterns:
            print(f"Keeping: {filename}")
            continue

        # Move to archive
        target = archive_dir / filename
        print(f"Archiving: {filename}")
        shutil.move(str(file_path), str(target))
        count += 1

    print(f"Done. Archived {count} files.")


if __name__ == "__main__":
    cleanup_configs()
