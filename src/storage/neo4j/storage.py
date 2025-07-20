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
    
    def store_entities(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]], document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Store entities and relationships with document provenance."""
        with self.driver.session() as session:
            # Create document node - handle optional fields safely
            doc_params = {"doc_id": document_info.get("id"), "title": document_info.get("title")}
            set_clauses = ["d.title = $title", "d.created = datetime()"]
            
            # Add optional fields only if they exist and are not None
            if document_info.get("path") is not None:
                doc_params["path"] = document_info.get("path")
                set_clauses.append("d.path = $path")
            if document_info.get("type") is not None:
                doc_params["doc_type"] = document_info.get("type")
                set_clauses.append("d.type = $doc_type")
            
            set_clause = ", ".join(set_clauses)
            
            session.run(f"""
                MERGE (d:Document {{id: $doc_id}})
                SET {set_clause}
            """, **doc_params)
            
            entities_created = 0
            relationships_created = 0
            
            # Store entities first
            for entity in entities:
                # Create entity node with flattened properties
                properties = entity.get("properties", {})
                
                # Build the SET clause dynamically for flattened properties
                set_clauses = ["e.name = $name", "e.type = $type", "e.confidence = $confidence"]
                params = {
                    "entity_id": entity.get("id"),
                    "name": entity.get("name"),
                    "type": entity.get("type"),
                    "confidence": entity.get("confidence", 1.0),
                    "doc_id": document_info.get("id")
                }
                
                # Flatten properties - convert complex types to strings
                for key, value in properties.items():
                    # Sanitize property key (Neo4j property names can't have special chars)
                    safe_key = key.replace("-", "_").replace(" ", "_").replace(".", "_")
                    param_key = f"prop_{safe_key}"
                    
                    if isinstance(value, (list, dict)):
                        # Convert complex types to JSON strings
                        import json
                        params[param_key] = json.dumps(value)
                    elif isinstance(value, (str, int, float, bool)):
                        # Keep primitive types as-is
                        params[param_key] = value
                    else:
                        # Convert other types to strings
                        params[param_key] = str(value)
                    
                    set_clauses.append(f"e.{safe_key} = ${param_key}")
                
                set_clause = ", ".join(set_clauses)
                
                session.run(f"""
                    MERGE (e:Entity {{id: $entity_id}})
                    SET {set_clause}
                    WITH e
                    MATCH (d:Document {{id: $doc_id}})
                    MERGE (e)-[:MENTIONED_IN]->(d)
                """, **params)
                entities_created += 1
            
            # Store relationships after entities
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
        
        return {
            "entities_created": entities_created,
            "relationships_created": relationships_created,
            "document_id": document_info.get("id")
        }
    
    def clear_database(self):
        """Clear all data from the Neo4j database."""
        with self.driver.session() as session:
            # Delete all nodes and relationships
            session.run('MATCH (n) DETACH DELETE n')
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()