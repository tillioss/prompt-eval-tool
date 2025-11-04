"""
Unit tests for prompt generation modules.
"""

import pytest
from prompts.curriculum import CurriculumPrompt
from prompts.intervention import InterventionPrompt


class TestCurriculumPrompt:
    """Tests for CurriculumPrompt class."""

    @pytest.mark.unit
    def test_get_prompt_with_valid_data(self):
        """Test that get_prompt generates a valid prompt with all required fields."""
        data = {"grade_level": "1", "skill_areas": ["emotional_awareness"], "score": 25.0}

        prompt = CurriculumPrompt.get_prompt("gemini", data)

        # Check that prompt contains all required fields
        assert "Grade Level: 1" in prompt
        assert "emotional_awareness" in prompt
        assert "Current Score: 25.0%" in prompt
        assert "schema" in prompt.lower() or "json" in prompt.lower()
        assert CurriculumPrompt.CURRICULUM_DATA in prompt

    @pytest.mark.unit
    def test_get_prompt_formats_skill_areas(self):
        """Test that multiple skill areas are properly formatted."""
        data = {
            "grade_level": "2",
            "skill_areas": ["emotional_awareness", "emotional_regulation"],
            "score": 50.0,
        }

        prompt = CurriculumPrompt.get_prompt("gemini", data)

        # Skill areas should be joined with comma and space
        assert "emotional_awareness, emotional_regulation" in prompt

    @pytest.mark.unit
    def test_get_prompt_uses_gemini_template(self):
        """Test that gemini provider uses GEMINI_TEMPLATE."""
        data = {"grade_level": "1", "skill_areas": ["emotional_awareness"], "score": 25.0}

        prompt = CurriculumPrompt.get_prompt("gemini", data)

        # Gemini template should include the additional note
        assert "Return only a valid JSON object" in prompt

    @pytest.mark.unit
    def test_get_prompt_uses_base_template_for_unknown_provider(self):
        """Test that unknown provider falls back to BASE_TEMPLATE."""
        data = {"grade_level": "1", "skill_areas": ["emotional_awareness"], "score": 25.0}

        prompt = CurriculumPrompt.get_prompt("unknown_provider", data)

        # Should not include gemini-specific text
        assert "Return only a valid JSON object" not in prompt
        # But should still have base content
        assert "Grade Level: 1" in prompt


