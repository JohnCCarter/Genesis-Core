#!/usr/bin/env python3
"""
Verifiera Model Registry
=======================

Detta script verifierar att alla modeller fungerar korrekt
efter uppdateringen.
"""

import json
import os
from pathlib import Path

def verify_models():
    """Verifiera att alla modeller fungerar."""
    print("Verifierar modeller...")
    
    registry_path = "config/models/registry.json"
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    issues = []
    verified_count = 0
    
    for key, value in registry.items():
        if isinstance(value, dict) and 'champion' in value:
            champion_path = value['champion']
            
            if os.path.exists(champion_path):
                try:
                    # Läs model fil
                    with open(champion_path, 'r') as f:
                        model_data = json.load(f)
                    
                    # Verifiera schema
                    if 'schema' in model_data:
                        schema = model_data['schema']
                        if len(schema) == 5:
                            print(f"OK: {key} - 5-feature schema")
                            verified_count += 1
                        else:
                            issues.append(f"{key}: Schema har {len(schema)} features, förväntar 5")
                    else:
                        issues.append(f"{key}: Saknar schema")
                    
                    # Verifiera weights
                    if 'buy' in model_data and 'sell' in model_data:
                        buy_w = model_data['buy'].get('w', [])
                        sell_w = model_data['sell'].get('w', [])
                        
                        if len(buy_w) == 5 and len(sell_w) == 5:
                            print(f"OK: {key} - Korrekta weights")
                        else:
                            issues.append(f"{key}: Buy weights: {len(buy_w)}, Sell weights: {len(sell_w)}")
                    else:
                        issues.append(f"{key}: Saknar buy/sell weights")
                        
                except Exception as e:
                    issues.append(f"{key}: JSON parse error: {e}")
            else:
                issues.append(f"{key}: Champion model saknas: {champion_path}")
    
    print(f"\nVerifierade modeller: {verified_count}")
    print(f"Problem: {len(issues)}")
    
    if issues:
        print("\nProblem:")
        for issue in issues:
            print(f"  - {issue}")
    
    return len(issues) == 0

def main():
    """Huvudfunktion."""
    print("Startar model verifiering...")
    
    try:
        success = verify_models()
        
        if success:
            print("\nSUCCESS: Alla modeller verifierade!")
        else:
            print("\nWARNING: Några modeller har problem.")
        
    except Exception as e:
        print(f"Fel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
