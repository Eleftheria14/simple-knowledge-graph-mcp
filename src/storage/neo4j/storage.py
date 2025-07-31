"""Neo4j storage manager for entities, relationships, and vector storage."""
from typing import List, Dict, Any
from neo4j import GraphDatabase
import config
from storage.embedding.service import EmbeddingService

class Neo4jStorage:
    """Handle entity, relationship, and vector storage operations in Neo4j."""
    
    def __init__(self):
        """Initialize Neo4j connection and embedding service."""
        self.driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )
        self.embedding_service = EmbeddingService()
    
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
    
    def store_text_vector(self, content: str, vector_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store text content as vector in Neo4j."""
        try:
            # Generate embedding
            embedding = self.embedding_service.generate_embedding(content)
            
            with self.driver.session() as session:
                # Store as TextVector node with embedding
                # Flatten metadata to primitive types only
                flattened_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        flattened_metadata[key] = value
                    else:
                        flattened_metadata[key] = str(value)
                
                # Build dynamic SET clause for metadata
                metadata_sets = []
                for key in flattened_metadata.keys():
                    metadata_sets.append(f"tv.{key} = $metadata_{key}")
                metadata_set_clause = ", ".join(metadata_sets) if metadata_sets else ""
                
                query = f"""
                    MERGE (tv:TextVector {{id: $vector_id}})
                    SET tv.content = $content,
                        tv.embedding = $embedding,
                        tv.stored_at = $stored_at
                    {', ' + metadata_set_clause if metadata_set_clause else ''}
                    WITH tv
                    MATCH (d:Document {{id: $document_id}})
                    MERGE (tv)-[:FROM_DOCUMENT]->(d)
                """
                
                # Prepare parameters
                params = {
                    'vector_id': vector_id,
                    'content': content,
                    'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                    'stored_at': metadata.get('stored_at', ''),
                    'document_id': metadata.get('document_id', '')
                }
                
                # Add flattened metadata parameters
                for key, value in flattened_metadata.items():
                    params[f'metadata_{key}'] = value
                
                session.run(query, **params)
                
                return {
                    "success": True,
                    "vector_id": vector_id,
                    "embedding_dimension": len(embedding)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_similar_vectors(self, query_text: str, limit: int = 10, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity."""
        try:
            # Generate embedding for query  
            query_embedding = self.embedding_service.generate_embedding(query_text)
            
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (tv:TextVector)
                    WITH tv, 
                         gds.similarity.cosine(tv.embedding, $query_embedding) AS similarity
                    WHERE similarity >= $min_score
                    RETURN tv.id as vector_id,
                           tv.content as content,
                           tv.document_title as document_title,
                           tv.vector_type as vector_type,
                           tv.metadata as metadata,
                           similarity
                    ORDER BY similarity DESC
                    LIMIT $limit
                """,
                    query_embedding=query_embedding.tolist(),
                    min_score=min_score,
                    limit=limit
                )
                
                return [
                    {
                        "vector_id": record["vector_id"],
                        "content": record["content"],
                        "document_title": record["document_title"],
                        "vector_type": record["vector_type"],
                        "metadata": record["metadata"],
                        "similarity": record["similarity"]
                    }
                    for record in result
                ]
                
        except Exception as e:
            return []
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()