"""Neo4j query manager for entity and relationship retrieval."""
from typing import List, Dict, Any
from neo4j import GraphDatabase
import config

class Neo4jQuery:
    """Handle entity and relationship query operations in Neo4j."""
    
    def __init__(self):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
    
    def query_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query entities by name or type."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($query) 
                   OR toLower(e.type) CONTAINS toLower($query)
                OPTIONAL MATCH (e)-[:MENTIONED_IN]->(d:Document)
                RETURN e.id as id, e.name as name, e.type as type, 
                       e.properties as properties, e.confidence as confidence,
                       collect(d.title) as documents
                ORDER BY e.confidence DESC
                LIMIT $limit
            """, query=query, limit=limit)
            
            return [dict(record) for record in result]
    
    def get_entity_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get relationships for a specific entity."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity {id: $entity_id})-[r:RELATED]-(other:Entity)
                RETURN other.id as id, other.name as name, other.type as type,
                       r.type as relationship_type, r.confidence as confidence,
                       r.context as context
                ORDER BY r.confidence DESC
            """, entity_id=entity_id)
            
            return [dict(record) for record in result]
    
    def get_entities_by_document(self, document_id: str) -> Dict[str, Any]:
        """Get all entities and relationships for a specific document."""
        with self.driver.session() as session:
            # Get entities for this document via EntityExtraction nodes
            entities_result = session.run("""
                MATCH (d:Document {id: $document_id})
                MATCH (ex:EntityExtraction)-[:EXTRACTED_FROM]->(d)
                MATCH (e:ExtractedEntity)-[:EXTRACTED_IN]->(ex)
                RETURN e.id as id, e.name as name, e.type as type, 
                       e.properties as properties, e.confidence as confidence
                ORDER BY e.confidence DESC
            """, document_id=document_id)
            
            entities = [dict(record) for record in entities_result]
            
            # Get relationships between entities in this document
            relationships_result = session.run("""
                MATCH (d:Document {id: $document_id})
                MATCH (ex:EntityExtraction)-[:EXTRACTED_FROM]->(d)
                MATCH (r:ExtractedRelationship)-[:EXTRACTED_IN]->(ex)
                RETURN r.source as source_id, r.source as source_name,
                       r.target as target_id, r.target as target_name,
                       r.type as relationship_type, r.confidence as confidence,
                       r.context as context
                ORDER BY r.confidence DESC
            """, document_id=document_id)
            
            relationships = [dict(record) for record in relationships_result]
            
            return {
                "entities": entities,
                "relationships": relationships,
                "document_id": document_id
            }
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()