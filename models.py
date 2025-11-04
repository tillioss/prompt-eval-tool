"""
Pydantic models for validation
"""

from pydantic import BaseModel, Field
from typing import Optional


class ModelAnswer(BaseModel):
    """
    Schema for validating model-generated answers.
    Customize this schema based on your expected answer structure.
    """

    content: str = Field(..., min_length=1, description="The main content of the answer")
    reasoning: Optional[str] = Field(None, description="Optional reasoning or explanation")

    class Config:
        extra = "allow"  # Allow extra fields


class EvaluationResult(BaseModel):
    """
    Schema for evaluation results from the judge
    """

    feedback: str = Field(..., description="Feedback from the LLM judge")
    total_rating: int = Field(..., ge=1, le=10, description="Rating from 1 to 10")
