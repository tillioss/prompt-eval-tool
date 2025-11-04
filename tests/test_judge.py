"""
Unit tests for judge.py with mocked Gemini API
"""

from unittest.mock import patch, MagicMock

from judge import (
    extract_rating,
    extract_relevance_score,
    extract_clarity_score,
    extract_consistency_score,
    extract_creativity_score,
    _extract_json_object,
    flatten_json_schema,
    evaluate_with_gemini,
    evaluate_batch_with_gemini,
)


class TestScoreExtraction:
    def test_extract_rating(self):
        text = "Relevance Score: 8\n" "Clarity Score: 7\n" "Total Score: 9\n"
        assert extract_rating(text) == 9

    def test_extract_relevance_score(self):
        assert extract_relevance_score("Relevance Score: 6") == 6
        assert extract_relevance_score("Relevance Score: 11") is None
        assert extract_relevance_score("no score here") is None

    def test_extract_clarity_score(self):
        assert extract_clarity_score("Clarity Score: 5") == 5
        assert extract_clarity_score("Clarity Score: 0") is None

    def test_extract_consistency_score(self):
        assert extract_consistency_score("Consistency Score: 7") == 7
        assert extract_consistency_score("Consistency Score: 13") is None

    def test_extract_creativity_score(self):
        assert extract_creativity_score("Creativity Score: 8") == 8
        assert extract_creativity_score("Creativity/Innovation Score: 9") == 9
        assert extract_creativity_score("Creativity Score: 0") is None


class TestExtractJsonObject:
    def test_extract_json_plain(self):
        src = '{"a": 1, "b": {"c": 2}}'
        assert _extract_json_object(src) == src

    def test_extract_json_with_fences(self):
        src = """```json\n{\n  \"a\": 1,\n  \"b\": {\"c\": 2}\n}\n```"""
        expected = '{\n  "a": 1,\n  "b": {"c": 2}\n}'
        out = _extract_json_object(src)
        assert out is not None and out.replace(" ", "") == expected.replace(" ", "")

    def test_extract_json_missing(self):
        src = "no json here"
        assert _extract_json_object(src) is None


class TestFlattenJsonSchema:
    def test_flatten_minimal_defs(self):
        schema = {
            "$defs": {
                "Inner": {
                    "type": "object",
                    "properties": {"x": {"type": "string"}},
                    "required": ["x"],
                }
            },
            "type": "object",
            "properties": {
                "inner": {"$ref": "#/$defs/Inner"},
                "y": {"type": "array", "items": [{"type": "string"}]},
            },
            "required": ["inner", "y"],
            "title": "Should be removed",
        }
        flat = flatten_json_schema(schema)
        # Ensure unsupported keys are removed
        assert "title" not in flat
        # Should be an object with properties
        assert flat.get("type") == "object"
        assert isinstance(flat.get("properties"), dict)
        # Items list should be normalized to a single schema when applicable
        if "y" in flat["properties"]:
            assert flat["properties"]["y"]["items"]["type"] == "string"
        # Guarantee non-empty properties per implementation
        assert len(flat["properties"]) >= 1


class TestEvaluateFlows:
    @patch("judge.genai.GenerativeModel")
    def test_evaluate_with_gemini_parses_scores(self, MockModel):
        mock_model = MagicMock()
        MockModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = (
            "Relevance: Good\n"
            "Relevance Score: 8\n"
            "Clarity: OK\n"
            "Clarity Score: 7\n"
            "Consistency: -\n"
            "Creativity: -\n"
            "Total Score: 8\n"
        )
        mock_model.generate_content.return_value = mock_response

        feedback, scores, prompt = evaluate_with_gemini(
            question="Q?",
            answer="A",
            model_name="gemini-2.5-flash",
            temperature=0.2,
            mode="individual",
        )

        assert "Relevance Score" in feedback
        assert scores["relevance"] == 8
        assert scores["clarity"] == 7
        assert scores["total"] == 8
        # prompt should include the question and answer
        assert "Q?" in prompt and "A" in prompt
        # Ensure model called once
        MockModel.assert_called_once()
        mock_model.generate_content.assert_called_once()

    @patch("judge.genai.GenerativeModel")
    def test_evaluate_batch_with_gemini_parses_batch_scores(self, MockModel):
        mock_model = MagicMock()
        MockModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = (
            "Batch Evaluation\n"
            "Consistency: Stable across answers\n"
            "Consistency Score: 9\n"
            "Creativity: Diverse outputs\n"
            "Creativity Score: 7\n"
        )
        mock_model.generate_content.return_value = mock_response

        feedback, scores, prompt = evaluate_batch_with_gemini(
            pairs=[("in1", "out1"), ("in2", "out2")],
            model_name="gemini-2.5-flash",
            temperature=0.3,
        )

        assert scores["consistency"] == 9
        assert scores["creativity"] == 7
        assert "Pair 1:" in prompt and "Pair 2:" in prompt
        MockModel.assert_called_once()
        mock_model.generate_content.assert_called_once()
