# AI Travel Micro-Planner

A Python backend for an AI-powered travel planning web application that uses LangChain, LangGraph, and Google Gemini to help users plan their trips through natural language conversations.

## Features

- **Flask HTTP Server**: RESTful API for frontend integration
- **LangChain + LangGraph Agent**: Intelligent conversation orchestration
- **Google Gemini LLM**: Powered by Google's Gemini 2.0 Flash model
- **SQLite Cache**: Local storage for sessions and travel plans
- **Three Agent Tools**:
  - `web_resource_tool`: Parse travel content from public web pages (Reddit, Nextdoor, Expedia, Booking, blogs, etc.)
  - `plan_tool`: Create and update travel plans via chat
  - `map_route_tool`: Generate map routes with per-day color labels for frontend visualization

## Project Structure

```
trae_hackathon/
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py    # LangGraph agent orchestration
│   └── tools.py           # Agent tools (web_resource, plan, map_route)
├── cache/
│   ├── __init__.py
│   └── database.py        # SQLite database manager
├── server.py              # Flask HTTP server
├── pyproject.toml         # Project dependencies
└── readme.md              # This file
```

## Setup

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (or use pip)

### Installation

1. Install dependencies:
```bash
uv sync
# or
pip install -r requirements.txt  # if using pip
```

2. Set up environment variables:
   - Copy `.env.example` to `.env` (if it exists) or create a `.env` file
   - Add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. Run the server:
```bash
# Using uv (recommended)
uv run python server.py

# Or use the run script
./run_server.sh

# Or activate the virtual environment first
source .venv/bin/activate  # On macOS/Linux
python server.py
```

The server will start on `http://localhost:5000` by default.

**Note**: Make sure you have a `.env` file with your `GOOGLE_API_KEY` set, otherwise the agent will not be available.

## API Endpoints

### Health Check
- `GET /health` - Check server and agent status

### Chat
- `POST /api/chat` - Send a message to the travel planning agent
  ```json
  {
    "message": "Plan a 3-day trip to Paris",
    "session_id": "optional-session-id"
  }
  ```

### Sessions
- `GET /api/sessions/<session_id>` - Get session information
- `POST /api/sessions` - Create a new session
- `GET /api/sessions/<session_id>/history` - Get chat history
- `GET /api/sessions/<session_id>/plans` - Get all plans for a session

### Travel Plans
- `GET /api/plans/<plan_id>` - Get a specific travel plan
- `GET /api/plans/<plan_id>/route?session_id=<session_id>` - Get map route for a plan

## Usage Examples

### Example 1: Create a Travel Plan

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to plan a 3-day trip to Tokyo from 2024-06-01 to 2024-06-03. Include visits to Shibuya, Asakusa, and the Tokyo Skytree."
  }'
```

### Example 2: Research Travel Information

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you research the best hotels in Paris? Check https://www.booking.com/paris for recommendations.",
    "session_id": "your-session-id"
  }'
```

### Example 3: Get Map Route

```bash
curl "http://localhost:5000/api/plans/<plan_id>/route?session_id=<session_id>"
```

## Agent Tools

### web_resource_tool
Parses travel content from web pages. Supports:
- General web pages (blogs, articles)
- Reddit posts and comments
- Booking sites (Booking.com, Expedia)
- Extracts titles, content, metadata

### plan_tool
Manages travel plans with operations:
- `create`: Create a new travel plan
- `update`: Update an existing plan
- `get`: Retrieve a plan by ID
- `list`: List all plans for a session

### map_route_tool
Generates map route data including:
- Per-day color coding for visualization
- Location waypoints
- Route summary with total days and locations
- Structured data for frontend map integration

## Database Schema

The SQLite database includes three tables:

1. **sessions**: Stores user sessions
2. **travel_plans**: Stores travel plans with itinerary data
3. **chat_history**: Stores conversation history

## Environment Variables

- `GOOGLE_API_KEY`: Required. Your Google Gemini API key
- `FLASK_ENV`: Flask environment (default: development)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `PORT`: Server port (default: 5000)
- `DATABASE_PATH`: Path to SQLite database (default: ./cache/travel_planner.db)

## Development

The codebase is organized into:
- **Agent Layer**: LangGraph orchestration and tool definitions
- **Cache Layer**: Database operations for persistence
- **Server Layer**: Flask API endpoints

## Testing

The project includes a comprehensive test suite using pytest.

### Running Tests

```bash
# Install test dependencies
uv sync --extra test

# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov=agent --cov=cache --cov=server --cov-report=term-missing

# Generate HTML coverage report
uv run pytest tests/ --cov=agent --cov=cache --cov=server --cov-report=html
```

### Test Coverage

The test suite includes:
- **Database Tests** (`test_database.py`): 96% coverage - Tests all database operations
- **Tools Tests** (`test_tools.py`): 78% coverage - Tests web_resource_tool, plan_tool, and map_route_tool
- **Server Tests** (`test_server.py`): 65% coverage - Tests all Flask API endpoints
- **Orchestrator Tests** (`test_orchestrator.py`): 50% coverage - Tests agent initialization and basic functionality

**Overall Coverage: 72%**

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_database.py     # Database operation tests
├── test_tools.py        # Agent tool tests
├── test_server.py       # Flask API endpoint tests
└── test_orchestrator.py # Agent orchestration tests
```

## Notes

- The agent automatically saves chat history and travel plans
- Sessions are created automatically if not provided
- Map routes include color coding for multi-day visualization
- Web scraping respects robots.txt and uses appropriate headers

## License

This project is part of a hackathon submission.


