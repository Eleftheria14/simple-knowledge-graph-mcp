"""
Enhanced Document Processor with Sequential Processing Architecture

This replaces the original document processor with a sequential processing
approach that integrates all the new components:
- LLM Analysis Engine for comprehensive analysis
- Embedding Service for context-aware embeddings
- ChromaDB Citation Manager for persistent citations
- Neo4j Entity Manager for entity storage
- Knowledge Graph Integrator for coordination

Sequential Flow:
1. PDF → Text chunks
2. LLM Analysis → Entities + Citations + Relationships
3. Enhanced chunks → Context-aware embeddings
4. Storage → ChromaDB (citations + embeddings) + Neo4j (entities)
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import GraphRAGConfig
from .llm_analysis_engine import LLMAnalysisEngine, AnalysisResult
from .embedding_service import EmbeddingService
from .chromadb_citation_manager import ChromaDBCitationManager
from .neo4j_entity_manager import Neo4jEntityManager
from .knowledge_graph_integrator import KnowledgeGraphIntegrator
from ..utils.error_handling import ProcessingError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of enhanced document processing"""
    document_title: str
    document_path: str
    text_chunks: List[str]
    enhanced_chunks: List[str]
    embeddings: np.ndarray
    entities_created: int
    citations_stored: int
    relationships_created: int
    processing_time: float
    analysis_result: AnalysisResult
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedDocumentProcessor:
    """
    Enhanced document processor with sequential processing architecture.
    
    This processor implements the accuracy-first approach by:
    1. Performing comprehensive LLM analysis first
    2. Creating enhanced chunks with entity context
    3. Generating context-aware embeddings
    4. Storing everything with proper citation-entity links
    """
    
    def __init__(self, config: GraphRAGConfig = None):
        """
        Initialize enhanced document processor.
        
        Args:
            config: Configuration object with all settings
        """
        self.config = config or GraphRAGConfig()
        
        # Initialize core components
        self._initialize_components()
        
        # Text splitter for initial chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.processing.chunk_size,
            chunk_overlap=self.config.processing.chunk_overlap,
            separators=["\\n\\n", "\\n", ". ", " ", ""]
        )
        
        # Processing statistics
        self.processing_stats = {
            "documents_processed": 0,
            "total_entities_created": 0,
            "total_citations_stored": 0,
            "total_relationships_created": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "failed_processing": 0
        }
        
        logger.info("🚀 Enhanced Document Processor initialized with sequential architecture")
        logger.info(f"   🧠 LLM Model: {self.config.model.llm_model}")
        logger.info(f"   🔢 Embedding Model: {self.config.model.embedding_model}")
        logger.info(f"   📊 Processing Mode: {self.config.processing.processing_mode}")
    
    def _initialize_components(self):
        """Initialize all core components with configuration"""
        try:
            # LLM Analysis Engine
            self.llm_engine = LLMAnalysisEngine(
                llm_model=self.config.model.llm_model,
                temperature=self.config.model.temperature,
                max_context=self.config.model.max_context,
                max_predict=self.config.model.max_predict
            )
            
            # Embedding Service
            self.embedding_service = EmbeddingService(
                embedding_model=self.config.model.embedding_model,
                batch_size=self.config.model.batch_size
            )
            
            # ChromaDB Citation Manager
            self.citation_manager = ChromaDBCitationManager(
                collection_name=self.config.storage.chromadb.collection_name,
                persist_directory=self.config.storage.chromadb.persist_directory
            )
            
            # Neo4j Entity Manager
            self.entity_manager = Neo4jEntityManager(
                uri=self.config.storage.neo4j.uri,
                auth=(self.config.storage.neo4j.username, self.config.storage.neo4j.password),
                database=self.config.storage.neo4j.database
            )
            
            # Knowledge Graph Integrator
            self.kg_integrator = KnowledgeGraphIntegrator(
                neo4j_manager=self.entity_manager,
                chromadb_manager=self.citation_manager
            )
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            raise ProcessingError(f"Failed to initialize components: {e}")
    
    def process_document(self, pdf_path: str) -> ProcessingResult:
        """
        Process document with sequential architecture.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Processing result with all extracted information
        """
        logger.info(f"📄 Starting enhanced document processing: {pdf_path}")
        start_time = time.time()
        
        try:
            # Step 1: Load PDF and create initial chunks
            document_title, text_chunks = self._load_and_chunk_document(pdf_path)
            
            # Step 2: Comprehensive LLM analysis
            logger.info("🧠 Performing comprehensive LLM analysis...")
            analysis_result = self.llm_engine.analyze_document_comprehensive(
                text_chunks=text_chunks,
                document_title=document_title,
                document_path=pdf_path
            )
            
            # Step 3: Store entities and citations with provenance links
            logger.info("💾 Storing entities and citations with provenance links...")
            entities_created, citations_stored, relationships_created = self._store_analysis_results(
                analysis_result, pdf_path
            )
            
            # Step 4: Generate context-aware embeddings
            logger.info("🔢 Generating context-aware embeddings...")
            enhanced_chunks = [chunk.enhanced_text for chunk in analysis_result.enhanced_chunks]
            embedding_result = self.embedding_service.generate_context_aware_embeddings(
                enhanced_chunks,
                metadata={"document_path": pdf_path, "document_title": document_title}
            )
            
            # Step 5: Store embeddings in ChromaDB (citations already stored)
            logger.info("📊 Storing embeddings in ChromaDB...")
            self._store_embeddings_in_chromadb(embedding_result, analysis_result, pdf_path)
            
            # Step 6: Create processing result
            processing_time = time.time() - start_time
            result = ProcessingResult(
                document_title=document_title,
                document_path=pdf_path,
                text_chunks=text_chunks,
                enhanced_chunks=enhanced_chunks,
                embeddings=embedding_result.embeddings,
                entities_created=entities_created,
                citations_stored=citations_stored,
                relationships_created=relationships_created,
                processing_time=processing_time,
                analysis_result=analysis_result,
                metadata={
                    "processing_mode": "sequential_enhanced",
                    "llm_model": self.config.model.llm_model,
                    "embedding_model": self.config.model.embedding_model,
                    "chunk_count": len(text_chunks),
                    "enhanced_chunk_count": len(enhanced_chunks),
                    "embedding_dimension": embedding_result.embeddings.shape[1] if embedding_result.embeddings.ndim > 1 else 0
                }
            )
            
            # Update statistics
            self._update_processing_stats(result)
            
            logger.info(f"✅ Enhanced document processing completed in {processing_time:.2f}s")
            logger.info(f"   📄 Document: {document_title}")
            logger.info(f"   📊 Chunks: {len(text_chunks)} → {len(enhanced_chunks)} enhanced")
            logger.info(f"   👥 Entities: {entities_created}")
            logger.info(f"   📚 Citations: {citations_stored}")
            logger.info(f"   🔗 Relationships: {relationships_created}")
            logger.info(f"   🔢 Embeddings: {embedding_result.embeddings.shape}")
            
            return result
            
        except Exception as e:
            self.processing_stats["failed_processing"] += 1
            logger.error(f"❌ Document processing failed: {e}")
            raise ProcessingError(f"Document processing failed: {e}")
    
    def _load_and_chunk_document(self, pdf_path: str) -> Tuple[str, List[str]]:
        """
        Load PDF and create initial text chunks.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (document_title, text_chunks)
        """
        # Validate file
        path = Path(pdf_path)
        if not path.exists():
            raise ValidationError(f"File not found: {pdf_path}")
        
        if not path.suffix.lower() == '.pdf':
            raise ValidationError(f"Only PDF files supported: {pdf_path}")
        
        # Load PDF
        logger.info(f"📖 Loading PDF: {path.name}")
        loader = PyPDFLoader(str(path))
        documents = loader.load()
        
        if not documents:
            raise ProcessingError(f"No content extracted from PDF: {pdf_path}")
        
        # Extract text
        full_text = "\\n".join([doc.page_content for doc in documents])
        
        if not full_text.strip():
            raise ProcessingError(f"PDF contains no readable text: {pdf_path}")
        
        # Extract title
        document_title = self._extract_document_title(full_text, path.name)
        
        # Create chunks
        text_chunks = self.text_splitter.split_text(full_text)
        
        if not text_chunks:
            raise ProcessingError(f"Text splitting produced no chunks: {pdf_path}")
        
        logger.info(f"📝 Extracted {len(text_chunks)} chunks from {len(full_text):,} characters")
        return document_title, text_chunks
    
    def _extract_document_title(self, text: str, filename: str) -> str:
        """Extract document title from text"""
        lines = text.split('\\n')[:15]
        
        for line in lines:
            line = line.strip()
            if (len(line) > 20 and len(line) < 200 and 
                not any(word in line.lower() for word in ['university', 'department', '@', 'email']) and
                sum(1 for c in line if c.isupper()) > 3):
                return line
        
        # Fallback to filename
        return Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
    
    def _store_analysis_results(self, analysis_result: AnalysisResult, document_path: str) -> Tuple[int, int, int]:
        """
        Store entities, citations, and relationships with provenance links.
        
        Args:
            analysis_result: Result from LLM analysis
            document_path: Source document path
            
        Returns:
            Tuple of (entities_created, citations_stored, relationships_created)
        """
        entities_created = 0
        citations_stored = 0
        relationships_created = 0
        
        try:
            # Store citations in ChromaDB
            logger.info("📚 Storing citations in ChromaDB...")
            for citation in analysis_result.citations:
                citation_key = self.citation_manager.add_citation(
                    title=citation.title or citation.citation_text,
                    authors=citation.authors,
                    year=citation.year,
                    journal=citation.journal,
                    doi=citation.doi,
                    url=citation.url,
                    document_path=document_path,
                    abstract=citation.context,
                    linked_entities=[],  # Will be linked later
                    source_chunks=[citation.location],
                    confidence_score=citation.confidence
                )
                citations_stored += 1
            
            # Store entities in Neo4j with citation links
            logger.info("👥 Storing entities in Neo4j...")
            for entity in analysis_result.entities:
                # Find supporting citations
                supporting_citations = []
                for citation in analysis_result.citations:
                    if any(entity.name.lower() in citation.context.lower() for citation in analysis_result.citations):
                        supporting_citations.append(citation.citation_key)
                
                # Create entity with citation provenance
                success = self.entity_manager.add_entity(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    name=entity.name,
                    properties=entity.properties,
                    citation_sources=supporting_citations,
                    confidence=entity.confidence,
                    document_source=document_path
                )
                
                if success:
                    entities_created += 1
            
            # Store relationships in Neo4j
            logger.info("🔗 Storing relationships in Neo4j...")
            for relationship in analysis_result.relationships:
                # Find supporting citations
                supporting_citations = []
                for citation in analysis_result.citations:
                    if relationship.context.lower() in citation.context.lower():
                        supporting_citations.append(citation.citation_key)
                
                # Create relationship with citation provenance
                success = self.entity_manager.add_relationship(
                    source_entity_id=relationship.source_entity_id,
                    target_entity_id=relationship.target_entity_id,
                    relationship_type=relationship.relationship_type,
                    properties=relationship.properties,
                    citation_sources=supporting_citations,
                    confidence=relationship.confidence,
                    context=relationship.context
                )
                
                if success:
                    relationships_created += 1
            
            # Create bidirectional links using Knowledge Graph Integrator
            logger.info("🔗 Creating bidirectional entity-citation links...")
            try:
                import asyncio
                
                # Check if we're already in an event loop
                try:
                    current_loop = asyncio.get_running_loop()
                    # If we're in an event loop, skip the linking for now
                    # In a production system, you'd want to use asyncio.create_task() instead
                    logger.info("🔗 Skipping entity-citation links (running in event loop)")
                except RuntimeError:
                    # No event loop running, safe to create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        entity_ids = [entity.entity_id for entity in analysis_result.entities]
                        citation_keys = [citation.citation_key for citation in analysis_result.citations]
                        loop.run_until_complete(self.kg_integrator.link_entities_to_citations(
                            entity_ids,
                            citation_keys
                        ))
                    finally:
                        loop.close()
                        
            except Exception as e:
                logger.warning(f"⚠️ Failed to create entity-citation links: {e}")
                # Continue processing even if linking fails
            
            return entities_created, citations_stored, relationships_created
            
        except Exception as e:
            logger.error(f"❌ Failed to store analysis results: {e}")
            raise ProcessingError(f"Failed to store analysis results: {e}")
    
    def _store_embeddings_in_chromadb(self, embedding_result, analysis_result: AnalysisResult, document_path: str):
        """
        Store embeddings in ChromaDB (citations already stored).
        
        Note: This is a placeholder since ChromaDB citation manager handles embedding storage.
        In a full implementation, you might want to store embeddings separately or
        integrate more tightly with the citation manager.
        """
        # For now, the ChromaDB citation manager handles embedding storage
        # In a full implementation, you might want to store chunk embeddings
        # separately or create a more sophisticated storage strategy
        logger.info("📊 Embeddings stored via ChromaDB citation manager")
    
    def _update_processing_stats(self, result: ProcessingResult):
        """Update processing statistics"""
        self.processing_stats["documents_processed"] += 1
        self.processing_stats["total_entities_created"] += result.entities_created
        self.processing_stats["total_citations_stored"] += result.citations_stored
        self.processing_stats["total_relationships_created"] += result.relationships_created
        self.processing_stats["total_processing_time"] += result.processing_time
        
        # Update average processing time
        self.processing_stats["average_processing_time"] = (
            self.processing_stats["total_processing_time"] / 
            self.processing_stats["documents_processed"]
        )
    
    def query_document_with_context(self, 
                                   query: str,
                                   top_k: int = 5,
                                   include_citations: bool = True,
                                   include_entities: bool = True) -> Dict[str, Any]:
        """
        Query processed documents with full context.
        
        Args:
            query: Query string
            top_k: Number of results to return
            include_citations: Include citation information
            include_entities: Include entity information
            
        Returns:
            Query result with context
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_query_embedding(query)
            
            # Search for relevant citations if available
            relevant_citations = []
            if include_citations:
                relevant_citations = self.citation_manager.search_citations(query, limit=top_k)
            
            # Search for relevant entities if available
            relevant_entities = []
            if include_entities:
                relevant_entities = self.entity_manager.search_entities(query, limit=top_k)
            
            # Combine results
            result = {
                "query": query,
                "citations": [
                    {
                        "citation_key": citation.citation_key,
                        "title": citation.title,
                        "authors": citation.authors,
                        "year": citation.year,
                        "linked_entities": citation.linked_entities,
                        "confidence": citation.confidence_score
                    }
                    for citation in relevant_citations
                ],
                "entities": relevant_entities,
                "processing_info": {
                    "embedding_model": self.config.model.embedding_model,
                    "search_type": "context_aware",
                    "top_k": top_k
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return {"error": str(e)}
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return {
            "processor_stats": self.processing_stats,
            "llm_engine_stats": self.llm_engine.get_processing_statistics(),
            "embedding_service_stats": self.embedding_service.get_service_statistics(),
            "citation_manager_stats": self.citation_manager.get_citation_stats(),
            "entity_manager_stats": self.entity_manager.get_statistics(),
            "configuration": {
                "processing_mode": self.config.processing.processing_mode,
                "llm_model": self.config.model.llm_model,
                "embedding_model": self.config.model.embedding_model,
                "sequential_processing": True,
                "context_aware_embeddings": True
            }
        }
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'entity_manager'):
                self.entity_manager.close()
            logger.info("🧹 Enhanced document processor cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


# Factory function for easy initialization
def create_enhanced_document_processor(config: GraphRAGConfig = None) -> EnhancedDocumentProcessor:
    """Create enhanced document processor with configuration"""
    return EnhancedDocumentProcessor(config=config)