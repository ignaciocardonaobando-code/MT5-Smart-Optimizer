#!/usr/bin/env python3
"""Smoke Test para MT5 Smart Optimizer v2
Prueba básica de importaciones y configuración"""
import sys
import os
import json

def test_imports():
    """Verifica que todas las dependencias estén instaladas"""
    try:
        import optuna
        import psutil
        import yaml
        print("✅ Todas las dependencias instaladas correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando dependencias: {e}")
        return False

def test_config_files():
    """Verifica que existan los archivos de configuración"""
    files = ['config_template.json']
    all_ok = True
    for f in files:
        if os.path.exists(f):
            print(f"✅ Archivo {f} encontrado")
            try:
                with open(f, 'r') as file:
                    json.load(file)
                print(f"✅ {f} es JSON válido")
            except:
                print(f"⚠️ {f} no es JSON válido")
                all_ok = False
        else:
            print(f"⚠️ Archivo {f} no encontrado")
    return all_ok

def test_optimizer_module():
    """Verifica que el módulo optimizer_v2 exista"""
    if os.path.exists('optimizer_v2.py'):
        print("✅ optimizer_v2.py encontrado")
        return True
    print("❌ optimizer_v2.py no encontrado")
    return False

if __name__ == '__main__':
    print("\n=== Smoke Test MT5 Smart Optimizer ===")
    tests = [
        ("Importaciones", test_imports),
        ("Archivos de configuración", test_config_files),
        ("Módulo optimizer", test_optimizer_module)
    ]
    results = []
    for name, test in tests:
        print(f"\n[{name}]")
        results.append(test())
    print("\n" + "="*40)
    if all(results):
        print("✅ Smoke test PASADO")
        sys.exit(0)
    else:
        print("❌ Smoke test FALLIDO")
        sys.exit(1)
