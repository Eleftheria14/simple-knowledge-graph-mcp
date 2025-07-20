"""Literature review generation tool for MCP knowledge graph."""
from typing import Dict, Any
from datetime import datetime
from fastmcp import FastMCP

from storage.neo4j import Neo4jQuery
from storage.chroma import ChromaDBQuery
import config

def register_literature_tools(mcp: FastMCP, neo4j_query: Neo4jQuery, chromadb_query: ChromaDBQuery):
    """Register literature generation tools with the MCP server."""
    
    @mcp.tool()
    def generate_literature_review(
        topic: str,
        citation_style: str = "APA",
        max_sources: int = 20,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Generate formatted output by querying stored data.
        
        Args:
            topic: Topic to search for
            citation_style: Citation format (APA, IEEE, Nature, MLA) 
            max_sources: Maximum number of sources to include (default: 20)
            include_summary: Whether to include summary statistics (default: True)
            
        Returns:
            Structured output with organized entities, text, and citations
        """
        try:
            if citation_style not in config.CITATION_STYLES:
                citation_style = "APA"
            
            # Query knowledge graph for relevant content
            # Note: This would normally call the query_knowledge_graph tool,
            # but for modularity we'll implement the search directly here
            results = {
                "query": topic,
                "entities": [],
                "text_results": [],
                "success": True
            }
            
            # Search entities in Neo4j
            entities = neo4j_query.query_entities(topic, max_sources)
            results["entities"] = entities
            
            # Get relationships for top entities
            for entity in entities[:3]:  # Top 3 entities
                relationships = neo4j_query.get_entity_relationships(entity["id"])
                entity["relationships"] = relationships
            
            # Search text content in ChromaDB
            text_results = chromadb_query.query_similar_text(topic, max_sources)
            results["text_results"] = text_results
            
            # Get relevant citations
            citations = chromadb_query.get_citations_for_topic(topic, max_sources)
            results["citations"] = citations
            
            if not results.get("success"):
                return results
            
            # Organize results by themes
            entities = results.get("entities", [])
            text_results = results.get("text_results", [])
            citations = results.get("citations", [])
            
            # Group entities by type for organization
            entity_types = {}
            for entity in entities:
                entity_type = entity.get("type", "unknown")
                if entity_type not in entity_types:
                    entity_types[entity_type] = []
                entity_types[entity_type].append(entity)
            
            # Format literature review
            review_sections = {
                "topic": topic,
                "citation_style": citation_style,
                "entity_themes": entity_types,
                "key_concepts": [e for e in entities if e.get("type") == "concept"],
                "key_researchers": [e for e in entities if e.get("type") == "person"],
                "technologies": [e for e in entities if e.get("type") == "technology"],
                "relevant_text": text_results[:10],  # Top 10 most relevant passages
                "citations": citations[:max_sources],
                "generated_at": datetime.now().isoformat()
            }
            
            # Add summary if requested
            if include_summary:
                review_sections["summary"] = {
                    "total_entities": len(entities),
                    "total_citations": len(citations),
                    "main_themes": list(entity_types.keys()),
                    "coverage": f"Review covers {len(citations)} sources with {len(entities)} key entities"
                }
            
            return {
                "success": True,
                "literature_review": review_sections,
                "message": f"Generated literature review for '{topic}' with {len(citations)} sources"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate literature review"
            }