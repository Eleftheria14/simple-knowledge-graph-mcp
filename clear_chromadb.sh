#!/bin/bash

# Clear ChromaDB Script
# Removes all persistent ChromaDB databases to start fresh

echo "🧹 Clearing All ChromaDB Databases"
echo "=================================="

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

echo ""
echo "🎯 Database Status:"
echo "=================="

# Check what's left
if find . -name "chroma*.sqlite3" -o -name "*chroma*" -type d 2>/dev/null | head -1 > /dev/null; then
    echo "📋 Remaining ChromaDB files:"
    find . -name "chroma*.sqlite3" -o -name "*chroma*" -type d 2>/dev/null | while read file; do
        echo "   📄 $file"
    done
    echo ""
    echo "💡 Some files may be in use. Stop Jupyter and try again if needed."
else
    echo "✅ All ChromaDB databases successfully cleared!"
fi

echo ""
echo "🔄 What happens next:"
echo "   • Tutorial paper counts will start from 0"
echo "   • Knowledge graphs will build fresh"
echo "   • No interference from previous runs"
echo "   • Clean learning experience"

echo ""
echo "🚀 Ready to run tutorials with fresh databases!"