class TestInterventionPrompt:
    """Tests for InterventionPrompt class."""

    @pytest.mark.unit
    def test_get_prompt_with_valid_emt_data(self):
        """Test that get_prompt generates a valid prompt for EMT data."""
        data = {
            "class_id": "TEST_CLASS_1A",
            "num_students": 25,
            "deficient_area": "EMT1",
            "emt1_avg": 65.0,
            "emt2_avg": 70.0,
            "emt3_avg": 68.0,
            "emt4_avg": 72.0,
        }

        prompt = InterventionPrompt.get_prompt("gemini", data)

        # Check that prompt contains all required fields
        assert "Class ID: TEST_CLASS_1A" in prompt
        assert "Number of Students: 25" in prompt
        assert "Primary Area Needing Intervention: EMT1" in prompt
        assert "65.00%" in prompt
        assert "EMT1" in prompt
        assert "schema" in prompt.lower() or "json" in prompt.lower()

    @pytest.mark.unit
    def test_get_prompt_includes_strategies_for_known_emt(self):
        """Test that known EMT areas include their strategies."""
        data = {
            "class_id": "TEST_CLASS",
            "num_students": 25,
            "deficient_area": "EMT1",
            "emt1_avg": 65.0,
            "emt2_avg": 70.0,
            "emt3_avg": 68.0,
            "emt4_avg": 72.0,
        }

        prompt = InterventionPrompt.get_prompt("gemini", data)

        # Should include EMT1 strategies
        assert "Visual Emotion Recognition" in prompt
        assert "Emotion Flashcard Pairs" in prompt

    @pytest.mark.unit
    def test_get_prompt_handles_unknown_emt_area(self):
        """Test that unknown EMT areas get a fallback message."""
        data = {
            "class_id": "TEST_CLASS",
            "num_students": 25,
            "deficient_area": "UNKNOWN_EMT",
            "emt1_avg": 65.0,
            "emt2_avg": 70.0,
            "emt3_avg": 68.0,
            "emt4_avg": 72.0,
        }

        prompt = InterventionPrompt.get_prompt("gemini", data)

        # Should include fallback message
        assert "No specific strategies available" in prompt

    @pytest.mark.unit
    def test_get_prompt_uses_default_emt1_if_missing(self):
        """Test that missing deficient_area defaults to EMT1."""
        data = {
            "class_id": "TEST_CLASS",
            "num_students": 25,
            "emt1_avg": 65.0,
            "emt2_avg": 70.0,
            "emt3_avg": 68.0,
            "emt4_avg": 72.0,
        }

        prompt = InterventionPrompt.get_prompt("gemini", data)

        # Should default to EMT1 strategies
        assert "Visual Emotion Recognition" in prompt

    @pytest.mark.unit
    def test_get_prompt_formats_all_emt_scores(self):
        """Test that all EMT scores are properly formatted in prompt."""
        data = {
            "class_id": "TEST_CLASS",
            "num_students": 25,
            "deficient_area": "EMT2",
            "emt1_avg": 65.5,
            "emt2_avg": 70.25,
            "emt3_avg": 68.75,
            "emt4_avg": 72.0,
        }

        prompt = InterventionPrompt.get_prompt("gemini", data)

        # Check all scores are formatted with 2 decimal places
        assert "65.50%" in prompt
        assert "70.25%" in prompt
        assert "68.75%" in prompt
        assert "72.00%" in prompt

    @pytest.mark.unit
    def test_get_prompt_uses_gemini_template(self):
        """Test that gemini provider uses GEMINI_TEMPLATE."""
        data = {
            "class_id": "TEST_CLASS",
            "num_students": 25,
            "deficient_area": "EMT1",
            "emt1_avg": 65.0,
            "emt2_avg": 70.0,
            "emt3_avg": 68.0,
            "emt4_avg": 72.0,
        }

        prompt = InterventionPrompt.get_prompt("gemini", data)

        # Gemini template should include final check instructions
        assert "FINAL CHECK" in prompt
        assert "opening curly brace" in prompt

    @pytest.mark.unit
    def test_get_prompt_uses_base_template_for_unknown_provider(self):
        """Test that unknown provider falls back to BASE_TEMPLATE."""
        data = {
            "class_id": "TEST_CLASS",
            "num_students": 25,
            "deficient_area": "EMT1",
            "emt1_avg": 65.0,
            "emt2_avg": 70.0,
            "emt3_avg": 68.0,
            "emt4_avg": 72.0,
        }

        prompt = InterventionPrompt.get_prompt("unknown_provider", data)

        # Should not include gemini-specific text
        assert "FINAL CHECK" not in prompt
        # But should still have base content
        assert "Class ID: TEST_CLASS" in prompt

    @pytest.mark.unit
    def test_format_strategies_for_prompt(self):
        """Test that _format_strategies_for_prompt formats correctly."""
        strategy_info = InterventionPrompt.EMT_STRATEGIES["EMT1"]

        formatted = InterventionPrompt._format_strategies_for_prompt(strategy_info)

        # Should include focus and description
        assert "Visual Emotion Recognition" in formatted
        assert "Visual-to-visual emotion matching difficulties" in formatted
        # Should include activities
        assert "Emotion Flashcard Pairs" in formatted
        assert "Mirror Expression Practice" in formatted
        # Should include implementation steps
        assert "Use emotion flashcard pairs" in formatted
        # Should include resources
        assert "Emotion flashcard sets" in formatted

    @pytest.mark.unit
    def test_all_emt_areas_have_strategies(self):
        """Test that all expected EMT areas have strategies defined."""
        expected_areas = ["EMT1", "EMT2", "EMT3", "EMT4"]

        for area in expected_areas:
            assert area in InterventionPrompt.EMT_STRATEGIES
            assert "focus" in InterventionPrompt.EMT_STRATEGIES[area]
            assert "description" in InterventionPrompt.EMT_STRATEGIES[area]
            assert "strategies" in InterventionPrompt.EMT_STRATEGIES[area]
            assert len(InterventionPrompt.EMT_STRATEGIES[area]["strategies"]) > 0

