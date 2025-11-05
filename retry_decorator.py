#!/usr/bin/env python3
"""Retry decorator para MT5 Smart Optimizer v2
Provee lógica de reintentos con backoff exponencial"""
import time
import functools
from typing import Callable, Optional, Tuple, Type
import random

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
    jitter: bool = True
):
    """Decorador para reintentar una función si falla
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Delay inicial en segundos
        backoff: Factor multiplicador del delay
        exceptions: Tupla de excepciones a capturar
        on_retry: Callback a ejecutar en cada reintento
        jitter: Si True, añade variación aleatoria al delay
    
    Ejemplo:
        @retry(max_attempts=5, delay=2.0, exceptions=(ConnectionError,))
        def connect_to_mt5():
            # código de conexión
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        # Último intento, relanzar excepción
                        raise
                    
                    # Calcular delay con jitter opcional
                    wait_time = current_delay
                    if jitter:
                        wait_time *= (0.5 + random.random())  # 50%-150% del delay
                    
                    # Ejecutar callback si existe
                    if on_retry:
                        on_retry(attempt, max_attempts, e, wait_time)
                    
                    # Esperar antes del siguiente intento
                    time.sleep(wait_time)
                    
                    # Incrementar delay para siguiente intento
                    current_delay *= backoff
            
            # Esto no debería alcanzarse, pero por seguridad
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

def retry_with_timeout(
    max_attempts: int = 3,
    delay: float = 1.0,
    timeout: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorador de retry con timeout global
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Delay entre intentos
        timeout: Timeout total en segundos
        exceptions: Tupla de excepciones a capturar
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                # Verificar timeout
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    raise TimeoutError(
                        f"Timeout de {timeout}s excedido después de {attempt-1} intentos"
                    )
                
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        raise
                    
                    time.sleep(min(delay, timeout - elapsed))
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

class RetryStrategy:
    """Clase para estrategias de retry personalizadas"""
    
    @staticmethod
    def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calcula delay con backoff exponencial"""
        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
        return delay
    
    @staticmethod
    def linear_backoff(attempt: int, base_delay: float = 1.0, increment: float = 1.0) -> float:
        """Calcula delay con backoff lineal"""
        return base_delay + (increment * (attempt - 1))
    
    @staticmethod
    def fibonacci_backoff(attempt: int, base_delay: float = 1.0) -> float:
        """Calcula delay con secuencia de Fibonacci"""
        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)
        return base_delay * fib(attempt)

# Ejemplo de uso con logger
def create_retry_callback(logger):
    """Crea un callback de retry que usa el logger"""
    def callback(attempt, max_attempts, exception, wait_time):
        logger.warning(
            f"Intento {attempt}/{max_attempts} fallido",
            exception=str(exception),
            wait_time=wait_time,
            next_attempt=attempt + 1
        )
    return callback
