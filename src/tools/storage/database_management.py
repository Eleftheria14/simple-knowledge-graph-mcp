"""Database management tools for MCP knowledge graph."""
from typing import Dict, Any
from datetime import datetime
from fastmcp import FastMCP

from storage.neo4j import Neo4jStorage

def register_management_tools(mcp: FastMCP, neo4j_storage: Neo4jStorage):
    """Register database management tools with the MCP server."""
    
    @mcp.tool()
    def clear_knowledge_graph() -> Dict[str, Any]:
        """
        Clear all data from Neo4j database.
        
        WARNING: Permanently deletes all stored data. Cannot be undone.
        
        Returns:
            Confirmation of data clearing with timestamp
        """
        try:
            # Clear all Neo4j data
            with neo4j_storage.driver.session() as session:
                # Delete all nodes and relationships
                session.run("MATCH (n) DETACH DELETE n")
                
                # Get count to verify clearing
                result = session.run("MATCH (n) RETURN count(n) as count")
                remaining_nodes = result.single()["count"]
            
            return {
                "success": True,
                "message": f"Knowledge graph cleared successfully. {remaining_nodes} nodes remaining.",
                "timestamp": datetime.now().isoformat(),
                "nodes_remaining": remaining_nodes
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to clear knowledge graph"
            }