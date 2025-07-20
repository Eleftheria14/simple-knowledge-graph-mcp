#!/bin/bash

# Start services for Simple Knowledge Graph MCP

set -e  # Exit on any error

echo "🚀 Starting Simple Knowledge Graph MCP Services..."
echo ""

# Check if UV environment exists
if [ -f "pyproject.toml" ] && [ -d ".venv" ]; then
    echo "🔧 Using UV environment..."
    echo "   ✅ UV environment detected"
else
    echo "❌ UV environment not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Check if Neo4j container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^neo4j-kg$"; then
    if docker ps --format 'table {{.Names}}' | grep -q "^neo4j-kg$"; then
        echo "📊 Neo4j container is already running"
    else
        echo "📊 Starting existing Neo4j container..."
        docker start neo4j-kg
    fi
else
    echo "📊 Creating and starting Neo4j container..."
    docker run -d --name neo4j-kg \
      -p 7474:7474 -p 7687:7687 \
      -e NEO4J_AUTH=neo4j/password \
      -e NEO4J_PLUGINS='["apoc"]' \
      -v neo4j_data:/data \
      -v neo4j_logs:/logs \
      neo4j:latest
fi

# Wait for Neo4j to start and test connection
echo "⏳ Waiting for Neo4j to start..."
for i in {1..30}; do
    if curl -f http://localhost:7474/ > /dev/null 2>&1; then
        echo "   ✅ Neo4j is ready after ${i}0 seconds"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ Neo4j failed to start after 5 minutes"
        echo "   💡 Try: docker logs neo4j-kg"
        exit 1
    fi
    sleep 10
done

# Test Neo4j connection
echo "🧪 Testing Neo4j connection..."
uv run python -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
    with driver.session() as session:
        result = session.run('RETURN 1 as test')
        record = result.single()
        print('   ✅ Neo4j connection successful')
    driver.close()
except Exception as e:
    print(f'   ❌ Neo4j connection failed: {e}')
    exit(1)
"

# Test ChromaDB (it will be created automatically when first used)
echo "🧪 Testing ChromaDB setup..."
uv run python -c "
import chromadb
from chromadb.config import Settings
try:
    client = chromadb.PersistentClient(
        path='./chroma_db',
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_or_create_collection('test_collection')
    print('   ✅ ChromaDB setup successful')
except Exception as e:
    print(f'   ❌ ChromaDB setup failed: {e}')
    exit(1)
"

# Test sentence-transformers (download model if needed)
echo "🧪 Testing embedding model..."
uv run python -c "
from sentence_transformers import SentenceTransformer
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    test_embedding = model.encode(['test sentence'])
    print(f'   ✅ Embedding model ready (dimension: {len(test_embedding[0])})')
except Exception as e:
    print(f'   ❌ Embedding model failed: {e}')
    exit(1)
"

echo ""
echo "🎉 All services are running successfully!"
echo ""
echo "📊 Service Status:"
echo "   • Neo4j Browser: http://localhost:7474 (neo4j/password)"
echo "   • Neo4j Bolt: bolt://localhost:7687"
echo "   • ChromaDB: ./chroma_db (local files)"
echo "   • Embeddings: all-MiniLM-L6-v2 model ready"
echo ""
echo "Next steps:"
echo "1. Start MCP server: ./start_mcp_server.sh"
echo "2. Configure Claude Desktop with this server"
echo "3. Upload PDFs to Claude and start building your knowledge graph!"