#!/bin/bash

# Clear all databases for Simple Knowledge Graph MCP

echo "🗑️  Clearing Simple Knowledge Graph MCP Databases..."
echo ""

# Warning message
echo "⚠️  WARNING: This will permanently delete ALL data in your knowledge graph!"
echo "   • Neo4j: All entities, relationships, and documents"
echo "   • ChromaDB: All text chunks, embeddings, and citations"
echo ""

read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operation cancelled"
    exit 0
fi

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Using system Python..."
fi

# Clear Neo4j database
echo "🗑️  Clearing Neo4j database..."
if curl -f http://localhost:7474/ > /dev/null 2>&1; then
    python3 -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
    with driver.session() as session:
        # Delete all nodes and relationships
        session.run('MATCH (n) DETACH DELETE n')
        
        # Delete all constraints and indexes
        result = session.run('SHOW CONSTRAINTS')
        for record in result:
            constraint_name = record['name']
            session.run(f'DROP CONSTRAINT {constraint_name}')
        
        result = session.run('SHOW INDEXES')
        for record in result:
            if record['type'] != 'LOOKUP':  # Don't drop system indexes
                index_name = record['name']
                session.run(f'DROP INDEX {index_name}')
        
        print('   ✅ Neo4j database cleared')
    driver.close()
except Exception as e:
    print(f'   ❌ Neo4j clearing failed: {e}')
"
else
    echo "   ⚠️  Neo4j not running - skipping Neo4j cleanup"
fi

# Clear ChromaDB database
echo "🗑️  Clearing ChromaDB database..."
if [ -d "chroma_db" ]; then
    rm -rf chroma_db
    echo "   ✅ ChromaDB directory removed"
else
    echo "   ℹ️  ChromaDB directory doesn't exist"
fi

# Test that databases are empty
echo "🧪 Verifying databases are empty..."

# Test Neo4j
if curl -f http://localhost:7474/ > /dev/null 2>&1; then
    python3 -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
    with driver.session() as session:
        result = session.run('MATCH (n) RETURN count(n) as node_count')
        count = result.single()['node_count']
        if count == 0:
            print('   ✅ Neo4j is empty')
        else:
            print(f'   ⚠️  Neo4j still has {count} nodes')
    driver.close()
except Exception as e:
    print(f'   ❌ Neo4j verification failed: {e}')
"
fi

# Test ChromaDB
python3 -c "
import chromadb
from chromadb.config import Settings
try:
    client = chromadb.PersistentClient(
        path='./chroma_db',
        settings=Settings(anonymized_telemetry=False)
    )
    collections = client.list_collections()
    if len(collections) == 0:
        print('   ✅ ChromaDB is empty')
    else:
        print(f'   ⚠️  ChromaDB still has {len(collections)} collections')
except Exception as e:
    print(f'   ❌ ChromaDB verification failed: {e}')
"

echo ""
echo "🎉 Database cleanup complete!"
echo ""
echo "💡 Your knowledge graph is now empty and ready for new documents."
echo "   To add documents, upload PDFs to Claude and ask it to extract entities."