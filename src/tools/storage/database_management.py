"""Database management tools for MCP knowledge graph."""
from typing import Dict, Any
from datetime import datetime
from fastmcp import FastMCP

from storage.neo4j import Neo4jStorage
from storage.chroma import ChromaDBStorage

def register_management_tools(mcp: FastMCP, neo4j_storage: Neo4jStorage, chromadb_storage: ChromaDBStorage):
    """Register database management tools with the MCP server."""
    
    @mcp.tool()
    def clear_knowledge_graph() -> Dict[str, Any]:
        """
        Clear all data from both databases.
        
        WARNING: Permanently deletes all stored data. Cannot be undone.
        
        Returns:
            Confirmation of data clearing with timestamp
        """
        try:
            # Clear ChromaDB
            chromadb_storage.clear_collection()
            
            # Clear Neo4j
            neo4j_storage.clear_database()
            
            return {
                "success": True,
                "message": "Knowledge graph cleared successfully (Neo4j + ChromaDB)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to clear knowledge graph"
            }