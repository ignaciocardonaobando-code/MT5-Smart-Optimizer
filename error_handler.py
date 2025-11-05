#!/usr/bin/env python3
"""Manejo de errores personalizado para MT5 Smart Optimizer v2
Provee excepciones personalizadas y handlers para diferentes tipos de errores"""
import sys
import traceback
from typing import Optional, Callable, Any
from functools import wraps

# Excepciones personalizadas

class OptimizerError(Exception):
    """Excepción base para errores del optimizer"""
    pass

class ConfigurationError(OptimizerError):
    """Error en la configuración"""
    pass

class MT5ConnectionError(OptimizerError):
    """Error de conexión con MT5"""
    pass

class OptimizationError(OptimizerError):
    """Error durante el proceso de optimización"""
    pass

class ValidationError(OptimizerError):
    """Error de validación de datos"""
    pass

class FileError(OptimizerError):
    """Error relacionado con archivos"""
    pass

# Handler de errores

class ErrorHandler:
    """Manejador centralizado de errores"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.error_count = 0
        self.error_history = []
    
    def handle(self, error: Exception, context: Optional[dict] = None) -> None:
        """Maneja un error y registra información"""
        self.error_count += 1
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        self.error_history.append(error_info)
        
        if self.logger:
            self.logger.error(
                f"{error_info['type']}: {error_info['message']}",
                **error_info['context']
            )
            self.logger.debug(f"Traceback: {error_info['traceback']}")
    
    def handle_critical(self, error: Exception, context: Optional[dict] = None) -> None:
        """Maneja un error crítico y termina el programa"""
        self.handle(error, context)
        if self.logger:
            self.logger.critical("Error crítico detectado. Terminando programa.")
        sys.exit(1)
    
    def get_error_summary(self) -> dict:
        """Retorna resumen de errores"""
        return {
            'total_errors': self.error_count,
            'error_types': list(set(e['type'] for e in self.error_history)),
            'recent_errors': self.error_history[-5:] if self.error_history else []
        }

# Decorador para manejo de errores

def handle_errors(error_handler: Optional[ErrorHandler] = None, 
                 reraise: bool = False,
                 default_return: Any = None):
    """Decorador para manejo automático de errores
    
    Args:
        error_handler: Handler de errores a usar
        reraise: Si True, relanza la excepción después de manejarla
        default_return: Valor a retornar si hay error y no se relanza
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler:
                    context = {
                        'function': func.__name__,
                        'args': str(args)[:100],
                        'kwargs': str(kwargs)[:100]
                    }
                    error_handler.handle(e, context)
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator

# Función helper para validación

def validate_or_raise(condition: bool, message: str, 
                     error_type: type = ValidationError) -> None:
    """Valida una condición y lanza excepción si falla
    
    Args:
        condition: Condición a validar
        message: Mensaje de error
        error_type: Tipo de excepción a lanzar
    """
    if not condition:
        raise error_type(message)

# Instancia global
_global_error_handler = None

def get_error_handler(logger=None):
    """Obtiene o crea el error handler global"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler(logger)
    return _global_error_handler
