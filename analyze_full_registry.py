#!/usr/bin/env python3
"""
Analysera hela registry.json för alla symbols och timeframes.
"""

import json
from pathlib import Path

def analyze_full_registry():
    """Analysera hela registry.json för alla symbols och timeframes."""
    
    print("=" * 60)
    print("FULL REGISTRY ANALYSIS")
    print("=" * 60)
    
    # Load registry
    registry_path = Path("config/models/registry.json")
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    # Get available data files
    data_dir = Path("data/candles")
    data_files = list(data_dir.glob("*.parquet")) + list(data_dir.glob("*.feather"))
    
    # Extract all symbols and timeframes from data
    data_symbols_timeframes = {}
    for file in data_files:
        filename = file.stem
        if "_" in filename:
            symbol, timeframe = filename.split("_", 1)
            if symbol not in data_symbols_timeframes:
                data_symbols_timeframes[symbol] = set()
            data_symbols_timeframes[symbol].add(timeframe)
    
    print("Available data:")
    for symbol, timeframes in data_symbols_timeframes.items():
        print(f"  {symbol}: {sorted(timeframes)}")
    
    # Extract all symbols and timeframes from registry
    registry_symbols_timeframes = {}
    for key in registry.keys():
        if ":" in key:
            symbol, timeframe = key.split(":", 1)
            if symbol not in registry_symbols_timeframes:
                registry_symbols_timeframes[symbol] = set()
            registry_symbols_timeframes[symbol].add(timeframe)
    
    print(f"\nCurrent registry:")
    for symbol, timeframes in registry_symbols_timeframes.items():
        print(f"  {symbol}: {sorted(timeframes)}")
    
    # Find all symbols that need updating
    all_symbols = set(data_symbols_timeframes.keys()) | set(registry_symbols_timeframes.keys())
    
    print(f"\n=== ANALYSIS BY SYMBOL ===")
    
    updates_needed = {}
    
    for symbol in sorted(all_symbols):
        data_tf = data_symbols_timeframes.get(symbol, set())
        registry_tf = registry_symbols_timeframes.get(symbol, set())
        
        # Find timeframes to add (in data but not in registry)
        to_add = data_tf - registry_tf
        
        # Find timeframes to remove (in registry but not in data, or 4h)
        to_remove = (registry_tf - data_tf) | {"4h"}
        
        if to_add or to_remove:
            updates_needed[symbol] = {
                'add': sorted(to_add),
                'remove': sorted(to_remove)
            }
            print(f"{symbol}:")
            if to_add:
                print(f"  Add: {sorted(to_add)}")
            if to_remove:
                print(f"  Remove: {sorted(to_remove)}")
        else:
            print(f"{symbol}: No changes needed")
    
    return updates_needed, data_symbols_timeframes

if __name__ == "__main__":
    updates_needed, data_symbols_timeframes = analyze_full_registry()
    
    print(f"\n=== SUMMARY ===")
    print(f"Symbols needing updates: {len(updates_needed)}")
    
    for symbol, changes in updates_needed.items():
        print(f"{symbol}: +{len(changes['add'])} -{len(changes['remove'])}")
