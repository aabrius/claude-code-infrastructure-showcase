# 🧪 GAM API Testing Guide

## 📋 Overview

This guide provides comprehensive documentation for testing the GAM API project. The test suite includes unit tests, integration tests, and end-to-end tests to ensure code quality and reliability.

## 🏗️ Test Structure

```
tests/
├── unit/                    # Unit tests for individual modules
│   ├── test_auth.py        # ✅ Authentication tests
│   ├── test_client.py      # ✅ GAM client tests
│   ├── test_config.py      # ✅ Configuration tests
│   ├── test_models.py      # ✅ Data model tests
│   └── test_reports.py     # ✅ Report generation tests
├── integration/            # Integration tests
│   ├── test_mcp_tools.py   # ✅ MCP server tests
│   ├── test_rest_api.py    # ✅ REST API tests
│   └── test_gam_end_to_end.py # ✅ End-to-end workflows
├── fixtures/               # Test data and mocks
│   ├── __init__.py
│   ├── api_responses.py    # Mock API responses
│   └── mock_data.py        # ✅ Mock data generators
├── utils/                  # Test utilities
│   ├── __init__.py
│   └── test_helpers.py     # ✅ Helper functions
└── conftest.py            # ✅ Pytest configuration
```

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_auth.py

# Run specific test class
pytest tests/unit/test_auth.py::TestAuthManager

# Run specific test method
pytest tests/unit/test_auth.py::TestAuthManager::test_init_with_config
```

### Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run tests excluding slow ones
pytest -m "not slow"

# Run tests that don't require network
pytest -m "not network"
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Generate terminal coverage report
pytest --cov=src --cov-report=term

# Generate XML coverage report (for CI)
pytest --cov=src --cov-report=xml

# Check coverage with minimum threshold
pytest --cov=src --cov-fail-under=70
```

## 📊 Test Coverage Goals

| Module | Target Coverage | Current Status |
|--------|----------------|----------------|
| Core Modules | 90%+ | ✅ Implemented |
| API Routes | 85%+ | ✅ Implemented |
| MCP Tools | 80%+ | ✅ Implemented |
| Utils | 75%+ | 🔄 In Progress |
| Overall | 70%+ | ✅ Achieved |

## 🧩 Test Fixtures

### Common Fixtures (conftest.py)

```python
@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return Config(
        auth=AuthConfig(
            network_code="123456789",
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token"
        )
    )

@pytest.fixture
def mock_auth_manager():
    """Mock authentication manager."""
    # Returns configured mock auth manager

@pytest.fixture
def mock_gam_client():
    """Mock GAM client."""
    # Returns configured mock client

@pytest.fixture
def sample_report_data():
    """Sample report data for testing."""
    # Returns test report data
```

### Mock Data Generators

```python
from tests.fixtures.mock_data import MockDataGenerator

# Generate test data
delivery_data = MockDataGenerator.generate_delivery_report_data(days=7)
inventory_data = MockDataGenerator.generate_inventory_report_data(days=7)
sales_data = MockDataGenerator.generate_sales_report_data(days=7)

# Generate complete report
report = MockDataGenerator.generate_complete_report('delivery', days=30)
```

## 🧪 Writing Tests

### Unit Test Example

```python
class TestReportGenerator:
    """Test cases for ReportGenerator class."""
    
    def test_generate_quick_report(self, mock_gam_client, mock_config):
        """Test generating a quick report."""
        # Arrange
        generator = ReportGenerator(mock_gam_client, mock_config)
        
        # Act
        result = generator.generate_quick_report('delivery', days_back=7)
        
        # Assert
        assert isinstance(result, ReportResult)
        assert result.total_rows > 0
        assert len(result.dimension_headers) > 0
```

### Integration Test Example

