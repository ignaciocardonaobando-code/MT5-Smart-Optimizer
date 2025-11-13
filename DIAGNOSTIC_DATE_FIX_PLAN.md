# Plan Diagnóstico Completo - Problema de Fechas en report.json

## Resumen Ejecutivo

El problema: report.json muestra fechas incorrectas (2021.01.04 - 2025.06.27) cuando debe mostrar (2022.01.01 - 2025.06.30).

**Hallazgo**: Los trades se ejecutan correctamente → El backtest usa las fechas correctas → **El problema está SOLO en el JSON export**.

## Análisis Completado

### ✅ Capa Python (optimizer_v2.py)
- Líneas 456-457: `so_start_date` y `so_end_date` se establecen correctamente desde config
- Función `norm_date_for_ini()` normaliza fechas a formato YYYY.MM.DD
- Parámetros se incluyen en `so_block` y se escriben al archivo .set
- Lógica: **CORRECTA ✅**

### ✅ Capa MQL5 (so_report.mqh)
- Líneas 13-14: Input variables declaradas correctamente
- Líneas 308-335: Lógica de override de fechas **EXISTE Y ES CORRECTA**
- `SO_ParseDateTime()` parsea fechas en formato YYYY.MM.DD
- Si los parámetros llegaran al EA, funcionaría perfectamente
- Lógica: **CORRECTA ✅**

### ❓ Problema: El Eslabón Perdido
**MetaTrader 5 NO está leyendo los parámetros del archivo .set**

Flujo esperado:
1. Python escribe .set file con `so_start_date` y `so_end_date`
2. MT5 lee el .set file
3. MT5 pasa los parámetros al EA como input strings
4. EA recibe parámetros NO VACÍOS
5. EA parsea fechas correctamente

Flujo real (hipotetizado):
1. ✅ Python escribe .set file
2. ❌ MT5 NO lee los parámetros (o los pasa como strings vacíos "")
3. ❌ EA recibe parámetros VACÍOS
4. ❌ EA usa fallback: SERIES_FIRSTDATE y TimeCurrent()
5. ❌ JSON export usa fechas incorrectas

## Pasos de Diagnóstico

### Paso 1: Verificar que el .set file se crea correctamente

En **optimizer_v2.py**, línea ~427, agregar logging:

```python
# DESPUÉS DE: set_lines = build_set_lines(set_kv)
print(f"\n{'='*70}")
print(f"DIAGNÓSTICO: Contenido del archivo .set")
print(f"{'='*70}")
for line in set_lines:
    if 'date' in line.lower() or 'so_' in line.lower():
        print(f"  {line}")
print(f"{'='*70}\n")
```

### Paso 2: Verificar que MT5 recibe los parámetros

En **so_report.mqh**, línea ~308, ANTES de procesar las fechas:

```mql
// DIAGNÓSTICO DE PARÁMETROS RECIBIDOS
PrintFormat("DIAG: so_start_date RECIBIDO: '%s' (length=%d)", so_start_date, StringLen(so_start_date));
PrintFormat("DIAG: so_end_date RECIBIDO: '%s' (length=%d)", so_end_date, StringLen(so_end_date));
```

Este PrintFormat aparecerá en el archivo de log del Expert: `tester.log`

### Paso 3: Ejecutar el diagnóstico

```powershell
# Descargar la rama de diagnóstico
git fetch origin ignaciocardonaobando-code-patch-1
git checkout ignaciocardonaobando-code-patch-1

# Aplicar los cambios de logging a optimizer_v2.py y so_report.mqh
# (Ver instrucciones en secciones siguientes)

# Ejecutar con la configuración diagnóstica
python optimizer_v2.py --config examples/config_diagnostic.json --single-run

# Analizar la salida
# - Buscar "DIAGNÓSTICO" en stdout
# - Buscar "DIAG:" en tester.log de MetaTrader 5
```

## Posibles Resultados y Soluciones

### Resultado A: MT5 SÍ recibe los parámetros
```
DIAG: so_start_date RECIBIDO: '2022.01.01' (length=10)
DIAG: so_end_date RECIBIDO: '2025.06.30' (length=10)
```
**Causa**: Problema en `SO_ParseDateTime()` o en la lógica de override
**Solución**: Revisar por qué StringToTime() falla o por qué las fechas no se aplican al JSON

### Resultado B: MT5 recibe strings VACÍOS
```
DIAG: so_start_date RECIBIDO: '' (length=0)
DIAG: so_end_date RECIBIDO: '' (length=0)
```
**Causa**: MetaTrader 5 no está leyendo los parámetros del .set file
**Soluciones posibles**:
1. La ruta del .set file es incorrecta
2. MT5 espera un formato diferente
3. El nombre del parámetro no coincide (verificar case-sensitivity)
4. Usar un método alternativo para pasar parámetros (archivo JSON)

## Configuración de Test

Usa `examples/config_diagnostic.json` (ya creado en PR #16):

```json
"from": "2022.01.01",
"to": "2025.06.30"
```

Si report.json sigue mostrando 2021.01.04 - 2025.06.27, confirma que MT5 no lee los parámetros.

## Próximos Pasos

1. ✅ Crear config_diagnostic.json (COMPLETADO)
2. ⏳ Agregar logging a optimizer_v2.py (EN PROGRESO)
3. ⏳ Agregar logging a so_report.mqh (EN PROGRESO)
4. ⏳ Ejecutar diagnóstico localmente
5. ⏳ Analizar resultados
6. ⏳ Implementar solución basada en resultados
7. ⏳ Crear PR final con fix
