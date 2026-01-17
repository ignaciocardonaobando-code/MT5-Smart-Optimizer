//+------------------------------------------------------------------+
//|  Estrategia IC (Ignacio Cardona)                                 |
//|  Basada en Estrategia Boll Stoch ATR Agresiva VFinal             |
//|  Modificación: permitir 2 órdenes por símbolo con espera         |
//|  mínima de barras para la segunda entrada.                       |
//+------------------------------------------------------------------+
#property strict
#include <Trade\Trade.mqh>
#include <so_report.mqh>

CTrade trade;

//=============================//
//  PARÁMETROS CONFIGURABLES   //
input int    bb_period                      = 20;
input double bb_deviation                   = 2.0;
input int    sto_period_k                   = 14;
input int    sto_period_d                   = 3;
input int    sto_slowing                    = 3;
input ENUM_TIMEFRAMES timeframe_indicadores = PERIOD_CURRENT;

input double lot_size                       = 0.01;
input int    sl_atr_multiplier              = 20;
input int    tp_atr_multiplier              = 2;
input double atrMultiplierTrailing          = 0.5;
input double margen_cruce                   = 0.5;

//=============================//
//   PARÁMETROS GENERALES      //
input double minDistanceToTPMultiplier      = 0.5;
input bool   allow_one_order_per_symbol     = false;
input bool   allow_one_order_per_account    = false;
input int    atr_period                     = 14;

//=============================//
//   PARÁMETROS IC (NUEVOS)    //
input int    max_orders_per_symbol          = 2;   // Límite máximo por símbolo.
input int    bars_wait_second_order         = 6;   // Barras mínimas desde la 1a orden.

//=============================//
int bb_handle=INVALID_HANDLE, sto_handle=INVALID_HANDLE, atr_handle=INVALID_HANDLE;

//=============================//
//   Helpers de exportación    //
string BuildInputsJSON()
{
  string inputs_json="{";
  inputs_json += "\"bb_period\":"+IntegerToString((int)bb_period)+",";
  inputs_json += "\"bb_deviation\":"+DoubleToString((double)bb_deviation,2)+",";
  inputs_json += "\"sto_period_k\":"+IntegerToString((int)sto_period_k)+",";
  inputs_json += "\"sto_period_d\":"+IntegerToString((int)sto_period_d)+",";
  inputs_json += "\"sto_slowing\":"+IntegerToString((int)sto_slowing)+",";
  inputs_json += "\"timeframe_indicadores\":\""+EnumToString(timeframe_indicadores)+"\",";
  inputs_json += "\"lot_size\":"+DoubleToString(lot_size,2)+",";
  inputs_json += "\"sl_atr_multiplier\":"+IntegerToString((int)sl_atr_multiplier)+",";
  inputs_json += "\"tp_atr_multiplier\":"+IntegerToString((int)tp_atr_multiplier)+",";
  inputs_json += "\"atrMultiplierTrailing\":"+DoubleToString(atrMultiplierTrailing,2)+",";
  inputs_json += "\"margen_cruce\":"+DoubleToString(margen_cruce,2)+",";
  inputs_json += "\"minDistanceToTPMultiplier\":"+DoubleToString(minDistanceToTPMultiplier,2)+",";
  inputs_json += "\"allow_one_order_per_symbol\":"+string(allow_one_order_per_symbol?"true":"false")+",";
  inputs_json += "\"allow_one_order_per_account\":"+string(allow_one_order_per_account?"true":"false")+",";
  inputs_json += "\"atr_period\":"+IntegerToString((int)atr_period)+",";
  inputs_json += "\"max_orders_per_symbol\":"+IntegerToString((int)max_orders_per_symbol)+",";
  inputs_json += "\"bars_wait_second_order\":"+IntegerToString((int)bars_wait_second_order)+",";
  inputs_json += "\"symbol\":\""+_Symbol+"\"";
  inputs_json += "}";
  return inputs_json;
}

