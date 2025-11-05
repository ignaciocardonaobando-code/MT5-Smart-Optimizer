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
