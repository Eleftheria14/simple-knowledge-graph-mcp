#!/bin/bash

# Clear ChromaDB and Neo4j Databases Script
# Removes all persistent ChromaDB and Neo4j databases to start fresh

echo "🧹 Clearing All ChromaDB and Neo4j Databases"
echo "============================================="

# Function to safely remove directory
remove_db() {
    local db_path="$1"
    local db_name="$2"
    
    if [ -d "$db_path" ]; then
        echo "🗑️  Removing $db_name..."
        rm -rf "$db_path"
        echo "   ✅ $db_name cleared"
    else
        echo "   ℹ️  $db_name not found (already clean)"
    fi
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Remove all ChromaDB databases
remove_db "chroma_graph_db" "Main GraphRAG Database"
remove_db "tutorial/chroma_graph_db" "Tutorial GraphRAG Database" 
remove_db "tutorial/chroma_db" "Tutorial RAG Database"
remove_db "tutorial/tutorial_graph_db" "Tutorial Graph Database"
remove_db "notebooks/chroma_db" "Notebooks Database"

# Also clear any other potential ChromaDB directories
remove_db "chroma_db" "Legacy ChromaDB Database"
remove_db "test_chroma_db" "Test ChromaDB Database"
remove_db "test_chroma_validation" "Test Validation Database"
remove_db "chroma_citations_db" "Citations Database"

echo ""
echo "🗄️  Clearing Neo4j Database"
echo "=========================="

# Function to clear Neo4j database
clear_neo4j() {
    echo "🔍 Checking Neo4j connection..."
    
    # Check if Neo4j is running
    if curl -f -s http://localhost:7474/ > /dev/null 2>&1; then
        echo "✅ Neo4j is running"
        
        # Clear all GraphRAG related data
        echo "🧹 Clearing GraphRAG data from Neo4j..."
        
        # Use cypher-shell if available, otherwise use curl
        if command -v cypher-shell > /dev/null 2>&1; then
            echo "📝 Using cypher-shell to clear data..."
            cypher-shell -u neo4j -p password --non-interactive << 'EOF'
MATCH (n) WHERE n.project_name IS NOT NULL OR labels(n) IN ['Entity', 'Citation', 'Episodic', 'Community'] DETACH DELETE n;
MATCH ()-[r:MENTIONS|CITES|RELATES_TO|PART_OF]->() DELETE r;
EOF
        else
            echo "📝 Using curl to clear data..."
            curl -X POST \
                -H "Content-Type: application/json" \
                -u neo4j:password \
                -d '{"statements":[{"statement":"MATCH (n) WHERE n.project_name IS NOT NULL OR labels(n) IN [\"Entity\", \"Citation\", \"Episodic\", \"Community\"] DETACH DELETE n"}]}' \
                http://localhost:7474/db/data/transaction/commit > /dev/null 2>&1
        fi
        
        echo "   ✅ Neo4j GraphRAG data cleared"
    else
        echo "   ℹ️  Neo4j not running (no data to clear)"
    fi
}

# Clear Neo4j
clear_neo4j

echo ""
echo "🎯 Database Status:"
echo "=================="

# Check what's left (exclude library files)
remaining_files=$(find . -name "chroma*.sqlite3" -o -name "*chroma*" -type d 2>/dev/null | grep -v "lib/python" | grep -v "dist-info" | grep -v "site-packages")

if [ -n "$remaining_files" ]; then
    echo "📋 Remaining ChromaDB files:"
    echo "$remaining_files" | while read file; do
        echo "   📄 $file"
    done
    echo ""
    echo "💡 Some files may be in use. Stop Jupyter and try again if needed."
else
    echo "✅ All ChromaDB databases successfully cleared!"
fi

# Check Neo4j status
echo ""
echo "🗄️  Neo4j Database Status:"
if curl -f -s http://localhost:7474/ > /dev/null 2>&1; then
    # Count remaining nodes
    if command -v cypher-shell > /dev/null 2>&1; then
        node_count=$(cypher-shell -u neo4j -p password --non-interactive "MATCH (n) RETURN count(n) as count" --format plain 2>/dev/null | tail -1)
        echo "   📊 Total nodes remaining: $node_count"
    else
        echo "   ✅ Neo4j is running (install cypher-shell for node count)"
    fi
else
    echo "   ℹ️  Neo4j not running"
fi

echo ""
echo "🔄 What happens next:"
echo "   • Tutorial paper counts will start from 0"
echo "   • Knowledge graphs will build fresh (both ChromaDB and Neo4j)"
echo "   • No interference from previous runs"
echo "   • Clean learning experience"
echo "   • All entities, citations, and relationships removed"

echo ""
echo "💡 Note: Neo4j indexes and constraints are preserved for performance"
echo "🚀 Ready to run tutorials with completely fresh databases!"