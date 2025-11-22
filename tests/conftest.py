"""Pytest configuration and fixtures."""
import pytest
import os
import tempfile
import shutil
from pathlib import Path

from cache.database import TravelPlannerDB


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    # Create database
    db = TravelPlannerDB(db_path)
    
    yield db
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_session_id():
    """Sample session ID for testing."""
    return "test-session-123"


@pytest.fixture
def sample_plan_data():
    """Sample travel plan data."""
    return {
        "itinerary": [
            {
                "day": 1,
                "date": "2024-06-01",
                "activities": [
                    {
                        "name": "Visit Shibuya",
                        "location": "Shibuya, Tokyo",
                        "time": "10:00",
                        "description": "Explore Shibuya crossing"
                    },
                    {
                        "name": "Lunch",
                        "location": "Shibuya, Tokyo",
                        "time": "12:00"
                    }
                ]
            },
            {
                "day": 2,
                "date": "2024-06-02",
                "activities": [
                    {
                        "name": "Visit Asakusa",
                        "location": "Asakusa, Tokyo",
                        "time": "09:00"
                    }
                ]
            }
        ],
        "destination": "Tokyo",
        "notes": "Test travel plan"
    }

