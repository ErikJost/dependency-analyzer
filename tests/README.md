# MCP Server Test Suite

This directory contains tests for the Dependency Analyzer MCP Server.

## Test Structure

The test suite is organized as follows:

- `unit/`: Unit tests for individual modules
- `integration/`: Integration tests that test interactions between components
- `conftest.py`: Shared fixtures and test utilities

## Running Tests

To run the entire test suite:

```bash
pytest
```

To run tests with coverage reporting:

```bash
pytest --cov=. --cov-report=term --cov-report=html
```

To run a specific test file:

```bash
pytest tests/unit/test_validation.py
```

To run a specific test:

```bash
pytest tests/unit/test_validation.py::TestValidation::test_validate_valid_resource_uri
```

## Test Coverage

The test suite aims to cover:

1. **Validation**: Testing that request parameters are properly validated against schemas
2. **Error Handling**: Testing error responses and error codes
3. **Logging**: Testing structured logging and correlation IDs
4. **API**: Testing API endpoints for tools and resources

## Adding New Tests

When adding a new feature, follow these guidelines:

1. Create a unit test for any new module in the `unit/` directory
2. Create integration tests for interactions between components
3. Use fixtures from `conftest.py` when possible
4. Follow the naming conventions:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

## Mocking

For tests that require external dependencies (such as file system or subprocess calls), use mock objects from `pytest-mock`:

```python
def test_with_mock(mocker):
    # Mock external function
    mock_func = mocker.patch('module.function')
    mock_func.return_value = 'mocked result'
    
    # Test code that calls the function
    result = code_under_test()
    
    # Assert that the function was called and result is as expected
    mock_func.assert_called_once()
    assert result == 'expected result'
``` 