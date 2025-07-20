#!/bin/bash

# Docker Setup Script for Knowledge Graph MCP
# Builds and runs the entire stack with Docker Compose

set -e

echo "🐳 Setting up Knowledge Graph MCP with Docker..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Create docker-compose.yml if it doesn't exist
if [ ! -f "docker-compose.yml" ]; then
    echo "📝 Creating docker-compose.yml..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  neo4j:
    image: neo4j:5.25
    container_name: knowledge-graph-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474/"]
      interval: 30s
      timeout: 10s
      retries: 5

  mcp-server:
    build: .
    container_name: knowledge-graph-mcp
    ports:
      - "3001:3001"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - CHROMADB_PATH=/app/chroma_db
    volumes:
      - chroma_data:/app/chroma_db
    depends_on:
      neo4j:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/mcp/"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  neo4j_data:
  neo4j_logs:
  chroma_data:
EOF
    echo "   ✅ docker-compose.yml created"
fi

# Update Dockerfile for better container setup
echo "📝 Updating Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install UV
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY requirements.txt .
COPY src/ ./src/
COPY .env.example .env

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Create ChromaDB directory
RUN mkdir -p /app/chroma_db

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3001/mcp/ || exit 1

# Start HTTP server
CMD ["uv", "run", "python", "src/server/main.py", "--http"]
EOF

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🔍 Checking service status..."
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ Services are running and healthy!"
else
    echo "⚠️  Services are starting up, checking logs..."
    docker-compose logs --tail=20
fi

echo ""
echo "🎯 MCP Server Configuration:"
echo "   • HTTP URL: http://localhost:3001"
echo "   • Neo4j Web: http://localhost:7474 (neo4j/password)"
echo "   • MCP Endpoint: http://localhost:3001/mcp/"
echo ""
echo "📋 To connect in Claude Desktop or ChatGPT Desktop:"
echo "   1. Settings → Connectors → Add custom connector"
echo "   2. Name: Knowledge Graph"
echo "   3. URL: http://localhost:3001"
echo "   4. Click Add and restart"
echo ""
echo "🔧 Useful commands:"
echo "   docker-compose logs -f          # View logs"
echo "   docker-compose stop             # Stop services"
echo "   docker-compose down -v          # Stop and remove data"
echo "   docker-compose restart          # Restart services"
echo ""
echo "✅ Docker setup complete!"