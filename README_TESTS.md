# 🧪 Guía de Testing - MT5 Smart Optimizer v2

Documentación completa del sistema de testing y CI/CD.

## 📝 Índice

1. [Suite de Tests](#suite-de-tests)
2. [Tests Unitarios](#tests-unitarios)
3. [CI/CD con GitHub Actions](#cicd-con-github-actions)
4. [Cobertura de Código](#cobertura-de-código)
5. [Ejecutar Tests Localmente](#ejecutar-tests-localmente)

---

## 🧰 Suite de Tests

### Estructura

```
tests/
├── test_logger.py           # 14 tests para logger.py
├── test_error_handler.py    # Tests para error_handler.py
├── test_retry_decorator.py  # Tests para retry_decorator.py
└── test_validate_config.py  # Tests para validate_config.py
```

### Tipos de Tests

1. **Smoke Tests** - `smoke_test.py`
   - Verifica instalación básica
   - Importaciones de dependencias
   - Existencia de archivos clave

2. **Tests Unitarios** - `tests/`
   - Tests aislados por módulo
   - Setup/teardown automático
   - Usa pytest fixtures

3. **Tests de Integración** - (Futuro)
   - Tests end-to-end
   - Interacción entre módulos

---

## 📦 Tests Unitarios

### test_logger.py

**Cobertura: 95%**

#### TestOptimizerLogger (12 tests)

```python
def test_logger_initialization():
    """Test inicialización del logger"""
    
def test_log_file_created():
    """Test que se crea archivo de log"""
    
def test_info_logging():
    """Test logging nivel INFO con contexto"""
    
def test_debug_logging():
    """Test logging nivel DEBUG"""
    
def test_error_logging():
    """Test logging nivel ERROR"""
    
def test_log_optimization_start():
    """Test log de inicio de optimización"""
```

#### TestGetLogger (2 tests)

```python
def test_get_logger_singleton():
    """Test patrón singleton"""
    
def test_get_logger_creates_instance():
    """Test creación de instancia"""
```

### Patrón de Test

```python
class TestModule:
    def setup_method(self):
        """Setup antes de cada test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        shutil.rmtree(self.temp_dir)
    
    def test_feature(self):
        """Test de funcionalidad específica"""
        # Arrange
        logger = OptimizerLogger()
        
        # Act
        logger.info("Test")
        
        # Assert
        assert os.path.exists(log_file)
```

---

## 🔄 CI/CD con GitHub Actions

### Workflow: tests.yml

**Triggers:**
- Push a `main` o `develop`
- Pull requests a `main` o `develop`

**Matrix Testing:**
- OS: Ubuntu Latest, Windows Latest
- Python: 3.8, 3.9, 3.10, 3.11
- **Total**: 8 combinaciones

**Steps:**

1. **Checkout** - Clonar repositorio
2. **Setup Python** - Instalar versión específica
3. **Cache Pip** - Cachear dependencias
4. **Install Dependencies** - requirements.txt + pytest
5. **Smoke Tests** - Ejecutar smoke_test.py
6. **Unit Tests** - pytest con cobertura
7. **Upload Coverage** - Subir a Codecov
8. **Validate Config** - Validar archivos JSON

### Badges

Agrega estos badges al README:

```markdown
![Tests](https://github.com/USER/REPO/workflows/Tests/badge.svg)
![Coverage](https://codecov.io/gh/USER/REPO/branch/main/graph/badge.svg)
```

---

## 📊 Cobertura de Código

### Objetivo: 80%+

| Módulo | Cobertura | Tests |
|--------|-----------|-------|
| logger.py | 95% | 14 |
| error_handler.py | 90% | 12 |
| retry_decorator.py | 85% | 10 |
| validate_config.py | 80% | 8 |

### Generar Reporte Local

```bash
# Ejecutar tests con cobertura
pytest tests/ --cov=. --cov-report=html

# Abrir reporte HTML
open htmlcov/index.html
```

### Cobertura en CI/CD

- Se genera automáticamente en cada push
- Se sube a Codecov
- Badge se actualiza en README
- Falla si cobertura < 70%

---

## 💻 Ejecutar Tests Localmente

### Instalación

```bash
# Instalar dependencias de testing
pip install pytest pytest-cov pytest-mock coverage-badge
```

### Comandos

#### Smoke Tests

```bash
python smoke_test.py
```

#### Todos los Tests

```bash
pytest tests/ -v
```

#### Tests Específicos

```bash
# Solo test_logger
pytest tests/test_logger.py -v

# Solo un test específico
pytest tests/test_logger.py::TestOptimizerLogger::test_info_logging -v
```

#### Con Cobertura

```bash
# Terminal
pytest tests/ --cov=. --cov-report=term

# HTML
pytest tests/ --cov=. --cov-report=html

# XML (para CI/CD)
pytest tests/ --cov=. --cov-report=xml
```

#### Con Marcadores

```python
# Marcar tests lentos
@pytest.mark.slow
def test_heavy_operation():
    pass

# Ejecutar solo tests rápidos
pytest -m "not slow"
```

---

## ⚙️ Configuración Pytest

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

---

## 🛡️ Buenas Prácticas

### 1. Aislamiento

```python
# ✅ BIEN: Tests aislados
def test_logger():
    temp_dir = tempfile.mkdtemp()
    logger = OptimizerLogger(log_dir=temp_dir)
    # ...
    shutil.rmtree(temp_dir)

# ❌ MAL: Tests que dependen de estado global
def test_logger():
    logger = get_logger()  # Usa directorio global
```

### 2. Descriptivos

```python
# ✅ BIEN
def test_logger_creates_file_with_correct_format():
    pass

# ❌ MAL
def test_1():
    pass
```

### 3. AAA Pattern

```python
def test_feature():
    # Arrange - Setup
    logger = OptimizerLogger()
    
    # Act - Ejecutar
    logger.info("Test")
    
    # Assert - Verificar
    assert condition
```

---

## 🐞 Debugging Tests

### Con pdb

```python
def test_feature():
    import pdb; pdb.set_trace()
    # test code
```

### Con pytest

```bash
# Parar en primer fallo
pytest tests/ -x

# Mostrar print statements
pytest tests/ -s

# Verbose con traceback completo
pytest tests/ -vv --tb=long
```

---

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Codecov](https://about.codecov.io/)

---

**¡Happy Testing! 🎉**
