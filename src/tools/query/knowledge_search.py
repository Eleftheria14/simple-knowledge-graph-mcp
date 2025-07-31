"""Knowledge search tool for MCP knowledge graph."""
from typing import Dict, Any
from fastmcp import FastMCP

from storage.neo4j import Neo4jQuery, Neo4jStorage

def register_search_tools(mcp: FastMCP, neo4j_query: Neo4jQuery, neo4j_storage: Neo4jStorage):
    """Register knowledge search tools with the MCP server."""
    
    @mcp.tool()
    def query_knowledge_graph(
        query: str,
        include_entities: bool = True,
        include_text: bool = True,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search Neo4j for matching entities and text content.
        
        Args:
            query: Search query
            include_entities: Whether to search entities in Neo4j (default: True)
            include_text: Whether to search text content (default: True)
            limit: Maximum results per category (default: 10)
            
        Returns:
            Combined results with entities, text passages, and citations
        """
        try:
            results = {
                "query": query,
                "entities": [],
                "text_results": [],
                "success": True
            }
            
            # Search entities in Neo4j
            if include_entities:
                entities = neo4j_query.query_entities(query, limit)
                results["entities"] = entities
                
                # Get relationships for top entities
                for entity in entities[:3]:  # Top 3 entities
                    relationships = neo4j_query.get_entity_relationships(entity["id"])
                    entity["relationships"] = relationships
            
            # Search text content using vector similarity in Neo4j
            if include_text:
                text_results = neo4j_storage.search_similar_vectors(query, limit)
                results["text_results"] = text_results
            
            # Get document citations from found content
            citations = []
            document_titles = set()
            
            # Extract unique documents from results
            for text_result in results["text_results"]:
                doc_title = text_result.get("document_title")
                if doc_title and doc_title not in document_titles:
                    document_titles.add(doc_title)
                    citations.append({
                        "title": doc_title,
                        "type": text_result.get("metadata", {}).get("document_type", "document"),
                        "relevance_score": text_result.get("similarity", 0.0)
                    })
            
            results["citations"] = citations
            results["message"] = f"Found {len(results['entities'])} entities, {len(results['text_results'])} text matches, {len(citations)} citations"
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to query knowledge graph"
            }