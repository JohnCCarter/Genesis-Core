#!/usr/bin/env python3
"""
Model Registry Update Plan
=========================

Detta script analyserar och planerar uppdateringen av alla model filer
från gamla 2-feature schema till avancerade 5-feature schema.

Plan:
1. Analysera nuvarande modeller
2. Identifiera vilka som behöver uppdateras
3. Skapa nya modeller med 5-feature schema
4. Uppdatera registry.json
5. Verifiera att allt fungerar
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

def analyze_current_models():
    """Analysera nuvarande modeller och identifiera problem."""
    print("Analyserar nuvarande modeller...")
    
    models_dir = Path("config/models")
    current_models = {}
    problems = []
    
    # Analysera alla JSON-filer
    for model_file in models_dir.glob("*.json"):
        if model_file.name == "registry.json":
            continue
            
        try:
            with open(model_file, 'r') as f:
                data = json.load(f)
            
            model_name = model_file.stem
            current_models[model_name] = data
            
            # Kontrollera schema
            for timeframe, config in data.items():
                if isinstance(config, dict) and 'schema' in config:
                    schema = config['schema']
                    if len(schema) == 2 and schema == ["ema_delta_pct", "rsi"]:
                        problems.append({
                            'file': model_file.name,
                            'timeframe': timeframe,
                            'issue': 'Gamla 2-feature schema',
                            'current_schema': schema
                        })
                    elif len(schema) == 5:
                        print(f"OK {model_file.name}:{timeframe} - Redan avancerad schema")
                    else:
                        problems.append({
                            'file': model_file.name,
                            'timeframe': timeframe,
                            'issue': 'Okänd schema längd',
                            'current_schema': schema
                        })
                        
        except Exception as e:
            problems.append({
                'file': model_file.name,
                'issue': f'JSON parse error: {e}'
            })
    
    return current_models, problems

def analyze_registry():
    """Analysera registry.json för att se vilka modeller som används."""
    print("\nAnalyserar registry.json...")
    
    try:
        with open("config/models/registry.json", 'r') as f:
            registry = json.load(f)
        
        registry_issues = []
        for key, value in registry.items():
            if isinstance(value, dict) and 'champion' in value:
                champion_path = value['champion']
                if not os.path.exists(champion_path):
                    registry_issues.append({
                        'key': key,
                        'issue': f'Champion model saknas: {champion_path}'
                    })
                elif 'tBTCUSD.json' in champion_path:
                    registry_issues.append({
                        'key': key,
                        'issue': f'Pekar på gammal model: {champion_path}'
                    })
        
        return registry, registry_issues
        
    except Exception as e:
        print(f"Fel vid läsning av registry.json: {e}")
        return {}, []

def create_advanced_schema_template():
    """Skapa template för avancerad 5-feature schema."""
    return {
        "version": "v3",
        "schema": [
            "rsi_inv_lag1",
            "volatility_shift_ma3", 
            "bb_position_inv_ma3",
            "rsi_vol_interaction",
            "vol_regime"
        ],
        "buy": {
            "w": [0.24632984264101013, 0.29627872058253374, 0.37364758207066845, -0.1015278767772536, -0.10937285558591385],
            "b": -0.3012037705902129,
            "calib": {"a": 1.0, "b": 0.0}
        },
        "sell": {
            "w": [-0.24632984264093774, -0.2962787205824723, -0.3736475820705902, 0.10152787677724555, 0.10937285558588404],
            "b": 0.30120377059013576,
            "calib": {"a": 1.0, "b": 0.0}
        },
        "calibration_by_regime": {
            "buy": {
                "bear": {"method": "platt", "a": 4.1452196845980405, "b": -0.0950151904841081},
                "bull": {"method": "platt", "a": 1.2429055852810174, "b": -0.12182298132360019},
                "ranging": {"method": "platt", "a": 1.9755742797512388, "b": -0.012889927514931985}
            },
            "sell": {
                "bear": {"method": "platt", "a": 2.792164583392896, "b": 0.28828286412864296},
                "bull": {"method": "platt", "a": 0.7254672583677596, "b": 0.13367963516248377},
                "ranging": {"method": "platt", "a": 1.025879191958136, "b": 0.027000282000388818}
            }
        }
    }

def plan_model_updates():
    """Planera vilka modeller som behöver uppdateras."""
    print("\nPlanerar model uppdateringar...")
    
    # Analysera nuvarande tillstånd
    current_models, problems = analyze_current_models()
    registry, registry_issues = analyze_registry()
    
    # Skapa uppdateringsplan
    update_plan = {
        'models_to_update': [],
        'new_models_to_create': [],
        'registry_updates': [],
        'timeframe_fixes': []
    }
    
    # Identifiera modeller som behöver uppdateras
    for problem in problems:
        if problem['issue'] == 'Gamla 2-feature schema':
            update_plan['models_to_update'].append({
                'file': problem['file'],
                'timeframe': problem['timeframe'],
                'action': 'Uppdatera till 5-feature schema'
            })
    
    # Identifiera nya modeller som behöver skapas
    symbols = ['tBTCUSD', 'tETHUSD', 'tADAUSD', 'tDOTUSD', 'tDOGEUSD', 'tEOSUSD', 
               'tFILUSD', 'tLTCUSD', 'tNEARUSD', 'tSOLUSD', 'tXTZUSD', 'tXAUTUSD']
    
    timeframes = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '1D']
    
    for symbol in symbols:
        for timeframe in timeframes:
            model_file = f"{symbol}_{timeframe}.json"
            if not os.path.exists(f"config/models/{model_file}"):
                update_plan['new_models_to_create'].append({
                    'file': model_file,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'action': 'Skapa ny model med 5-feature schema'
                })
    
    # Identifiera registry uppdateringar
    for issue in registry_issues:
        if 'Pekar på gammal model' in issue['issue']:
            update_plan['registry_updates'].append({
                'key': issue['key'],
                'action': 'Uppdatera till ny model'
            })
    
    # Identifiera timeframe fixes (4h -> 3h/6h)
    for problem in problems:
        if problem.get('timeframe') == '4h':
            update_plan['timeframe_fixes'].append({
                'file': problem['file'],
                'timeframe': '4h',
                'action': 'Byt till 3h eller 6h'
            })
    
    return update_plan, current_models, registry

def print_analysis_report(update_plan, current_models, registry):
    """Skriv ut analysrapport."""
    print("\n" + "="*80)
    print("MODEL REGISTRY ANALYS RAPPORT")
    print("="*80)
    
    print(f"\nTotalt antal modeller analyserade: {len(current_models)}")
    print(f"Registry entries: {len(registry)}")
    
    print(f"\nModeller som behöver uppdateras: {len(update_plan['models_to_update'])}")
    for item in update_plan['models_to_update']:
        print(f"   - {item['file']}:{item['timeframe']} - {item['action']}")
    
    print(f"\nNya modeller att skapa: {len(update_plan['new_models_to_create'])}")
    for item in update_plan['new_models_to_create'][:10]:  # Visa första 10
        print(f"   - {item['file']} - {item['action']}")
    if len(update_plan['new_models_to_create']) > 10:
        print(f"   ... och {len(update_plan['new_models_to_create']) - 10} fler")
    
    print(f"\nRegistry uppdateringar: {len(update_plan['registry_updates'])}")
    for item in update_plan['registry_updates']:
        print(f"   - {item['key']} - {item['action']}")
    
    print(f"\nTimeframe fixes: {len(update_plan['timeframe_fixes'])}")
    for item in update_plan['timeframe_fixes']:
        print(f"   - {item['file']}:{item['timeframe']} - {item['action']}")
    
    print("\n" + "="*80)
    print("NASTA STEG:")
    print("1. Skapa nya modeller med 5-feature schema")
    print("2. Uppdatera registry.json")
    print("3. Ta bort gamla modeller")
    print("4. Verifiera att allt fungerar")
    print("="*80)

def main():
    """Huvudfunktion för att köra analysen."""
    print("Startar Model Registry Analys...")
    
    try:
        # Analysera och planera
        update_plan, current_models, registry = plan_model_updates()
        
        # Skriv ut rapport
        print_analysis_report(update_plan, current_models, registry)
        
        # Spara planen till fil
        with open("model_update_plan.json", 'w') as f:
            json.dump(update_plan, f, indent=2)
        
        print(f"\nUppdateringsplan sparad till: model_update_plan.json")
        
    except Exception as e:
        print(f"Fel under analys: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()