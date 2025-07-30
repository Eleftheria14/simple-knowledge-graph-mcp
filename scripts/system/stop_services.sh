#!/bin/bash

# This script now stops the integrated DocsGPT + Knowledge Graph system
# For backwards compatibility, we redirect to the new integrated stop script

echo "🔄 Redirecting to integrated system stop script..."
echo ""

# Check if the integrated stop script exists
if [ -f "$(dirname "$0")/stop_integrated_system.sh" ]; then
    # Run the integrated stop script
    "$(dirname "$0")/stop_integrated_system.sh"
else
    # Fallback to original behavior if integrated script doesn't exist
    echo "🛑 Stopping Simple Knowledge Graph MCP Services..."
    echo ""
    
    # Stop Neo4j container
    if docker ps --format 'table {{.Names}}' | grep -q "^neo4j-kg$"; then
        echo "📊 Stopping Neo4j container..."
        docker stop neo4j-kg
        echo "   ✅ Neo4j stopped"
    else
        echo "   ℹ️  Neo4j container is not running"
    fi
    
    # Optional: Remove Neo4j container completely
    read -p "🗑️  Do you want to remove the Neo4j container entirely? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if docker ps -a --format 'table {{.Names}}' | grep -q "^neo4j-kg$"; then
            echo "🗑️  Removing Neo4j container..."
            docker rm neo4j-kg
            echo "   ✅ Neo4j container removed"
        fi
        
        read -p "🗑️  Do you also want to remove Neo4j data volume? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🗑️  Removing Neo4j data volume..."
            docker volume rm neo4j_data neo4j_logs 2>/dev/null || echo "   ℹ️  Volumes may not exist or already removed"
            echo "   ✅ Neo4j data volume removed"
        fi
    fi
    
    # ChromaDB is file-based, so no service to stop
    echo "💾 ChromaDB data remains in ./chroma_db directory"
    
    echo ""
    echo "🎉 Services stopped successfully!"
    echo ""
    echo "💡 To start services again, run: ./start_integrated_docsgpt.sh"
fi