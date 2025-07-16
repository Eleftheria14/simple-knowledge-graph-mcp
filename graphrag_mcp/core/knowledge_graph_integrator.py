"""
Knowledge Graph Integrator

Coordinates between Neo4j Entity Manager and ChromaDB Citation Manager
to create a unified knowledge graph with full citation provenance tracking.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from .neo4j_entity_manager import Neo4jEntityManager, EntityRecord, RelationshipRecord
from .chromadb_citation_manager import ChromaDBCitationManager, CitationRecord
from ..utils.error_handling import ProcessingError, ValidationError, handle_processing_error

logger = logging.getLogger(__name__)


@dataclass
class ProvenanceInfo:
    """Complete provenance information for knowledge graph elements"""
    element_id: str
    element_type: str  # 'entity' or 'relationship'
    element_name: str
    citations: List[CitationRecord] = field(default_factory=list)
    citation_contexts: Dict[str, str] = field(default_factory=dict)
    confidence_score: float = 1.0
    creation_source: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_citation_summary(self) -> Dict[str, Any]:
        """Get summary of citation support"""
        return {
            "total_citations": len(self.citations),
            "citation_keys": [c.citation_key for c in self.citations],
            "avg_confidence": sum(c.confidence_score for c in self.citations) / len(self.citations) if self.citations else 0,
            "year_range": self._get_year_range(),
            "primary_journals": self._get_primary_journals()
        }
    
    def _get_year_range(self) -> Tuple[Optional[int], Optional[int]]:
        """Get year range of citations"""
        years = [c.year for c in self.citations if c.year]
        if not years:
            return (None, None)
        return (min(years), max(years))
    
    def _get_primary_journals(self) -> List[str]:
        """Get primary journals from citations"""
        journals = [c.journal for c in self.citations if c.journal]
        # Count occurrences and return top 3
        journal_counts = {}
        for journal in journals:
            journal_counts[journal] = journal_counts.get(journal, 0) + 1
        
        return sorted(journal_counts.keys(), key=lambda x: journal_counts[x], reverse=True)[:3]


@dataclass
class KnowledgeGraphQuery:
    """Query configuration for knowledge graph operations"""
    query_type: str  # 'entity', 'relationship', 'provenance', 'citation_impact'
    entity_ids: List[str] = field(default_factory=list)
    relationship_types: List[str] = field(default_factory=list)
    citation_keys: List[str] = field(default_factory=list)
    include_citations: bool = True
    include_provenance: bool = True
    confidence_threshold: float = 0.0
    max_results: int = 100


class KnowledgeGraphIntegrator:
    """
    Unified knowledge graph integrator that coordinates between Neo4j Entity Manager
    and ChromaDB Citation Manager to provide complete provenance tracking.
    
    Features:
    - Create entities with citation provenance
    - Link entities to citations bidirectionally
    - Track complete provenance chains
    - Unified knowledge graph queries
    - Citation impact analysis
    - Relationship creation with citation support
    """
    
    def __init__(self, 
                 neo4j_manager: Optional[Neo4jEntityManager] = None,
                 chromadb_manager: Optional[ChromaDBCitationManager] = None,
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_auth: Tuple[str, str] = ("neo4j", "password"),
                 chromadb_collection: str = "citations",
                 chromadb_persist_dir: str = "chroma_citations_db"):
        """
        Initialize Knowledge Graph Integrator.
        
        Args:
            neo4j_manager: Optional Neo4j entity manager instance
            chromadb_manager: Optional ChromaDB citation manager instance
            neo4j_uri: Neo4j connection URI
            neo4j_auth: Neo4j authentication
            chromadb_collection: ChromaDB collection name
            chromadb_persist_dir: ChromaDB persistence directory
        """
        # Initialize or use provided managers
        self.neo4j_manager = neo4j_manager or Neo4jEntityManager(
            uri=neo4j_uri, 
            auth=neo4j_auth
        )
        
        self.chromadb_manager = chromadb_manager or ChromaDBCitationManager(
            collection_name=chromadb_collection,
            persist_directory=chromadb_persist_dir
        )
        
        # Internal tracking
        self._entity_citation_links: Dict[str, List[str]] = {}
        self._citation_entity_links: Dict[str, List[str]] = {}
        
        logger.info("🔗 Knowledge Graph Integrator initialized")
        logger.info(f"   📊 Neo4j: {neo4j_uri}")
        logger.info(f"   💾 ChromaDB: {chromadb_persist_dir}")
    
    @handle_processing_error
    async def create_entity_with_provenance(self,
                                          entity_id: str,
                                          entity_type: str,
                                          name: str,
                                          properties: Dict[str, Any] = None,
                                          citations: List[Dict[str, Any]] = None,
                                          citation_contexts: Dict[str, str] = None,
                                          confidence: float = 1.0,
                                          document_source: str = None) -> bool:
        """
        Create entity in Neo4j with full citation provenance tracking.
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity (author, concept, method, etc.)
            name: Human-readable name
            properties: Additional entity properties
            citations: List of citation data supporting this entity
            citation_contexts: Context for each citation
            confidence: Confidence score (0.0-1.0)
            document_source: Source document path
            
        Returns:
            Success status
        """
        try:
            # Process citations first
            citation_keys = []
            if citations:
                for citation_data in citations:
                    citation_key = await self._add_citation_with_entity_link(
                        citation_data, 
                        entity_id, 
                        citation_contexts.get(citation_data.get("title", ""), "") if citation_contexts else ""
                    )
                    if citation_key:
                        citation_keys.append(citation_key)
            
            # Create entity in Neo4j
            success = self.neo4j_manager.add_entity(
                entity_id=entity_id,
                entity_type=entity_type,
                name=name,
                properties=properties or {},
                citation_sources=citation_keys,
                confidence=confidence,
                document_source=document_source
            )
            
            if success:
                # Update internal tracking
                self._entity_citation_links[entity_id] = citation_keys
                for citation_key in citation_keys:
                    if citation_key not in self._citation_entity_links:
                        self._citation_entity_links[citation_key] = []
                    self._citation_entity_links[citation_key].append(entity_id)
                
                logger.info(f"✅ Created entity with provenance: {entity_id}")
                logger.info(f"   🔗 Linked to {len(citation_keys)} citations")
                return True
            else:
                logger.error(f"Failed to create entity: {entity_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating entity with provenance: {e}")
            raise ProcessingError(f"Entity creation failed: {e}")
    
    @handle_processing_error
    async def link_entities_to_citations(self,
                                       entity_ids: List[str],
                                       citation_keys: List[str],
                                       contexts: Dict[str, str] = None) -> bool:
        """
        Create bidirectional links between entities and citations.
        
        Args:
            entity_ids: List of entity identifiers
            citation_keys: List of citation keys
            contexts: Context for each entity-citation pair
            
        Returns:
            Success status
        """
        try:
            success_count = 0
            total_links = len(entity_ids) * len(citation_keys)
            
            for entity_id in entity_ids:
                for citation_key in citation_keys:
                    context = contexts.get(f"{entity_id}_{citation_key}", "") if contexts else ""
                    
                    # Link in Neo4j
                    neo4j_success = self.neo4j_manager.link_entity_to_citation(
                        entity_id=entity_id,
                        citation_key=citation_key,
                        context=context
                    )
                    
                    # Link in ChromaDB
                    chromadb_success = self.chromadb_manager.link_citation_to_entity(
                        citation_key=citation_key,
                        entity_id=entity_id,
                        context=context
                    )
                    
                    if neo4j_success and chromadb_success:
                        success_count += 1
                        
                        # Update internal tracking
                        if entity_id not in self._entity_citation_links:
                            self._entity_citation_links[entity_id] = []
                        if citation_key not in self._entity_citation_links[entity_id]:
                            self._entity_citation_links[entity_id].append(citation_key)
                        
                        if citation_key not in self._citation_entity_links:
                            self._citation_entity_links[citation_key] = []
                        if entity_id not in self._citation_entity_links[citation_key]:
                            self._citation_entity_links[citation_key].append(entity_id)
            
            logger.info(f"🔗 Linked {success_count}/{total_links} entity-citation pairs")
            return success_count == total_links
            
        except Exception as e:
            logger.error(f"Error linking entities to citations: {e}")
            raise ProcessingError(f"Entity-citation linking failed: {e}")
    
    @handle_processing_error
    async def query_entity_provenance(self, entity_id: str) -> ProvenanceInfo:
        """
        Get complete provenance chain for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Complete provenance information
        """
        try:
            # Get entity information from Neo4j
            entity_provenance = self.neo4j_manager.get_entity_provenance(entity_id)
            
            if "error" in entity_provenance:
                raise ProcessingError(f"Entity not found: {entity_id}")
            
            # Get citation details from ChromaDB
            citation_records = []
            citation_contexts = {}
            
            for citation_info in entity_provenance.get("citations", []):
                citation_key = citation_info.get("citation_key")
                if citation_key:
                    citation_record = self.chromadb_manager._get_citation_by_key(citation_key)
                    if citation_record:
                        citation_records.append(citation_record)
                        citation_contexts[citation_key] = citation_info.get("context", "")
            
            # Create provenance info
            provenance = ProvenanceInfo(
                element_id=entity_id,
                element_type="entity",
                element_name=entity_provenance.get("entity_name", ""),
                citations=citation_records,
                citation_contexts=citation_contexts,
                confidence_score=entity_provenance.get("confidence", 1.0),
                creation_source=entity_provenance.get("document_source", ""),
                last_updated=datetime.now()
            )
            
            logger.info(f"📋 Retrieved provenance for entity: {entity_id}")
            logger.info(f"   📚 {len(citation_records)} citations found")
            
            return provenance
            
        except Exception as e:
            logger.error(f"Error querying entity provenance: {e}")
            raise ProcessingError(f"Provenance query failed: {e}")
    
    @handle_processing_error
    async def get_entities_by_citation(self, citation_key: str) -> List[Dict[str, Any]]:
        """
        Find all entities supported by a specific citation.
        
        Args:
            citation_key: Citation identifier
            
        Returns:
            List of entities with their relationship to the citation
        """
        try:
            # Get entities from Neo4j
            neo4j_entities = self.neo4j_manager.query_entities_by_citation(citation_key)
            
            # Get citation details from ChromaDB
            citation_record = self.chromadb_manager._get_citation_by_key(citation_key)
            
            # Enhance with ChromaDB information
            enhanced_entities = []
            for entity in neo4j_entities:
                entity_id = entity.get("entity_id")
                
                # Add citation context from ChromaDB
                chromadb_context = ""
                if citation_record and entity_id in citation_record.entity_contexts:
                    chromadb_context = citation_record.entity_contexts[entity_id]
                
                enhanced_entity = {
                    **entity,
                    "citation_key": citation_key,
                    "citation_title": citation_record.title if citation_record else "",
                    "citation_year": citation_record.year if citation_record else None,
                    "chromadb_context": chromadb_context,
                    "combined_context": f"{entity.get('citation_context', '')} {chromadb_context}".strip()
                }
                
                enhanced_entities.append(enhanced_entity)
            
            logger.info(f"📊 Found {len(enhanced_entities)} entities for citation: {citation_key}")
            return enhanced_entities
            
        except Exception as e:
            logger.error(f"Error getting entities by citation: {e}")
            raise ProcessingError(f"Entity-by-citation query failed: {e}")
    
    @handle_processing_error
    async def create_relationship_with_citations(self,
                                               source_entity_id: str,
                                               target_entity_id: str,
                                               relationship_type: str,
                                               properties: Dict[str, Any] = None,
                                               citation_keys: List[str] = None,
                                               citation_contexts: Dict[str, str] = None,
                                               confidence: float = 1.0,
                                               context: str = "") -> bool:
        """
        Create relationship between entities with citation support.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
            properties: Additional relationship properties
            citation_keys: Citation keys supporting this relationship
            citation_contexts: Context for each citation
            confidence: Confidence score
            context: General context description
            
        Returns:
            Success status
        """
        try:
            # Create relationship in Neo4j
            success = self.neo4j_manager.add_relationship(
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                relationship_type=relationship_type,
                properties=properties or {},
                citation_sources=citation_keys or [],
                confidence=confidence,
                context=context
            )
            
            if success and citation_keys:
                # Update ChromaDB citations with relationship context
                for citation_key in citation_keys:
                    citation_context = citation_contexts.get(citation_key, context) if citation_contexts else context
                    
                    # Add relationship context to citation
                    citation_record = self.chromadb_manager._get_citation_by_key(citation_key)
                    if citation_record:
                        relationship_context = f"Relationship: {source_entity_id} -[{relationship_type}]-> {target_entity_id}"
                        if citation_context:
                            relationship_context += f" ({citation_context})"
                        
                        # Add both entities to citation's linked entities
                        for entity_id in [source_entity_id, target_entity_id]:
                            if entity_id not in citation_record.linked_entities:
                                citation_record.linked_entities.append(entity_id)
                            citation_record.entity_contexts[entity_id] = relationship_context
                        
                        # Update citation in ChromaDB
                        self.chromadb_manager._update_citation_in_chromadb(citation_record)
                
                logger.info(f"✅ Created relationship with citations: {source_entity_id} -[{relationship_type}]-> {target_entity_id}")
                logger.info(f"   📚 Supported by {len(citation_keys or [])} citations")
                return True
            else:
                logger.error(f"Failed to create relationship: {source_entity_id} -[{relationship_type}]-> {target_entity_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating relationship with citations: {e}")
            raise ProcessingError(f"Relationship creation failed: {e}")
    
    @handle_processing_error
    async def query_knowledge_graph(self, query: KnowledgeGraphQuery) -> Dict[str, Any]:
        """
        Unified knowledge graph query interface.
        
        Args:
            query: Query configuration
            
        Returns:
            Query results with entities, relationships, and citations
        """
        try:
            results = {
                "query_type": query.query_type,
                "results": [],
                "metadata": {
                    "total_results": 0,
                    "query_time": datetime.now().isoformat(),
                    "confidence_threshold": query.confidence_threshold
                }
            }
            
            if query.query_type == "entity":
                results["results"] = await self._query_entities(query)
            elif query.query_type == "relationship":
                results["results"] = await self._query_relationships(query)
            elif query.query_type == "provenance":
                results["results"] = await self._query_provenance(query)
            elif query.query_type == "citation_impact":
                results["results"] = await self._query_citation_impact(query)
            else:
                raise ValidationError(f"Unsupported query type: {query.query_type}")
            
            results["metadata"]["total_results"] = len(results["results"])
            
            logger.info(f"🔍 Knowledge graph query completed: {query.query_type}")
            logger.info(f"   📊 {results['metadata']['total_results']} results found")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in knowledge graph query: {e}")
            raise ProcessingError(f"Knowledge graph query failed: {e}")
    
    async def _query_entities(self, query: KnowledgeGraphQuery) -> List[Dict[str, Any]]:
        """Query entities with optional citation information"""
        results = []
        
        if query.entity_ids:
            # Query specific entities
            for entity_id in query.entity_ids:
                entity_provenance = self.neo4j_manager.get_entity_provenance(entity_id)
                if "error" not in entity_provenance:
                    entity_result = {
                        "entity_id": entity_id,
                        "entity_type": entity_provenance.get("entity_type"),
                        "entity_name": entity_provenance.get("entity_name"),
                        "confidence": entity_provenance.get("confidence", 0)
                    }
                    
                    if query.include_citations:
                        entity_result["citations"] = entity_provenance.get("citations", [])
                    
                    if query.include_provenance:
                        provenance = await self.query_entity_provenance(entity_id)
                        entity_result["provenance"] = provenance.get_citation_summary()
                    
                    results.append(entity_result)
        else:
            # Search entities (simplified - would need more sophisticated search)
            # This would integrate with Neo4j search capabilities
            pass
        
        return results
    
    async def _query_relationships(self, query: KnowledgeGraphQuery) -> List[Dict[str, Any]]:
        """Query relationships with citation support"""
        results = []
        
        for entity_id in query.entity_ids:
            relationships = self.neo4j_manager.get_entity_relationships(entity_id)
            
            for rel in relationships:
                if not query.relationship_types or rel.get("relationship_type") in query.relationship_types:
                    if rel.get("confidence", 0) >= query.confidence_threshold:
                        results.append(rel)
        
        return results[:query.max_results]
    
    async def _query_provenance(self, query: KnowledgeGraphQuery) -> List[Dict[str, Any]]:
        """Query provenance information"""
        results = []
        
        for entity_id in query.entity_ids:
            try:
                provenance = await self.query_entity_provenance(entity_id)
                results.append({
                    "entity_id": entity_id,
                    "provenance": provenance.get_citation_summary(),
                    "citations": [c.citation_key for c in provenance.citations]
                })
            except ProcessingError:
                continue
        
        return results
    
    async def _query_citation_impact(self, query: KnowledgeGraphQuery) -> List[Dict[str, Any]]:
        """Query citation impact analysis"""
        results = []
        
        for citation_key in query.citation_keys:
            # Get impact from Neo4j
            impact = self.neo4j_manager.get_citation_impact(citation_key)
            
            # Get citation details from ChromaDB
            citation_record = self.chromadb_manager._get_citation_by_key(citation_key)
            
            if citation_record:
                results.append({
                    "citation_key": citation_key,
                    "citation_title": citation_record.title,
                    "citation_year": citation_record.year,
                    "impact": impact,
                    "usage_count": citation_record.citation_count
                })
        
        return results
    
    async def _add_citation_with_entity_link(self, 
                                           citation_data: Dict[str, Any],
                                           entity_id: str,
                                           context: str = "") -> Optional[str]:
        """Helper to add citation and link to entity"""
        try:
            citation_key = self.chromadb_manager.add_citation(
                title=citation_data.get("title", ""),
                authors=citation_data.get("authors", []),
                year=citation_data.get("year"),
                linked_entities=[entity_id],
                entity_contexts={entity_id: context},
                **{k: v for k, v in citation_data.items() if k not in ["title", "authors", "year"]}
            )
            
            return citation_key
            
        except Exception as e:
            logger.error(f"Error adding citation with entity link: {e}")
            return None
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get statistics about the integrated knowledge graph"""
        try:
            # Get Neo4j statistics
            neo4j_stats = self.neo4j_manager.get_statistics()
            
            # Get ChromaDB statistics
            chromadb_stats = self.chromadb_manager.get_citation_stats()
            
            # Calculate integration metrics
            total_entity_citation_links = len(self._entity_citation_links)
            total_citation_entity_links = len(self._citation_entity_links)
            
            return {
                "neo4j_stats": neo4j_stats,
                "chromadb_stats": chromadb_stats,
                "integration_stats": {
                    "total_entity_citation_links": total_entity_citation_links,
                    "total_citation_entity_links": total_citation_entity_links,
                    "avg_citations_per_entity": total_entity_citation_links / max(neo4j_stats.get("total_entities", 1), 1),
                    "avg_entities_per_citation": total_citation_entity_links / max(chromadb_stats.get("total_citations", 1), 1)
                },
                "system_health": {
                    "neo4j_connected": "error" not in neo4j_stats,
                    "chromadb_connected": "error" not in chromadb_stats,
                    "integration_active": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting integration statistics: {e}")
            return {"error": str(e)}
    
    @asynccontextmanager
    async def batch_operation(self):
        """Context manager for batch operations"""
        logger.info("🔄 Starting batch operation")
        try:
            yield self
        finally:
            logger.info("✅ Batch operation completed")
    
    def close(self):
        """Close all connections"""
        try:
            self.neo4j_manager.close()
            logger.info("🔌 Knowledge Graph Integrator closed")
        except Exception as e:
            logger.error(f"Error closing Knowledge Graph Integrator: {e}")


# Factory function for easy initialization
def create_knowledge_graph_integrator(
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_username: str = "neo4j",
    neo4j_password: str = "password",
    chromadb_collection: str = "citations",
    chromadb_persist_dir: str = "chroma_citations_db"
) -> KnowledgeGraphIntegrator:
    """
    Create Knowledge Graph Integrator with default settings.
    
    Args:
        neo4j_uri: Neo4j connection URI
        neo4j_username: Neo4j username
        neo4j_password: Neo4j password
        chromadb_collection: ChromaDB collection name
        chromadb_persist_dir: ChromaDB persistence directory
        
    Returns:
        Configured Knowledge Graph Integrator instance
    """
    return KnowledgeGraphIntegrator(
        neo4j_uri=neo4j_uri,
        neo4j_auth=(neo4j_username, neo4j_password),
        chromadb_collection=chromadb_collection,
        chromadb_persist_dir=chromadb_persist_dir
    )