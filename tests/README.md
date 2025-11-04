# Testing Guide

This directory contains tests for the LLM Evaluation Playground project.

## Test Structure

```
tests/
├── __init__.py
├── test_models.py          # Unit tests for Pydantic models
├── test_logger.py          # Unit tests for logging functionality
├── test_judge.py           # Unit tests for judge.py (evaluation logic)
├── test_prompts.py         # Unit tests for prompts (curriculum and intervention)
└── README.md               # This file
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_models.py
```

### Run specific test
```bash
pytest tests/test_models.py::TestModelAnswer::test_valid_model_answer
```

### Run only unit tests (fast)
```bash
pytest -m unit
```

### Run only integration tests
```bash
pytest -m integration
```

### Skip slow tests
```bash
pytest -m "not slow"
```

## Test Types

### Unit Tests
- Fast, isolated tests
- No external dependencies (API keys, network calls)
- Test individual functions and classes
- Mark with `@pytest.mark.unit`

### Integration Tests
- May require external services or API keys
- Test interactions between components
- Mark with `@pytest.mark.integration`

### Functional Tests
- Test complete workflows
- May require setup of test data
- Mark with `@pytest.mark.functional`

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test Structure
```python
import pytest
from your_module import YourClass

class TestYourClass:
    """Test cases for YourClass"""
    
    def test_valid_case(self):
        """Test that valid input works correctly"""
        obj = YourClass(valid_input)
        assert obj.property == expected_value
    
    def test_invalid_case(self):
        """Test that invalid input raises error"""
        with pytest.raises(ValidationError):
            YourClass(invalid_input)
```

## Bug Fix Testing Pattern

When fixing a bug, follow this pattern:

1. **Write a test that demonstrates the bug** (it should fail)
2. **Fix the bug**
3. **Run the test again** (it should now pass)
4. **Keep the test** to prevent regression

Example:
```python
def test_bug_demonstration(self):
    """This test demonstrates the bug"""
    with pytest.raises(ExpectedError):
        # Code that should fail due to bug
        pass

def test_fix_verification(self):
    """This test proves the fix works"""
    # Code that should work after fix
    result = fixed_function()
    assert result == expected_value
```

## Code Coverage

Aim for >80% code coverage. Focus on:
- Core business logic
- Error handling paths
- Edge cases
- Bug fixes

Coverage reports are generated in `htmlcov/` directory.

## Mocking External Dependencies

Use `pytest-mock` or `unittest.mock` to mock:
- API calls (Gemini API)
- File I/O operations
- External services

Example:
```python
from unittest.mock import patch

@patch('your_module.external_function')
def test_with_mock(mock_function):
    mock_function.return_value = "mocked result"
    # Your test code
```

## Best Practices

1. **One assertion per test** (when possible)
2. **Use descriptive test names** that explain what is being tested
3. **Test edge cases** and error conditions
4. **Keep tests independent** - don't rely on execution order
5. **Use fixtures** for common setup/teardown
6. **Keep tests fast** - unit tests should run in milliseconds
7. **Document why** tests exist, especially for bug fixes

## Continuous Integration

Tests should pass before merging PRs. Run locally before pushing:
```bash
pytest
```

