#!/bin/bash

# Check status of Simple Knowledge Graph MCP services

echo "🔍 Simple Knowledge Graph MCP - Service Status"
echo ""

# Check UV environment
if [ -f "pyproject.toml" ] && [ -d ".venv" ]; then
    echo "✅ UV environment: Ready"
else
    echo "❌ UV environment: Not found (run ./scripts/setup.sh)"
fi

# Check Docker
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo "✅ Docker: Running"
    else
        echo "❌ Docker: Not running"
    fi
else
    echo "❌ Docker: Not installed"
fi

# Check Neo4j
if docker ps --format 'table {{.Names}}' | grep -q "^neo4j-kg$"; then
    if curl -f http://localhost:7474/ > /dev/null 2>&1; then
        echo "✅ Neo4j: Running (http://localhost:7474)"
        
        # Check database content
        uv run python -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
    with driver.session() as session:
        result = session.run('MATCH (n) RETURN count(n) as node_count')
        node_count = result.single()['node_count']
        result = session.run('MATCH ()-[r]-() RETURN count(r) as rel_count')
        rel_count = result.single()['rel_count']
        print(f'   📊 Entities: {node_count}, Relationships: {rel_count}')
    driver.close()
except Exception as e:
    print(f'   ⚠️  Connection error: {e}')
" 2>/dev/null
    else
        echo "⚠️  Neo4j: Container running but not responding"
    fi
else
    echo "❌ Neo4j: Not running (run ./start_services.sh)"
fi

# Check ChromaDB
if [ -d "chroma_db" ]; then
    echo "✅ ChromaDB: Directory exists (./chroma_db)"
    
    # Check database content
    uv run python -c "
import chromadb
from chromadb.config import Settings
try:
    client = chromadb.PersistentClient(
        path='./chroma_db',
        settings=Settings(anonymized_telemetry=False)
    )
    collections = client.list_collections()
    total_docs = 0
    for collection in collections:
        try:
            count = collection.count()
            total_docs += count
        except:
            pass
    print(f'   📊 Collections: {len(collections)}, Documents: {total_docs}')
except Exception as e:
    print(f'   ⚠️  Access error: {e}')
" 2>/dev/null
else
    echo "ℹ️  ChromaDB: No database yet (will be created on first use)"
fi

# Check embedding model
echo -n "🤖 Embedding model: "
uv run python -c "
from sentence_transformers import SentenceTransformer
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('Ready (all-MiniLM-L6-v2)')
except Exception as e:
    print(f'Error - {e}')
" 2>/dev/null

# Check Python dependencies
echo -n "📦 Dependencies: "
uv run python -c "
try:
    import fastmcp, neo4j, chromadb, sentence_transformers, pydantic
    print('All installed')
except ImportError as e:
    print(f'Missing - {e}')
" 2>/dev/null

echo ""
echo "🎯 Quick Actions:"
if [ ! -f "pyproject.toml" ] || [ ! -d ".venv" ]; then
    echo "   ./scripts/setup.sh        # First-time setup"
fi
if ! docker ps --format 'table {{.Names}}' | grep -q "^neo4j-kg$"; then
    echo "   ./scripts/start_services.sh   # Start Neo4j and test connections"
fi
echo "   ./scripts/start_mcp_server.sh # Start MCP server for Claude"
echo "   ./scripts/clear_databases.sh  # Clear all data"
echo "   ./scripts/stop_services.sh    # Stop services"