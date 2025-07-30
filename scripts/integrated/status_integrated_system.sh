#!/bin/bash

echo "📊 DocsGPT + Knowledge Graph System Status"
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

# Function to check service health
check_service() {
    local name="$1"
    local url="$2"
    local container="$3"
    
    # Check if container is running
    if [ -n "$container" ] && docker ps --format '{{.Names}}' | grep -q "^$container$"; then
        # Container is running, check if service responds
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_status "✅ $name: Running and responding" $GREEN
        else
            print_status "⚠️  $name: Container running but not responding" $YELLOW
        fi
    else
        print_status "❌ $name: Not running" $RED
    fi
}

print_status "🔍 Checking Services..." $BLUE
echo ""

# Check each service
check_service "DocsGPT Frontend" "http://localhost:5173" "docsgpt-oss-frontend-1"
check_service "DocsGPT Backend" "http://localhost:7091/api/config" "docsgpt-oss-backend-1"
check_service "Neo4j Database" "http://localhost:7474" "docsgpt-oss-neo4j-1"
check_service "n8n Workflows" "http://localhost:5678/healthz" "docsgpt-oss-n8n-1"
check_service "n8n MCP Server" "http://localhost:3001/health" "docsgpt-oss-n8n-mcp-server-1"
check_service "Redis Cache" "http://localhost:6379" "docsgpt-oss-redis-1"
check_service "MongoDB" "http://localhost:27017" "docsgpt-oss-mongo-1"

echo ""
print_status "📦 Container Details:" $BLUE

if docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -q "docsgpt-oss"; then
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep "docsgpt-oss"
else
    print_status "❌ No DocsGPT containers running" $RED
fi

echo ""
print_status "🌐 Service URLs:" $BLUE
echo "   • DocsGPT UI:        http://localhost:5173"
echo "   • DocsGPT API:       http://localhost:7091"
echo "   • Neo4j Browser:     http://localhost:7474 (neo4j/password123)"
echo "   • n8n Workflows:     http://localhost:5678 (admin/password123)"
echo "   • n8n MCP Server:    http://localhost:3001"

echo ""
print_status "🛠️  Management Commands:" $BLUE
echo "   • Start system:      ./scripts/start_integrated_docsgpt.sh"
echo "   • Stop system:       ./scripts/stop_integrated_system.sh"
echo "   • View logs:         docker-compose -f docsgpt-source/deployment/docker-compose.yaml logs -f"
echo "   • Test integration:  python3 test_docsgpt_integration.py"

echo ""