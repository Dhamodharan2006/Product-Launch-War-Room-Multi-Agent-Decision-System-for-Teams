"""Pytest configuration and fixtures."""

import pytest
import os


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Set up test environment variables."""
    os.environ.setdefault("GROQ_API_KEY", "test_key_for_unit_tests")
    os.environ.setdefault("ENVIRONMENT", "test")
    yield


@pytest.fixture
def sample_metrics():
    """Provide sample metrics for testing."""
    return {
        "dates": ["2024-01-0{}".format(i) for i in range(1, 8)],
        "crash_rate": [1.0, 1.2, 1.1, 1.3, 5.5, 1.2, 1.1],
        "activation_rate": [45.0, 46.0, 44.0, 47.0, 43.0, 46.0, 48.0],
        "payment_success_rate": [98.0, 97.5, 98.2, 97.8, 96.5, 98.0, 98.5]
    }


@pytest.fixture
def sample_feedback():
    """Provide sample feedback for testing."""
    return [
        {"id": "f1", "text": "Great feature!", "category": "positive", "sentiment_score": 0.85, "user_segment": "pro", "source": "app_store", "timestamp": "2024-01-01"},
        {"id": "f2", "text": "App crashes sometimes", "category": "negative", "sentiment_score": 0.25, "user_segment": "free", "source": "support_ticket", "timestamp": "2024-01-02"}
    ]