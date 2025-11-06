# 📚 Tutorial Completo - MT5 Smart Optimizer v2

Esta guía te llevará paso a paso desde la instalación hasta la ejecución de optimizaciones avanzadas.

## 📝 Índice

1. [Prerequisitos](#prerequisitos)
2. [Instalación](#instalación)
3. [Configuración Básica](#configuración-básica)
4. [Primera Optimización](#primera-optimización)
5. [Configuraciones Avanzadas](#configuraciones-avanzadas)
6. [Interpretación de Resultados](#interpretación-de-resultados)
7. [Mejores Prácticas](#mejores-prácticas)

---

## 🔧 Prerequisitos

Antes de comenzar, asegúrate de tener:

### Software Requerido
- **Python 3.8 o superior**
- **MetaTrader 5** instalado
- **Git** (opcional, para clonar el repositorio)

### Conocimientos Básicos
- Conceptos básicos de trading
- Familiaridad con terminal de comandos
- Conceptos de optimización de parámetros

---

## 📦 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/ignaciocardonaobando-code/MT5-Smart-Optimizer.git
cd MT5-Smart-Optimizer
```

### Paso 2: Crear Entorno Virtual

```bash
python -m venv venv
venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En Linux/Mac
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Verificar Instalación

```bash
python smoke_test.py
```

Deberías ver:
```
=== Smoke Test MT5 Smart Optimizer ===
✅ Todas las dependencias instaladas correctamente
✅ Archivo config_template.json encontrado
✅ optimizer_v2.py encontrado
✅ Smoke test PASADO
```

---

## ⚙️ Configuración Básica

### Paso 1: Copiar Plantilla de Configuración

```bash
cp config_template.json mi_config.json
```

### Paso 2: Editar Configuración

Abre `mi_config.json` y configura:

#### Sección MT5
```json
"mt5": {
  "terminal": "C:/Program Files/MetaTrader 5/terminal64.exe",
  "login": 12345678,
  "password": "tu_password",
  "server": "TuBroker-Demo"
}
```

#### Sección Test
```json
"test": {
  "symbol": "EURUSD",
  "timeframe": "H1",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31",
  "deposit": 10000,
  "leverage": 100
}
```

#### Sección EA
```json
"ea": {
  "name": "Estrategia_Boll_Stoch_ATR_Agresiva_VFinal",
  "path": "Experts/Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5"
}
```

### Paso 3: Validar Configuración
```bash
python validate_config.py mi_config.json
```

---

## 🚀 Primera Optimización

### Optimización Rápida (10 trials)

```bash
python optimizer_v2.py --config mi_config.json --trials 10
```

### Qué Esperar

1. **Inicio**: El optimizer se conecta a MT5
```
INFO     | Iniciando optimización | Context: {"symbol":"EURUSD","timeframe":"H1"}
```

2. **Ejecución**: Verás el progreso de cada trial
```
Trial 1/10: Testing params {"BBPeriod":20, "StochK":14...}
Trial 2/10: Testing params {"BBPeriod":25, "StochK":12...}
...
```

3. **Resultados**: Al finalizar verás los mejores parámetros
```
✅ Optimización completada
Mejor Profit Factor: 1.85
Mejores Parámetros:
  BBPeriod: 22
  StochK: 13
  ATRPeriod: 14
  ...
```

---

## 🔥 Configuraciones Avanzadas

### 1. Optimización Exhaustiva

**Configuración**: 100+ trials para exploración profunda

```json
"optimizer": {
  "n_trials": 200,
  "timeout": 7200,
  "n_jobs": 4
}
```

Ejecución:
```bash
python optimizer_v2.py --config config_exhaustivo.json
```

### 2. Optimización Multi-Timeframe

Prueba el mismo EA en diferentes timeframes:

```bash
python optimizer_v2.py --config config_h1.json --trials 50
python optimizer_v2.py --config config_h4.json --trials 50
python optimizer_v2.py --config config_d1.json --trials 50
```

### 3. Walk-Forward Optimization

Divide datos en periodos:

**Periodo 1**: Entrenamiento
```json
"from_date": "2024-01-01",
"to_date": "2024-06-30"
```

**Periodo 2**: Validación
```json
"from_date": "2024-07-01",
"to_date": "2024-12-31"
```

---

## 📊 Interpretación de Resultados

### Métricas Clave

#### Profit Factor
- **> 2.0**: Excelente
- **1.5 - 2.0**: Bueno
- **1.0 - 1.5**: Aceptable
- **< 1.0**: Evitar

#### Drawdown
- **< 10%**: Muy conservador
- **10% - 20%**: Moderado
- **20% - 30%**: Agresivo
- **> 30%**: Muy arriesgado

#### Sharpe Ratio
- **> 2.0**: Excelente
- **1.0 - 2.0**: Bueno
- **< 1.0**: Mejorar

### Logs

Los logs se guardan en `logs/MT5Optimizer.log`:

```bash
tail -f logs/MT5Optimizer.log
```

---

## ✅ Mejores Prácticas

### 1. Validación de Datos

```bash
# Siempre validar antes de ejecutar
python validate_config.py mi_config.json
```

### 2. Backups de Configuración

```bash
# Guardar configuraciones exitosas
cp mi_config.json configs/backup_2024_11_05.json
```

### 3. Testing Incremental

1. **10 trials**: Prueba rápida
2. **50 trials**: Validación intermedia  
3. **200 trials**: Optimización final

### 4. Documentar Resultados

Crea un log de tus optimizaciones:

```markdown
# Optimizaciones EURUSD H1

## 2024-11-05
- Trials: 200
- Mejor PF: 1.85
- DD: 12.5%
- Parámetros: ver config_eurusd_h1_best.json
```

### 5. Evitar Overfitting

- No optimizar con periodos muy cortos (< 3 meses)
- Validar siempre en datos out-of-sample
- Preferir parámetros simples sobre complejos

---

## 🔗 Recursos Adicionales

- **Troubleshooting**: Ver `TROUBLESHOOTING.md`
- **Ejemplos**: Ver carpeta `examples/`
- **API Reference**: Ver comentarios en `optimizer_v2.py`

---

## 📞 Soporte

¿Problemas? Consulta:
1. `TROUBLESHOOTING.md` - Soluciones comunes
2. Issues en GitHub
3. Logs en `logs/MT5Optimizer.log`

---

**¡Feliz Optimización! 🚀**
