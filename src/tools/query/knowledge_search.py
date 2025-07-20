"""Knowledge search tool for MCP knowledge graph."""
from typing import Dict, Any
from fastmcp import FastMCP

from storage.neo4j import Neo4jQuery
from storage.chroma import ChromaDBQuery

def register_search_tools(mcp: FastMCP, neo4j_query: Neo4jQuery, chromadb_query: ChromaDBQuery):
    """Register knowledge search tools with the MCP server."""
    
    @mcp.tool()
    def query_knowledge_graph(
        query: str,
        include_entities: bool = True,
        include_text: bool = True,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search Neo4j and ChromaDB for matching content.
        
        Args:
            query: Search query
            include_entities: Whether to search entities in Neo4j (default: True)
            include_text: Whether to search text content (default: True)
            limit: Maximum results per category (default: 10)
            
        Returns:
            Combined results with entities, text passages, and citations
        """
        try:
            # Get fresh collection reference for debug info
            from storage.chroma.client import get_shared_chromadb_client
            fresh_client, fresh_collection = get_shared_chromadb_client()
            
            results = {
                "query": query,
                "entities": [],
                "text_results": [],
                "success": True,
                "debug_info": {
                    "query_collection_id": fresh_collection.id,
                    "query_collection_name": fresh_collection.name,
                    "query_client_id": id(fresh_client)
                }
            }
            
            # Search entities in Neo4j
            if include_entities:
                entities = neo4j_query.query_entities(query, limit)
                results["entities"] = entities
                
                # Get relationships for top entities
                for entity in entities[:3]:  # Top 3 entities
                    relationships = neo4j_query.get_entity_relationships(entity["id"])
                    entity["relationships"] = relationships
            
            # Search text content in ChromaDB
            if include_text:
                # Debug: Show collection info at start of query
                print(f"🔍 query_knowledge_graph using collection ID: {chromadb_query.collection.id}")
                print(f"🔍 Collection name: {chromadb_query.collection.name}")
                
                text_results = chromadb_query.query_similar_text(query, limit)
                results["text_results"] = text_results
            
            # Get relevant citations
            citations = chromadb_query.get_citations_for_topic(query, limit)
            results["citations"] = citations
            
            results["message"] = f"Found {len(results['entities'])} entities, {len(results['text_results'])} text matches, {len(citations)} citations"
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to query knowledge graph"
            }