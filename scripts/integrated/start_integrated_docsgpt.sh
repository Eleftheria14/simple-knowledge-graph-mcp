#!/bin/bash

echo "🚀 Starting DocsGPT + Knowledge Graph Integrated System"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

print_status "📋 Pre-flight Checks" $BLUE

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    print_status "❌ Docker is not running. Please start Docker first." $RED
    exit 1
fi

print_status "✅ Docker is running" $GREEN

# Check if docker-compose file exists
if [ ! -f "docsgpt-source/deployment/docker-compose.yaml" ]; then
    print_status "❌ DocsGPT docker-compose.yaml not found. Are you in the correct directory?" $RED
    print_status "   Expected path: $(pwd)/docsgpt-source/deployment/docker-compose.yaml" $RED
    exit 1
fi

print_status "✅ DocsGPT docker-compose.yaml found" $GREEN

# Check if API key is set
if [ ! -f "docsgpt-source/application/.env" ] || ! grep -q "^API_KEY=" docsgpt-source/application/.env; then
    print_status "⚠️  API Key not found in docsgpt-source/application/.env" $YELLOW
    print_status "   You'll need to add your Anthropic/OpenAI API key to start the backend" $YELLOW
fi

print_status "🚀 Starting Integrated Services" $BLUE

# Stop existing containers and remove orphans
print_status "🛑 Stopping existing containers..." $YELLOW
docker-compose -f docsgpt-source/deployment/docker-compose.yaml down --remove-orphans > /dev/null 2>&1

# Start the integrated stack with environment variables
print_status "🐳 Starting integrated Docker stack..." $YELLOW
cd docsgpt-source

# Set default environment variables if not provided
export API_KEY=${API_KEY:-"your_api_key_here"}
export LLM_PROVIDER=${LLM_PROVIDER:-"anthropic"}
export LLM_NAME=${LLM_NAME:-"claude-3-sonnet-20240229"}
export VITE_API_STREAMING=${VITE_API_STREAMING:-"true"}

docker-compose -f deployment/docker-compose.yaml up -d

# Wait for services to start
print_status "⏳ Waiting for services to initialize..." $YELLOW
sleep 30

# Check service health
print_status "🔍 Checking Service Health" $BLUE

# Check DocsGPT frontend
if curl -s -f http://localhost:5173 > /dev/null 2>&1; then
    print_status "✅ DocsGPT Frontend: Running" $GREEN
else
    print_status "⚠️  DocsGPT Frontend: Starting..." $YELLOW
fi

# Check DocsGPT backend
if curl -s -f http://localhost:7091/api/config > /dev/null 2>&1; then
    print_status "✅ DocsGPT Backend: Running" $GREEN
else
    # Check if container is running but not ready
    if docker ps --format '{{.Names}}' | grep -q "docsgpt-oss-backend"; then
        print_status "⚠️  DocsGPT Backend: Starting (check API key in .env)" $YELLOW
    else
        print_status "❌ DocsGPT Backend: Failed to start" $RED
    fi
fi

# Check Neo4j
if curl -s -f http://localhost:7474 > /dev/null 2>&1; then
    print_status "✅ Neo4j Database: Running" $GREEN
else
    print_status "⚠️  Neo4j Database: Starting..." $YELLOW
fi

# Check n8n
if curl -s -f http://localhost:5678/healthz > /dev/null 2>&1; then
    print_status "✅ n8n Workflow Engine: Running" $GREEN
else
    print_status "⚠️  n8n Workflow Engine: Starting..." $YELLOW
fi

# Check n8n MCP Server
if curl -s -f http://localhost:3001/health > /dev/null 2>&1; then
    print_status "✅ n8n MCP Server: Running" $GREEN
else
    print_status "⚠️  n8n MCP Server: Starting..." $YELLOW
fi

cd ..

print_status "🎉 Integrated System Startup Complete!" $PURPLE
echo ""
print_status "📊 Service Access Points:" $BLUE
echo "   🌐 DocsGPT UI:        http://localhost:5173"
echo "   🔧 DocsGPT API:       http://localhost:7091"
echo "   ⚙️  n8n Workflows:    http://localhost:5678 (admin/password123)"
echo "   🗄️  Neo4j Browser:    http://localhost:7474 (neo4j/password123)"
echo "   📡 n8n MCP Server:    http://localhost:3001"
echo ""

print_status "⚡ Next Steps:" $BLUE
echo "   1. Add API key: Edit docsgpt-source/application/.env"
echo "   2. Import n8n workflow: ./scripts/import_docsgpt_workflow.sh"
echo "   3. Test integration: python3 test_docsgpt_integration.py"
echo "   4. Upload documents via DocsGPT UI to test knowledge graph"
echo ""

print_status "🛑 To stop the system:" $YELLOW
echo "   ./scripts/stop_integrated_system.sh"
echo ""

# Show container status
print_status "📦 Container Status:" $BLUE
docker-compose -f docsgpt-source/deployment/docker-compose.yaml ps

# Optional: Run integration test
echo ""
read -p "🧪 Run integration tests now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "🧪 Running Integration Tests..." $BLUE
    python3 test_docsgpt_integration.py
fi

print_status "✨ Setup Complete!" $PURPLE