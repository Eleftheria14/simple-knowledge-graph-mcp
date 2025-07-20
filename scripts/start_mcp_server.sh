#!/bin/bash

# Start the Simple Knowledge Graph MCP Server
#
# NOTE: For Claude Code MCP integration, use this direct command instead:
# claude mcp add knowledge-graph -e PYTHONPATH=src -- uv run python src/server/main.py
# This script is for interactive development/testing with status checks.

set -e  # Exit on any error

echo "🚀 Starting Simple Knowledge Graph MCP Server..."
echo ""

# Check if UV environment exists
if [ -f "pyproject.toml" ] && [ -d ".venv" ]; then
    echo "🔧 Using UV environment..."
    echo "   ✅ UV environment detected"
else
    echo "❌ UV environment not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Check if services are running
echo "🔍 Checking service dependencies..."

# Check Neo4j
if curl -f http://localhost:7474/ > /dev/null 2>&1; then
    echo "   ✅ Neo4j is running"
else
    echo "   ❌ Neo4j not running. Please run ./start_services.sh first"
    exit 1
fi

# Test database connections
echo "🧪 Testing database connections..."
uv run python -c "
import sys
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
    driver.verify_connectivity()
    driver.close()
    print('   ✅ Neo4j connection verified')
except Exception as e:
    print(f'   ❌ Neo4j connection failed: {e}')
    sys.exit(1)

try:
    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(
        path='./chroma_db',
        settings=Settings(anonymized_telemetry=False)
    )
    client.heartbeat()
    print('   ✅ ChromaDB connection verified')
except Exception as e:
    print(f'   ❌ ChromaDB connection failed: {e}')
    sys.exit(1)
"

# Test MCP server imports
echo "🔍 Testing MCP server imports..."
uv run python -c "
import sys
sys.path.insert(0, 'src')
try:
    from server.main import mcp
    from storage.neo4j import Neo4jStorage, Neo4jQuery
    from storage.chroma import ChromaDBStorage, ChromaDBQuery
    from storage.embedding import EmbeddingService
    print('   ✅ All MCP server imports successful')
except Exception as e:
    print(f'   ❌ Import failed: {e}')
    exit(1)
"

# Show server configuration
echo ""
echo "⚙️  MCP Server Configuration:"
echo "   • Server Name: Simple Knowledge Graph"
echo "   • Tools Available: 5 (store_entities, store_vectors, query_knowledge_graph, generate_literature_review, clear_knowledge_graph)"
echo "   • Neo4j: bolt://localhost:7687"
echo "   • ChromaDB: ./chroma_db"
echo "   • Embedding Model: all-MiniLM-L6-v2"
echo ""

# Start the MCP server
echo "🎯 Starting MCP server..."
echo "   Press Ctrl+C to stop the server"
echo ""

cd src && PYTHONPATH=. uv run python server/main.py