"""
Unit tests for logger module
"""

import pytest
import pandas as pd
from pathlib import Path

from logger import log_evaluation, log_batch_summary, get_evaluation_history, CSV_FILE, CSV_HEADER


class TestLogEvaluation:
    """Test cases for log_evaluation function"""

    @pytest.fixture
    def cleanup_csv(self):
        """Fixture to clean up CSV file before and after tests"""
        # Clean up before test
        csv_path = Path(CSV_FILE)
        if csv_path.exists():
            csv_path.unlink()
        yield
        # Clean up after test
        if csv_path.exists():
            csv_path.unlink()

    def test_log_evaluation_creates_new_file(self, cleanup_csv):
        """Test that log_evaluation creates a new CSV file if it doesn't exist"""
        log_evaluation(
            model="test-model",
            temperature=0.5,
            question="Test question?",
            answer="Test answer",
            judge_feedback="Good feedback",
            judge_prompt="Test prompt",
            total_rating=8,
            validation_status="Valid",
            relevance_score=7,
            clarity_score=8,
            consistency_score=None,
            creativity_score=None,
        )

        assert Path(CSV_FILE).exists()
        df = pd.read_csv(CSV_FILE)
        assert len(df) == 1
        assert df.iloc[0]["model"] == "test-model"
        assert df.iloc[0]["total_rating(1-10)"] == 8

    def test_log_evaluation_appends_to_existing_file(self, cleanup_csv):
        """Test that log_evaluation appends to existing CSV file"""
        # Create first entry
        log_evaluation(
            model="model-1",
            temperature=0.5,
            question="Q1",
            answer="A1",
            judge_feedback="F1",
            judge_prompt="P1",
            total_rating=7,
            validation_status="Valid",
            relevance_score=6,
            clarity_score=7,
            consistency_score=None,
            creativity_score=None,
        )

        # Create second entry
        log_evaluation(
            model="model-2",
            temperature=0.6,
            question="Q2",
            answer="A2",
            judge_feedback="F2",
            judge_prompt="P2",
            total_rating=9,
            validation_status="Valid",
            relevance_score=8,
            clarity_score=9,
            consistency_score=None,
            creativity_score=None,
        )

        df = pd.read_csv(CSV_FILE)
        assert len(df) == 2
        assert df.iloc[0]["model"] == "model-1"
        assert df.iloc[1]["model"] == "model-2"

    def test_log_evaluation_with_batch_id(self, cleanup_csv):
        """Test that batch_id is correctly logged"""
        log_evaluation(
            model="test-model",
            temperature=0.5,
            question="Test",
            answer="Answer",
            judge_feedback="Feedback",
            judge_prompt="Prompt",
            total_rating=8,
            validation_status="Valid",
            relevance_score=7,
            clarity_score=8,
            consistency_score=None,
            creativity_score=None,
            batch_id="batch-123",
            row_type="item",
        )

        df = pd.read_csv(CSV_FILE)
        assert df.iloc[0]["batch_id"] == "batch-123"
        assert df.iloc[0]["row_type"] == "item"


class TestLogBatchSummary:
    """Test cases for log_batch_summary function"""

    @pytest.fixture
    def cleanup_csv(self):
        """Fixture to clean up CSV file before and after tests"""
        # Clean up before test
        csv_path = Path(CSV_FILE)
        if csv_path.exists():
            csv_path.unlink()
        yield
        # Clean up after test
        if csv_path.exists():
            csv_path.unlink()

    def test_log_batch_summary(self, cleanup_csv):
        """Test that log_batch_summary creates a batch summary row"""
        log_batch_summary(
            model="test-model",
            temperature=0.5,
            judge_feedback="Batch feedback",
            judge_prompt="Batch prompt",
            consistency_score=8,
            creativity_score=7,
            batch_id="batch-123",
        )

        df = pd.read_csv(CSV_FILE)
        assert len(df) == 1
        assert df.iloc[0]["row_type"] == "batch_summary"
        assert df.iloc[0]["batch_id"] == "batch-123"
        assert df.iloc[0]["consistency_score"] == 8
        assert df.iloc[0]["creativity_score"] == 7
        assert pd.isna(df.iloc[0]["total_rating(1-10)"])


class TestGetEvaluationHistory:
    """Test cases for get_evaluation_history function"""

    @pytest.fixture
    def cleanup_csv(self):
        """Fixture to clean up CSV file before and after tests"""
        # Clean up before test
        csv_path = Path(CSV_FILE)
        if csv_path.exists():
            csv_path.unlink()
        yield
        # Clean up after test
        if csv_path.exists():
            csv_path.unlink()

    def test_get_evaluation_history_empty(self, cleanup_csv):
        """Test getting history when no CSV exists"""
        df = get_evaluation_history()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == CSV_HEADER

    def test_get_evaluation_history_with_data(self, cleanup_csv):
        """Test getting history when CSV exists with data"""
        # Log some data
        log_evaluation(
            model="test-model",
            temperature=0.5,
            question="Test",
            answer="Answer",
            judge_feedback="Feedback",
            judge_prompt="Prompt",
            total_rating=8,
            validation_status="Valid",
            relevance_score=7,
            clarity_score=8,
            consistency_score=None,
            creativity_score=None,
        )

        # Get history
        df = get_evaluation_history()
        assert len(df) == 1
        assert df.iloc[0]["model"] == "test-model"
