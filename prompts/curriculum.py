"""Prompt templates for curriculum-based intervention generation."""

from typing import Dict, Any
import json
from schemas.curriculum import CurriculumResponse


class CurriculumPrompt:
    """Manages prompt templates for curriculum-based intervention generation."""

    BASE_TEMPLATE = """You are an expert Educational Intervention Specialist focusing on emotional intelligence development in children.

TASK: Create a personalized intervention plan based on grade level and current performance.

SAFETY GUIDELINES - CRITICAL:
- Use ONLY positive, encouraging, and age-appropriate language
- Focus on growth, learning, and development opportunities
- Avoid any negative, harmful, or inappropriate content
- Use simple language that children can understand
- Ensure all activities are safe and suitable for the classroom
- Promote inclusivity and respect for all students
- All interventions must be developmentally appropriate for the specified grade level

STUDENT INFORMATION:
- Grade Level: {grade_level}
- Focus Areas: {skill_areas}
- Current Score: {score}%

AVAILABLE INTERVENTIONS:
{interventions}

Your response MUST be in valid JSON format matching this schema:
{schema}

Guidelines:
1. Select interventions appropriate for the grade level
2. Focus on areas where the score indicates need for improvement
3. Consider the developmental stage and capabilities
4. Provide a clear implementation order
5. Ensure all activities are age-appropriate and engaging
6. For strategy titles, keep them under 50 characters.
7. For descriptions, keep them under 200 characters.
8. For implementation steps, provide exactly 4 clear, concise steps.
9. For success metrics, provide 2-3 clear, measurable metrics.
10. ENSURE ALL CONTENT IS POSITIVE, SAFE, AND AGE-APPROPRIATE

Ensure your response is properly formatted and includes all required fields according to the schema. All content must be suitable for teachers to use with children in educational settings."""

    GEMINI_TEMPLATE = (
        BASE_TEMPLATE
        + """
Note: Return only a valid JSON object matching the schema exactly."""
    )

    # The curriculum data is stored as a class variable
    CURRICULUM_DATA = """
    10 Interventions for Emotional Awareness, Regulation, and Anger Management

    Emotional Awareness:
    1. Color Me (Grade 1):
       - Summary: Use color to represent different feelings
       - Implementation: Provide coloring pages with images or mandalas. Assign colors to specific emotions
       - Purpose: Develop emotional vocabulary and connect feelings with visual representations

    2. Feelings Chart (Grades 2 & 5):
       - Summary: Create a visual aid for emotion identification
       - Implementation: Display emotion charts, encourage pointing to current feelings
       - Purpose: Expand emotional vocabulary and promote self-awareness

    3. Who am I? (Grade 2):
       - Summary: Explore identity and self-perception
       - Implementation: Journal personal values, share thoughts safely
       - Purpose: Understanding self-identity

    4. This is me (Grade 2):
       - Summary: Create identity collages
       - Implementation: Students create collages showing different aspects of self
       - Purpose: Share and explore personal identity

    Emotional Regulation:
    5. Animal Sounds (Grade 1):
       - Summary: Use animal sounds for self-awareness
       - Implementation: Watch and learn from animal sound videos
       - Purpose: Build self-awareness through sound

    6. Mindfulness Exercise (Grades 2 & 5):
       - Summary: Practice body awareness
       - Implementation: Guide through body scan meditation
       - Purpose: Reduce stress and improve focus

    7. Heart Breathing (Grades 2 & 5):
       - Summary: Connect breath with body
       - Implementation: Feel heartbeat while practicing deep breathing
       - Purpose: Learn breath-body connection

    8. Growth Mindset Plan (Grade 2):
       - Summary: Develop positive affirmations
       - Implementation: Create and practice growth mindset activities
       - Purpose: Foster growth mindset

    Anger Management:
    9. Play the Judge (Grades 2 & 5):
       - Summary: Analyze scenarios and consequences
       - Implementation: Discuss various scenarios and appropriate responses
       - Purpose: Develop character and anger management skills

    10. Time Management (Grade 2 & 5):
        - Summary: Create time blocking charts
        - Implementation: Practice time management through scenarios
        - Purpose: Reduce anger through better time management
    """

    @classmethod
    def get_prompt(cls, provider: str, data: Dict[str, Any]) -> str:
        """Get formatted prompt for specified provider.

        Args:
            provider: LLM provider name ('gemini', 'openai', etc.)
            data: Dictionary containing template variables

        Returns:
            Formatted prompt string
        """
        # Add schema and curriculum data to template variables
        data["schema"] = json.dumps(CurriculumResponse.model_json_schema(), indent=2)
        data["interventions"] = cls.CURRICULUM_DATA

        # Format skill areas for prompt
        data["skill_areas"] = ", ".join(data["skill_areas"])

        # Select template based on provider
        template = {
            "gemini": cls.GEMINI_TEMPLATE,
        }.get(provider, cls.BASE_TEMPLATE)

        return template.format(**data)
