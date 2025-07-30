#!/bin/bash

echo "🛑 Stopping DocsGPT + Knowledge Graph Integrated System"
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

# Check if docker-compose file exists
if [ ! -f "docsgpt-source/deployment/docker-compose.yaml" ]; then
    print_status "❌ DocsGPT docker-compose.yaml not found. Are you in the correct directory?" $RED
    print_status "   Expected path: $(pwd)/docsgpt-source/deployment/docker-compose.yaml" $RED
    exit 1
fi

print_status "🛑 Stopping all integrated services..." $YELLOW

# Stop and remove containers
docker-compose -f docsgpt-source/deployment/docker-compose.yaml down --remove-orphans

print_status "🧹 Cleaning up..." $YELLOW

# Show what was stopped
print_status "📊 Services stopped:" $BLUE
echo "   🌐 DocsGPT Frontend (port 5173)"
echo "   🔧 DocsGPT Backend (port 7091)"
echo "   ⚙️  n8n Workflows (port 5678)"
echo "   🗄️  Neo4j Database (ports 7474, 7687)"
echo "   📡 n8n MCP Server (port 3001)"
echo "   🔴 Redis Cache (port 6379)"
echo "   📚 MongoDB (port 27017)"
echo ""

print_status "💾 Data Preservation:" $GREEN
echo "   ✅ Neo4j data preserved in Docker volume 'neo4j_data'"
echo "   ✅ n8n workflows preserved in Docker volume 'n8n_data'"
echo "   ✅ MongoDB data preserved in Docker volume 'mongodb_data_container'"
echo "   ✅ ChromaDB data preserved in local './chroma_db' directory"
echo ""

print_status "🚀 To restart the system:" $GREEN
echo "   ./scripts/start_integrated_docsgpt.sh"
echo ""

print_status "🗑️  To completely remove data volumes:" $RED
echo "   docker volume rm docsgpt-oss_neo4j_data docsgpt-oss_n8n_data docsgpt-oss_mongodb_data_container docsgpt-oss_n8n_mcp_data"
echo ""

print_status "✅ Integrated system stopped successfully!" $PURPLE