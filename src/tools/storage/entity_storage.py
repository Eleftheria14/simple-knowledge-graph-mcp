"""Entity storage tool for MCP knowledge graph."""
from typing import List, Dict, Any
import uuid
from fastmcp import FastMCP
from pydantic import BaseModel

from storage.neo4j import Neo4jStorage
from typing import Optional
from utils.citation_quality import CitationQualityScorer

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
     "path": "/papers/attention_paper.pdf", "doi": "10.xxx/xxx"}
    """
    title: str  # Document title or filename
    type: str = "document"  # Document type: research_paper, book, article, etc.
    id: Optional[str] = None  # Optional unique document ID (auto-generated if not provided)
    path: Optional[str] = None  # Optional file path or URL
    doi: Optional[str] = None  # Digital Object Identifier for academic papers
    journal: Optional[str] = None  # Journal name for academic papers
    year: Optional[int] = None  # Publication year
    citation_preview: Optional[str] = None  # Formatted citation preview

def validate_citation_completeness(entities: List[EntityData]) -> Dict[str, Any]:
    """Validate that academic papers have complete citation information using advanced quality scoring."""
    
    # Find publication entities (citations)
    publication_entities = [e for e in entities if e.type == "publication"]
    
    if not publication_entities:
        return {
            "warning": "No publication entity found. Academic papers should include complete citation.",
            "missing_citation": True,
            "citation_quality_score": 0.0
        }
    
    # Use the advanced citation quality scorer
    scorer = CitationQualityScorer()
    validation_results = []
    
    for pub in publication_entities:
        # Convert Pydantic model to dict for scorer
        pub_dict = {
            "id": pub.id,
            "name": pub.name,
            "type": pub.type,
            "properties": pub.properties or {}
        }
        
        # Get comprehensive quality assessment
        quality_report = scorer.assess_citation_quality(pub_dict)
        
        validation_results.append({
            "entity_id": pub.id,
            "entity_name": pub.name,
            "quality_score": quality_report.overall_score / 100.0,  # Convert to 0-1 scale
            "completeness_score": quality_report.completeness_score,
            "credibility_score": quality_report.credibility_score,
            "missing_fields": quality_report.missing_fields,
            "warnings": quality_report.warnings,
            "recommendations": quality_report.recommendations,
            "citation_preview": quality_report.citation_preview
        })
    
    # Calculate overall quality metrics
    avg_quality = sum(r["quality_score"] for r in validation_results) / len(validation_results)
    
    return {
        "citation_validation": validation_results,
        "overall_quality": avg_quality,
        "citation_quality_score": avg_quality * 100,  # 0-100 scale
        "total_publications": len(publication_entities),
        "research_integrity_status": "excellent" if avg_quality >= 0.9 else "good" if avg_quality >= 0.75 else "needs_improvement"
    }

def register_entity_tools(mcp: FastMCP, neo4j_storage: Neo4jStorage):
    """Register entity storage tools with the MCP server."""
    
    @mcp.tool()
    def store_entities(
        entities: List[Dict[str, Any]],  # Accept raw dicts from Claude Desktop
        relationships: List[Dict[str, Any]],  # Accept raw dicts from Claude Desktop
        document_info: Dict[str, Any]  # Accept raw dict from Claude Desktop
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
            # Validate input data format
            if not entities:
                return {"success": False, "error": "No entities provided", "message": "Entity list is empty"}
            
            # Validate and convert raw dicts to proper format
            validated_entities = []
            for i, entity in enumerate(entities):
                if not isinstance(entity, dict):
                    return {"success": False, "error": f"Entity {i} is not a dict: {type(entity)}", "message": "Invalid entity format"}
                
                # Ensure required fields exist
                if 'id' not in entity or not entity['id']:
                    return {"success": False, "error": f"Entity {i} missing or null 'id' field: {entity}", "message": "Entity ID required"}
                
                if 'name' not in entity or not entity['name']:
                    return {"success": False, "error": f"Entity {i} missing 'name' field: {entity}", "message": "Entity name required"}
                
                # Create properly formatted entity dict
                validated_entity = {
                    'id': entity['id'],
                    'name': entity['name'],
                    'type': entity.get('type', 'unknown'),
                    'properties': entity.get('properties', {}),
                    'confidence': entity.get('confidence', 1.0)
                }
                validated_entities.append(validated_entity)
            
            # Validate relationships
            validated_relationships = []
            if relationships:
                for rel in relationships:
                    validated_rel = {
                        'source': rel.get('source', ''),
                        'target': rel.get('target', ''),
                        'type': rel.get('type', 'RELATED'),
                        'confidence': rel.get('confidence', 1.0),
                        'context': rel.get('context', '')
                    }
                    validated_relationships.append(validated_rel)
            
            # Validate document info and generate ID if needed
            validated_document = {
                'title': document_info.get('title', 'Untitled Document'),
                'type': document_info.get('type', 'document'),
                'id': document_info.get('id') or str(uuid.uuid4())
            }
            
            # Add optional fields if they exist
            for field in ['path', 'doi', 'journal', 'year', 'citation_preview']:
                if field in document_info and document_info[field] is not None:
                    validated_document[field] = document_info[field]
            
            # Validate citation completeness
            # Convert to Pydantic models for validation
            pydantic_entities = [EntityData(**entity) for entity in validated_entities]
            citation_validation = validate_citation_completeness(pydantic_entities)
            
            # Store in Neo4j
            result = neo4j_storage.store_entities(
                validated_entities,
                validated_relationships,
                validated_document
            )
            
            return {
                "success": True,
                "message": f"Stored {result['entities_created']} entities and {result['relationships_created']} relationships",
                "document_id": result["document_id"],
                "citation_quality": citation_validation,
                **result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store entities"
            }