"""Tests for database module."""
import pytest
import json
from cache.database import TravelPlannerDB


class TestTravelPlannerDB:
    """Test cases for TravelPlannerDB."""
    
    def test_create_session(self, temp_db, sample_session_id):
        """Test creating a new session."""
        result = temp_db.create_session(sample_session_id, {"test": "data"})
        assert result is True
        
        # Try to create duplicate session
        result = temp_db.create_session(sample_session_id)
        assert result is False
    
    def test_get_session(self, temp_db, sample_session_id):
        """Test retrieving a session."""
        # Create session first
        temp_db.create_session(sample_session_id, {"key": "value"})
        
        # Retrieve session
        session = temp_db.get_session(sample_session_id)
        assert session is not None
        assert session["session_id"] == sample_session_id
        assert session["metadata"]["key"] == "value"
        
        # Non-existent session
        session = temp_db.get_session("non-existent")
        assert session is None
    
    def test_update_session(self, temp_db, sample_session_id):
        """Test updating session metadata."""
        temp_db.create_session(sample_session_id)
        
        # Update with new metadata
        temp_db.update_session(sample_session_id, {"updated": True})
        
        session = temp_db.get_session(sample_session_id)
        assert session["metadata"]["updated"] is True
    
    def test_save_travel_plan(self, temp_db, sample_session_id, sample_plan_data):
        """Test saving a travel plan."""
        temp_db.create_session(sample_session_id)
        
        plan_id = "test-plan-123"
        result = temp_db.save_travel_plan(
            plan_id=plan_id,
            session_id=sample_session_id,
            destination="Tokyo",
            start_date="2024-06-01",
            end_date="2024-06-03",
            plan_data=sample_plan_data
        )
        
        assert result is True
        
        # Verify plan was saved
        plan = temp_db.get_travel_plan(plan_id)
        assert plan is not None
        assert plan["destination"] == "Tokyo"
        assert plan["plan_data"]["destination"] == "Tokyo"
        assert len(plan["plan_data"]["itinerary"]) == 2
    
    def test_get_travel_plan(self, temp_db, sample_session_id, sample_plan_data):
        """Test retrieving a travel plan."""
        temp_db.create_session(sample_session_id)
        
        plan_id = "test-plan-456"
        temp_db.save_travel_plan(
            plan_id=plan_id,
            session_id=sample_session_id,
            destination="Paris",
            start_date="2024-07-01",
            end_date="2024-07-05",
            plan_data=sample_plan_data
        )
        
        plan = temp_db.get_travel_plan(plan_id)
        assert plan is not None
        assert plan["plan_id"] == plan_id
        assert plan["destination"] == "Paris"
        
        # Non-existent plan
        plan = temp_db.get_travel_plan("non-existent")
        assert plan is None
    
    def test_get_session_plans(self, temp_db, sample_session_id, sample_plan_data):
        """Test retrieving all plans for a session."""
        temp_db.create_session(sample_session_id)
        
        # Create multiple plans
        for i in range(3):
            temp_db.save_travel_plan(
                plan_id=f"plan-{i}",
                session_id=sample_session_id,
                destination=f"City-{i}",
                start_date="2024-06-01",
                end_date="2024-06-03",
                plan_data=sample_plan_data
            )
        
        plans = temp_db.get_session_plans(sample_session_id)
        assert len(plans) == 3
        
        # Different session should have no plans
        temp_db.create_session("other-session")
        plans = temp_db.get_session_plans("other-session")
        assert len(plans) == 0
    
    def test_add_chat_message(self, temp_db, sample_session_id):
        """Test adding chat messages."""
        temp_db.create_session(sample_session_id)
        
        temp_db.add_chat_message(sample_session_id, "user", "Hello")
        temp_db.add_chat_message(sample_session_id, "assistant", "Hi there!")
        
        history = temp_db.get_chat_history(sample_session_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["message"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["message"] == "Hi there!"
    
    def test_get_chat_history(self, temp_db, sample_session_id):
        """Test retrieving chat history."""
        temp_db.create_session(sample_session_id)
        
        # Add multiple messages
        for i in range(10):
            role = "user" if i % 2 == 0 else "assistant"
            temp_db.add_chat_message(sample_session_id, role, f"Message {i}")
        
        # Get all history
        history = temp_db.get_chat_history(sample_session_id)
        assert len(history) == 10
        
        # Get limited history
        history = temp_db.get_chat_history(sample_session_id, limit=5)
        assert len(history) == 5
        
        # Verify order (oldest first)
        assert history[0]["message"] == "Message 0"
    
    def test_update_existing_plan(self, temp_db, sample_session_id, sample_plan_data):
        """Test updating an existing travel plan."""
        temp_db.create_session(sample_session_id)
        
        plan_id = "update-test-plan"
        
        # Create initial plan
        temp_db.save_travel_plan(
            plan_id=plan_id,
            session_id=sample_session_id,
            destination="Tokyo",
            start_date="2024-06-01",
            end_date="2024-06-03",
            plan_data=sample_plan_data
        )
        
        # Update plan
        updated_data = sample_plan_data.copy()
        updated_data["notes"] = "Updated notes"
        
        temp_db.save_travel_plan(
            plan_id=plan_id,
            session_id=sample_session_id,
            destination="Tokyo",
            start_date="2024-06-01",
            end_date="2024-06-05",  # Extended end date
            plan_data=updated_data
        )
        
        plan = temp_db.get_travel_plan(plan_id)
        assert plan["end_date"] == "2024-06-05"
        assert plan["plan_data"]["notes"] == "Updated notes"

