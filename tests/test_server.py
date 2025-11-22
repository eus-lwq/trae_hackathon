"""Tests for Flask server endpoints."""
import pytest
import json
from unittest.mock import patch, MagicMock
import server


@pytest.fixture
def client(temp_db):
    """Create a Flask test client."""
    # Replace the global db with test version
    original_db = server.db
    server.db = temp_db
    
    # Create a mock agent
    mock_agent = MagicMock()
    mock_agent.chat.return_value = "Test response from agent"
    original_agent = server.agent
    server.agent = mock_agent
    
    app = server.app
    app.config['TESTING'] = True
    
    with app.test_client() as test_client:
        yield test_client
    
    # Restore original values
    server.db = original_db
    server.agent = original_agent


class TestHealthEndpoint:
    """Test cases for /health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert data["status"] == "healthy"


class TestChatEndpoint:
    """Test cases for /api/chat endpoint."""
    
    def test_chat_success(self, client, temp_db, sample_session_id):
        """Test successful chat request."""
        # Mock agent is already set up in fixture
        server.agent.chat.return_value = "I can help you plan your trip!"
        
        response = client.post('/api/chat', json={
            "message": "Plan a trip to Tokyo",
            "session_id": sample_session_id
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "response" in data
        assert "session_id" in data
    
    def test_chat_missing_message(self, client):
        """Test chat endpoint with missing message."""
        response = client.post('/api/chat', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    
    def test_chat_no_agent(self, client, temp_db):
        """Test chat endpoint when agent is not available."""
        # Temporarily set agent to None
        original_agent = server.agent
        server.agent = None
        
        response = client.post('/api/chat', json={
            "message": "Test message"
        })
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert "error" in data
        
        # Restore agent
        server.agent = original_agent


class TestSessionEndpoints:
    """Test cases for session endpoints."""
    
    def test_create_session(self, client, temp_db):
        """Test creating a new session."""
        response = client.post('/api/sessions', json={
            "metadata": {"test": "data"}
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "session_id" in data
        assert "created_at" in data
    
    def test_get_session(self, client, temp_db, sample_session_id):
        """Test retrieving a session."""
        temp_db.create_session(sample_session_id)
        
        response = client.get(f'/api/sessions/{sample_session_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["session_id"] == sample_session_id
    
    def test_get_session_not_found(self, client, temp_db):
        """Test retrieving non-existent session."""
        response = client.get('/api/sessions/non-existent')
        assert response.status_code == 404
    
    def test_get_chat_history(self, client, temp_db, sample_session_id):
        """Test retrieving chat history."""
        temp_db.create_session(sample_session_id)
        temp_db.add_chat_message(sample_session_id, "user", "Hello")
        temp_db.add_chat_message(sample_session_id, "assistant", "Hi!")
        
        response = client.get(f'/api/sessions/{sample_session_id}/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "messages" in data
        assert len(data["messages"]) == 2


class TestPlanEndpoints:
    """Test cases for plan endpoints."""
    
    def test_get_plan(self, client, temp_db, sample_session_id, sample_plan_data):
        """Test retrieving a travel plan."""
        temp_db.create_session(sample_session_id)
        
        plan_id = "test-plan-123"
        temp_db.save_travel_plan(
            plan_id=plan_id,
            session_id=sample_session_id,
            destination="Tokyo",
            start_date="2024-06-01",
            end_date="2024-06-03",
            plan_data=sample_plan_data
        )
        
        response = client.get(f'/api/plans/{plan_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["plan_id"] == plan_id
        assert data["destination"] == "Tokyo"
    
    def test_get_plan_not_found(self, client, temp_db):
        """Test retrieving non-existent plan."""
        response = client.get('/api/plans/non-existent')
        assert response.status_code == 404
    
    def test_get_session_plans(self, client, temp_db, sample_session_id, sample_plan_data):
        """Test retrieving all plans for a session."""
        temp_db.create_session(sample_session_id)
        
        # Create multiple plans
        for i in range(2):
            temp_db.save_travel_plan(
                plan_id=f"plan-{i}",
                session_id=sample_session_id,
                destination=f"City-{i}",
                start_date="2024-06-01",
                end_date="2024-06-03",
                plan_data=sample_plan_data
            )
        
        response = client.get(f'/api/sessions/{sample_session_id}/plans')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["count"] == 2
        assert len(data["plans"]) == 2

