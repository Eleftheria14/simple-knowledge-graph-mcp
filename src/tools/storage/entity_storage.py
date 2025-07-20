"""Entity storage tool for MCP knowledge graph."""
from typing import List, Dict, Any
import uuid
from fastmcp import FastMCP
from pydantic import BaseModel

from storage.neo4j import Neo4jStorage

# Data models
class EntityData(BaseModel):
    """Represents an important entity extracted from a document.
    
    Examples:
    - Person: {"id": "smith_2023", "name": "Dr. Jane Smith", "type": "person", 
              "properties": {"affiliation": "MIT", "role": "corresponding_author"}}
    - Concept: {"id": "ml_concept", "name": "machine learning", "type": "concept",
               "properties": {"domain": "AI", "definition": "algorithms that learn from data"}}
    - Technology: {"id": "transformer", "name": "Transformer Architecture", "type": "technology",
                  "properties": {"domain": "NLP", "year_introduced": "2017"}}
    """
    id: str  # Unique identifier for this entity
    name: str  # Display name of the entity
    type: str  # Category: person, concept, technology, organization, method, etc.
    properties: Dict[str, Any] = {}  # Additional attributes specific to this entity
    confidence: float = 1.0  # Confidence score 0-1 for extraction quality

class RelationshipData(BaseModel):
    """Represents a relationship between two entities.
    
    Examples:
    - Research: {"source": "smith_2023", "target": "ml_concept", "type": "researches",
                "context": "Dr. Smith's primary research focus is machine learning"}
    - Uses: {"source": "ml_concept", "target": "transformer", "type": "implemented_with",
            "context": "Modern ML systems often use transformer architectures"}
    """
    source: str  # ID of the source entity
    target: str  # ID of the target entity  
    type: str  # Relationship type: researches, uses, part_of, collaborates_with, etc.
    confidence: float = 1.0  # Confidence score 0-1 for relationship extraction
    context: str = ""  # Text snippet that supports this relationship

class DocumentInfo(BaseModel):
    """Metadata about the source document for provenance tracking.
    
    Example:
    {"title": "Attention Is All You Need", "type": "research_paper", 
     "path": "/papers/attention_paper.pdf"}
    """
    title: str  # Document title or filename
    type: str = "document"  # Document type: research_paper, book, article, etc.
    id: str = None  # Optional unique document ID (auto-generated if not provided)
    path: str = None  # Optional file path or URL

def register_entity_tools(mcp: FastMCP, neo4j_storage: Neo4jStorage):
    """Register entity storage tools with the MCP server."""
    
    @mcp.tool()
    def store_entities(
        entities: List[EntityData],
        relationships: List[RelationshipData],
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """
        Store entities and relationships in Neo4j graph database.
        
        Args:
            entities: List of entities with id, name, type, properties, confidence
            relationships: Connections between entities with source, target, type, context  
            document_info: Document metadata (title, type, optional id/path)
        
        Returns:
            Success status and counts of stored entities/relationships
        """
        try:
            # Generate document ID if not provided
            if not document_info.id:
                document_info.id = str(uuid.uuid4())
            
            # Convert Pydantic models to dicts for storage
            entities_dict = [entity.model_dump() for entity in entities]
            relationships_dict = [rel.model_dump() for rel in relationships]
            entities_dict.append({"relationships": relationships_dict})
            
            # Store in Neo4j
            result = neo4j_storage.store_entities(
                entities_dict, 
                document_info.model_dump()
            )
            
            return {
                "success": True,
                "message": f"Stored {result['entities_created']} entities and {result['relationships_created']} relationships",
                "document_id": result["document_id"],
                **result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store entities"
            }