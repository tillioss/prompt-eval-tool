# Contributing to LLM Evaluation Playground

Thank you for your interest in contributing! This guide explains how to set up testing and code style checks.

## Quick Start

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
# Open htmlcov/index.html in your browser
```

### 3. Check Code Style

```bash
# Format code
black .

# Check formatting (without changing)
black --check .

# Lint code
flake8 .
```

### 4. Run All Checks

**Linux/Mac:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Windows:**
```cmd
run_tests.bat
```

## Testing Requirements

### Have Unit Tests, Functional Tests, and Fuzz Tests

#### Unit Tests
Fast, isolated tests that test individual functions/classes:

```python
import pytest
from models import ModelAnswer

@pytest.mark.unit
class TestModelAnswer:
    def test_valid_answer(self):
        answer = ModelAnswer(content="Test")
        assert answer.content == "Test"
```

#### Functional Tests
Test complete workflows:

```python
@pytest.mark.functional
def test_complete_evaluation_workflow():
    # Test the entire evaluation process
    pass
```

#### Fuzz Tests (Where Appropriate)
For input validation, use property-based testing:

```python
import pytest
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_model_answer_accepts_any_text(text):
    answer = ModelAnswer(content=text)
    assert answer.content == text
```

### Follow Code Style Guidelines

1. **Format with Black** (line length: 100)
   ```bash
   black .
   ```

2. **Lint with Flake8**
   ```bash
   flake8 .
   ```

3. **Follow PEP 8** conventions

### Not Break the Existing Test Suite

**Before making changes:**
```bash
pytest  # Ensure all tests pass
```

**After making changes:**
```bash
pytest  # Ensure tests still pass
```

**If tests fail:**
- Fix bugs if behavior unintentionally changed
- Update tests if behavior intentionally changed

### Bug Fix Testing Pattern

When fixing a bug, **always** include tests that:

1. **Demonstrate the bug** (test that shows the bug exists)
2. **Prove the fix works** (test that verifies the bug is fixed)

**Example:**

```python
class TestBugFix:
    def test_bug_demonstration(self):
        """This test demonstrates the bug"""
        with pytest.raises(ValidationError):
            ModelAnswer(content="")  # Should fail
    
    def test_fix_verification(self):
        """This test proves the fix works"""
        answer = ModelAnswer(content="Valid")
        assert answer.content == "Valid"
```

## Workflow Example

Here's a complete example workflow for fixing a bug:

```bash
# 1. Create branch
git checkout -b fix-empty-string-validation

# 2. Write test that demonstrates bug
# (Add test to tests/test_models.py)

# 3. Run test - it should fail
pytest tests/test_models.py::TestBugFix::test_bug_demonstration -v

# 4. Fix the bug
# (Edit models.py)

# 5. Run test again - it should pass
pytest tests/test_models.py::TestBugFix::test_bug_demonstration -v

# 6. Add verification tests
# (Add test_fix_verification tests)

# 7. Run all tests
pytest

# 8. Format code
black .

# 9. Check linting
flake8 .

# 10. Commit
git add .
git commit -m "Fix: Add validation for empty string in ModelAnswer"
```

## Pre-Commit Checklist

Before submitting a PR, ensure:

- ✅ All tests pass: `pytest`
- ✅ Code is formatted: `black --check .`
- ✅ No linting errors: `flake8 .`
- ✅ Code coverage maintained (>80% for new code)
- ✅ Tests included for bug fixes (demonstrating bug + proving fix)

## Resources

- **Testing Guide**: See `TESTING_GUIDE.md` for detailed testing instructions
- **Test Examples**: See `tests/` directory for example tests
- **pytest docs**: https://docs.pytest.org/
- **black docs**: https://black.readthedocs.io/
- **flake8 docs**: https://flake8.pycqa.org/

## Getting Help

If you have questions:
1. Check `TESTING_GUIDE.md` for detailed instructions
2. Look at existing tests in `tests/` for examples
3. Open an issue on GitHub

Thank you for contributing! 🎉

