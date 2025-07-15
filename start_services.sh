#!/bin/bash

echo "🚀 Starting GraphRAG MCP Services"
echo "================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Function to check if a service is running
check_service() {
    curl -s -f "$2" > /dev/null 2>&1
}

echo "1. Starting Ollama..."
if check_service "Ollama" "http://localhost:11434/api/tags"; then
    print_status "Ollama already running"
else
    print_warning "Starting Ollama server..."
    # Start Ollama in background
    nohup ollama serve > /dev/null 2>&1 &
    sleep 3
    if check_service "Ollama" "http://localhost:11434/api/tags"; then
        print_status "Ollama started successfully"
    else
        print_error "Failed to start Ollama"
    fi
fi

echo ""
echo "2. Starting Neo4j..."
if check_service "Neo4j" "http://localhost:7474/"; then
    print_status "Neo4j already running"
else
    print_warning "Starting Neo4j container..."
    # Start or create Neo4j container
    if docker ps -a --format "table {{.Names}}" | grep -q "neo4j"; then
        docker start neo4j
    else
        docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
    fi
    sleep 10
    if check_service "Neo4j" "http://localhost:7474/"; then
        print_status "Neo4j started successfully"
    else
        print_error "Failed to start Neo4j"
    fi
fi

echo ""
echo "3. Checking required models..."
if ollama list | grep -q "llama3.1:8b"; then
    print_status "llama3.1:8b model available"
else
    print_warning "Pulling llama3.1:8b model..."
    ollama pull llama3.1:8b
fi

if ollama list | grep -q "nomic-embed-text"; then
    print_status "nomic-embed-text model available"
else
    print_warning "Pulling nomic-embed-text model..."
    ollama pull nomic-embed-text
fi

echo ""
echo "🎉 Services Status:"
echo "=================="
echo "- Ollama API: http://localhost:11434"
echo "- Neo4j Browser: http://localhost:7474 (neo4j/password)"
echo ""
echo "✅ Ready to run notebooks/Main/Simple_Document_Processing.ipynb"
echo ""
echo "💡 To run the full notebook startup:"
echo "   ./start_notebook_processing.sh"