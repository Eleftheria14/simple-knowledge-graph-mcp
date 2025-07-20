#!/bin/bash

# Docker MCP Server Only Script
# Uses existing Neo4j and ChromaDB installations

set -e

echo "🐳 Setting up MCP Server Docker container..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Check if existing services are running
echo "🔍 Checking existing services..."
if curl -f http://localhost:7474/ > /dev/null 2>&1; then
    echo "   ✅ Neo4j is running"
else
    echo "   ❌ Neo4j not running. Please start it first with ./scripts/start_services.sh"
    exit 1
fi

# Build MCP server Docker image
echo "🔨 Building MCP server Docker image..."
docker build -t knowledge-graph-mcp:latest .

# Stop any existing MCP container
echo "🛑 Stopping any existing MCP container..."
docker stop knowledge-graph-mcp-server 2>/dev/null || true
docker rm knowledge-graph-mcp-server 2>/dev/null || true

# Run MCP server container
echo "🚀 Starting MCP server container..."
docker run -d \
  --name knowledge-graph-mcp-server \
  -p 3001:3001 \
  -e NEO4J_URI=bolt://host.docker.internal:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=password \
  -e CHROMADB_PATH=/app/chroma_db \
  -v "$(pwd)/chroma_db:/app/chroma_db" \
  --add-host=host.docker.internal:host-gateway \
  knowledge-graph-mcp:latest

# Wait for container to start
echo "⏳ Waiting for MCP server to start..."
sleep 5

# Check if container is running
if docker ps | grep -q knowledge-graph-mcp-server; then
    echo "✅ MCP server container is running!"
else
    echo "❌ MCP server failed to start. Checking logs..."
    docker logs knowledge-graph-mcp-server
    exit 1
fi

# Test MCP endpoint
echo "🧪 Testing MCP endpoint..."
sleep 5
if curl -f http://localhost:3001/mcp/ > /dev/null 2>&1; then
    echo "✅ MCP server is responding!"
else
    echo "⚠️  MCP server starting up, checking logs..."
    docker logs --tail=10 knowledge-graph-mcp-server
fi

echo ""
echo "🎯 MCP Server Configuration:"
echo "   • HTTP URL: http://localhost:3001"
echo "   • MCP Endpoint: http://localhost:3001/mcp/"
echo "   • Container: knowledge-graph-mcp-server"
echo ""
echo "📋 To connect in Claude Desktop or ChatGPT Desktop:"
echo "   1. Settings → Connectors → Add custom connector"
echo "   2. Name: Knowledge Graph"
echo "   3. URL: http://localhost:3001"
echo "   4. Click Add and restart"
echo ""
echo "🔧 Useful commands:"
echo "   docker logs -f knowledge-graph-mcp-server    # View logs"
echo "   docker stop knowledge-graph-mcp-server       # Stop container"
echo "   docker start knowledge-graph-mcp-server      # Start container"
echo "   docker rm knowledge-graph-mcp-server         # Remove container"
echo ""
echo "✅ MCP Docker server setup complete!"