"""Neo4j storage manager for entities and relationships."""
from typing import List, Dict, Any
from neo4j import GraphDatabase
import config

class Neo4jStorage:
    """Handle entity and relationship storage operations in Neo4j."""
    
    def __init__(self):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
    
    def store_entities(self, entities: List[Dict[str, Any]], document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Store entities with document provenance."""
        with self.driver.session() as session:
            # Create document node
            session.run("""
                MERGE (d:Document {id: $doc_id})
                SET d.title = $title, d.path = $path, d.created = datetime()
            """, doc_id=document_info.get("id"), 
                title=document_info.get("title"), 
                path=document_info.get("path"))
            
            entities_created = 0
            relationships_created = 0
            
            for entity in entities:
                if entity.get("relationships"):
                    # This is the relationships data
                    relationships = entity.get("relationships", [])
                    for rel in relationships:
                        session.run("""
                            MATCH (source:Entity {id: $source_id})
                            MATCH (target:Entity {id: $target_id})
                            MERGE (source)-[r:RELATED {type: $rel_type}]->(target)
                            SET r.confidence = $confidence,
                                r.context = $context
                        """,
                            source_id=rel.get("source"),
                            target_id=rel.get("target"),
                            rel_type=rel.get("type", "RELATED"),
                            confidence=rel.get("confidence", 1.0),
                            context=rel.get("context", "")
                        )
                        relationships_created += 1
                else:
                    # Create entity node
                    session.run("""
                        MERGE (e:Entity {id: $entity_id})
                        SET e.name = $name, 
                            e.type = $type, 
                            e.properties = $properties,
                            e.confidence = $confidence
                        WITH e
                        MATCH (d:Document {id: $doc_id})
                        MERGE (e)-[:MENTIONED_IN]->(d)
                    """, 
                        entity_id=entity.get("id"),
                        name=entity.get("name"),
                        type=entity.get("type"),
                        properties=entity.get("properties", {}),
                        confidence=entity.get("confidence", 1.0),
                        doc_id=document_info.get("id")
                    )
                    entities_created += 1
        
        return {
            "entities_created": entities_created,
            "relationships_created": relationships_created,
            "document_id": document_info.get("id")
        }
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()