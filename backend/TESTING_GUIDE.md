# Testing Guide - Festipin Backend

## Quick Start

### Run All Tests
```bash
source venv-3.12/bin/activate
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only (fast)
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v -m integration

# Specific test file
python -m pytest tests/unit/test_runware_provider.py -v

# Specific test class
python -m pytest tests/unit/test_runware_provider.py::TestRunwareProviderInitialization -v

# Specific test
python -m pytest tests/unit/test_runware_provider.py::TestRunwareProviderInitialization::test_initialize_with_valid_api_key -v
```

## Test Structure

```
tests/
├── unit/                           # Fast, isolated unit tests
│   └── test_runware_provider.py   # 22 tests for Runware provider
└── integration/                    # Integration tests with external services
    └── test_provider_integration.py # 11 tests for end-to-end workflows
```

## Test Categories

### Unit Tests (22 tests)
- **Initialization**: 9 tests for provider initialization edge cases
- **Validation**: 6 tests for request parameter validation
- **Generation**: 3 tests for image generation logic
- **Properties**: 4 tests for provider metadata

### Integration Tests (11 tests)
- **Service Manager**: Provider registration and initialization
- **Generation**: End-to-end image generation workflows
- **Robustness**: Error handling and edge cases
- **Concurrency**: Multiple concurrent requests

## Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

## Debugging Failed Tests

### Verbose Output
```bash
pytest tests/ -vv --tb=long
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Run Only Failed Tests
```bash
pytest --lf  # last failed
pytest --ff  # failed first
```

### Stop on First Failure
```bash
pytest -x
```

## Coverage Reports

### Generate HTML Coverage Report
```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Terminal Coverage Report
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## Continuous Integration

### Run Tests in CI Pipeline
```bash
#!/bin/bash
source venv-3.12/bin/activate
python -m pytest tests/ -v --tb=short --maxfail=5
```

## Common Issues

### Import Errors
- Ensure virtual environment is activated: `source venv-3.12/bin/activate`
- Ensure you're in backend directory: `cd backend`

### Async Test Warnings
- These are normal and handled by pytest-asyncio
- Configuration in pytest.ini: `asyncio_mode = auto`

### Timeout Issues
- Default timeout: 300s per test
- Increase if needed: `pytest --timeout=600`

## Writing New Tests

### Unit Test Template
```python
import pytest
from unittest.mock import patch, AsyncMock

class TestMyFeature:
    @pytest.mark.asyncio
    async def test_feature_works(self):
        # Arrange
        with patch('module.dependency') as mock_dep:
            mock_dep.return_value = "expected"
            
            # Act
            result = await my_function()
            
            # Assert
            assert result == "expected"
            mock_dep.assert_called_once()
```

### Integration Test Template
```python
import pytest

class TestMyIntegration:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_integration_works(self):
        # Arrange
        manager = ServiceManager()
        await manager.initialize()
        
        # Act
        result = await manager.do_something()
        
        # Assert
        assert result is not None
        assert result.success is True
```

## Best Practices

1. **Isolate Tests**: Use mocks for external dependencies
2. **Clear Names**: Test names should describe what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Fast Tests**: Keep unit tests under 1 second
5. **Independent Tests**: Tests should not depend on each other
6. **Clean Up**: Use fixtures for setup/teardown

## Useful Commands

```bash
# List all tests without running
pytest --collect-only

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Generate JUnit XML report
pytest --junit-xml=test-results.xml

# Watch for file changes and re-run tests
pytest-watch
```
