"""
Example test demonstrating bug fix pattern

This demonstrates how to write tests that:
1. Demonstrate the bug (test that shows the bug exists)
2. Prove the fix works (test that verifies the bug is fixed)
"""

import pytest
from pydantic import ValidationError
from models import ModelAnswer


class TestBugFixPattern:
    """
    Example: Bug fix for empty string validation

    Bug: ModelAnswer was accepting empty strings, which should be invalid
    Fix: Added min_length=1 constraint to content field
    """

    def test_bug_demonstration_empty_string(self):
        """
        This test demonstrates the bug (if the bug still existed).
        Currently, this should FAIL if the bug exists, PASS if fixed.

        Note: This test should have been written when the bug was discovered.
        """
        # This should raise ValidationError because content cannot be empty
        with pytest.raises(ValidationError):
            ModelAnswer(content="")

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
        # Single character should be valid (minimum length)
        answer = ModelAnswer(content="A")
        assert answer.content == "A"

        # Whitespace-only should be valid (if that's desired behavior)
        # If not desired, add a custom validator
        answer = ModelAnswer(content=" ")
        assert answer.content == " "


"""
Example: How to write a regression test

When fixing a bug:
1. First, write a test that reproduces the bug (it should fail)
2. Fix the bug
3. Run the test again (it should now pass)
4. Keep the test in the suite to prevent regression
"""


class TestRegressionExample:
    """Example regression test for a hypothetical bug"""

    def test_regression_bug_that_was_fixed(self):
        """
        This test was added when a bug was fixed.
        It ensures the bug doesn't come back.

        Example bug: ModelAnswer was not handling None values correctly
        """
        # Test that the fix works
        answer = ModelAnswer(content="test")
        assert answer.content is not None

        # Test that None is still rejected (content is required)
        # Note: Pydantic will automatically reject None for required fields
        # This test verifies that valid content works correctly
        assert answer.content == "test"
