"""Example usage of the AI Travel Micro-Planner API."""
import requests
import json

BASE_URL = "http://localhost:5000"


def example_chat():
    """Example: Chat with the travel planning agent."""
    print("=== Example: Chat with Travel Planning Agent ===\n")
    
    # Create a session (optional - will be created automatically)
    response = requests.post(f"{BASE_URL}/api/sessions", json={})
    session_data = response.json()
    session_id = session_data.get("session_id")
    print(f"Session ID: {session_id}\n")
    
    # Send a chat message
    message = "I want to plan a 3-day trip to Tokyo from 2024-06-01 to 2024-06-03. Include visits to Shibuya, Asakusa, and the Tokyo Skytree."
    
    print(f"User: {message}\n")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": message,
            "session_id": session_id
        }
    )
    
    result = response.json()
    print(f"Agent: {result.get('response', 'No response')}\n")
    
    return session_id


def example_get_plans(session_id: str):
    """Example: Get all plans for a session."""
    print("=== Example: Get Travel Plans ===\n")
    
    response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/plans")
    plans_data = response.json()
    
    print(f"Found {plans_data.get('count', 0)} plans:\n")
    for plan in plans_data.get("plans", []):
        print(f"Plan ID: {plan['plan_id']}")
        print(f"Destination: {plan['destination']}")
        print(f"Dates: {plan['start_date']} to {plan['end_date']}")
        print(f"Plan Data: {json.dumps(plan['plan_data'], indent=2)}\n")


def example_web_research():
    """Example: Research travel information from web."""
    print("=== Example: Web Research ===\n")
    
    message = "Can you research information about Paris hotels? Check https://www.booking.com/city/fr/paris.html"
    
    print(f"User: {message}\n")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": message}
    )
    
    result = response.json()
    print(f"Agent: {result.get('response', 'No response')[:500]}...\n")


def example_get_route(plan_id: str, session_id: str):
    """Example: Get map route for a plan."""
    print("=== Example: Get Map Route ===\n")
    
    response = requests.get(
        f"{BASE_URL}/api/plans/{plan_id}/route",
        params={"session_id": session_id}
    )
    
    route_data = response.json()
    print(f"Route Data: {json.dumps(route_data, indent=2)}\n")


if __name__ == "__main__":
    print("AI Travel Micro-Planner - Example Usage\n")
    print("=" * 50 + "\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Error: Server is not responding correctly")
            exit(1)
        print("✓ Server is running\n")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Make sure it's running on", BASE_URL)
        print("Start the server with: python server.py")
        exit(1)
    
    # Run examples
    try:
        session_id = example_chat()
        example_get_plans(session_id)
        # example_web_research()  # Uncomment to test web research
        # example_get_route(plan_id, session_id)  # Uncomment with actual plan_id
    except Exception as e:
        print(f"Error running examples: {e}")