//=============================//
//         INIT / DEINIT       //
int OnInit()
{
  // iBands(symbol, tf, period, shift, deviation, price)
  bb_handle  = iBands(_Symbol, timeframe_indicadores, (int)bb_period, (int)0, (double)bb_deviation, (ENUM_APPLIED_PRICE)PRICE_CLOSE);
  if(bb_handle==INVALID_HANDLE){ Print("❌ iBands inválido"); return INIT_FAILED; }

  // iStochastic(symbol, tf, K, D, Slowing, MA, PRICE)
  sto_handle = iStochastic(_Symbol, timeframe_indicadores, (int)sto_period_k, (int)sto_period_d, (int)sto_slowing, (ENUM_MA_METHOD)MODE_SMA, (ENUM_STO_PRICE)STO_LOWHIGH);
  if(sto_handle==INVALID_HANDLE){ Print("❌ iStochastic inválido"); return INIT_FAILED; }

  atr_handle = iATR(_Symbol, timeframe_indicadores, (int)atr_period);
  if(atr_handle==INVALID_HANDLE){ Print("❌ iATR inválido"); return INIT_FAILED; }

  string tag = (StringLen(so_run_id)>0 ? so_run_id : "run_auto");
  PrintFormat("RUN_START %s | TF=%s", tag, EnumToString(timeframe_indicadores));
  return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
  // Exportar SIEMPRE al finalizar el test simple (y también útil en vivo)
  if(MQLInfoInteger(MQL_TESTER))
  {
    string inputs_json = BuildInputsJSON();
    SO_ReportOnTesterDeinit(inputs_json);

    double fb = AccountInfoDouble(ACCOUNT_BALANCE);
    string tag = (StringLen(so_run_id)>0 ? so_run_id : "run_auto");
    PrintFormat("final balance %.2f USD | run_tag=%s", fb, tag);
    PrintFormat("RUN_END %s", tag);
  }
}

//=============================//
//    UTILIDADES DE CONTROL    //
int CountOpenPositionsBySymbol(const string symbol)
{
  int count = 0;
  for(int i=0;i<PositionsTotal();i++)
  {
    ulong tk = PositionGetTicket(i);
    if(PositionSelectByTicket(tk))
    {
      string sym = PositionGetString(POSITION_SYMBOL);
      if(sym == symbol) count++;
    }
  }
  return count;
}

bool HasAnyOpenPosition()
{
  for(int i=0;i<PositionsTotal();i++)
  {
    ulong tk = PositionGetTicket(i);
    if(PositionSelectByTicket(tk)) return true;
  }
  return false;
}

bool CanOpenSecondOrder(const string symbol)
{
  // Se requiere que exista una primera orden abierta y que hayan pasado N barras.
  datetime oldest_time = 0;
  int count = 0;

  for(int i=0;i<PositionsTotal();i++)
  {
    ulong tk = PositionGetTicket(i);
    if(PositionSelectByTicket(tk))
    {
      string sym = PositionGetString(POSITION_SYMBOL);
      if(sym != symbol) continue;
      datetime open_time = (datetime)PositionGetInteger(POSITION_TIME);
      if(count == 0 || open_time < oldest_time) oldest_time = open_time;
      count++;
    }
  }

  if(count < 1) return false;

  int open_bar_index = iBarShift(symbol, timeframe_indicadores, oldest_time, true);
  if(open_bar_index < 0) return false;

  int current_bar_index = iBarShift(symbol, timeframe_indicadores, TimeCurrent(), true);
  if(current_bar_index < 0) return false;

  int bars_elapsed = open_bar_index - current_bar_index;
  return (bars_elapsed >= bars_wait_second_order);
}

bool IsOrderOpenAllowed()
{
  int symbol_positions = CountOpenPositionsBySymbol(_Symbol);

  if(allow_one_order_per_account && HasAnyOpenPosition()) return false;

  if(allow_one_order_per_symbol)
  {
    if(symbol_positions >= 1) return false;
    return true;
  }

  // Lógica IC: permitir hasta 2 órdenes por símbolo si se cumplen las barras.
  if(symbol_positions >= max_orders_per_symbol) return false;
  if(symbol_positions == 1) return CanOpenSecondOrder(_Symbol);
  return true;
}

void ExecuteOrder(const string type, const double price, const double sl, const double tp)
{
  if(!IsOrderOpenAllowed())
  {
    Print("⛔ Orden NO ejecutada: límite de posiciones o espera de barras.");
    return;
  }
  if(type=="BUY"){  if(trade.Buy (lot_size,_Symbol,price,sl,tp)) Print("🟢 BUY enviada | SL:", sl, " | TP:", tp); }
  if(type=="SELL"){ if(trade.Sell(lot_size,_Symbol,price,sl,tp)) Print("🔴 SELL enviada | SL:", sl, " | TP:", tp); }
}

