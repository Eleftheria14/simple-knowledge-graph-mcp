#!/bin/bash

# Start HTTP MCP Server for Claude Desktop GUI Setup

set -e

echo "🌐 Starting Knowledge Graph MCP Server in HTTP mode..."
echo ""

# Check if UV environment exists
if [ -f "pyproject.toml" ] && [ -d ".venv" ]; then
    echo "🔧 Using UV environment..."
else
    echo "❌ UV environment not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Check services
if ! curl -f http://localhost:7474/ > /dev/null 2>&1; then
    echo "❌ Neo4j not running. Please run ./scripts/start_services.sh first"
    exit 1
fi

echo "✅ All services ready"
echo ""
echo "🎯 HTTP MCP Server will be available at:"
echo "   📍 URL: http://localhost:3001"
echo ""
echo "📋 To connect in Claude Desktop:"
echo "   1. Go to Settings → Connectors" 
echo "   2. Click 'Add custom connector'"
echo "   3. Name: Knowledge Graph"
echo "   4. URL: http://localhost:3001"
echo "   5. Click Add"
echo ""
echo "🚀 Starting server... (Press Ctrl+C to stop)"
echo ""

cd src && PYTHONPATH=. uv run python server/main.py --http