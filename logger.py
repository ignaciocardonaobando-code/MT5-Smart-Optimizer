#!/usr/bin/env python3
"""Logger estructurado para MT5 Smart Optimizer v2
Proporciona logging con rotación, niveles y formato estructurado"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import json

class OptimizerLogger:
    """Logger estructurado con soporte para archivo y consola"""
    
    def __init__(self, name="MT5Optimizer", log_dir="logs", level=logging.INFO):
        self.name = name
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Crear directorio de logs si no existe
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers para archivo y consola"""
        # Formato detallado
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler de archivo con rotación (10MB, 5 archivos)
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler de consola (solo INFO y superior)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)-8s | %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message, **kwargs):
        """Log nivel INFO con contexto adicional"""
        self._log(logging.INFO, message, kwargs)
    
    def debug(self, message, **kwargs):
        """Log nivel DEBUG con contexto adicional"""
        self._log(logging.DEBUG, message, kwargs)
    
    def warning(self, message, **kwargs):
        """Log nivel WARNING con contexto adicional"""
        self._log(logging.WARNING, message, kwargs)
    
    def error(self, message, **kwargs):
        """Log nivel ERROR con contexto adicional"""
        self._log(logging.ERROR, message, kwargs)
    
    def critical(self, message, **kwargs):
        """Log nivel CRITICAL con contexto adicional"""
        self._log(logging.CRITICAL, message, kwargs)
    
    def _log(self, level, message, context):
        """Método interno para log con contexto"""
        if context:
            context_str = json.dumps(context, ensure_ascii=False)
            full_message = f"{message} | Context: {context_str}"
        else:
            full_message = message
        self.logger.log(level, full_message)
    
    def log_optimization_start(self, config):
        """Log inicio de optimización"""
        self.info("Iniciando optimización", 
                  symbol=config.get('test', {}).get('symbol'),
                  timeframe=config.get('test', {}).get('timeframe'),
                  n_trials=config.get('optimizer', {}).get('n_trials'))
    
    def log_trial(self, trial_number, params, value):
        """Log resultado de trial"""
        self.debug(f"Trial {trial_number} completado",
                   params=params,
                   value=value)
    
    def log_optimization_end(self, best_params, best_value, duration):
        """Log fin de optimización"""
        self.info("Optimización completada",
                  best_value=best_value,
                  duration_seconds=duration,
                  best_params=best_params)

# Instancia global
_default_logger = None

def get_logger(name="MT5Optimizer", log_dir="logs", level=logging.INFO):
    """Obtiene o crea el logger global"""
    global _default_logger
    if _default_logger is None:
        _default_logger = OptimizerLogger(name, log_dir, level)
    return _default_logger
