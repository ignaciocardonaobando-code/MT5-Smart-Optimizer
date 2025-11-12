# optimizer_v2.py
# MT5 Smart Optimizer v2 — robusto para Smoke y Optuna.

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# psutil opcional para gestión de procesos
try:
    import psutil  # type: ignore
except Exception:
    psutil = None


# ----------------------- Utilidades básicas -----------------------
def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def write_text(p: Path, s: str) -> None:
    ensure_dir(p.parent)
    p.write_text(s, encoding="utf-8")

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def windows_user_roaming() -> Path:
    return Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))

def now_run_id() -> str:
    return time.strftime("run_%Y%m%d_%H%M%S_") + ("%04x" % (int(time.time() * 10000) & 0xFFFF))

def norm_date_for_ini(s: str) -> str:
    s = s.strip()
    if re.match(r"^\d{4}\.\d{2}\.\d{2}$", s):
        return s
    m = re.match(r"^(\d{4})[-/](\d{2})[-/](\d{2})", s)
    if m:
        return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
    return s

def _quantize_params_for_broker(d: dict) -> dict:
    q = dict(d or {})
    if "lot_size" in q and isinstance(q["lot_size"], (int, float)):
        v = max(0.01, min(1.00, float(q["lot_size"])))
        q["lot_size"] = float(f"{v:.2f}")
    if "atrMultiplierTrailing" in q and isinstance(q["atrMultiplierTrailing"], (int, float)):
        q["atrMultiplierTrailing"] = float(f"{q['atrMultiplierTrailing']:.2f}")
    if "margen_cruce" in q and isinstance(q["margen_cruce"], (int, float)):
        q["margen_cruce"] = float(f"{q['margen_cruce']:.2f}")
    return q


# ----------------------- Dataclasses de config -----------------------
@dataclass
class Mt5Cfg:
    terminal_path: str
    terminal_hash: str
    datadir: Optional[str] = None

@dataclass
class TestCfg:
    symbol: str
    timeframe: str
    model: int
    from_: str
    to: str
    deposit: int
    leverage: int

@dataclass
class EaCfg:
    name: str
    inputs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchCfg:
    space: Dict[str, Any] = field(default_factory=dict)
    sampler: Optional[Any] = None

@dataclass
class Config:
    mt5: Mt5Cfg
    test: TestCfg
    ea: EaCfg
    search: Optional[SearchCfg] = None


# ----------------------- Loader (tolerante) -----------------------
def strip_inline_comments(s: str) -> str:
    out = []
    for line in s.splitlines():
        if re.match(r"^\s*#", line):
            continue
        if "#" in line:
            line = line.split("#", 1)[0]
        out.append(line)
    return "\n".join(out).strip()

def _friendly_missing_msg(ctx: str, missing: list[str], present_keys: list[str]) -> str:
    mk = ", ".join(missing)
    pk = ", ".join(present_keys)
    return (
        f"Config inválido ({ctx}). Faltan claves requeridas: {mk}.\n"
        f"Claves presentes en el documento: {pk if pk else '(ninguna)'}.\n\n"
        "Ejemplo mínimo esperado:\n"
        "{\n"
        '  \"mt5\": {\"terminal_path\": \"C:/.../terminal64.exe\", \"terminal_hash\": \"90A4...\"},\n'
        '  \"test\": {\"symbol\": \"EURUSD\", \"timeframe\": \"H1\", \"model\": 0, \"from\": \"2024.01.01\", \"to\": \"2024.12.31\", \"deposit\": 1000, \"leverage\": 100},\n'
        '  \"ea\": {\"name\": \"Estrategia_Boll_Stoch_ATR_Agresiva_VFinal.ex5\", \"inputs\": {}}\n'
        "}\n"
    )

