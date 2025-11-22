"""Tests for agent orchestrator."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from cache.database import TravelPlannerDB


class TestTravelPlannerAgent:
    """Test cases for TravelPlannerAgent."""
    
    @patch('agent.orchestrator.ChatGoogleGenerativeAI')
    def test_agent_initialization(self, mock_llm_class, temp_db):
        """Test agent initialization."""
        # Mock the LLM
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            from agent.orchestrator import TravelPlannerAgent
            
            agent = TravelPlannerAgent(temp_db, api_key='test-key')
            assert agent.db == temp_db
            assert agent.llm is not None
    
    def test_agent_initialization_no_api_key(self, temp_db):
        """Test agent initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            from agent.orchestrator import TravelPlannerAgent
            
            with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
                TravelPlannerAgent(temp_db)
    
    @patch('agent.orchestrator.ChatGoogleGenerativeAI')
    def test_agent_chat_basic(self, mock_llm_class, temp_db, sample_session_id):
        """Test basic chat functionality."""
        # Setup mocks
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "I can help you plan your trip!"
        mock_response.tool_calls = []
        mock_llm.bind_tools.return_value.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            from agent.orchestrator import TravelPlannerAgent
            
            agent = TravelPlannerAgent(temp_db, api_key='test-key')
            temp_db.create_session(sample_session_id)
            
            # Mock the graph invoke
            agent.graph = MagicMock()
            agent.graph.invoke.return_value = {
                "messages": [mock_response],
                "session_id": sample_session_id,
                "plan_context": {}
            }
            
            response = agent.chat("Hello", sample_session_id)
            assert "trip" in response.lower() or len(response) > 0
    
    @patch('agent.orchestrator.ChatGoogleGenerativeAI')
    def test_agent_session_creation(self, mock_llm_class, temp_db):
        """Test that agent creates session if it doesn't exist."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Response"
        mock_response.tool_calls = []
        mock_llm.bind_tools.return_value.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test-key'}):
            from agent.orchestrator import TravelPlannerAgent
            
            agent = TravelPlannerAgent(temp_db, api_key='test-key')
            new_session_id = "new-session-123"
            
            # Session should not exist
            assert temp_db.get_session(new_session_id) is None
            
            # Mock the graph
            agent.graph = MagicMock()
            agent.graph.invoke.return_value = {
                "messages": [mock_response],
                "session_id": new_session_id,
                "plan_context": {}
            }
            
            # Chat should create session
            agent.chat("Hello", new_session_id)
            
            # Session should now exist
            session = temp_db.get_session(new_session_id)
            assert session is not None

