#!/usr/bin/env python3
"""
Fixa 4h Timeframe Problem
========================

Detta script fixar 4h timeframes genom att byta dem till 3h
i alla model filer.
"""

import json
import os
from pathlib import Path

def fix_4h_timeframes():
    """Fixa 4h timeframes i alla model filer."""
    print("Fixar 4h timeframes...")
    
    # Läs planen
    with open("model_update_plan.json", 'r') as f:
        plan = json.load(f)
    
    fixed_count = 0
    
    for item in plan['timeframe_fixes']:
        model_file = item['file']
        model_path = f"config/models/{model_file}"
        
        if os.path.exists(model_path):
            try:
                # Läs model fil
                with open(model_path, 'r') as f:
                    data = json.load(f)
                
                # Byt 4h till 3h
                if '4h' in data:
                    data['3h'] = data['4h']
                    del data['4h']
                    
                    # Spara uppdaterad fil
                    with open(model_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    print(f"Fixade: {model_file} (4h -> 3h)")
                    fixed_count += 1
                else:
                    print(f"Ingen 4h i: {model_file}")
                    
            except Exception as e:
                print(f"Fel vid fix av {model_file}: {e}")
        else:
            print(f"Model fil saknas: {model_path}")
    
    print(f"\nTotalt fixade timeframes: {fixed_count}")
    return fixed_count

def main():
    """Huvudfunktion."""
    print("Startar 4h timeframe fix...")
    
    try:
        fixed = fix_4h_timeframes()
        print(f"\nKlart! Fixade {fixed} timeframes.")
        
    except Exception as e:
        print(f"Fel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