def _coerce_legacy_to_modern(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Si el JSON viene “plano” (legacy) intenta envolverlo al esquema moderno.
    Devuelve nuevo dict o None si no reconoce el patrón.
    """
    keys = set(k.lower() for k in data.keys())
    legacy_hits = {
        "terminal_path", "terminal_hash",
        "symbol", "timeframe", "model", "from", "to", "deposit", "leverage",
        "ea", "expert", "ea_name", "inputs"
    }
    if not (keys & legacy_hits):
        return None

    # mt5
    mt5 = {
        "terminal_path": data.get("terminal_path") or data.get("terminal") or data.get("exe") or "",
        "terminal_hash": data.get("terminal_hash") or data.get("hash") or "",
        "datadir": data.get("datadir")
    }

    # test
    test = {
        "symbol": data.get("symbol") or "",
        "timeframe": data.get("timeframe") or "",
        "model": int(data.get("model", 0)),
        "from": data.get("from") or data.get("start_date") or data.get("from_date") or "",
        "to": data.get("to") or data.get("end_date") or data.get("to_date") or "",
        "deposit": int(data.get("deposit", 1000)),
        "leverage": int(data.get("leverage", 100))
    }

    # ea
    ea_name = data.get("ea") or data.get("ea_name") or data.get("expert") or data.get("expert_name") or ""
    ea_inputs = data.get("inputs", {})
    if not isinstance(ea_inputs, dict):
        ea_inputs = {}

    modern = {
        "mt5": mt5,
        "test": test,
        "ea": {"name": ea_name, "inputs": ea_inputs}
    }

    # search (opcional)
    if "search" in data and isinstance(data["search"], dict):
        modern["search"] = data["search"]
    elif "search_space" in data and isinstance(data["search_space"], dict):
        modern["search"] = {"space": data["search_space"]}

    return modern

def load_config(path: str) -> Config:
    raw = Path(path).read_text(encoding="utf-8")
    txt = strip_inline_comments(raw)

    # JSON o YAML
    data: Dict[str, Any]
    try:
        data = json.loads(txt)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except Exception as e:
            raise RuntimeError("Config no es JSON válido y PyYAML no está disponible.") from e
        data = yaml.safe_load(txt)  # type: ignore
        if not isinstance(data, dict):
            raise RuntimeError("Config YAML inválido: no es un objeto.")

    # ¿Faltan bloques? Intentar legacy->modern
    if not all(k in data for k in ("mt5", "test", "ea")):
        maybe = _coerce_legacy_to_modern(data)
        if maybe:
            data = maybe

    # Si aún faltan, error amable
    missing_top = [k for k in ("mt5", "test", "ea") if k not in data]
    if missing_top:
        raise RuntimeError(_friendly_missing_msg("faltan bloques 'mt5'/'test'/'ea'", missing_top, list(data.keys())))

    # Validaciones por bloque
    def need(d: Dict[str, Any], req: list[str], ctx: str) -> None:
        miss = [k for k in req if k not in d or d[k] in (None, "")]
        if miss:
            raise RuntimeError(_friendly_missing_msg(ctx, miss, list(d.keys())))

    mt5d = data["mt5"]; testd = data["test"]; ead = data["ea"]
    need(mt5d, ["terminal_path", "terminal_hash"], "mt5")
    need(testd, ["symbol", "timeframe", "from", "to", "deposit", "leverage"], "test")
    need(ead, ["name"], "ea")

    mt5 = Mt5Cfg(
        terminal_path=str(mt5d["terminal_path"]).strip(),
        terminal_hash=str(mt5d["terminal_hash"]).strip(),
        datadir=mt5d.get("datadir"),
    )
    test = TestCfg(
        symbol=str(testd["symbol"]),
        timeframe=str(testd["timeframe"]),
        model=int(testd.get("model", 0)),
        from_=norm_date_for_ini(str(testd["from"])),
        to=norm_date_for_ini(str(testd["to"])),
        deposit=int(testd["deposit"]),
        leverage=int(testd["leverage"]),
    )
    ea = EaCfg(
        name=str(ead["name"]),
        inputs=dict(ead.get("inputs", {})),
    )

    search = None
    if "search" in data and data["search"] is not None:
        s = data["search"]
        search = SearchCfg(
            space=dict(s.get("space", {})),
            sampler=s.get("sampler"),
        )

    return Config(mt5=mt5, test=test, ea=ea, search=search)


# ----------------------- Paths por HASH -----------------------
def profiles_tester_dir(mt5_hash: str) -> Path:
    return windows_user_roaming() / "MetaQuotes" / "Terminal" / mt5_hash / "MQL5" / "Profiles" / "Tester"

def experts_root_dir(mt5_hash: str) -> Path:
    return windows_user_roaming() / "MetaQuotes" / "Terminal" / mt5_hash / "MQL5" / "Experts"

def common_mt5_so_dir() -> Path:
    return windows_user_roaming() / "MetaQuotes" / "Terminal" / "Common" / "Files" / "MT5_SO"

def local_agent_files_dir(mt5_hash: str) -> Optional[Path]:
    tester_root = windows_user_roaming() / "MetaQuotes" / "Tester" / mt5_hash
    if not tester_root.exists():
        return None
    for p in tester_root.glob("Agent-*-*"):
        candidate = p / "MQL5" / "Files" / "MT5_SO"
        if candidate.exists():
            return candidate
    agents = list(tester_root.glob("Agent-*-*"))
    if agents:
        return agents[0] / "MQL5" / "Files" / "MT5_SO"
    return None


# ----------------------- .set / .ini -----------------------
def build_set_lines(kv: Dict[str, Any]) -> list[str]:
    lines = []
    for k, v in kv.items():
        if isinstance(v, bool):
            v = 1 if v else 0
        lines.append(f"{k}={v}")
    return lines

def write_set_to_profiles_tester(mt5_hash: str, set_name: str, lines: list[str]) -> Path:
    dst = profiles_tester_dir(mt5_hash) / set_name
    write_text(dst, "\n".join(lines) + "\n")
    return dst

def write_ini(cfg: Config, set_name: str, ini_path: Path, report_path: Path) -> None:
    ini = []
    ini.append("[Tester]")
    ini.append(f"Symbol={cfg.test.symbol}")
    ini.append(f"Period={cfg.test.timeframe}")
    ini.append(f"Model={cfg.test.model}")
    ini.append(f"FromDate={cfg.test.from_}")
    ini.append(f"ToDate={cfg.test.to}")
    ini.append(f"Deposit={cfg.test.deposit}")
    ini.append(f"Leverage={cfg.test.leverage}")
    ini.append(f"Expert={cfg.ea.name}")
    ini.append(f"ExpertParameters=\"{set_name}\"")
    ini.append("Optimization=0")
    ini.append("ReportReplace=1")
    ini.append("ShutdownTerminal=1")
    report_value = str(report_path).replace("\\", "/")
    ini.append(f'Report="{report_value}"')
    write_text(ini_path, "\n".join(ini) + "\n")


# ----------------------- Proceso MT5 (PID) -----------------------
def _launch_mt5(exe_path: str, ini_path: Path) -> subprocess.Popen:
    args = [exe_path, f"/config:{str(ini_path)}", "/test", "/skipupdate"]
    print(f'INFO Lanzando MT5: "{exe_path}" /config:{str(ini_path)} /test /skipupdate', flush=True)
    creation = 0
    if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        creation |= subprocess.CREATE_NEW_PROCESS_GROUP
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        creation |= subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(args, creationflags=creation)

def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if psutil:
        return psutil.pid_exists(pid)
    try:
        out = subprocess.check_output(["tasklist"], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).decode("utf-8", errors="ignore")
        return str(pid) in out
    except Exception:
        return False

def _stop_pid_gently(pid: int, timeout: int = 60) -> bool:
    if pid <= 0:
        return True
    if not _pid_alive(pid):
        return True
    try:
        if psutil:
            p = psutil.Process(pid)
            try:
                p.terminate()
            except Exception:
                pass
            try:
                p.wait(timeout=timeout)
                return True
            except Exception:
                try:
                    p.kill()
                    p.wait(timeout=10)
                    return True
                except Exception:
                    pass
        try:
            subprocess.call(["taskkill", "/T", "/PID", str(pid)], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            time.sleep(1.5)
        except Exception:
            pass
        if _pid_alive(pid):
            try:
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(pid)], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                time.sleep(1.0)
            except Exception:
                pass
        return not _pid_alive(pid)
    except Exception:
        return False


# ----------------------- Helpers de espera / fallback -----------------------
def _dir_has_progress(run_dir: Path) -> bool:
    for name in ("_READY", "report.json", "trades.csv"):
        if (run_dir / name).exists():
            return True
    return False

def _try_parse_final_balance_from_html(html: str) -> Optional[float]:
    m = re.search(r"final balance\s+([0-9]+(?:\.[0-9]+)?)\s+USD", html, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass
    m = re.search(r"Final\s*balance.*?([0-9]+(?:\.[0-9]+)?)", html, re.IGNORECASE | re.DOTALL)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*USD", html, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            pass
    return None

def _override_html_dates_text(html: str, start: str, end: str) -> Tuple[str, bool]:
    date_pattern = re.compile(r"\d{4}\.\d{2}\.\d{2}")
    datetime_pattern = re.compile(r"\d{4}\.\d{2}\.\d{2}(?:\s+\d{2}:\d{2})")

    start_date_match = date_pattern.search(start)
    end_date_match = date_pattern.search(end)
    if not start_date_match or not end_date_match:
        return html, False

    start_date = start_date_match.group(0)
    end_date = end_date_match.group(0)

    start_datetime_match = datetime_pattern.search(start)
    end_datetime_match = datetime_pattern.search(end)
    start_datetime = start_datetime_match.group(0) if start_datetime_match else start_date
    end_datetime = end_datetime_match.group(0) if end_datetime_match else end_date

    range_pattern = re.compile(
        r"(\d{4}\.\d{2}\.\d{2})(?:\s+\d{2}:\d{2})?\s*-\s*(\d{4}\.\d{2}\.\d{2})(?:\s+\d{2}:\d{2})?"
    )

    def _replace(match: re.Match[str]) -> str:
        segment = match.group(0)
        has_time = bool(re.search(r"\d{2}:\d{2}", segment))
        left = start_datetime if has_time else start_date
        right = end_datetime if has_time else end_date
        return f"{left} - {right}"

    new_html, count = range_pattern.subn(_replace, html)
    return new_html, bool(count)

def override_report_html_dates(report_html: Path, start: str, end: str) -> None:
    try:
        html = read_text(report_html)
    except Exception:
        print("WARNING No se pudo escribir HTML")
        return

    new_html, changed = _override_html_dates_text(html, start, end)
    if not changed:
        return

    try:
        write_text(report_html, new_html)
    except Exception:
        print("WARNING No se pudo escribir HTML")
        return

    print(f"INFO Rango de fechas HTML forzado a {start} - {end}")

def wait_ready_and_report(common_run: Path, local_run: Optional[Path], guard_sec: int, report_html: Path, short_watchdog_sec: int = 120) -> Tuple[bool, Optional[float]]:
    t0 = time.time()
    common_ready = common_run / "_READY"
    common_report = common_run / "report.json"
    local_ready = local_run / "_READY" if local_run else None
    local_report = local_run / "report.json" if local_run else None

    origin_only = True
    origin_seen = (common_run / "origin.txt").exists()

    while True:
        if common_ready.exists() and common_report.exists():
            try:
                data = json.loads(read_text(common_report))
                fb = float(data.get("final_balance")) if "final_balance" in data else None
                return True, fb
            except Exception:
                pass

        if local_ready and local_report and local_ready.exists() and local_report.exists():
            try:
                data = json.loads(read_text(local_report))
                fb = float(data.get("final_balance")) if "final_balance" in data else None
                write_text(common_report, json.dumps(data, indent=2))
                write_text(common_ready, "ok")
                return True, fb
            except Exception:
                pass

        if _dir_has_progress(common_run) or (local_run and _dir_has_progress(local_run)):
            origin_only = False

        elapsed = time.time() - t0
        if report_html.exists() and not common_report.exists() and elapsed > min(180, guard_sec * 0.5):
            try:
                html = read_text(report_html)
                fb = _try_parse_final_balance_from_html(html)
                if fb is not None:
                    data = {"final_balance": fb, "source": "html_fallback"}
                    write_text(common_report, json.dumps(data, indent=2))
                    write_text(common_ready, "ok")
                    return True, fb
            except Exception:
                pass

        if origin_seen and origin_only and elapsed >= short_watchdog_sec:
            return False, None

        if elapsed > guard_sec:
            return False, None

        time.sleep(0.5)


# ----------------------- Ejecución de un run -----------------------
def run_single(cfg: Config, exe_path: str, guard_sec: int, auto_close: bool, base_overrides: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[float], str, Path]:
    run_cfg = copy.deepcopy(cfg)
    overrides = dict(base_overrides or {})
    trial_timeframe = overrides.pop("timeframe", None)
    if trial_timeframe:
        run_cfg.test.timeframe = str(trial_timeframe)

    run_id = now_run_id()

    common_root = common_mt5_so_dir()
    common_run = common_root / run_id
    ensure_dir(common_run)
    local_base = local_agent_files_dir(run_cfg.mt5.terminal_hash)
    local_run = (local_base / run_id) if local_base else None
    if local_run:
        ensure_dir(local_run)

    write_text(common_root / "__WHERE.txt", str(common_run))
    write_text(common_run / "origin.txt", run_id)

    so_block = {
        "so_enable": 1,
        "so_report_enable": 1,
        "so_run_id": run_id,
        "so_out_dir": str(common_root),
        "so_prefix": f"{run_cfg.test.symbol}_{run_cfg.test.timeframe}_{run_cfg.test.from_}_{run_cfg.test.to}",
        "so_start_date": run_cfg.test.from_,
        "so_end_date": run_cfg.test.to,
    }

    merged = dict(run_cfg.ea.inputs or {})
    if overrides:
        merged.update(overrides)
    merged = _quantize_params_for_broker(merged)

    set_kv = dict(merged)
    set_kv.update(so_block)
    set_lines = build_set_lines(set_kv)
    set_name = f"params_{run_id[-4:]}_{abs(hash(run_id)) & 0xffffffff:08x}.set"
    set_path = write_set_to_profiles_tester(run_cfg.mt5.terminal_hash, set_name, set_lines)
    print(f"INFO Preset desplegado: {str(set_path)}")
    print(f"INFO Expert relativo: {run_cfg.ea.name}")
    print(f"INFO MT5 buscará: {str(experts_root_dir(run_cfg.mt5.terminal_hash) / run_cfg.ea.name)}")

    reports_root = Path.home() / "runs" / "reports"
    ensure_dir(reports_root)
    report_html = reports_root / f"report_{abs(hash(run_id)) & 0xffffffff:08x}.html"

    ini_path = Path.home() / f"{run_id[-4:]}_{abs(hash(run_id)) & 0xffff:04x}.ini"
    write_ini(run_cfg, set_path.name, ini_path, report_html)

    proc = _launch_mt5(exe_path, ini_path)
    pid = proc.pid if proc and proc.pid else -1

    ok, fb = wait_ready_and_report(common_run, local_run, guard_sec, report_html, short_watchdog_sec=120)
    override_report_html_dates(report_html, run_cfg.test.from_, run_cfg.test.to)

    if auto_close:
        closed = _stop_pid_gently(pid, timeout=45)
        if closed:
            print(f"INFO MT5 cerrado por PID: {pid}")
        else:
            print(f"WARNING No se pudo cerrar por PID: {pid}")
    else:
        try:
            proc.wait(timeout=10)
        except Exception:
            pass

    if not ok:
        try:
            items = [p.name for p in common_run.iterdir()]
        except Exception:
            items = []
        raise TimeoutError(
            f"Timeout esperando _READY + report.json. Esperado: {str(common_run)}. Contenido: {items}"
        )

    if fb is not None:
        print(f"INFO Final balance: {fb}")
        meta = {
            "final_balance": fb,
            "run_id": run_id,
            "symbol": run_cfg.test.symbol,
            "timeframe": run_cfg.test.timeframe,
            "from": run_cfg.test.from_,
            "to": run_cfg.test.to,
            "pid": pid,
        }
        write_text(common_run / "meta.json", json.dumps(meta, indent=2))
        print(f"INFO Meta guardada: {str(common_run / 'meta.json')}")

    return ok, fb, run_id, common_run


# ----------------------- Optuna -----------------------
def suggest_from_space(trial, space: Dict[str, Any]) -> Dict[str, Any]:
    params = {}
    for k, spec in space.items():
        kind = spec[0]
        if kind == "int":
            params[k] = trial.suggest_int(k, int(spec[1]), int(spec[2]))
        elif kind == "float":
            params[k] = trial.suggest_float(k, float(spec[1]), float(spec[2]))
        elif kind == "choice":
            params[k] = trial.suggest_categorical(k, list(spec[1]))
        else:
            raise RuntimeError(f"Tipo no soportado en search.space para {k}: {kind}")
    return params

def _resolve_sampler(search_cfg: SearchCfg):
    """Construye el sampler de Optuna según la configuración."""
    try:
        import optuna  # type: ignore  # noqa: F401
        from optuna.samplers import GridSampler, TPESampler  # type: ignore
    except Exception as e:
        raise RuntimeError("Optuna no está instalado. pip install optuna") from e

    cfg_sampler = search_cfg.sampler
    if cfg_sampler is None:
        return TPESampler(seed=42)

    def _normalize_grid_space(raw: Dict[str, Any]) -> Dict[str, list[Any]]:
        grid_space: Dict[str, list[Any]] = {}
        for key, values in raw.items():
            if isinstance(values, str) or not isinstance(values, (list, tuple, set)):
                raise RuntimeError(
                    f"GridSampler requiere un iterable de opciones en search.sampler.search_space para '{key}'."
                )
            if not values:
                raise RuntimeError(
                    f"GridSampler requiere al menos una opción para '{key}'."
                )
            grid_space[key] = list(values)
        if not grid_space:
            raise RuntimeError("GridSampler requiere al menos una variable en search.sampler.search_space.")
        return grid_space

    def _default_grid_space() -> Dict[str, list[Any]]:
        if not search_cfg.space:
            raise RuntimeError(
                "GridSampler requiere que search.space defina variables tipo 'choice'."
            )
        grid_space: Dict[str, list[Any]] = {}
        for key, spec in search_cfg.space.items():
            if not isinstance(spec, (list, tuple)) or not spec:
                raise RuntimeError(f"Spec inválida para GridSampler en '{key}'.")
            kind = spec[0]
            if kind != "choice":
                raise RuntimeError(
                    f"GridSampler requiere 'choice' en search.space para la variable '{key}'."
                )
            if len(spec) < 2:
                raise RuntimeError(f"Spec inválida para GridSampler en '{key}'.")
            values = spec[1]
            if isinstance(values, str) or not isinstance(values, (list, tuple, set)):
                raise RuntimeError(
                    f"GridSampler requiere un iterable de opciones en search.space para '{key}'."
                )
            if not values:
                raise RuntimeError(
                    f"GridSampler requiere al menos una opción para '{key}'."
                )
            grid_space[key] = list(values)
        return grid_space

    if isinstance(cfg_sampler, str):
        sampler_name = cfg_sampler.strip().lower()
        if sampler_name in {"tpe", "tp", "tpesampler"}:
            return TPESampler(seed=42)
        if sampler_name in {"grid", "grid_sampler", "gridsampler"}:
            return GridSampler(_default_grid_space())
        raise RuntimeError(f"Sampler desconocido en search.sampler: '{cfg_sampler}'.")

    if isinstance(cfg_sampler, dict):
        sampler_name = str(
            cfg_sampler.get("type")
            or cfg_sampler.get("name")
            or cfg_sampler.get("sampler")
            or ""
        ).strip().lower()
        if sampler_name in {"tpe", "tp", "tpesampler"}:
            seed = int(cfg_sampler.get("seed", 42))
            return TPESampler(seed=seed)
        if sampler_name in {"grid", "grid_sampler", "gridsampler"}:
            raw_space = cfg_sampler.get("search_space")
            if raw_space is None:
                return GridSampler(_default_grid_space())
            if not isinstance(raw_space, dict):
                raise RuntimeError(
                    "GridSampler requiere que search.sampler.search_space sea un objeto JSON con listas de opciones."
                )
            return GridSampler(_normalize_grid_space(raw_space))
        raise RuntimeError(f"Sampler desconocido en search.sampler: '{cfg_sampler}'.")

    raise RuntimeError(f"Tipo no soportado para search.sampler: {type(cfg_sampler)!r}.")


def run_optuna(cfg: Config, exe_path: str, guard_sec: int, n_trials: int, n_jobs: int, auto_close: bool) -> None:
    try:
        import optuna  # type: ignore
    except Exception as e:
        raise RuntimeError("Optuna no está instalado. pip install optuna") from e

    if cfg.search is None:
        raise RuntimeError("No hay configuración de 'search' para Optuna.")

    sampler = _resolve_sampler(cfg.search)
    study = optuna.create_study(
        direction="maximize",
        study_name=f"mt5_opt_{cfg.test.symbol}_{cfg.test.timeframe}",
        sampler=sampler,
    )
    print(f"INFO Study: {study.study_name}")

    def objective(trial):
        trial_params = suggest_from_space(trial, cfg.search.space)
        trial_params = _quantize_params_for_broker(trial_params)
        try:
            ok, fb, rid, rdir = run_single(cfg, exe_path, guard_sec, auto_close=auto_close, base_overrides=trial_params)
            if not ok or fb is None:
                return float("-inf")
        except TimeoutError:
            return float("-inf")
        return float(fb) - float(cfg.test.deposit)

    study.optimize(
        objective,
        n_trials=n_trials,
        n_jobs=max(1, n_jobs),
        gc_after_trial=True,
        catch=(TimeoutError,)
    )

    best = study.best_trial
    print("\n=== BEST TRIAL ===")
    print(f"value: {best.value}")
    print("params:")
    for k, v in best.params.items():
        print(f"  {k}: {v}")


# ----------------------- CLI -----------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", required=True, help="Ruta a JSON/YAML.")
    ap.add_argument("--exe", help="Override del terminal64.exe")
    ap.add_argument("--single-run", action="store_true", help="Ejecuta un solo test (Smoke).")
    ap.add_argument("--n-trials", dest="n_trials", type=int, default=0, help="Cantidad de trials para Optuna.")
    ap.add_argument("--trials", dest="n_trials_alias", type=int, default=None, help="Alias de --n-trials.")
    ap.add_argument("--n-jobs", dest="n_jobs", type=int, default=1, help="Paralelismo Optuna.")
    ap.add_argument("--timeout", type=int, default=None, help="(Reservado) Timeout total para Optuna.")
    ap.add_argument("--guard-sec", type=int, default=300, help="Tiempo máx de espera por artefactos por run.")
    ap.add_argument("--auto-close", action="store_true", help="Cierra MT5 por PID al terminar cada run.")
    args = ap.parse_args()

    cfg = load_config(args.config)
    exe_path = args.exe or cfg.mt5.terminal_path

    if args.n_trials_alias is not None and args.n_trials == 0:
        args.n_trials = args.n_trials_alias

    print(f"INFO Override --exe: {exe_path}")
    print(f"INFO Override --guard-sec: {args.guard_sec}")
    if args.auto_close:
        print("INFO Auto-close habilitado: se cerrará la instancia lanzada (por PID) al finalizar cada run.")

    if args.single_run:
        ok, fb, rid, rdir = run_single(cfg, exe_path, args.guard_sec, auto_close=args.auto_close, base_overrides=None)
        sys.exit(0 if ok else 1)

    if args.n_trials and args.n_trials > 0:
        if not cfg.search or not cfg.search.space:
            raise RuntimeError("No hay 'search.space' definido en el config para Optuna.")
        run_optuna(cfg, exe_path, args.guard_sec, n_trials=args.n_trials, n_jobs=max(1, args.n_jobs), auto_close=args.auto_close)
        sys.exit(0)

    print("ERROR: Especifica --single-run o --n-trials N (>0) para Optuna.")
    sys.exit(2)

if __name__ == "__main__":
    main()
