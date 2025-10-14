#!/usr/bin/env python3
"""
Cleanup tBTCUSD Metrics Models
==============================

Ta bort metrics modeller för tBTCUSD.
"""

import os
import shutil
import json
from pathlib import Path

def cleanup_metrics_models():
    """Ta bort metrics modeller."""
    print("Rensar tBTCUSD metrics modeller...")
    
    # Lista över metrics modeller att ta bort
    metrics_models = [
        "tBTCUSD_1h_v10_final_baseline_metrics.json",
        "tBTCUSD_1h_v10_final_metrics.json",
        "tBTCUSD_1h_v10_optimized_metrics.json",
        "tBTCUSD_1h_v7_final_top7_6m_metrics.json",
        "tBTCUSD_30m_v3_metrics.json",
        "tBTCUSD_6h_v3_metrics.json"
    ]
    
    # Skapa backup mapp
    backup_dir = Path("config/models/backup_tbtcusd_metrics")
    backup_dir.mkdir(exist_ok=True)
    
    removed_count = 0
    for model_file in metrics_models:
        model_path = Path(f"config/models/{model_file}")
        
        if model_path.exists():
            try:
                # Flytta till backup
                backup_path = backup_dir / model_file
                shutil.move(str(model_path), str(backup_path))
                print(f"Flyttade: {model_file} -> backup/")
                removed_count += 1
            except Exception as e:
                print(f"Fel vid flytt av {model_file}: {e}")
        else:
            print(f"Finns inte: {model_file}")
    
    print(f"\nTotalt flyttade metrics modeller: {removed_count}")
    print(f"Backup mapp: {backup_dir}")
    return removed_count

def verify_final_cleanup():
    """Verifiera final cleanup."""
    print("\nVerifierar final cleanup...")
    
    models_dir = Path("config/models")
    
    # Räkna aktuella tBTCUSD modeller
    current_models = list(models_dir.glob("tBTCUSD_*.json"))
    print(f"Aktuella tBTCUSD modeller: {len(current_models)}")
    
    # Kontrollera att inga föråldrade modeller finns kvar
    outdated_patterns = ["_v", "_holdout", "_provenance", "_metrics"]
    remaining_outdated = []
    
    for model_file in current_models:
        if any(pattern in model_file.name for pattern in outdated_patterns):
            remaining_outdated.append(model_file.name)
    
    if len(remaining_outdated) == 0:
        print("SUCCESS: Alla föråldrade modeller borttagna!")
        return True
    else:
        print("WARNING: Några föråldrade modeller kvarstår!")
        for model in remaining_outdated:
            print(f"  - {model}")
        return False

def list_final_models():
    """Lista finala modeller."""
    print("\nFinala tBTCUSD modeller:")
    
    models_dir = Path("config/models")
    current_models = list(models_dir.glob("tBTCUSD_*.json"))
    
    for model_file in sorted(current_models):
        try:
            with open(model_file, 'r') as f:
                data = json.load(f)
            
            schema_len = len(data.get('schema', [])) if 'schema' in data else 0
            print(f"  - {model_file.name} - {schema_len} features")
            
        except Exception as e:
            print(f"  - {model_file.name} - Error: {e}")

def main():
    """Huvudfunktion."""
    print("CLEANUP tBTCUSD METRICS MODELLER")
    print("="*50)
    
    try:
        # Steg 1: Ta bort metrics modeller
        removed = cleanup_metrics_models()
        
        # Steg 2: Verifiera final cleanup
        success = verify_final_cleanup()
        
        # Steg 3: Lista finala modeller
        list_final_models()
        
        print("\n" + "="*50)
        print("FINAL CLEANUP RESULTAT:")
        print(f"Flyttade metrics modeller: {removed}")
        print(f"Verifiering: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            print("\nSUCCESS: Alla föråldrade modeller borttagna!")
            print("tBTCUSD modeller är nu rena och aktuella")
        else:
            print("\nWARNING: Några problem kvarstår")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
