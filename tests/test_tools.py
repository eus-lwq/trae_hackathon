"""Tests for agent tools."""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from agent.tools import web_resource_tool, plan_tool, map_route_tool, set_db_instance
from cache.database import TravelPlannerDB


class TestWebResourceTool:
    """Test cases for web_resource_tool."""
    
    @patch('agent.tools.requests.get')
    def test_web_resource_tool_success(self, mock_get, temp_db):
        """Test successful web resource parsing."""
        set_db_instance(temp_db)
        
        # Mock HTML response
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <head><title>Test Travel Page</title></head>
            <body>
                <main>
                    <h1>Best Hotels in Paris</h1>
                    <p>Here are some great hotels...</p>
                </main>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = web_resource_tool.invoke({
            "url": "https://example.com/travel",
            "extract_type": "general"
        })
        
        data = json.loads(result)
        assert data["url"] == "https://example.com/travel"
        assert "Test Travel Page" in data["title"]
        assert "Best Hotels" in data["content"]
    
    @patch('agent.tools.requests.get')
    def test_web_resource_tool_reddit(self, mock_get, temp_db):
        """Test Reddit-specific extraction."""
        set_db_instance(temp_db)
        
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <title>Reddit Post</title>
            <div class="Post">
                <p>This is a Reddit post about travel</p>
            </div>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = web_resource_tool.invoke({
            "url": "https://reddit.com/r/travel/post",
            "extract_type": "reddit"
        })
        
        data = json.loads(result)
        assert data["extract_type"] == "reddit"
        assert "travel" in data["content"].lower()
    
    @patch('agent.tools.requests.get')
    def test_web_resource_tool_error(self, mock_get, temp_db):
        """Test error handling for web resource tool."""
        set_db_instance(temp_db)
        
        mock_get.side_effect = Exception("Connection error")
        
        result = web_resource_tool.invoke({
            "url": "https://invalid-url.com",
            "extract_type": "general"
        })
        
        data = json.loads(result)
        assert "error" in data


class TestPlanTool:
    """Test cases for plan_tool."""
    
    def test_plan_tool_create(self, temp_db, sample_session_id, sample_plan_data):
        """Test creating a travel plan."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        result = plan_tool.invoke({
            "action": "create",
            "session_id": sample_session_id,
            "destination": "Tokyo",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "plan_data": sample_plan_data
        })
        
        data = json.loads(result)
        assert data["success"] is True
        assert data["action"] == "create"
        assert "plan_id" in data
        
        # Verify plan was created
        plan = temp_db.get_travel_plan(data["plan_id"])
        assert plan is not None
        assert plan["destination"] == "Tokyo"
    
    def test_plan_tool_create_missing_fields(self, temp_db, sample_session_id):
        """Test creating plan with missing required fields."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        result = plan_tool.invoke({
            "action": "create",
            "session_id": sample_session_id,
            "destination": "Tokyo"
            # Missing start_date, end_date, plan_data
        })
        
        data = json.loads(result)
        assert "error" in data
    
    def test_plan_tool_update(self, temp_db, sample_session_id, sample_plan_data):
        """Test updating a travel plan."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        # Create plan first
        create_result = plan_tool.invoke({
            "action": "create",
            "session_id": sample_session_id,
            "destination": "Tokyo",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "plan_data": sample_plan_data
        })
        plan_id = json.loads(create_result)["plan_id"]
        
        # Update plan
        updated_data = {"notes": "Updated plan"}
        result = plan_tool.invoke({
            "action": "update",
            "plan_id": plan_id,
            "session_id": sample_session_id,
            "plan_data": updated_data
        })
        
        data = json.loads(result)
        assert data["success"] is True
        
        # Verify update
        plan = temp_db.get_travel_plan(plan_id)
        assert "Updated plan" in plan["plan_data"]["notes"]
    
    def test_plan_tool_get(self, temp_db, sample_session_id, sample_plan_data):
        """Test retrieving a travel plan."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        # Create plan first
        create_result = plan_tool.invoke({
            "action": "create",
            "session_id": sample_session_id,
            "destination": "Paris",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "plan_data": sample_plan_data
        })
        plan_id = json.loads(create_result)["plan_id"]
        
        # Get plan
        result = plan_tool.invoke({
            "action": "get",
            "plan_id": plan_id,
            "session_id": sample_session_id
        })
        
        data = json.loads(result)
        assert data["success"] is True
        assert data["plan"]["destination"] == "Paris"
    
    def test_plan_tool_list(self, temp_db, sample_session_id, sample_plan_data):
        """Test listing all plans for a session."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        # Create multiple plans
        for i in range(3):
            plan_tool.invoke({
                "action": "create",
                "session_id": sample_session_id,
                "destination": f"City-{i}",
                "start_date": "2024-06-01",
                "end_date": "2024-06-03",
                "plan_data": sample_plan_data
            })
        
        # List plans
        result = plan_tool.invoke({
            "action": "list",
            "session_id": sample_session_id
        })
        
        data = json.loads(result)
        assert data["success"] is True
        assert data["count"] == 3
        assert len(data["plans"]) == 3
    
    def test_plan_tool_invalid_action(self, temp_db, sample_session_id):
        """Test plan tool with invalid action."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        result = plan_tool.invoke({
            "action": "invalid_action",
            "session_id": sample_session_id
        })
        
        data = json.loads(result)
        assert "error" in data


class TestMapRouteTool:
    """Test cases for map_route_tool."""
    
    def test_map_route_tool_success(self, temp_db, sample_session_id, sample_plan_data):
        """Test generating map route for a plan."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        # Create plan first
        create_result = plan_tool.invoke({
            "action": "create",
            "session_id": sample_session_id,
            "destination": "Tokyo",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "plan_data": sample_plan_data
        })
        plan_id = json.loads(create_result)["plan_id"]
        
        # Generate route
        result = map_route_tool.invoke({
            "plan_id": plan_id,
            "session_id": sample_session_id
        })
        
        data = json.loads(result)
        assert "plan_id" in data
        assert "days" in data
        assert len(data["days"]) == 2  # Two days in sample plan
        assert "color" in data["days"][0]
        assert "locations" in data["days"][0]
        assert data["summary"]["total_days"] == 2
    
    def test_map_route_tool_no_plan(self, temp_db, sample_session_id):
        """Test map route tool with non-existent plan."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        result = map_route_tool.invoke({
            "plan_id": "non-existent-plan",
            "session_id": sample_session_id
        })
        
        data = json.loads(result)
        assert "error" in data
    
    def test_map_route_tool_no_itinerary(self, temp_db, sample_session_id):
        """Test map route tool with plan that has no itinerary."""
        set_db_instance(temp_db)
        temp_db.create_session(sample_session_id)
        
        # Create plan without itinerary
        create_result = plan_tool.invoke({
            "action": "create",
            "session_id": sample_session_id,
            "destination": "Tokyo",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "plan_data": {"destination": "Tokyo"}  # No itinerary
        })
        plan_id = json.loads(create_result)["plan_id"]
        
        result = map_route_tool.invoke({
            "plan_id": plan_id,
            "session_id": sample_session_id
        })
        
        data = json.loads(result)
        assert "error" in data

