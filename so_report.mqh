//+------------------------------------------------------------------+
//|                         so_report.mqh                             |
//|   Exportador COMMON + LOCAL: report.json + trades.csv + _READY   |
//|   Métricas con TesterStatistics (tester) + fallback manual       |
//|   Tester-SAFE: FILE_COMMON + rutas relativas en FileOpen         |
//+------------------------------------------------------------------+
#property strict
#ifndef __SO_REPORT_MQH__
#define __SO_REPORT_MQH__

//---------------- Configuración del módulo ----------------
input string so_run_id       = "";   // acepta subcarpetas, p.ej. PRUEBA_MT5_SO\\r00012
input string so_start_date   = "";   // fecha deseada desde config (opcional)
input string so_end_date     = "";   // fecha deseada desde config (opcional)
input bool   export_trades   = true;  // exportar trades.csv

//---------------- Estructuras ----------------
struct SO_Stats
{
   double deposit, final_balance, net_profit;
   double gp, gl, pf, ep;
   double dd_abs, dd_rel_pct;
   int    trades;
};

//---------------- Rutas absolutas (para crear carpetas) ----------------
string SO_PathCommonBaseAbs(){ return TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\Files\\MT5_SO"; }
string SO_PathLocalBaseAbs() { return TerminalInfoString(TERMINAL_DATA_PATH)       + "\\MQL5\\Files\\MT5_SO"; }

//---------------- Rutas relativas (para FileOpen) ----------------
// Relativas a Common\Files   (con FILE_COMMON)
string SO_PathCommonBaseRel(){ return "MT5_SO"; }
// Relativas a terminal\MQL5\Files (sin FILE_COMMON)
string SO_PathLocalBaseRel() { return "MT5_SO"; }

//---------------- Helpers de carpetas/paths ----------------
bool SO_EnsureDirAbs(const string fullpath){ return FolderCreate(fullpath); }

string SO_RunStamp()
{
   datetime now=TimeLocal();
   string s=TimeToString(now, TIME_DATE|TIME_MINUTES|TIME_SECONDS);
   StringReplace(s,":",""); StringReplace(s," ","_"); StringReplace(s,".","");
   return "run_"+s;
}

void SO_ResolveRun(
   string &absCommonRun, string &absLocalRun,
   string &relCommonRun, string &relLocalRun
){
   string run = so_run_id;
   if(StringLen(run)==0) run = SO_RunStamp();

   string absCommonBase = SO_PathCommonBaseAbs();
   string absLocalBase  = SO_PathLocalBaseAbs();
   string relCommonBase = SO_PathCommonBaseRel();
   string relLocalBase  = SO_PathLocalBaseRel();

   absCommonRun = absCommonBase + "\\" + run;
   absLocalRun  = absLocalBase  + "\\" + run;
   relCommonRun = relCommonBase + "\\" + run;
   relLocalRun  = relLocalBase  + "\\" + run;

   // Crear árboles absolutos (funciona en Tester y en terminal)
   SO_EnsureDirAbs(absCommonBase);
   SO_EnsureDirAbs(absLocalBase);
   SO_EnsureDirAbs(absCommonRun);
   SO_EnsureDirAbs(absLocalRun);
}

//---------------- Escritura tester-safe ----------------
bool SO_WriteCommonRel(const string rel_path, const string content, uint flags = FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON)
{
   int h = FileOpen(rel_path, flags);
   if(h==INVALID_HANDLE){ PrintFormat("SO: FileOpen COMMON falló: %s (err %d)", rel_path, GetLastError()); return false; }
   FileWriteString(h, content);
   FileClose(h);
   return true;
}

bool SO_WriteLocalRel(const string rel_path, const string content, uint flags = FILE_WRITE|FILE_TXT|FILE_ANSI)
{
   int h = FileOpen(rel_path, flags);
   if(h==INVALID_HANDLE){ PrintFormat("SO: FileOpen LOCAL falló: %s (err %d)", rel_path, GetLastError()); return false; }
   FileWriteString(h, content);
   FileClose(h);
   return true;
}

bool SO_WriteBoth(const string filename, const string content, uint flags_common = FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON, uint flags_local = FILE_WRITE|FILE_TXT|FILE_ANSI)
{
   string absC, absL, relC, relL;
   SO_ResolveRun(absC, absL, relC, relL);

   string pC = relC + "\\" + filename; // relativo para COMMON
   string pL = relL + "\\" + filename; // relativo para LOCAL

   bool okC = SO_WriteCommonRel(pC, content, flags_common);
   bool okL = SO_WriteLocalRel (pL, content, flags_local);

   if(!okC || !okL)
      PrintFormat("SO: escritura parcial: common=%s local=%s | relC=%s | relL=%s", (okC?"ok":"fail"), (okL?"ok":"fail"), pC, pL);
   else
      PrintFormat("SO: escrito OK | %s  y  %s", pC, pL);

   return (okC && okL);
}

//---------------- Utilidades JSON/CSV ----------------
string SO_JsonEscape(string s){ StringReplace(s,"\\","\\\\"); StringReplace(s,"\"","\\\""); StringReplace(s,"\r","\\r"); StringReplace(s,"\n","\\n"); StringReplace(s,"\t","\\t"); return s; }
string SO_CsvQuote(string s){ StringReplace(s,"\"","\"\""); StringReplace(s,"\r"," "); StringReplace(s,"\n"," "); return "\""+s+"\""; }

string SO_StringTrim(string s){ StringTrimLeft(s); StringTrimRight(s); return s; }

bool SO_ParseDateTime(const string text, datetime &out)
{
   string trimmed = SO_StringTrim(text);
   if(StringLen(trimmed)==0)
      return false;

   datetime parsed = StringToTime(trimmed);
   if(parsed>0)
   {
      out = parsed;
      return true;
   }

   if(StringLen(trimmed)==10 && StringSubstr(trimmed,4,1)=="." && StringSubstr(trimmed,7,1)==".")
   {
      datetime alt = StringToTime(trimmed+" 00:00");
      if(alt>0)
      {
         out = alt;
         return true;
      }
   }

   return false;
}

//---------------- Pings ----------------
void SO_PingStart(){ SO_WriteBoth("__ping_start","START", FILE_WRITE|FILE_BIN|FILE_COMMON, FILE_WRITE|FILE_BIN); }
void SO_PingEnd()  { SO_WriteBoth("__ping_end","END",   FILE_WRITE|FILE_BIN|FILE_COMMON, FILE_WRITE|FILE_BIN); }

//---------------- Métricas manuales (fallback) ----------------
void SO_ComputeStats(SO_Stats &S)
{
   S.deposit=S.final_balance=S.net_profit=S.gp=S.gl=S.pf=S.ep=S.dd_abs=S.dd_rel_pct=0; S.trades=0;

   double final_balance=AccountInfoDouble(ACCOUNT_BALANCE);
   if(final_balance<=0) final_balance=1000.0;
   S.final_balance=final_balance;

   datetime from=(datetime)SeriesInfoInteger(Symbol(),Period(),SERIES_FIRSTDATE);
   datetime to  =TimeCurrent();
   HistorySelect(from,to);
   int n=HistoryDealsTotal();
   if(n<=0){ S.deposit=final_balance; return; }

   ulong tickets[]; ArrayResize(tickets,n);
   for(int i=0;i<n;i++) tickets[i]=HistoryDealGetTicket(i);

   // ordenar por tiempo asc
   for(int i=0;i<n-1;i++){
      datetime ti=(datetime)HistoryDealGetInteger(tickets[i],DEAL_TIME);
      for(int j=i+1;j<n;j++){
         datetime tj=(datetime)HistoryDealGetInteger(tickets[j],DEAL_TIME);
         if(tj<ti){ ulong t=tickets[i]; tickets[i]=tickets[j]; tickets[j]=t; ti=tj; }
      }
   }

   double net_sum=0;
   for(int k=0;k<n;k++){
      ulong   t  = tickets[k];
      string  sym= HistoryDealGetString(t, DEAL_SYMBOL);
      if(sym!=Symbol() && sym!="") continue;

      double pr = HistoryDealGetDouble(t,DEAL_PROFIT);
      double cm = HistoryDealGetDouble(t,DEAL_COMMISSION);
      double sw = HistoryDealGetDouble(t,DEAL_SWAP);
      double net= pr+cm+sw;

      if(pr>=0) S.gp+=pr; else S.gl+=(-pr);
      if(pr!=0.0 || cm!=0.0 || sw!=0.0) S.trades++;
      net_sum+=net;
   }

   S.deposit    = S.final_balance - net_sum; if(S.deposit<=0) S.deposit=1000.0;
   S.net_profit = S.final_balance - S.deposit;

   // drawdown equity sobre secuencia de deals
   double balance=S.deposit, peak=balance, maxdd=0.0;
   for(int k=0;k<n;k++){
      ulong   t  = tickets[k];
      string  sym= HistoryDealGetString(t, DEAL_SYMBOL);
      if(sym!=Symbol() && sym!="") continue;

      double pr = HistoryDealGetDouble(t,DEAL_PROFIT);
      double cm = HistoryDealGetDouble(t,DEAL_COMMISSION);
      double sw = HistoryDealGetDouble(t,DEAL_SWAP);
      double net= pr+cm+sw;

      balance+=net;
      if(balance>peak) peak=balance;
      double dd=peak-balance;
      if(dd>maxdd) maxdd=dd;
   }

   S.pf         = (S.gl>0 ? S.gp/S.gl : (S.gp>0? 9999.0:0.0));
   S.ep         = (S.trades>0? S.net_profit/(double)S.trades : 0.0);
   S.dd_abs     = maxdd;
   S.dd_rel_pct = (peak>0? (maxdd/peak)*100.0 : 0.0);
}

//---------------- trades.csv ----------------
bool SO_ExportTradesCSV()
{
   if(!export_trades) return true;

   string header="ticket,time,type,price,volume,profit,commission,swap,symbol,comment\n";
   string body="";

   datetime from=(datetime)SeriesInfoInteger(Symbol(),Period(),SERIES_FIRSTDATE);
   datetime to  =TimeCurrent();
   HistorySelect(from,to);
   int n=HistoryDealsTotal();

   for(int i=0;i<n;i++)
   {
      ulong   t  = HistoryDealGetTicket(i);
      string  sym= HistoryDealGetString(t, DEAL_SYMBOL);
      if(sym!=Symbol() && sym!="") continue;

      datetime tm=(datetime)HistoryDealGetInteger(t,DEAL_TIME);
      int      tp=(int)HistoryDealGetInteger(t,DEAL_TYPE);
      double   prc=HistoryDealGetDouble(t,DEAL_PRICE);
      double   vol=HistoryDealGetDouble(t,DEAL_VOLUME);
      double   pr =HistoryDealGetDouble(t,DEAL_PROFIT);
      double   cm =HistoryDealGetDouble(t,DEAL_COMMISSION);
      double   sw =HistoryDealGetDouble(t,DEAL_SWAP);
      string   cmt=HistoryDealGetString(t,DEAL_COMMENT);

      string times=TimeToString(tm, TIME_DATE|TIME_SECONDS);

      body += (string)t + "," + SO_CsvQuote(times) + "," + IntegerToString(tp) + ",";
      body += DoubleToString(prc,_Digits) + "," + DoubleToString(vol,2) + "," + DoubleToString(pr,2) + ",";
      body += DoubleToString(cm,2) + "," + DoubleToString(sw,2) + "," + SO_CsvQuote(sym) + "," + SO_CsvQuote(cmt) + "\n";
   }

   return SO_WriteBoth("trades.csv", header+body);
}

//---------------- report.json ----------------
bool SO_ExportReportJSON(const string inputs_json)
{
   const bool in_tester = (bool)MQLInfoInteger(MQL_TESTER);

   // Campos a serializar
   string   symbol_str    = _Symbol;
   string   timeframe_str = EnumToString(Period());
   datetime start_dt=0, end_dt=0;
   string   start_str="", end_str="";

   double initial_deposit=0, total_net_profit=0, gross_profit=0, gross_loss=0,
          profit_factor=0, expected_payoff=0, dd_abs=0, dd_rel_pct=0, final_balance=0;
   int    total_trades=0, total_deals=0;

   if(in_tester)
   {
      // Estadísticas nativas
      initial_deposit  = TesterStatistics(STAT_INITIAL_DEPOSIT);
      total_net_profit = TesterStatistics(STAT_PROFIT);
      gross_profit     = TesterStatistics(STAT_GROSS_PROFIT);
      gross_loss       = TesterStatistics(STAT_GROSS_LOSS); // NEGATIVO
      profit_factor    = TesterStatistics(STAT_PROFIT_FACTOR);
      expected_payoff  = TesterStatistics(STAT_EXPECTED_PAYOFF);
      dd_abs           = TesterStatistics(STAT_EQUITY_DD);
      dd_rel_pct       = TesterStatistics(STAT_EQUITY_DDREL_PERCENT);
      total_trades     = (int)TesterStatistics(STAT_TRADES);
      total_deals      = (int)TesterStatistics(STAT_DEALS);

      start_dt = (datetime)SeriesInfoInteger(Symbol(), Period(), SERIES_FIRSTDATE);
      end_dt   = TimeCurrent();
   }
   else
   {
      // Fallback manual
      SO_Stats S; SO_ComputeStats(S);
      initial_deposit  = (S.final_balance - S.net_profit);
      total_net_profit = S.net_profit;
      gross_profit     = S.gp;
      gross_loss       = -S.gl;
      profit_factor    = (S.gl>0 ? S.gp/S.gl : 0.0);
      expected_payoff  = S.ep;
      dd_abs           = S.dd_abs;
      dd_rel_pct       = S.dd_rel_pct;
      total_trades     = S.trades;
      total_deals      = S.trades;

      start_dt = (datetime)SeriesInfoInteger(Symbol(), Period(), SERIES_FIRSTDATE);
      end_dt   = TimeCurrent();
   }

   final_balance = initial_deposit + total_net_profit;

   int build = (int)TerminalInfoInteger(TERMINAL_BUILD);

   string start_override = SO_StringTrim(so_start_date);
   if(StringLen(start_override)>0)
   {
      datetime parsed;
      if(SO_ParseDateTime(start_override, parsed))
      {
         start_dt = parsed;
         start_str = TimeToString(start_dt, TIME_DATE|TIME_MINUTES);
      }
      else
      {
         start_str = start_override;
      }
   }

   string end_override = SO_StringTrim(so_end_date);
   if(StringLen(end_override)>0)
   {
      datetime parsed_end;
      if(SO_ParseDateTime(end_override, parsed_end))
      {
         end_dt = parsed_end;
         end_str = TimeToString(end_dt, TIME_DATE|TIME_MINUTES);
      }
      else
      {
         end_str = end_override;
      }
   }

   if(StringLen(start_str)==0)
      start_str = TimeToString(start_dt, TIME_DATE|TIME_MINUTES);

   if(StringLen(end_str)==0)
      end_str = TimeToString(end_dt, TIME_DATE|TIME_MINUTES);

   // Serialización JSON
   string j="{\n";
   j+="  \"run_id\": \""+SO_JsonEscape(so_run_id)+"\",\n";
   j+="  \"symbol\": \""+SO_JsonEscape(symbol_str)+"\",\n";
   j+="  \"timeframe\": \""+SO_JsonEscape(timeframe_str)+"\",\n";
   j+="  \"start_date\": \""+SO_JsonEscape(start_str)+"\",\n";
   j+="  \"end_date\": \""+SO_JsonEscape(end_str)+"\",\n";
   j+="  \"initial_deposit\": "+DoubleToString(initial_deposit,2)+",\n";
   j+="  \"final_balance\": "+DoubleToString(final_balance,2)+",\n";
   j+="  \"total_net_profit\": "+DoubleToString(total_net_profit,2)+",\n";
   j+="  \"gross_profit\": "+DoubleToString(gross_profit,2)+",\n";
   j+="  \"gross_loss\": "+DoubleToString(gross_loss,2)+",\n";
   j+="  \"profit_factor\": "+DoubleToString(profit_factor,2)+",\n";
   j+="  \"expected_payoff\": "+DoubleToString(expected_payoff,2)+",\n";
   j+="  \"max_dd_abs\": "+DoubleToString(dd_abs,2)+",\n";
   j+="  \"max_dd_rel_pct\": "+DoubleToString(dd_rel_pct,2)+",\n";
   j+="  \"total_trades\": "+IntegerToString(total_trades)+",\n";
   j+="  \"total_deals\": "+IntegerToString(total_deals)+",\n";
   j+="  \"account_info\": {\n";
   j+="    \"leverage\": "+IntegerToString((int)AccountInfoInteger(ACCOUNT_LEVERAGE))+",\n";
   j+="    \"currency\": \""+SO_JsonEscape(AccountInfoString(ACCOUNT_CURRENCY))+"\"\n";
   j+="  },\n";
   j+="  \"ea\": {\n";
   j+="    \"name\": \""+SO_JsonEscape(MQLInfoString(MQL_PROGRAM_NAME))+"\",\n";
   j+="    \"version\": \""+SO_JsonEscape(MQLInfoString(MQL_PROGRAM_PATH))+"\",\n";
   j+="    \"build\": "+IntegerToString(build)+",\n";
   j+="    \"mode\": \""+SO_JsonEscape("Agresivo")+"\"\n";
   j+="  },\n";
   j+="  \"inputs\": "+(StringLen(inputs_json)>0? inputs_json:"{}")+"\n";
   j+="}\n";

   return SO_WriteBoth("report.json", j);
}

//---------------- Marcador de rutas (diagnóstico) ----------------
void SO_DumpPathsMarker()
{
   string absC, absL, relC, relL;
   SO_ResolveRun(absC, absL, relC, relL);
   string info = "COMMON_REL="+relC+"\nLOCAL_REL="+relL+"\nCOMMON_ABS="+absC+"\nLOCAL_ABS="+absL+"\n";
   SO_WriteBoth("__WHERE.txt", info, FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON, FILE_WRITE|FILE_TXT|FILE_ANSI);
}

//---------------- Orquestador principal ----------------
void SO_ReportOnTesterDeinit(const string inputs_json)
{
   SO_PingStart();

   bool ok_json = SO_ExportReportJSON(inputs_json);
   bool ok_csv  = SO_ExportTradesCSV();

   string ready = (ok_json? "OK_JSON":"FAIL_JSON"); ready += (ok_csv? "|OK_CSV":"|FAIL_CSV");
   SO_WriteBoth("_READY", ready, FILE_WRITE|FILE_BIN|FILE_COMMON, FILE_WRITE|FILE_BIN);

   // Dump de rutas para ubicar archivos en el Agente del Tester
   SO_DumpPathsMarker();

   // Log resumen
   string absC, absL, relC, relL; SO_ResolveRun(absC,absL,relC,relL);
   PrintFormat("SO_REPORT: JSON=%s CSV=%s | COMMON(rel)=%s | LOCAL(rel)=%s", (ok_json?"OK":"FAIL"), (ok_csv?"OK":"FAIL"), relC, relL);
   PrintFormat("SO_REPORT: COMMON(abs)=%s | LOCAL(abs)=%s", absC, absL);

   SO_PingEnd();
}

#endif // __SO_REPORT_MQH__
