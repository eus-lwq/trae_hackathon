"""Flask HTTP server for AI Travel Micro-Planner."""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import uuid

from cache.database import TravelPlannerDB
from agent.orchestrator import TravelPlannerAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize database
db_path = os.getenv("DATABASE_PATH", "./cache/travel_planner.db")
db = TravelPlannerDB(db_path)

# Initialize agent
try:
    agent = TravelPlannerAgent(db)
except ValueError as e:
    print(f"Warning: {e}. Agent will not be available until GOOGLE_API_KEY is set.")
    agent = None


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "agent_available": agent is not None
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint for interacting with the travel planning agent.
    
    Request body:
        {
            "message": "user message",
            "session_id": "optional session id"
        }
    
    Response:
        {
            "response": "agent response",
            "session_id": "session id"
        }
    """
    if not agent:
        return jsonify({
            "error": "Agent not available. Please set GOOGLE_API_KEY environment variable."
        }), 503
    
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400
    
    message = data["message"]
    session_id = data.get("session_id") or str(uuid.uuid4())
    
    try:
        response = agent.chat(message, session_id)
        return jsonify({
            "response": response,
            "session_id": session_id
        })
    except Exception as e:
        return jsonify({
            "error": f"Error processing chat: {str(e)}"
        }), 500


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    """Get session information.
    
    Response:
        {
            "session_id": "...",
            "created_at": "...",
            "updated_at": "...",
            "metadata": {...}
        }
    """
    session = db.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(session)


@app.route("/api/sessions", methods=["POST"])
def create_session():
    """Create a new session.
    
    Request body (optional):
        {
            "metadata": {...}
        }
    
    Response:
        {
            "session_id": "...",
            "created_at": "..."
        }
    """
    data = request.get_json() or {}
    session_id = str(uuid.uuid4())
    metadata = data.get("metadata")
    
    success = db.create_session(session_id, metadata)
    if success:
        session = db.get_session(session_id)
        return jsonify(session), 201
    else:
        return jsonify({"error": "Failed to create session"}), 500


@app.route("/api/plans/<plan_id>", methods=["GET"])
def get_plan(plan_id: str):
    """Get a travel plan by ID.
    
    Response:
        {
            "plan_id": "...",
            "session_id": "...",
            "destination": "...",
            "start_date": "...",
            "end_date": "...",
            "plan_data": {...}
        }
    """
    plan = db.get_travel_plan(plan_id)
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    
    return jsonify(plan)


@app.route("/api/sessions/<session_id>/plans", methods=["GET"])
def get_session_plans(session_id: str):
    """Get all travel plans for a session.
    
    Response:
        {
            "plans": [...],
            "count": 0
        }
    """
    plans = db.get_session_plans(session_id)
    return jsonify({
        "plans": plans,
        "count": len(plans)
    })


@app.route("/api/sessions/<session_id>/history", methods=["GET"])
def get_chat_history(session_id: str):
    """Get chat history for a session.
    
    Query params:
        limit: Maximum number of messages (default: 50)
    
    Response:
        {
            "messages": [...],
            "count": 0
        }
    """
    limit = request.args.get("limit", 50, type=int)
    messages = db.get_chat_history(session_id, limit=limit)
    return jsonify({
        "messages": messages,
        "count": len(messages)
    })


@app.route("/api/plans/<plan_id>/route", methods=["GET"])
def get_plan_route(plan_id: str):
    """Get map route for a travel plan.
    
    Query params:
        session_id: Session ID (required)
    
    Response:
        {
            "plan_id": "...",
            "days": [...],
            "summary": {...}
        }
    """
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id query parameter is required"}), 400
    
    if not agent:
        return jsonify({
            "error": "Agent not available"
        }), 503
    
    try:
        from agent.tools import map_route_tool
        result = map_route_tool.invoke({
            "plan_id": plan_id,
            "session_id": session_id
        })
        import json
        return jsonify(json.loads(result))
    except Exception as e:
        return jsonify({
            "error": f"Error generating route: {str(e)}"
        }), 500


if __name__ == "__main__":
    import socket
    
    def find_free_port(start_port=5000, max_attempts=10):
        """Find a free port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    return port
        return start_port  # Fallback
    
    requested_port = int(os.getenv("PORT", 5000))
    port = find_free_port(requested_port)
    
    if port != requested_port:
        print(f"Warning: Port {requested_port} is in use. Using port {port} instead.")
        print("To use a specific port, set the PORT environment variable.")
    
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    print(f"Starting AI Travel Micro-Planner server on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)


