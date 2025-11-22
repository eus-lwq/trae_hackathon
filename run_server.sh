#!/bin/bash
# Run the AI Travel Micro-Planner server using uv

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Create one with your GOOGLE_API_KEY"
    echo "Example: echo 'GOOGLE_API_KEY=your_key_here' > .env"
fi

# Check if port 5000 is in use and suggest alternative
if lsof -ti:5000 > /dev/null 2>&1; then
    echo "Note: Port 5000 is in use. The server will automatically use the next available port."
    echo "To use a specific port, set PORT environment variable: PORT=5001 uv run python server.py"
fi

# Run the server using uv
uv run python server.py

