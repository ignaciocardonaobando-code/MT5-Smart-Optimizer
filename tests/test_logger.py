#!/usr/bin/env python3
"""Tests unitarios para logger.py"""
import pytest
import os
import tempfile
import shutil
import logging
from logger import OptimizerLogger, get_logger


class TestOptimizerLogger:
    """Tests para la clase OptimizerLogger"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        self.test_log_dir = tempfile.mkdtemp()
        self.logger = OptimizerLogger(
            name="TestLogger",
            log_dir=self.test_log_dir,
            level=logging.DEBUG
        )
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
    
    def test_logger_initialization(self):
        """Test que el logger se inicializa correctamente"""
        assert self.logger.name == "TestLogger"
        assert self.logger.log_dir == self.test_log_dir
        assert os.path.exists(self.test_log_dir)
    
    def test_log_file_created(self):
        """Test que se crea el archivo de log"""
        self.logger.info("Test message")
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        assert os.path.exists(log_file)
    
    def test_info_logging(self):
        """Test logging nivel INFO"""
        self.logger.info("Info message", param1="value1")
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Info message" in content
            assert "param1" in content
    
    def test_debug_logging(self):
        """Test logging nivel DEBUG"""
        self.logger.debug("Debug message", test="data")
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Debug message" in content
    
    def test_error_logging(self):
        """Test logging nivel ERROR"""
        self.logger.error("Error occurred", error_code=500)
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Error occurred" in content
            assert "error_code" in content
    
    def test_warning_logging(self):
        """Test logging nivel WARNING"""
        self.logger.warning("Warning message")
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Warning message" in content
    
    def test_critical_logging(self):
        """Test logging nivel CRITICAL"""
        self.logger.critical("Critical error")
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Critical error" in content
    
    def test_log_optimization_start(self):
        """Test log de inicio de optimización"""
        config = {
            'test': {'symbol': 'EURUSD', 'timeframe': 'H1'},
            'optimizer': {'n_trials': 100}
        }
        self.logger.log_optimization_start(config)
        
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Iniciando optimización" in content
            assert "EURUSD" in content
    
    def test_log_trial(self):
        """Test log de trial individual"""
        params = {'BBPeriod': 20, 'StochK': 14}
        self.logger.log_trial(1, params, 1.85)
        
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Trial 1 completado" in content
    
    def test_log_optimization_end(self):
        """Test log de fin de optimización"""
        best_params = {'BBPeriod': 22, 'StochK': 13}
        self.logger.log_optimization_end(best_params, 1.95, 3600)
        
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Optimización completada" in content
            assert "1.95" in content
    
    def test_context_in_log(self):
        """Test que el contexto se incluye en JSON"""
        self.logger.info("Test", key1="value1", key2="value2")
        
        log_file = os.path.join(self.test_log_dir, "TestLogger.log")
        with open(log_file, 'r') as f:
            content = f.read()
            assert "key1" in content
            assert "value1" in content


class TestGetLogger:
    """Tests para la función get_logger"""
    
    def test_get_logger_singleton(self):
        """Test que get_logger retorna el mismo logger"""
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2
    
    def test_get_logger_creates_instance(self):
        """Test que get_logger crea una instancia"""
        logger = get_logger()
        assert logger is not None
        assert isinstance(logger, OptimizerLogger)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
