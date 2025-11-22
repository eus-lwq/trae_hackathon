"""LangChain + LangGraph agent orchestration with Google Gemini."""
import os
from typing import Dict, List, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import TypedDict, Annotated

from agent.tools import web_resource_tool, plan_tool, map_route_tool, find_community_links_tool, set_db_instance
from cache.database import TravelPlannerDB


class AgentState(TypedDict):
    """State for the travel planning agent."""
    messages: Annotated[list, add_messages]
    session_id: str
    plan_context: Dict[str, Any]


class TravelPlannerAgent:
    """Travel planning agent using LangGraph and Google Gemini."""
    
    def __init__(self, db: TravelPlannerDB, api_key: Optional[str] = None):
        """Initialize the agent.
        
        Args:
            db: Database instance
            api_key: Google Gemini API key (or from env)
        """
        self.db = db
        set_db_instance(db)
        
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools([
            web_resource_tool,
            plan_tool,
            map_route_tool,
            find_community_links_tool
        ])
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self._tools_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent node that processes messages and decides on tool usage."""
        messages = state["messages"]
        
        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            system_prompt = """You are an AI Travel Micro-Planner assistant. Your role is to help users plan their trips by AUTOMATICALLY researching and scraping travel information from the web.

WORKFLOW - Follow this automatically:
1. When a user mentions a destination or tourist spot:
   a. FIRST use find_community_links_tool to get Xiaohongshu, Reddit, and Nextdoor search URLs
   b. THEN use web_resource_tool to scrape those community links
   c. ALSO scrape from Booking.com, Expedia, and travel blogs
2. Use the scraped information to create detailed recommendations with community insights
3. Use plan_tool to save the travel plan with community links included
4. Continue researching and updating as needed

You have access to four tools:
- web_resource_tool: Parse travel content from web pages. USE THIS AUTOMATICALLY and PROACTIVELY.
  * Construct URLs for common travel sites (booking.com, expedia.com, reddit.com/r/travel, etc.)
  * Scrape multiple sources to get comprehensive information
  * Use extract_type: "booking" for booking sites, "reddit" for Reddit, "expedia" for Expedia, "general" for blogs
- find_community_links_tool: Find community links (Xiaohongshu, Reddit, Nextdoor) for tourist spots
  * Use this to get search URLs for community platforms
  * Then use web_resource_tool to scrape those URLs
- plan_tool: Create, update, get, and list travel plans
- map_route_tool: Generate map routes with per-day color labels

CRITICAL RULES:
- You ALREADY have the session_id - NEVER ask the user for it. It's automatically provided in the context.
- AUTOMATICALLY use web_resource_tool when users mention destinations, hotels, restaurants, or activities
- Don't wait for permission - proactively scrape information from multiple sources
- After scraping, immediately use that information to create detailed plans
- Scrape at least 2-3 different sources for each destination to get comprehensive information

When creating plans, include:
- Destination information (from scraped data)
- Daily itineraries with activities, locations, and times
- Hotel/accommodation recommendations (scrape booking sites)
- Restaurant recommendations (scrape travel sites)
- Attraction recommendations (scrape travel guides)
- Budget estimates based on scraped pricing information
- Local tips and insights (scrape Reddit, travel forums)

ALWAYS use web_resource_tool FIRST to gather real information, THEN create plans with plan_tool."""
            
            messages = [SystemMessage(content=system_prompt)] + messages
        
        # Get response from LLM
        response = self.llm_with_tools.invoke(messages)
        
        # Save assistant message to chat history
        if state.get("session_id"):
            self.db.add_chat_message(
                state["session_id"],
                "assistant",
                response.content
            )
        
        return {"messages": [response]}
    
    def _tools_node(self, state: AgentState) -> AgentState:
        """Tools node that executes tool calls."""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_results = []
        
        # Execute tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                # Handle different tool_call formats
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    tool_call_id = tool_call.get("id", "")
                else:
                    # Handle tool_call as object
                    tool_name = getattr(tool_call, "name", "")
                    tool_args = getattr(tool_call, "args", {})
                    tool_call_id = getattr(tool_call, "id", "")
                
                # Inject session_id into tool args if needed
                session_id = state.get("session_id", "")
                if session_id and isinstance(tool_args, dict):
                    # Tools that require session_id
                    if tool_name in ["plan_tool", "map_route_tool"]:
                        if "session_id" not in tool_args:
                            tool_args["session_id"] = session_id
                
                # Execute the appropriate tool
                try:
                    if tool_name == "web_resource_tool":
                        result = web_resource_tool.invoke(tool_args)
                    elif tool_name == "plan_tool":
                        result = plan_tool.invoke(tool_args)
                    elif tool_name == "map_route_tool":
                        result = map_route_tool.invoke(tool_args)
                    elif tool_name == "find_community_links_tool":
                        result = find_community_links_tool.invoke(tool_args)
                    else:
                        result = f"Unknown tool: {tool_name}"
                except Exception as e:
                    result = f"Error executing {tool_name}: {str(e)}"
                
                tool_results.append({
                    "tool_call_id": tool_call_id,
                    "content": result
                })
        
        # Create tool message responses
        from langchain_core.messages import ToolMessage
        tool_messages = [
            ToolMessage(
                content=str(result["content"]),
                tool_call_id=result["tool_call_id"]
            )
            for result in tool_results
        ]
        
        return {"messages": tool_messages}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue or end."""
        messages = state["messages"]
        if not messages:
            return "end"
        
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, 'tool_calls'):
            tool_calls = last_message.tool_calls
            if tool_calls and len(tool_calls) > 0:
                return "continue"
        return "end"
    
    def chat(self, message: str, session_id: str, context: Optional[Dict] = None) -> str:
        """Process a chat message and return response.
        
        Args:
            message: User message
            session_id: Session identifier
            context: Optional context dictionary
            
        Returns:
            Agent response text
        """
        # Ensure session exists
        if not self.db.get_session(session_id):
            self.db.create_session(session_id)
        
        # Save user message to chat history
        self.db.add_chat_message(session_id, "user", message)
        
        # Get chat history for context
        history = self.db.get_chat_history(session_id, limit=10)
        
        # Build message list
        messages = []
        for hist_item in history[-10:]:  # Last 10 messages
            if hist_item["role"] == "user":
                messages.append(HumanMessage(content=hist_item["message"]))
            elif hist_item["role"] == "assistant":
                messages.append(AIMessage(content=hist_item["message"]))
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Create initial state
        initial_state: AgentState = {
            "messages": messages,
            "session_id": session_id,
            "plan_context": context or {}
        }
        
        # Run the graph with config to allow multiple iterations
        config = {"recursion_limit": 50}  # Allow up to 50 tool call iterations
        final_state = self.graph.invoke(initial_state, config=config)
        
        # Extract final response - find the last non-tool message
        final_messages = final_state["messages"]
        if final_messages:
            # Look for the last message that has content (not a tool message)
            for message in reversed(final_messages):
                if hasattr(message, 'content') and message.content:
                    # Don't return tool messages or system messages
                    from langchain_core.messages import ToolMessage, SystemMessage
                    if not isinstance(message, (ToolMessage, SystemMessage)):
                        return message.content
            # Fallback to last message
            last_message = final_messages[-1]
            if hasattr(last_message, 'content'):
                return last_message.content
            return str(last_message)
        
        return "I apologize, but I couldn't generate a response. Please try again."

