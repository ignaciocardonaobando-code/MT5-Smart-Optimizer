# MT5 Smart Optimizer v2

## 📊 Descripción del Proyecto

**MT5 Smart Optimizer v2** es un optimizador inteligente de estrategias de trading desarrollado para **MetaTrader 5**, diseñado específicamente para optimizar la estrategia **Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5** mediante el uso de Optuna y backtesting automatizado.

Este optimizador automatiza el proceso de búsqueda de los mejores parámetros para maximizar el **Net Profit**, ejecutando múltiples combinaciones de parámetros y devolviendo las configuraciones óptimas.

---

## 📁 Estructura del Proyecto

### Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| `optimizer_v2.py` | Script principal en Python que ejecuta la optimización usando Optuna |
| `Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5` | Estrategia compilada de MT5 (Expert Advisor) a optimizar |
| `so_report.mqh` | Librería MQL5 para exportar resultados del backtesting |
| `optuna_h4_fast.json` | Archivo de configuración con parámetros para optimización rápida en H4 |
| `test_single_h1_structured.json` | Archivo de configuración para pruebas estructuradas en H1 |

---

## ⚙️ Funcionalidades Principales

El optimizador está diseñado para:

✅ **Importar configuraciones** desde archivos `.json` o `.yaml`
✅ **Exportar resultados** mediante el archivo `.mqh` (so_report.mqh)  
✅ **Analizar parámetros configurables** de la estrategia en MetaEditor  
✅ **Probar múltiples combinaciones** de parámetros automáticamente  
✅ **Identificar los mejores valores** basados en Net Profit  
✅ **Ejecutar backtests en lote** desde el Probador de Estrategias de MT5  
✅ **Devolver combinaciones óptimas** al finalizar el proceso

---

## 📝 Parámetros de Configuración

### 🔒 Parámetros Fijos (obligatorios en cada ejecución)

Estos parámetros deben definirse al iniciar la optimización:

1. **Experto (Expert Advisor)**: Ruta del archivo `.ex5` compilado
   - Ejemplo: `C:\\Users\\ignac\\AppData\\Roaming\\MetaQuotes\\Terminal\\XXXXXXXXXXX\\MQL5\\Experts\\Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5`
2. **Símbolo**: Par de divisas o activo a evaluar (ej: EURUSD, GBPUSD)
3. **Intervalo de fechas**: Período de backtesting (fecha inicio - fecha fin)
4. **Depósito inicial**: Capital inicial para las pruebas
5. **Lot Size**: Tamaño de lote para las operaciones
6. **Apalancamiento**: Relación de apalancamiento (ej: 1:100, 1:500)
7. **Parámetros constantes** (se mantienen iguales en todas las pruebas):
   - Mínima distancia entre SL y TP basada en ATR
   - Solo una orden por símbolo
   - Solo una orden por cuenta
   - El Timeframe para BB y Stochastic coincidirá con la periodicidad evaluada

**Modo de Ejecución**: Cada Tick con datos de **Ticks reales**, sin retrasos, ejecución ideal.

---

### 🔄 Parámetros Variables (optimizados automáticamente)

El optimizador evaluará las siguientes variables para encontrar la mejor combinación:

1. **Periodicidad**: M30, H1, H2, H3, H4, H6
2. **Periodo de Bollinger Bands** (número de periodos)
3. **Desviación Estándar de BB** (multiplicador de desviación)
4. **%K del Stochastic** (período de %K)
5. **%D del Stochastic** (período de %D)
6. **Slowing del Stochastic** (suavizado)
7. **Stop Loss**: ATR × multiplicador
8. **Take Profit**: ATR × multiplicador
9. **Trailing Stop**: ATR × multiplicador
10. **Mínima diferencia entre %K y %D** (para validación de señales)

---

## 💾 Instalación

### 1. Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11 (MetaTrader 5 es exclusivo de Windows)
- **Python**: 3.8 o superior
- **MetaTrader 5**: Instalado y configurado
- **Git**: Para clonar el repositorio (opcional)

### 2. Clonar el Repositorio

```bash
git clone https://github.com/ignaciocardonaobando-code/MT5-Smart-Optimizer.git
cd MT5-Smart-Optimizer
```

