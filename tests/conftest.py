"""
Pytest configuration and fixtures for the FastAPI test suite.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src directory to path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that resets the activities to their initial state after each test.
    This ensures test isolation by clearing any participant modifications.
    """
    yield
    # Reset activities to original state after test
    for activity in activities.values():
        activity["participants"] = []
