from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class SkillArea(str, Enum):
    EMOTIONAL_AWARENESS = "emotional_awareness"
    EMOTIONAL_REGULATION = "emotional_regulation"
    ANGER_MANAGEMENT = "anger_management"


class GradeLevel(str, Enum):
    GRADE_1 = "1"
    GRADE_2 = "2"
    GRADE_5 = "5"


class Implementation(BaseModel):
    steps: List[str] = Field(..., description="Implementation steps")
    materials: Optional[List[str]] = Field(default=None, description="Required materials")
    time_allocation: Optional[str] = Field(
        default=None, description="Suggested time for the activity"
    )


class CurriculumIntervention(BaseModel):
    name: str = Field(..., description="Name of the intervention")
    grade_levels: List[GradeLevel] = Field(..., description="Applicable grade levels")
    skill_area: SkillArea = Field(..., description="Primary skill area targeted")
    summary: str = Field(..., description="Brief summary of the intervention")
    implementation: Implementation = Field(..., description="Implementation details")
    intended_purpose: str = Field(..., description="Educational purpose and expected outcomes")


class CurriculumRequest(BaseModel):
    grade_level: GradeLevel = Field(..., description="Student grade level")
    skill_areas: List[SkillArea] = Field(..., description="Skill areas to focus on")
    score: float = Field(..., ge=0, le=100, description="Current performance score")


class CurriculumResponse(BaseModel):
    recommended_interventions: List[CurriculumIntervention] = Field(
        ..., description="List of recommended interventions"
    )
    skill_focus: List[str] = Field(..., description="Areas of focus based on score")
    implementation_order: List[str] = Field(..., description="Suggested order of implementation")
