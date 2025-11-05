#!/usr/bin/env python3
"""validate_config.py - Validador de configuración para MT5 Smart Optimizer v2"""
import argparse, json, sys
from pathlib import Path

class ConfigValidator:
    REQUIRED = {'mt5': ['terminal_path', 'terminal_hash'], 'test': ['symbol', 'timeframe', 'from', 'to', 'deposit', 'leverage'], 'ea': ['name']}
    TIMEFRAMES = ['M30', 'H1', 'H2', 'H3', 'H4', 'H6', 'D1']
    
    def __init__(self, path): self.path, self.errors, self.warnings = Path(path), [], []
    
    def validate(self):
        try: self.cfg = json.loads(Path(self.path).read_text())
        except Exception as e: self.errors.append(f"Error: {e}"); return False
        
        for b in ['mt5', 'test', 'ea']:
            if b not in self.cfg: self.errors.append(f"Falta bloque: {b}")
        
        if 'mt5' in self.cfg:
            for f in self.REQUIRED['mt5']:
                if not self.cfg['mt5'].get(f): self.errors.append(f"Falta mt5.{f}")
            if 'terminal_path' in self.cfg['mt5'] and not Path(self.cfg['mt5']['terminal_path']).exists():
                self.warnings.append("Terminal MT5 no encontrado")
        
        if 'test' in self.cfg:
            t = self.cfg['test']
            for f in self.REQUIRED['test']:
                if not t.get(f): self.errors.append(f"Falta test.{f}")
            if t.get('timeframe') not in self.TIMEFRAMES:
                self.errors.append(f"Timeframe inválido: {t.get('timeframe')}")
        
        if 'ea' in self.cfg and not self.cfg['ea'].get('name'):
            self.errors.append("Falta ea.name")
        
        print(f"\n{'='*60}\nValidación: {self.path}\n{'='*60}")
        if self.errors: print(f"\n❌ ERRORES:\n" + "\n".join(f"  {i+1}. {e}" for i,e in enumerate(self.errors)))
        if self.warnings: print(f"\n⚠️  ADVERTENCIAS:\n" + "\n".join(f"  {i+1}. {w}" for i,w in enumerate(self.warnings)))
        if not self.errors: print("\n✅ Configuración válida")
        print(f"\n{'='*60}\n")
        return len(self.errors) == 0

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('config', help='Archivo de configuración')
    args = p.parse_args()
    sys.exit(0 if ConfigValidator(args.config).validate() else 1)
