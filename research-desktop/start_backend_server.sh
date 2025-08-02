#!/bin/bash
# Start the backend HTTP API server for research-desktop

echo "🚀 Starting Research Desktop Backend API Server..."
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if Neo4j is running
echo "🔍 Checking Neo4j connection..."
if ! curl -s http://localhost:7474 > /dev/null; then
    echo "⚠️  Warning: Neo4j might not be running on localhost:7474"
    echo "   Start with: ./scripts/start_services.sh"
    echo ""
fi

# Check if GROBID is running
echo "🔍 Checking GROBID connection..."
if ! curl -s http://localhost:8070/api/isalive > /dev/null; then
    echo "⚠️  Warning: GROBID might not be running on localhost:8070"
    echo "   Start with: docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0"
    echo ""
fi

# Install required dependencies
echo "📦 Installing API server dependencies..."
uv add fastapi uvicorn[standard] pydantic

echo ""
echo "🌐 Starting server on http://localhost:8001"
echo "📖 API documentation: http://localhost:8001/docs"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start the server
cd "$(dirname "$0")"
uv run python backend_api_server.py