```python
class TestMCPTools:
    """Integration tests for MCP tools."""
    
    @patch('src.mcp.fastmcp_server.get_auth_manager')
    def test_quick_report_integration(self, mock_auth):
        """Test quick report tool integration."""
        # Arrange
        mock_auth.return_value = Mock()
        
        # Act
        result = gam_quick_report(
            report_type="delivery",
            days_back=7,
            format="json"
        )
        
        # Assert
        result_data = json.loads(result)
        assert result_data["success"] is True
        assert result_data["report_type"] == "delivery"
```

### End-to-End Test Example

```python
class TestEndToEndWorkflow:
    """End-to-end workflow tests."""
    
    def test_complete_report_workflow(self):
        """Test complete report generation workflow."""
        # Test auth → client → report → download flow
        with patch('src.core.auth.AuthManager') as MockAuth:
            # Setup mocks
            # Execute workflow
            # Verify all steps
```

## 🔍 Test Utilities

### Test Helpers

```python
from tests.utils.test_helpers import ExtendedTestHelpers

# Capture logs during test
with ExtendedTestHelpers.capture_logs() as log_buffer:
    # Run code that generates logs
    logs = log_buffer.getvalue()
    assert "Expected log message" in logs

# Compare report data with tolerance
ExtendedTestHelpers.compare_report_data(
    actual_data,
    expected_data,
    tolerance=0.01
)

# Validate MCP response
response_data = ExtendedTestHelpers.validate_mcp_response(
    mcp_response,
    expected_success=True
)
```

### Performance Testing

```python
from tests.utils.test_helpers import PerformanceTimer

# Measure execution time
with PerformanceTimer() as timer:
    # Execute operation
    pass

assert timer.elapsed < 2.0  # Should complete in under 2 seconds
```

## 🐛 Debugging Tests

### Verbose Output

```bash
# Run with verbose output
pytest -v

# Run with extra verbose output
pytest -vv

# Show print statements
pytest -s

# Show locals on failure
pytest -l
```

### Debugging Specific Failures

```bash
# Run failed tests only
pytest --lf

# Run failed tests first, then others
pytest --ff

# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb
```

### Test Markers

```python
# Mark test as slow
@pytest.mark.slow
def test_large_report_generation():
    pass

# Mark test as requiring network
@pytest.mark.network
def test_api_connection():
    pass

# Skip test conditionally
@pytest.mark.skipif(
    not os.getenv('GAM_REFRESH_TOKEN'),
    reason="No credentials available"
)
def test_real_api():
    pass
```

## 📈 Coverage Analysis

### Generating Coverage Reports

```bash
# Generate detailed coverage report
coverage run -m pytest
coverage report
coverage html

# Check uncovered lines
coverage report -m

# Generate coverage badge
coverage-badge -o coverage.svg
```

### Coverage Configuration (.coveragerc)

```ini
[run]
source = src
omit = 
    */tests/*
    */conftest.py
    */__init__.py

[report]
precision = 2
skip_empty = True

[html]
directory = htmlcov
```

## 🔧 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -e ".[test]"
    
    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 🎯 Best Practices

### 1. Test Naming
- Use descriptive test names that explain what is being tested
- Follow pattern: `test_<what>_<condition>_<expected_result>`

### 2. Test Organization
- Group related tests in classes
- Use fixtures to avoid repetition
- Keep tests focused and independent

### 3. Mocking
- Mock external dependencies
- Use specific mocks rather than generic ones
- Verify mock calls when appropriate

### 4. Assertions
- Use specific assertions with clear messages
- Test both success and failure cases
- Verify edge cases

### 5. Performance
- Mark slow tests appropriately
- Use fixtures to share expensive setup
- Consider parallel test execution

## 🚨 Common Issues

### 1. Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .
```

### 2. Missing Dependencies
```bash
# Install test dependencies
pip install -e ".[test]"
```

### 3. Credential Issues
```bash
# Tests use mocks by default
# For integration tests with real API:
export GAM_REFRESH_TOKEN="your-token"
```

### 4. Flaky Tests
- Use proper mocking
- Avoid time-dependent assertions
- Handle async operations correctly

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

---

*Last updated: 2025-07-22 | Test Coverage: 70%+ achieved*