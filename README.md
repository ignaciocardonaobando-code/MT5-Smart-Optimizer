# MT5-Smart-Optimizer

Vamos crear y construir un optimizador de estrategias inteligente para la Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5.

* Que importe las bases de datos de un archivo .json o .yaml.
* Que se apoye en un archivo .mqh para exportar la información.
* Que sea capaz de analizar los parámetros configurables de la estrategia (ya existente) en MetaEditor (editor del lenguaje MetraQuotes).
* Que pueda probar diferentes combinaciones de los parámetros configurables de la estrategia que estamos evaluando (archivo .json o yaml).
* Que sea capaz de devolverme automáticamente los mejores valores (net profit de las pruebas).
* Que importe la base de datos / ficheros del Probador de Estrategias, lance backtests en lote y devuelva las combinaciones óptimas.

## El optimizador inteligente debe pedir (items fijos siempre):

1. **Experto**: Estrategia a probar (ya compilada en: C:\\Users\\ignac\\AppData\\Roaming\\MetaQuotes\\Terminal\\XXXXXXXXXXX\\MQL5\\Experts).
2. **Símbolo**: Activo a evaluar.
3. **Intervalo**: El rango de fecha para la prueba (período personalizado).
4. **Depósito inicial**.
5. **Lot Size**.
6. **Apalancamiento**.
7. **El resto de los items** que no se vayan a evaluar y que sean siempre iguales en todas las pruebas. Por ejemplo:
   - Mínima distancia entre SL y TP basada en ATR
   - Solo una orden por símbolo
   - Solo una orden por cuenta
   - El Timeframe único para BB y Stochastic siempre será igual a la periodicidad que estemos evaluando
   - Etc...

El optimizador inteligente debe trabajar siempre cada Tick a base de Ticks reales, sin retrasos, ejecución ideal y debe revisar todos los parámetros configurables de la estrategia y buscar la mejor combinación (la más rentable).

## El optimizador inteligente debe evaluar (items variables siempre):

1. **Periodicidad**: Solo M30, H1, H2, H3, H4 y H6
2. **Periodo de las Bollinger Bands**
3. **Desviación estándar BB**
4. **%K del Stochastic**
5. **%D del Stochastic**
6. **Slowing del Stochastic**
7. **SL = ATR * multiplicador**
8. **TP = ATR * multiplicador**
9. **Trailing Stop = ATR * multiplicador**
10. **Mínima diferencia entre %K y %D**
