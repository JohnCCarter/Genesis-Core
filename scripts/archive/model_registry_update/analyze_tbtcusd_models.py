#!/usr/bin/env python3
"""
Analyze tBTCUSD Models
=====================

Analysera alla tBTCUSD modeller för att identifiera föråldrade.
"""

import json
from datetime import datetime
from pathlib import Path


def analyze_tbtcusd_models():
    """Analysera alla tBTCUSD modeller."""
    print("Analyserar tBTCUSD modeller...")

    models_dir = Path("config/models")
    tbtcusd_models = list(models_dir.glob("tBTCUSD*.json"))

    print(f"Totalt tBTCUSD modeller: {len(tbtcusd_models)}")

    # Kategorisera modeller
    current_models = []
    outdated_models = []
    metrics_models = []
    other_models = []

    for model_file in tbtcusd_models:
        try:
            with open(model_file) as f:
                data = json.load(f)

            model_name = model_file.name

            # Kontrollera om det är en aktuell model
            if "_" in model_name and not any(
                x in model_name for x in ["_v", "_metrics", "_holdout", "_provenance"]
            ):
                # Detta är en aktuell model (tBTCUSD_1h.json, etc.)
                current_models.append(
                    {
                        "file": model_name,
                        "size": model_file.stat().st_size,
                        "modified": datetime.fromtimestamp(model_file.stat().st_mtime),
                        "schema_len": len(data.get("schema", [])) if "schema" in data else 0,
                    }
                )

            elif "_metrics" in model_name:
                # Metrics filer
                metrics_models.append(
                    {
                        "file": model_name,
                        "size": model_file.stat().st_size,
                        "modified": datetime.fromtimestamp(model_file.stat().st_mtime),
                    }
                )

            elif any(x in model_name for x in ["_v", "_holdout", "_provenance"]):
                # Föråldrade modeller
                outdated_models.append(
                    {
                        "file": model_name,
                        "size": model_file.stat().st_size,
                        "modified": datetime.fromtimestamp(model_file.stat().st_mtime),
                        "reason": "Versioned model" if "_v" in model_name else "Supporting file",
                    }
                )

            else:
                # Andra modeller
                other_models.append(
                    {
                        "file": model_name,
                        "size": model_file.stat().st_size,
                        "modified": datetime.fromtimestamp(model_file.stat().st_mtime),
                    }
                )

        except Exception as e:
            print(f"Fel vid analys av {model_file.name}: {e}")

    return current_models, outdated_models, metrics_models, other_models


def print_analysis_report(current_models, outdated_models, metrics_models, other_models):
    """Skriv ut analysrapport."""
    print("\n" + "=" * 80)
    print("tBTCUSD MODELLER ANALYS")
    print("=" * 80)

    print(f"\nAKTUELLA MODELLER ({len(current_models)}):")
    for model in current_models:
        print(
            f"  OK {model['file']} - {model['schema_len']} features - {model['size']} bytes - {model['modified'].strftime('%Y-%m-%d %H:%M')}"
        )

    print(f"\nFÖRÅLDRADE MODELLER ({len(outdated_models)}):")
    for model in outdated_models:
        print(
            f"  OLD {model['file']} - {model['reason']} - {model['size']} bytes - {model['modified'].strftime('%Y-%m-%d %H:%M')}"
        )

    print(f"\nMETRICS MODELLER ({len(metrics_models)}):")
    for model in metrics_models:
        print(
            f"  METRICS {model['file']} - {model['size']} bytes - {model['modified'].strftime('%Y-%m-%d %H:%M')}"
        )

    print(f"\nANDRA MODELLER ({len(other_models)}):")
    for model in other_models:
        print(
            f"  OTHER {model['file']} - {model['size']} bytes - {model['modified'].strftime('%Y-%m-%d %H:%M')}"
        )

    print("\n" + "=" * 80)
    print("REKOMMENDATIONER:")
    print("=" * 80)

    if outdated_models:
        print(f"\nTA BORT {len(outdated_models)} föråldrade modeller:")
        for model in outdated_models:
            print(f"   - {model['file']}")

    if metrics_models:
        print(f"\nBEHÅLL {len(metrics_models)} metrics modeller (för referens)")

    if other_models:
        print(f"\nGRANSKA {len(other_models)} andra modeller:")
        for model in other_models:
            print(f"   - {model['file']}")

    print(f"\nBEHÅLL {len(current_models)} aktuella modeller")


def create_cleanup_plan(outdated_models, other_models):
    """Skapa cleanup plan."""
    print("\n" + "=" * 80)
    print("CLEANUP PLAN")
    print("=" * 80)

    files_to_remove = []
    files_to_review = []

    for model in outdated_models:
        files_to_remove.append(model["file"])

    for model in other_models:
        files_to_review.append(model["file"])

    print(f"\nFiler att ta bort ({len(files_to_remove)}):")
    for file in files_to_remove:
        print(f"   - {file}")

    print(f"\nFiler att granska ({len(files_to_review)}):")
    for file in files_to_review:
        print(f"   - {file}")

    return files_to_remove, files_to_review


def main():
    """Huvudfunktion."""
    print("ANALYSERAR tBTCUSD MODELLER")
    print("=" * 50)

    try:
        # Analysera modeller
        current_models, outdated_models, metrics_models, other_models = analyze_tbtcusd_models()

        # Skriv ut rapport
        print_analysis_report(current_models, outdated_models, metrics_models, other_models)

        # Skapa cleanup plan
        files_to_remove, files_to_review = create_cleanup_plan(outdated_models, other_models)

        # Spara plan
        cleanup_plan = {
            "files_to_remove": files_to_remove,
            "files_to_review": files_to_review,
            "current_models": [m["file"] for m in current_models],
            "metrics_models": [m["file"] for m in metrics_models],
        }

        with open("tbtcusd_cleanup_plan.json", "w") as f:
            json.dump(cleanup_plan, f, indent=2)

        print("\nCleanup plan sparad till: tbtcusd_cleanup_plan.json")

    except Exception as e:
        print(f"Fel: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
