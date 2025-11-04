from typing import Dict, List
from pydantic import BaseModel, Field, validator


class EMTScores(BaseModel):
    EMT1: List[float] = Field(
        ..., description="Visual Emotion Matching scores", example=[65.0, 70.0, 68.0, 72.0, 69.0]
    )
    EMT2: List[float] = Field(
        ..., description="Emotion Description scores", example=[58.0, 62.0, 60.0, 64.0, 61.0]
    )
    EMT3: List[float] = Field(
        ..., description="Expression Labeling scores", example=[72.0, 75.0, 70.0, 78.0, 74.0]
    )
    EMT4: List[float] = Field(
        ..., description="Label Matching scores", example=[63.0, 65.0, 64.0, 67.0, 66.0]
    )

    @validator("*")
    def validate_scores(cls, v):
        if not all(0 <= score <= 100 for score in v):
            raise ValueError("All scores must be between 0 and 100")
        return v


class ClassMetadata(BaseModel):
    class_id: str = Field(
        ..., description="Unique identifier for the class", example="CLASS_5A_2024"
    )
    deficient_area: str = Field(
        ..., description="Primary area needing intervention", example="EMT2"
    )
    num_students: int = Field(..., description="Number of students in the class", example=25)

    @validator("deficient_area")
    def validate_deficient_area(cls, v):
        valid_areas = {"EMT1", "EMT2", "EMT3", "EMT4"}
        if v not in valid_areas:
            raise ValueError(f"deficient_area must be one of {valid_areas}")
        return v


class InterventionRequest(BaseModel):
    scores: EMTScores
    metadata: ClassMetadata

    class Config:
        json_schema_extra = {
            "example": {
                "scores": {
                    "EMT1": [65.0, 70.0, 68.0, 72.0, 69.0],
                    "EMT2": [58.0, 62.0, 60.0, 64.0, 61.0],
                    "EMT3": [72.0, 75.0, 70.0, 78.0, 74.0],
                    "EMT4": [63.0, 65.0, 64.0, 67.0, 66.0],
                },
                "metadata": {
                    "class_id": "CLASS_5A_2024",
                    "deficient_area": "EMT2",
                    "num_students": 25,
                },
            }
        }


class InterventionStrategy(BaseModel):
    activity: str = Field(..., description="Name of the EMT activity")
    implementation: List[str] = Field(..., description="Implementation steps")
    expected_outcomes: List[str] = Field(..., description="Expected outcomes")
    time_allocation: str = Field(..., description="Time required for the activity")
    resources: List[str] = Field(..., description="Required resources")


class SuccessMetrics(BaseModel):
    quantitative: List[str] = Field(..., description="Quantitative targets")
    qualitative: List[str] = Field(..., description="Qualitative indicators")
    assessment_methods: List[str] = Field(..., description="Methods for assessment")


class InterventionPlan(BaseModel):
    analysis: str = Field(..., description="Analysis of performance data")
    strategies: List[InterventionStrategy] = Field(..., min_items=1, max_items=5)
    timeline: Dict[str, List[str]] = Field(..., description="4-week implementation timeline")
    success_metrics: SuccessMetrics


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="Service version")
    llm_provider: str = Field(..., description="Current LLM provider")
