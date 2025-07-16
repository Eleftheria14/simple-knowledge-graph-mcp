"""
Neo4j Entity Manager with Citation Provenance Tracking

Stores entities and relationships in Neo4j with full citation links
for provenance tracking and knowledge graph navigation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None

from ..utils.error_handling import ProcessingError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class EntityRecord:
    """Entity record with citation provenance"""
    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    citation_sources: List[str] = field(default_factory=list)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    document_source: Optional[str] = None
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j node properties"""
        return {
            "id": self.entity_id,
            "type": self.entity_type,
            "name": self.name,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "document_source": self.document_source or "",
            **self.properties
        }


@dataclass
class RelationshipRecord:
    """Relationship record with citation provenance"""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    citation_sources: List[str] = field(default_factory=list)
    confidence: float = 1.0
    context: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j relationship properties"""
        return {
            "type": self.relationship_type,
            "confidence": self.confidence,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            **self.properties
        }


class Neo4jEntityManager:
    """
    Neo4j-based entity storage with citation provenance tracking.
    
    Features:
    - Entity storage with citation links
    - Relationship tracking with provenance
    - Provenance queries (entity → citations → sources)
    - Knowledge graph navigation
    - Citation impact analysis
    """
    
    def __init__(self, 
                 uri: str = "bolt://localhost:7687",
                 auth: Tuple[str, str] = ("neo4j", "password"),
                 database: str = "neo4j"):
        """
        Initialize Neo4j entity manager.
        
        Args:
            uri: Neo4j connection URI
            auth: Authentication tuple (username, password)
            database: Database name
        """
        if not NEO4J_AVAILABLE:
            raise ProcessingError("Neo4j driver not available. Install with: pip install neo4j")
        
        self.uri = uri
        self.auth = auth
        self.database = database
        
        # Initialize driver
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth)
            self._verify_connection()
            self._create_constraints()
            logger.info(f"🗄️ Neo4j Entity Manager connected to {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise ProcessingError(f"Neo4j connection failed: {e}")
    
    def _verify_connection(self):
        """Verify Neo4j connection is working"""
        with self.driver.session(database=self.database) as session:
            result = session.run("RETURN 1 as test")
            if not result.single():
                raise ProcessingError("Neo4j connection verification failed")
    
    def _create_constraints(self):
        """Create necessary constraints and indexes"""
        constraints = [
            "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT citation_key_unique IF NOT EXISTS FOR (c:Citation) REQUIRE c.key IS UNIQUE",
            "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX citation_title_index IF NOT EXISTS FOR (c:Citation) ON (c.title)"
        ]
        
        with self.driver.session(database=self.database) as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.debug(f"Constraint/index creation note: {e}")
    
    def add_entity(self, 
                   entity_id: str,
                   entity_type: str,
                   name: str,
                   properties: Dict[str, Any] = None,
                   citation_sources: List[str] = None,
                   confidence: float = 1.0,
                   document_source: str = None) -> bool:
        """
        Add entity with citation provenance.
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity (author, concept, method, etc.)
            name: Human-readable name
            properties: Additional properties
            citation_sources: List of citation keys supporting this entity
            confidence: Confidence score (0.0-1.0)
            document_source: Source document path
            
        Returns:
            Success status
        """
        entity = EntityRecord(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            properties=properties or {},
            citation_sources=citation_sources or [],
            confidence=confidence,
            document_source=document_source
        )
        
        try:
            with self.driver.session(database=self.database) as session:
                # Create or update entity
                session.run("""
                    MERGE (e:Entity {id: $entity_id})
                    SET e += $properties
                    SET e.updated_at = datetime()
                """, entity_id=entity_id, properties=entity.to_neo4j_properties())
                
                # Link to citations
                for citation_key in entity.citation_sources:
                    session.run("""
                        MATCH (e:Entity {id: $entity_id})
                        MERGE (c:Citation {key: $citation_key})
                        MERGE (e)-[r:CITED_BY]->(c)
                        SET r.linked_at = datetime()
                        SET r.confidence = $confidence
                    """, entity_id=entity_id, citation_key=citation_key, confidence=confidence)
                
                logger.info(f"✅ Added entity: {entity_id} ({entity_type})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add entity {entity_id}: {e}")
            return False
    
    def add_relationship(self,
                        source_entity_id: str,
                        target_entity_id: str,
                        relationship_type: str,
                        properties: Dict[str, Any] = None,
                        citation_sources: List[str] = None,
                        confidence: float = 1.0,
                        context: str = "") -> bool:
        """
        Add relationship with citation provenance.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
            properties: Additional properties
            citation_sources: Citation keys supporting this relationship
            confidence: Confidence score
            context: Context description
            
        Returns:
            Success status
        """
        relationship = RelationshipRecord(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            properties=properties or {},
            citation_sources=citation_sources or [],
            confidence=confidence,
            context=context
        )
        
        try:
            with self.driver.session(database=self.database) as session:
                # Create relationship
                session.run(f"""
                    MATCH (s:Entity {{id: $source_id}})
                    MATCH (t:Entity {{id: $target_id}})
                    MERGE (s)-[r:{relationship_type}]->(t)
                    SET r += $properties
                    SET r.updated_at = datetime()
                """, source_id=source_entity_id, target_id=target_entity_id, 
                    properties=relationship.to_neo4j_properties())
                
                # Link relationship to citations
                for citation_key in relationship.citation_sources:
                    session.run(f"""
                        MATCH (s:Entity {{id: $source_id}})-[r:{relationship_type}]->(t:Entity {{id: $target_id}})
                        MERGE (c:Citation {{key: $citation_key}})
                        MERGE (r)-[:SUPPORTED_BY]->(c)
                    """, source_id=source_entity_id, target_id=target_entity_id, 
                        citation_key=citation_key)
                
                logger.info(f"✅ Added relationship: {source_entity_id} -[{relationship_type}]-> {target_entity_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            return False
    
    def link_entity_to_citation(self,
                               entity_id: str,
                               citation_key: str,
                               context: str = "",
                               confidence: float = 1.0) -> bool:
        """
        Link existing entity to citation.
        
        Args:
            entity_id: Entity identifier
            citation_key: Citation key
            context: Context of the citation
            confidence: Confidence score
            
        Returns:
            Success status
        """
        try:
            with self.driver.session(database=self.database) as session:
                session.run("""
                    MATCH (e:Entity {id: $entity_id})
                    MERGE (c:Citation {key: $citation_key})
                    MERGE (e)-[r:CITED_BY]->(c)
                    SET r.context = $context
                    SET r.confidence = $confidence
                    SET r.linked_at = datetime()
                """, entity_id=entity_id, citation_key=citation_key, 
                    context=context, confidence=confidence)
                
                logger.info(f"🔗 Linked entity {entity_id} to citation {citation_key}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to link entity to citation: {e}")
            return False
    
    def get_entity_provenance(self, entity_id: str) -> Dict[str, Any]:
        """
        Get full provenance chain for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Provenance information including citations and sources
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (e:Entity {id: $entity_id})
                    OPTIONAL MATCH (e)-[r:CITED_BY]->(c:Citation)
                    RETURN e, collect({
                        citation_key: c.key,
                        citation_title: c.title,
                        context: r.context,
                        confidence: r.confidence,
                        linked_at: r.linked_at
                    }) as citations
                """, entity_id=entity_id)
                
                record = result.single()
                if not record:
                    return {"error": f"Entity {entity_id} not found"}
                
                entity = record["e"]
                citations = record["citations"]
                
                return {
                    "entity_id": entity_id,
                    "entity_type": entity.get("type"),
                    "entity_name": entity.get("name"),
                    "confidence": entity.get("confidence"),
                    "created_at": entity.get("created_at"),
                    "document_source": entity.get("document_source"),
                    "citations": citations,
                    "citation_count": len([c for c in citations if c["citation_key"]])
                }
                
        except Exception as e:
            logger.error(f"Failed to get provenance for {entity_id}: {e}")
            return {"error": str(e)}
    
    def query_entities_by_citation(self, citation_key: str) -> List[Dict[str, Any]]:
        """
        Get all entities supported by a specific citation.
        
        Args:
            citation_key: Citation identifier
            
        Returns:
            List of entities with their relationships to the citation
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (c:Citation {key: $citation_key})<-[r:CITED_BY]-(e:Entity)
                    RETURN e, r
                    ORDER BY e.name
                """, citation_key=citation_key)
                
                entities = []
                for record in result:
                    entity = record["e"]
                    relationship = record["r"]
                    
                    entities.append({
                        "entity_id": entity.get("id"),
                        "entity_type": entity.get("type"),
                        "entity_name": entity.get("name"),
                        "confidence": entity.get("confidence"),
                        "citation_context": relationship.get("context"),
                        "citation_confidence": relationship.get("confidence"),
                        "linked_at": relationship.get("linked_at")
                    })
                
                return entities
                
        except Exception as e:
            logger.error(f"Failed to query entities by citation {citation_key}: {e}")
            return []
    
    def search_entities(self, 
                       query: str,
                       entity_type: str = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search entities by name or properties.
        
        Args:
            query: Search query
            entity_type: Filter by entity type
            limit: Maximum results
            
        Returns:
            List of matching entities
        """
        try:
            with self.driver.session(database=self.database) as session:
                where_clause = "WHERE e.name CONTAINS $query"
                if entity_type:
                    where_clause += " AND e.type = $entity_type"
                
                result = session.run(f"""
                    MATCH (e:Entity)
                    {where_clause}
                    RETURN e
                    ORDER BY e.confidence DESC, e.name
                    LIMIT $limit
                """, query=query, entity_type=entity_type, limit=limit)
                
                entities = []
                for record in result:
                    entity = record["e"]
                    entities.append({
                        "entity_id": entity.get("id"),
                        "entity_type": entity.get("type"),
                        "entity_name": entity.get("name"),
                        "confidence": entity.get("confidence"),
                        "document_source": entity.get("document_source"),
                        "created_at": entity.get("created_at")
                    })
                
                return entities
                
        except Exception as e:
            logger.error(f"Entity search failed: {e}")
            return []
    
    def get_entity_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all relationships for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            List of relationships
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (e:Entity {id: $entity_id})
                    MATCH (e)-[r]->(target:Entity)
                    RETURN type(r) as relationship_type, target, r
                    UNION
                    MATCH (e:Entity {id: $entity_id})
                    MATCH (source:Entity)-[r]->(e)
                    RETURN type(r) as relationship_type, source as target, r
                """, entity_id=entity_id)
                
                relationships = []
                for record in result:
                    rel_type = record["relationship_type"]
                    target = record["target"]
                    rel_props = record["r"]
                    
                    relationships.append({
                        "relationship_type": rel_type,
                        "target_entity_id": target.get("id"),
                        "target_entity_name": target.get("name"),
                        "target_entity_type": target.get("type"),
                        "confidence": rel_props.get("confidence"),
                        "context": rel_props.get("context"),
                        "created_at": rel_props.get("created_at")
                    })
                
                return relationships
                
        except Exception as e:
            logger.error(f"Failed to get relationships for {entity_id}: {e}")
            return []
    
    def get_citation_impact(self, citation_key: str) -> Dict[str, Any]:
        """
        Get impact analysis for a citation.
        
        Args:
            citation_key: Citation identifier
            
        Returns:
            Impact analysis including entity count and relationship influence
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (c:Citation {key: $citation_key})
                    OPTIONAL MATCH (c)<-[:CITED_BY]-(e:Entity)
                    OPTIONAL MATCH (c)<-[:SUPPORTED_BY]-(r)
                    RETURN 
                        count(DISTINCT e) as entity_count,
                        count(DISTINCT r) as relationship_count,
                        collect(DISTINCT e.type) as entity_types,
                        avg(e.confidence) as avg_entity_confidence
                """, citation_key=citation_key)
                
                record = result.single()
                if not record:
                    return {"error": f"Citation {citation_key} not found"}
                
                return {
                    "citation_key": citation_key,
                    "entity_count": record["entity_count"],
                    "relationship_count": record["relationship_count"],
                    "entity_types": record["entity_types"],
                    "avg_entity_confidence": record["avg_entity_confidence"],
                    "impact_score": record["entity_count"] + record["relationship_count"]
                }
                
        except Exception as e:
            logger.error(f"Failed to get citation impact: {e}")
            return {"error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Neo4j database statistics"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (e:Entity)
                    OPTIONAL MATCH (c:Citation)
                    OPTIONAL MATCH ()-[r]->()
                    RETURN 
                        count(DISTINCT e) as entity_count,
                        count(DISTINCT c) as citation_count,
                        count(DISTINCT r) as relationship_count
                """)
                
                record = result.single()
                
                # Get entity types
                type_result = session.run("""
                    MATCH (e:Entity)
                    RETURN e.type as entity_type, count(*) as count
                    ORDER BY count DESC
                """)
                
                entity_types = {}
                for record in type_result:
                    entity_types[record["entity_type"]] = record["count"]
                
                return {
                    "total_entities": record["entity_count"],
                    "total_citations": record["citation_count"],
                    "total_relationships": record["relationship_count"],
                    "entity_types": entity_types,
                    "database": self.database,
                    "connection_uri": self.uri
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
    
    def clear_database(self):
        """Clear all entities and relationships (for testing)"""
        try:
            with self.driver.session(database=self.database) as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.info("🗑️ Cleared Neo4j database")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("🔌 Neo4j connection closed")


# Factory function for easy initialization
def create_neo4j_entity_manager(uri: str = "bolt://localhost:7687",
                               username: str = "neo4j",
                               password: str = "password") -> Neo4jEntityManager:
    """Create Neo4j entity manager with default settings"""
    return Neo4jEntityManager(uri=uri, auth=(username, password))