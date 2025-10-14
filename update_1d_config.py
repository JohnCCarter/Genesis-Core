#!/usr/bin/env python3
"""
Update 1D Configuration
======================

Uppdatera 1D konfiguration baserat på lärdomar från 6h och 1h.
"""

import json
from pathlib import Path

def update_1d_config():
    """Uppdatera 1D konfiguration."""
    print("Uppdaterar 1D konfiguration...")
    
    # Lärdomar från 6h (excellent performance):
    # - entry_conf_overall: 0.35
    # - regime_proba: 0.5 för alla
    # - max_hold_bars: 20
    # - partial_1_pct: 0.40
    
    # Lärdomar från 1h (good performance):
    # - entry_conf_overall: 0.40
    # - regime_proba: ranging: 0.8, bull: 0.7, bear: 0.7, balanced: 0.8
    # - max_hold_bars: 25
    # - partial_1_pct: 0.55
    
    # 1D specifika överväganden:
    # - Längre holds för macro trends
    # - Högre confidence för kvalitet
    # - Större position sizes
    # - Mindre partial exits
    
    new_1d_config = {
        "thresholds": {
            "entry_conf_overall": 0.30,  # Balanserad - inte för låg, inte för hög
            "regime_proba": {
                "ranging": 0.6,   # Högre än 6h (0.5) för kvalitet
                "bull": 0.5,      # Samma som 6h
                "bear": 0.5,      # Samma som 6h
                "balanced": 0.6   # Högre än 6h (0.5) för kvalitet
            },
        },
        "risk": {
            "risk_map": [
                [0.30, 0.15],  # Större size än 6h för 1D
                [0.40, 0.20],
                [0.50, 0.25],
                [0.60, 0.30],
                [0.70, 0.35],
            ]
        },
        "exit": {
            "enabled": True,
            "exit_conf_threshold": 0.25,  # Högre än 6h (0.3) för kvalitet
            "max_hold_bars": 30,  # Längre än 6h (20) för macro trends
            "regime_aware_exits": True,
        },
        "gates": {
            "cooldown_bars": 1,  # Mer än 6h (0) för kvalitet
            "hysteresis_steps": 2,  # Samma som 6h
        },
        "htf_exit_config": {
            "enable_partials": True,
            "enable_trailing": True,
            "enable_structure_breaks": True,
            "partial_1_pct": 0.35,  # Mindre än 6h (0.40) för längre holds
            "partial_2_pct": 0.25,  # Mindre än 6h (0.30) för längre holds
            "fib_threshold_atr": 0.4,  # Högre än 6h (0.3) för kvalitet
            "trail_atr_multiplier": 1.5,  # Högre än 6h (1.3) för längre holds
            "swing_update_strategy": "fixed",
        },
        "warmup_bars": 30,  # Mer än 6h (50) för 1D data
    }
    
    return new_1d_config

def update_timeframe_configs_file(new_1d_config):
    """Uppdatera timeframe_configs.py filen."""
    print("Uppdaterar timeframe_configs.py...")
    
    config_file = Path("config/timeframe_configs.py")
    
    if not config_file.exists():
        print("ERROR: timeframe_configs.py finns inte!")
        return False
    
    try:
        # Läs nuvarande fil
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Hitta get_1d_config funktionen
        start_marker = "def get_1d_config():"
        end_marker = "def get_timeframe_config"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("ERROR: Kunde inte hitta get_1d_config funktionen!")
            return False
        
        # Skapa ny funktion
        new_function = f'''def get_1d_config():
    """1D timeframe config - OPTIMIZED based on 6h and 1h learnings."""
    return {json.dumps(new_1d_config, indent=4)}
'''
        
        # Ersätt funktionen
        new_content = content[:start_idx] + new_function + content[end_idx:]
        
        # Spara filen
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("SUCCESS: timeframe_configs.py uppdaterad!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def verify_updated_config():
    """Verifiera att konfigurationen är uppdaterad."""
    print("Verifierar uppdaterad konfiguration...")
    
    try:
        from config.timeframe_configs import get_1d_config
        
        config = get_1d_config()
        
        print("Uppdaterad 1D konfiguration:")
        print(f"  entry_conf_overall: {config['thresholds']['entry_conf_overall']}")
        print(f"  regime_proba: {config['thresholds']['regime_proba']}")
        print(f"  max_hold_bars: {config['exit']['max_hold_bars']}")
        print(f"  warmup_bars: {config['warmup_bars']}")
        print(f"  risk_map: {config['risk']['risk_map']}")
        print(f"  partial_1_pct: {config['htf_exit_config']['partial_1_pct']}")
        print(f"  fib_threshold_atr: {config['htf_exit_config']['fib_threshold_atr']}")
        
        # Kontrollera att värdena är rimliga
        if 0.2 <= config['thresholds']['entry_conf_overall'] <= 0.4:
            print("SUCCESS: Entry confidence är rimlig")
        else:
            print("WARNING: Entry confidence kanske inte optimal")
        
        if 20 <= config['exit']['max_hold_bars'] <= 40:
            print("SUCCESS: Max hold bars är rimlig")
        else:
            print("WARNING: Max hold bars kanske inte optimal")
        
        if 0.3 <= config['htf_exit_config']['partial_1_pct'] <= 0.5:
            print("SUCCESS: Partial exit är rimlig")
        else:
            print("WARNING: Partial exit kanske inte optimal")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Huvudfunktion."""
    print("UPDATING 1D CONFIGURATION")
    print("="*50)
    
    try:
        # Skapa ny 1D konfiguration
        new_config = update_1d_config()
        
        # Uppdatera timeframe_configs.py
        success = update_timeframe_configs_file(new_config)
        
        if success:
            # Verifiera uppdateringen
            verify_updated_config()
            
            print("\n" + "="*50)
            print("SUCCESS: 1D konfiguration uppdaterad!")
            print("Baserat på lärdomar från 6h och 1h timeframes.")
            print("Vi kan nu testa den nya konfigurationen.")
        else:
            print("\n" + "="*50)
            print("ERROR: Kunde inte uppdatera 1D konfiguration!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
