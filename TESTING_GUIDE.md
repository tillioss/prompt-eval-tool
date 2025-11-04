# Testing and Code Style Guide

This guide explains how to implement the testing and code style requirements for contributing to the LLM Evaluation Playground.

## Table of Contents

1. [Setting Up Testing](#setting-up-testing)
2. [Writing Tests](#writing-tests)
3. [Running Tests](#running-tests)
4. [Code Style Guidelines](#code-style-guidelines)
5. [Bug Fix Testing Pattern](#bug-fix-testing-pattern)

## Setting Up Testing

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-cov` - Code coverage reporting
- `pytest-mock` - Mocking utilities
- `black` - Code formatter
- `flake8` - Linter
- `pylint` - Code quality checker
- `mypy` - Type checker

### 2. Verify Setup

Run a quick test to ensure everything is installed:
```bash
pytest tests/ -v
```

## Writing Tests

### Test Structure

Tests are organized in the `tests/` directory. Follow this structure:

```
tests/
├── test_models.py          # Tests for models.py
├── test_logger.py          # Tests for logger.py
├── test_judge.py           # Tests for judge.py
└── test_*.py              # Other test files
```

### Test Types

#### 1. Unit Tests (Fast, Isolated)
```python
import pytest
from models import ModelAnswer

@pytest.mark.unit
class TestModelAnswer:
    def test_valid_answer(self):
        """Test creating a valid ModelAnswer"""
        answer = ModelAnswer(content="Test")
        assert answer.content == "Test"
```

#### 2. Integration Tests (May Require External Services)
```python
@pytest.mark.integration
def test_api_integration():
    """Test integration with external API"""
    # This might require API keys or external services
    pass
```

#### 3. Functional Tests (End-to-End Workflows)
```python
@pytest.mark.functional
def test_complete_evaluation_workflow():
    """Test the complete evaluation workflow"""
    # Test the entire process from input to output
    pass
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```
View coverage report: Open `htmlcov/index.html` in your browser

### Run Specific Test Types
```bash
# Only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Only integration tests
pytest -m integration
```

### Run Specific Test File
```bash
pytest tests/test_models.py
```

### Run Specific Test
```bash
pytest tests/test_models.py::TestModelAnswer::test_valid_answer
```

### Verify Tests Pass Before Committing
```bash
# Run all tests
pytest

# Check code style
black --check .
flake8 .

# If all pass, you're good to commit!
```

## Code Style Guidelines

### 1. Format Code with Black

Black is an opinionated code formatter. It ensures consistent code style.

**Format all code:**
```bash
black .
```

**Check formatting (without changing):**
```bash
black --check .
```

**Format specific file:**
```bash
black app.py
```

### 2. Lint with Flake8

Flake8 checks for style guide violations and programming errors.

**Run flake8:**
```bash
flake8 .
```

**Common issues:**
- Line too long (>100 characters)
- Unused imports
- Missing whitespace
- Syntax errors

### 3. Type Checking with Mypy (Optional)

Mypy checks for type errors:
```bash
mypy .
```

Note: This is optional as the project may not have complete type annotations yet.

### 4. Pre-commit Checklist

Before committing, ensure:
- ✅ All tests pass: `pytest`
- ✅ Code is formatted: `black --check .`
- ✅ No linting errors: `flake8 .`
- ✅ Code coverage is maintained (>80% for new code)

## Bug Fix Testing Pattern

When fixing a bug, **always** include tests that:

1. **Demonstrate the bug** (test that shows the bug exists)
2. **Prove the fix works** (test that verifies the bug is fixed)

### Example: Bug Fix Testing

**Bug**: ModelAnswer was accepting empty strings

```python
class TestBugFix:
    def test_bug_demonstration_empty_string(self):
        """
        This test demonstrates the bug.
        If the bug still exists, this test would fail.
        """
        # This should raise ValidationError
        with pytest.raises(ValidationError):
            ModelAnswer(content="")  # Empty string should be invalid
    
    def test_fix_verification_valid_content(self):
        """
        This test proves the fix works correctly.
        It verifies that valid content is still accepted.
        """
        # Valid content should work
        answer = ModelAnswer(content="Valid content")
        assert answer.content == "Valid content"
        assert len(answer.content) > 0
    
    def test_fix_verification_edge_cases(self):
        """
        Additional test to verify edge cases are handled correctly.
        This helps prevent regression.
        """
        # Single character should be valid
        answer = ModelAnswer(content="A")
        assert answer.content == "A"
```

### Steps for Bug Fix

1. **Identify the bug** - Understand what's wrong
2. **Write a failing test** - Test that demonstrates the bug
3. **Fix the bug** - Implement the fix
4. **Run the test** - Verify it now passes
5. **Add regression tests** - Ensure the bug doesn't come back
6. **Run all tests** - Make sure nothing else broke

## Not Breaking Existing Tests

### Before Making Changes

1. **Run all tests** to ensure they pass:
   ```bash
   pytest
   ```

2. **Check test coverage**:
   ```bash
   pytest --cov=. --cov-report=term-missing
   ```

### After Making Changes

1. **Run tests again** to ensure nothing broke:
   ```bash
   pytest
   ```

2. **If tests fail**, fix them:
   - Update tests if behavior intentionally changed
   - Fix bugs if behavior unintentionally changed

### When Adding New Features

1. **Write tests first** (Test-Driven Development):
   ```python
   def test_new_feature():
       # Test the new feature
       result = new_function()
       assert result == expected
   ```

2. **Implement the feature**

3. **Run tests** to verify they pass

## Example Workflow

Here's a complete example workflow for fixing a bug:

```bash
# 1. Create a branch for your fix
git checkout -b fix-empty-string-validation

# 2. Write a test that demonstrates the bug
# (Add test to test_models.py)

# 3. Run the test - it should fail (demonstrating the bug)
pytest tests/test_models.py::TestBugFix::test_bug_demonstration -v

# 4. Fix the bug in models.py
# (Add min_length=1 to content field)

# 5. Run the test again - it should now pass
pytest tests/test_models.py::TestBugFix::test_bug_demonstration -v

# 6. Add verification tests
# (Add test_fix_verification tests)

# 7. Run all tests to ensure nothing broke
pytest

# 8. Format code
black .

# 9. Check linting
flake8 .

# 10. Commit
git add .
git commit -m "Fix: Add validation for empty string in ModelAnswer"
```

## Quick Reference

### Test Commands
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=.            # With coverage
pytest -m unit            # Only unit tests
pytest tests/test_*.py    # Specific test files
```

### Code Style Commands
```bash
black .                   # Format all code
black --check .          # Check formatting
flake8 .                 # Lint code
```

### Pre-commit Checklist
```bash
pytest                    # ✅ Tests pass
black --check .          # ✅ Code formatted
flake8 .                 # ✅ No lint errors
```

## Getting Help

- Check existing tests in `tests/` for examples
- Read pytest documentation: https://docs.pytest.org/
- Read black documentation: https://black.readthedocs.io/
- Read flake8 documentation: https://flake8.pycqa.org/

## Summary

- ✅ **Write tests** for new features and bug fixes
- ✅ **Run tests** before committing: `pytest`
- ✅ **Format code** with black: `black .`
- ✅ **Check linting** with flake8: `flake8 .`
- ✅ **Don't break** existing tests
- ✅ **Include tests** that demonstrate bugs and prove fixes

Following these guidelines ensures code quality and prevents regressions! 🎉

