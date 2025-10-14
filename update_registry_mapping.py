#!/usr/bin/env python3
"""
Uppdatera Registry Mapping
=========================

Detta script uppdaterar registry.json för att peka på nya modeller
istället för gamla.
"""

import json
import os
from pathlib import Path

def update_registry_mapping():
    """Uppdatera registry.json mapping."""
    print("Uppdaterar registry mapping...")
    
    # Läs nuvarande registry
    registry_path = "config/models/registry.json"
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    # Läs planen
    with open("model_update_plan.json", 'r') as f:
        plan = json.load(f)
    
    updated_count = 0
    
    # Uppdatera registry entries
    for item in plan['registry_updates']:
        key = item['key']
        
        if key in registry:
            # Extrahera symbol och timeframe
            parts = key.split(':')
            if len(parts) == 2:
                symbol, timeframe = parts
                
                # Skapa ny model path
                new_model_path = f"config/models/{symbol}_{timeframe}.json"
                
                if os.path.exists(new_model_path):
                    # Uppdatera registry entry
                    registry[key] = {
                        "champion": new_model_path
                    }
                    print(f"Uppdaterade: {key} -> {new_model_path}")
                    updated_count += 1
                else:
                    print(f"Varning: Ny model saknas: {new_model_path}")
            else:
                print(f"Varning: Ogiltig key format: {key}")
        else:
            print(f"Varning: Key saknas i registry: {key}")
    
    # Spara uppdaterad registry
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"\nTotalt uppdaterade registry entries: {updated_count}")
    return updated_count

def main():
    """Huvudfunktion."""
    print("Startar registry mapping uppdatering...")
    
    try:
        updated = update_registry_mapping()
        print(f"\nKlart! Uppdaterade {updated} registry entries.")
        
    except Exception as e:
        print(f"Fel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
