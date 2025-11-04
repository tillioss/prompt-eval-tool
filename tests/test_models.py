"""
Unit tests for Pydantic models
"""
import pytest
from pydantic import ValidationError

from models import ModelAnswer, EvaluationResult


class TestModelAnswer:
    """Test cases for ModelAnswer model"""
    
    def test_valid_model_answer(self):
        """Test creating a valid ModelAnswer"""
        answer = ModelAnswer(content="This is a test answer")
        assert answer.content == "This is a test answer"
        assert answer.reasoning is None
    
    def test_model_answer_with_reasoning(self):
        """Test ModelAnswer with reasoning field"""
        answer = ModelAnswer(
            content="Test content",
            reasoning="This is the reasoning"
        )
        assert answer.content == "Test content"
        assert answer.reasoning == "This is the reasoning"
    
    def test_model_answer_empty_content_fails(self):
        """Test that empty content raises ValidationError"""
        with pytest.raises(ValidationError):
            ModelAnswer(content="")
    
    def test_model_answer_extra_fields_allowed(self):
        """Test that extra fields are allowed (Config.extra = 'allow')"""
        answer = ModelAnswer(
            content="Test",
            extra_field="This should be allowed"
        )
        assert answer.content == "Test"
        assert hasattr(answer, 'extra_field')


class TestEvaluationResult:
    """Test cases for EvaluationResult model"""
    
    def test_valid_evaluation_result(self):
        """Test creating a valid EvaluationResult"""
        result = EvaluationResult(
            feedback="Good answer",
            total_rating=8
        )
        assert result.feedback == "Good answer"
        assert result.total_rating == 8
    
    def test_evaluation_result_rating_bounds(self):
        """Test that rating must be between 1 and 10"""
        # Valid ratings
        EvaluationResult(feedback="Test", total_rating=1)
        EvaluationResult(feedback="Test", total_rating=10)
        EvaluationResult(feedback="Test", total_rating=5)
        
        # Invalid ratings
        with pytest.raises(ValidationError):
            EvaluationResult(feedback="Test", total_rating=0)
        
        with pytest.raises(ValidationError):
            EvaluationResult(feedback="Test", total_rating=11)
        
        with pytest.raises(ValidationError):
            EvaluationResult(feedback="Test", total_rating=-1)

