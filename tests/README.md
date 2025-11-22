# Test Suite Documentation

This directory contains comprehensive tests for the AI Travel Micro-Planner backend.

## Test Files

### `test_database.py` (9 tests, 96% coverage)
Tests all database operations:
- Session creation, retrieval, and updates
- Travel plan CRUD operations
- Chat history management
- Plan updates and queries

### `test_tools.py` (12 tests, 78% coverage)
Tests all three agent tools:
- **web_resource_tool**: Web scraping and content extraction
- **plan_tool**: Create, update, get, and list travel plans
- **map_route_tool**: Map route generation with per-day colors

### `test_server.py` (10 tests, 65% coverage)
Tests all Flask API endpoints:
- Health check endpoint
- Chat endpoint with various scenarios
- Session management endpoints
- Plan retrieval endpoints

### `test_orchestrator.py` (4 tests, 50% coverage)
Tests agent orchestration:
- Agent initialization
- API key validation
- Basic chat functionality
- Session auto-creation

## Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test file
uv run pytest tests/test_database.py

# Run specific test
uv run pytest tests/test_database.py::TestTravelPlannerDB::test_create_session

# Run with coverage
uv run pytest tests/ --cov=agent --cov=cache --cov=server --cov-report=html
```

## Test Fixtures

The `conftest.py` file provides shared fixtures:
- `temp_db`: Temporary database for each test
- `sample_session_id`: Sample session ID
- `sample_plan_data`: Sample travel plan data structure

## Coverage Goals

- Database: 96% ✅
- Tools: 78% ✅
- Server: 65% (can be improved)
- Orchestrator: 50% (limited by LLM mocking complexity)

## Notes

- Tests use temporary databases to avoid conflicts
- External API calls (web scraping) are mocked
- LLM calls are mocked to avoid API costs
- All tests are isolated and can run in parallel