//=============================//
//     TRAILING POR ATR        //
void ManageTrailingStop()
{
  double v[1]; if(CopyBuffer(atr_handle,0,0,1,v)<=0 || v[0]<=0) return;
  double atr = v[0];

  double bid = SymbolInfoDouble(_Symbol,SYMBOL_BID);
  double ask = SymbolInfoDouble(_Symbol,SYMBOL_ASK);
  double mind = atr*minDistanceToTPMultiplier;

  // Aplicar trailing a TODAS las posiciones del símbolo.
  for(int i=0;i<PositionsTotal();i++)
  {
    ulong tk = PositionGetTicket(i);
    if(!PositionSelectByTicket(tk)) continue;

    string sym = PositionGetString(POSITION_SYMBOL);
    if(sym != _Symbol) continue;

    double slc = PositionGetDouble(POSITION_SL);
    double tp  = PositionGetDouble(POSITION_TP);
    long   typ = PositionGetInteger(POSITION_TYPE);
    double op  = PositionGetDouble(POSITION_PRICE_OPEN);

    double nsl;

    if(typ==POSITION_TYPE_BUY)
    {
      if(bid<=op) continue;
      nsl = NormalizeDouble(bid - atr*atrMultiplierTrailing, _Digits);
      if( (slc<=0 || nsl>slc) && (tp-nsl)>mind && nsl>op )
        if(trade.PositionModify(tk,nsl,tp)) Print("🔁 TS (BUY) actualizado: SL =", nsl);
    }
    else if(typ==POSITION_TYPE_SELL)
    {
      if(ask>=op) continue;
      nsl = NormalizeDouble(ask + atr*atrMultiplierTrailing, _Digits);
      if( (slc<=0 || nsl<slc) && (nsl-tp)>mind && nsl<op )
        if(trade.PositionModify(tk,nsl,tp)) Print("🔁 TS (SELL) actualizado: SL =", nsl);
    }
  }
}

//=============================//
//           ONTICK            //
void OnTick()
{
  ManageTrailingStop();

  double up[1], lo[1], k[1], d[1], a[1];
  if(CopyBuffer(bb_handle,1,0,1,up)<=0) return;   // upper
  if(CopyBuffer(bb_handle,2,0,1,lo)<=0) return;   // lower
  if(CopyBuffer(sto_handle,0,0,1,k)<=0) return;   // %K
  if(CopyBuffer(sto_handle,1,0,1,d)<=0) return;   // %D
  if(CopyBuffer(atr_handle,0,0,1,a)<=0 || a[0]<=0) return; // ATR

  double close = iClose(_Symbol, PERIOD_CURRENT, 0);
  double ask   = SymbolInfoDouble(_Symbol,SYMBOL_ASK);
  double bid   = SymbolInfoDouble(_Symbol,SYMBOL_BID);

  // Reglas iguales a VFinal
  bool priceBuy  = (close < lo[0]);
  bool stochBuy  = (k[0] < 20 && k[0] > d[0] && (k[0]-d[0]) > margen_cruce);

  bool priceSell = (close > up[0]);
  bool stochSell = (k[0] > 80 && k[0] < d[0] && (d[0]-k[0]) > margen_cruce);

  if(priceBuy && stochBuy)
  {
    double sl = NormalizeDouble(ask - a[0]*sl_atr_multiplier, _Digits);
    double tp = NormalizeDouble(ask + a[0]*tp_atr_multiplier, _Digits);
    PrintFormat("✅ BUY: Close=%.5f | Lower=%.5f | K=%.2f | D=%.2f | K-D=%.2f", close, lo[0], k[0], d[0], (k[0]-d[0]));
    ExecuteOrder("BUY", ask, sl, tp);
  }
  if(priceSell && stochSell)
  {
    double sl = NormalizeDouble(bid + a[0]*sl_atr_multiplier, _Digits);
    double tp = NormalizeDouble(bid - a[0]*tp_atr_multiplier, _Digits);
    PrintFormat("✅ SELL: Close=%.5f | Upper=%.5f | K=%.2f | D=%.2f | D-K=%.2f", close, up[0], k[0], d[0], (d[0]-k[0]));
    ExecuteOrder("SELL", bid, sl, tp);
  }
}

//=============================//
//       OnTesterDeinit        //
void OnTesterDeinit()
{
  string inputs_json = BuildInputsJSON();
  SO_ReportOnTesterDeinit(inputs_json);

  double fb=AccountInfoDouble(ACCOUNT_BALANCE);
  string tag=(StringLen(so_run_id)>0? so_run_id : "run_auto");
  PrintFormat("final balance %.2f USD | run_tag=%s", fb, tag);
  PrintFormat("RUN_END %s", tag);
}
