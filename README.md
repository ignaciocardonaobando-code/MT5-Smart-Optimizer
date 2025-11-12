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
   - Copia `Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5` a:
     `C:\\Users\\TU_USUARIO\\AppData\\Roaming\\MetaQuotes\\Terminal\\TU_HASH\\MQL5\\Experts\\`
   
   - Copia `so_report.mqh` a:
     `C:\\Users\\TU_USUARIO\\AppData\\Roaming\\MetaQuotes\\Terminal\\TU_HASH\\MQL5\\Include\\`

---

## 🚀 Cómo Usar

### Requisitos Previos

- **MetaTrader 5** instalado
- **Python 3.8+** con las siguientes librerías:
  - `optuna`
  - `pyyaml` (para archivos .yaml)
  - `json` (incluido en Python)

### Pasos de Ejecución
1. **Configurar el archivo .json o .yaml** con los parámetros deseados
2. **Compilar la estrategia** en MetaEditor (si no está compilada)
3. **Ejecutar el optimizador**:
   ```bash
   python optimizer_v2.py --config optuna_h4_fast.json
   ```
4. **Revisar los resultados** exportados por `so_report.mqh`
5. **Aplicar la mejor combinación** encontrada en tu estrategia

### Proceso de optimización por etapas

El flujo recomendado para optimizar la estrategia **Boll Stoch ATR Agresiva VFinal** se divide en cinco etapas consecutivas. Todos los comandos siguientes se ejecutan desde **PowerShell** en Windows, ajustando rutas y símbolos según tu entorno.

> 📁 **Archivos de configuración incluidos**
>
> Cada etapa cuenta con su propio archivo base en la raíz del repositorio:
>
> - `test_stage01_grid.json`: búsqueda de timeframe y `sto_period_k`.
> - `test_stage02_grid.json`: ajuste de `atrMultiplierTrailing` y `margen_cruce`.
> - `test_stage03_grid.json`: ajuste de `sto_period_d` y `sto_slowing`.
> - `test_stage04_grid.json`: ajuste de `sl_atr_multiplier` y `tp_atr_multiplier`.
> - `test_stage05_grid.json`: ajuste de `bb_period` y `bb_deviation`.
>
> Duplica el archivo correspondiente por cada activo, cambia `symbol` y cualquier valor fijo necesario (por ejemplo `timeframe`, `sto_period_k`, etc.) y, si deseas identificar los runs en los reportes, modifica también `so_run_id` dentro de `ea.inputs`.

#### Paso 01: Timeframe y Sto_K

1. Duplica `test_stage01_grid.json` por cada activo a optimizar y reemplaza `"symbol": "X"` por el ticker deseado.
2. Mantén `so_run_id` y, si utilizas un Optuna Storage externo, el `study_name` únicos para cada activo, por ejemplo: `"so_run_id": "stage01_eurusd_2025-11-10"`.
3. Ejecuta la búsqueda de parámetros:
   ```powershell
   python C:\MT5_Smart_Optimizer\optimizer_v2.py `
     -c C:\MT5_Smart_Optimizer\test_stage01_grid.json `
     --exe "C:\Program Files\Pepperstone 61421063\terminal64.exe" `
     --n-trials 60 --n-jobs 1 `
     --guard-sec 1200 `
     --auto-close
   ```
4. Para revisar los mejores resultados utiliza `top5_from_runs.py` o, preferiblemente, `top5_from_runs_fixed.py`:
   ```powershell
   python C:\MT5_Smart_Optimizer\top5_from_runs.py `
     --base "$env:APPDATA\MetaQuotes\Terminal\Common\Files\MT5_SO" `
     --out "C:\MT5_Smart_Optimizer\runs\reports\top5_runs.csv" `
     --top 5 `
     --assumed_deposit 1000

   python C:\MT5_Smart_Optimizer\top5_from_runs_fixed.py `
     --base "$env:APPDATA\MetaQuotes\Terminal\Common\Files\MT5_SO" `
     --out "C:\MT5_Smart_Optimizer\runs\reports\top5_runs.csv" `
     --top 5 `
     --assumed_deposit 1000
   ```
   Estos scripts generan un ranking y un CSV con métricas clave (profit, profit factor, expected payoff, drawdown, entre otros).

#### Paso 02: Trailing Stop y margen de cruce

1. Toma los dos mejores resultados del paso anterior y fija el `timeframe` y `sto_period_k` (sto_k) correspondientes en `test_stage02_grid.json`.
2. Ejecuta dos veces la optimización (una por cada combinación seleccionada):
   ```powershell
   python C:\MT5_Smart_Optimizer\optimizer_v2.py `
     -c C:\MT5_Smart_Optimizer\test_stage02_grid.json `
     --exe "C:\Program Files\Pepperstone 61421063\terminal64.exe" `
     --n-trials 70 --n-jobs 1 `
     --guard-sec 1500 `
     --auto-close
   ```

#### Paso 03: Sto_D y Sto_S

Utiliza los parámetros fijados anteriormente y busca las mejores combinaciones de `sto_d` y `sto_s`:
```powershell
python C:\MT5_Smart_Optimizer\optimizer_v2.py `
  -c C:\MT5_Smart_Optimizer\test_stage03_grid.json `
  --exe "C:\Program Files\Pepperstone 61421063\terminal64.exe" `
  --n-trials 36 --n-jobs 1 `
  --guard-sec 1200 `
  --auto-close
```

#### Paso 04: Stop Loss y Take Profit

```powershell
python C:\MT5_Smart_Optimizer\optimizer_v2.py `
  -c C:\MT5_Smart_Optimizer\test_stage04_grid.json `
  --exe "C:\Program Files\Pepperstone 61421063\terminal64.exe" `
  --n-trials 50 --n-jobs 1 `
  --guard-sec 1500 `
  --auto-close
```

#### Paso 05: Bollinger Bands

```powershell
python C:\MT5_Smart_Optimizer\optimizer_v2.py `
  -c C:\MT5_Smart_Optimizer\test_stage05_grid.json `
  --exe "C:\Program Files\Pepperstone 61421063\terminal64.exe" `
  --n-trials 49 --n-jobs 1 `
  --guard-sec 1500 `
  --auto-close
```

#### Validación final

Con la mejor combinación encontrada, ejecuta una corrida directa y guarda los artefactos generados (HTML, PNG y Excel) en la carpeta de resultados elegida, por ejemplo: `C:\MT5_Smart_Optimizer\runs\20251108 EURUSD BEST`.

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
