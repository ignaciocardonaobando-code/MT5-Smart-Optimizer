# 🔧 Guía de Troubleshooting - MT5 Smart Optimizer v2

Esta guía te ayudará a resolver los problemas más comunes al usar el optimizer.

## 📝 Índice

1. [Problemas de Instalación](#problemas-de-instalación)
2. [Errores de Conexión MT5](#errores-de-conexión-mt5)
3. [Errores de Configuración](#errores-de-configuración)
4. [Problemas de Optimización](#problemas-de-optimización)
5. [Errores de Rendimiento](#errores-de-rendimiento)
6. [Logs y Debugging](#logs-y-debugging)

---

## 📦 Problemas de Instalación

### Error: "ModuleNotFoundError: No module named 'optuna'"

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r requirements.txt
```

**Verificar**:
```bash
python smoke_test.py
```

### Error: "Python version 3.7 not supported"

**Causa**: Versión de Python antigua

**Solución**:
- Instalar Python 3.8 o superior
- Verificar versión:
```bash
python --version
```

### Smoke Test Falla

**Síntomas**: `python smoke_test.py` muestra errores

**Solución paso a paso**:
1. Verificar entorno virtual activado
2. Reinstalar dependencias:
```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```
3. Verificar archivos:
```bash
ls -la  # Linux/Mac
dir     # Windows
```

---

## 🔌 Errores de Conexión MT5

### Error: "MT5 terminal not found"

**Causa**: Ruta incorrecta al terminal MT5

**Solución**:
1. Verificar ruta en `config.json`:
```json
"terminal": "C:/Program Files/MetaTrader 5/terminal64.exe"
```

2. Rutas comunes:
   - Windows: `C:/Program Files/MetaTrader 5/terminal64.exe`
   - Windows (32-bit): `C:/Program Files (x86)/MetaTrader 5/terminal.exe`

3. Buscar manualmente:
```bash
# Windows
where terminal64.exe
```

### Error: "Login failed - Invalid credentials"

**Causa**: Credenciales incorrectas

**Verificaciones**:
1. Login correcto (número de cuenta)
2. Password correcta
3. Servidor correcto (ej: "TuBroker-Demo")
4. Cuenta activa en MT5

**Solución**:
- Probar login manual en MT5
- Verificar en MT5: Tools > Options > Server
- Para demo: Usar credenciales de cuenta demo

### Error: "Connection timeout"

**Causa**: Firewall o conexión lenta

**Solución**:
1. Verificar conexión a internet
2. Desactivar firewall temporalmente
3. Aumentar timeout en config:
```json
"optimizer": {
  "timeout": 3600
}
```

---

## ⚙️ Errores de Configuración

### Error: "Invalid timeframe"

**Causa**: Timeframe no soportado

**Timeframes válidos**:
- M30, H1, H2, H3, H4, H6, D1

**Solución**:
```json
"timeframe": "H1"  // Correcto
"timeframe": "M15" // ER