### 3. Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv
# Activar entorno virtual
# En Windows:
venv\\Scripts\\activate
# En PowerShell:
venv\\Scripts\\Activate.ps1
```

### 4. Instalar Dependencias

```bash
# Instalar dependencias básicas (requeridas)
pip install -r requirements.txt
# O instalar manualmente:
pip install optuna psutil PyYAML
# Dependencias opcionales para análisis:
pip install pandas numpy matplotlib
```

### 5. Verificar Instalación

```bash
python optimizer_v2.py --help
```

Deberías ver la ayuda del optimizador con todas las opciones disponibles.

### 6. Configurar MetaTrader 5

1. **Ubicar tu terminal MT5**:
   - Ejemplo: `C:\\Program Files\\MetaTrader 5\\terminal64.exe`
2. **Obtener el Hash de tu terminal**:
   - Ve a: `C:\\Users\\TU_USUARIO\\AppData\\Roaming\\MetaQuotes\\Terminal\\`
   - Copia el nombre de la carpeta con hash (ejemplo: `90A4D8F274B2E2A5D8E3F1C2B9A7E6D4`)
3. **Copiar archivos de la estrategia**:
   - Copia `Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5` a: `C:\\Users\\TU_USUARIO\\AppData\\Roaming\\MetaQuotes\\Terminal\\TU_HASH\\MQL5\\Experts\\`
   - Copia `so_report.mqh` a: `C:\\Users\\TU_USUARIO\\AppData\\Roaming\\MetaQuotes\\Terminal\\TU_HASH\\MQL5\\Include\\`

---

## 🚀 Cómo Usar

### Requisitos Previos

- **MetaTrader 5** instalado
- **Python 3.8+** con las siguientes librerías:
  - `optuna`
  - `pyyaml` (para archivos .yaml)
  - `json` (incluido en Python)

### Pasos de Ejecución

1. **Configurar el archivo .json o .yaml** con los parámetros deseados (usa `config_template.json` como base)
2. **Compilar la estrategia** en MetaEditor (si no está compilada)
3. **Lanzar un smoke test** para validar conectividad MT5 + presets:
```bash
python optimizer_v2.py --config test_single_h1_structured.json --single-run --auto-close
```
4. **Ejecutar optimizaciones completas** (Optuna) una vez validado el entorno:
```bash
python optimizer_v2.py --config optuna_h4_fast.json --n-trials 50 --auto-close
```
5. **Revisar los resultados** exportados por `so_report.mqh` (JSON + CSV en `MT5_SO/<run_id>`)
6. **Aplicar la mejor combinación** encontrada en tu estrategia o reutiliza los presets generados

> 💡 El optimizador fuerza las fechas visibles del reporte HTML usando la utilidad `override_report_html_dates`, asegurando que coincidan con el rango configurado (`test.from`, `test.to`).

### Configuración rápida del optimizador

Los archivos de configuración aceptan los siguientes bloques principales:

```json
{
  "mt5": {
    "terminal_path": "C:/Program Files/MetaTrader 5/terminal64.exe",
    "terminal_hash": "90A4D8F274B2E2A5D8E3F1C2B9A7E6D4"
  },
  "test": {
    "symbol": "EURUSD",
    "timeframe": "H1",
    "model": 0,
    "from": "2024.01.01",
    "to": "2024.06.30",
    "deposit": 1000,
    "leverage": 100
  },
  "ea": {
    "name": "Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5",
    "inputs": {
      "lot_size": 0.10,
      "atrPeriod": 14
    }
  }
}
```

Para optimizaciones con Optuna agrega el bloque `search`:

```json
  "search": {
    "space": {
      "lot_size": ["choice", [0.05, 0.10, 0.15]],
      "atrMultiplier": ["float", 1.0, 4.0]
    },
    "sampler": "tpe"
  }
```

- **TPE (por defecto)**: Omite `sampler` o usa `"tpe"` para exploración bayesiana.
- **GridSampler**: Permite barridos exhaustivos declarando todas las combinaciones.

```json
  "search": {
    "space": {
      "lot_size": ["choice", [0.05, 0.10]],
      "atrMultiplier": ["choice", [1.5, 2.0, 2.5]]
    },
    "sampler": {
      "type": "grid",
      "search_space": {
        "lot_size": [0.05, 0.10],
        "atrMultiplier": [1.5, 2.0, 2.5]
      }
    }
  }
```

Si omites `search.sampler.search_space`, el optimizador derivará el grid a partir de las variables `choice` definidas en `search.space`.

### Validaciones y smoke tests

- `smoke_test.py`: Ejecuta un ciclo corto verificando lectura de config, despliegue de presets y logging.
- `python optimizer_v2.py --config <cfg> --single-run --auto-close`: Ejecuta un único backtest y guarda los artefactos en `Common\Files\MT5_SO`.
- `pytest`: Corre los tests unitarios disponibles (logger).

---

## 📊 Resultados Esperados

Al finalizar, el optimizador generará:

✅ **Archivo de reporte** con las mejores combinaciones de parámetros  
✅ **Métricas de rendimiento**: Net Profit, Drawdown, Win Rate, etc.  
✅ **Archivos JSON/YAML actualizados** con los valores óptimos encontrados

---

## 💻 Tecnologías Utilizadas

- **Python**: Script de optimización
- **Optuna**: Framework de optimización bayesiana
- **MQL5**: Lenguaje de MetaTrader 5
- **MetaTrader 5**: Plataforma de backtesting
- **JSON/YAML**: Formato de configuración

---

## 📄 Licencia

Este proyecto es de uso personal y educativo.

---

## 👤 Autor

**Ignacio Cardona Obando**

Para dudas o sugerencias, abre un Issue en este repositorio.
