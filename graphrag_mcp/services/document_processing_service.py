"""
Unified Document Processing Service

This replaces the 5-layer wrapper hierarchy with a single service that:
- Handles all document processing logic
- Works with CLI, notebook, API, and MCP interfaces
- Provides clear error handling and progress tracking
- Manages resources efficiently
- Eliminates subprocess and async wrapper complexity
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime

from ..core.enhanced_document_processor import EnhancedDocumentProcessor, ProcessingResult
from ..core.graphiti_engine import GraphitiKnowledgeGraph
from ..core.config import GraphRAGConfig
from ..utils.error_handling import ProcessingError, ValidationError
from .storage_service import StorageService

logger = logging.getLogger(__name__)


@dataclass
class ProcessingProgress:
    """Progress tracking for document processing"""
    current_document: str = ""
    documents_completed: int = 0
    total_documents: int = 0
    current_stage: str = ""
    processing_start_time: float = field(default_factory=time.time)
    errors: List[str] = field(default_factory=list)
    
    @property
    def progress_percent(self) -> float:
        if self.total_documents == 0:
            return 0.0
        return (self.documents_completed / self.total_documents) * 100
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.processing_start_time


@dataclass
class ProjectProcessingResult:
    """Result of processing an entire project"""
    project_name: str
    documents_processed: List[Dict[str, Any]]
    total_entities: int
    total_citations: int
    total_relationships: int
    processing_time: float
    knowledge_graph_stats: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_count(self) -> int:
        return len([d for d in self.documents_processed if d.get("status") == "success"])
    
    @property
    def failure_count(self) -> int:
        return len([d for d in self.documents_processed if d.get("status") == "failed"])


class DocumentProcessingService:
    """
    Unified document processing service that replaces the wrapper hierarchy.
    
    This service provides a clean interface for all clients and handles:
    - Document discovery and validation
    - Sequential document processing
    - Progress tracking and error handling
    - Knowledge graph integration
    - Resource management
    """
    
    def __init__(self, config: GraphRAGConfig = None):
        """Initialize the document processing service."""
        self.config = config or GraphRAGConfig()
        self.storage_service = StorageService(self.config)
        
        # Initialize core components
        self.document_processor = EnhancedDocumentProcessor(self.config)
        self.graphiti_engine: Optional[GraphitiKnowledgeGraph] = None
        
        # Service state
        self._processing_active = False
        self._current_progress: Optional[ProcessingProgress] = None
        
        logger.info("🔧 Document Processing Service initialized")
    
    async def initialize_knowledge_graph(self, timeout_config: Dict[str, Any] = None) -> bool:
        """
        Initialize the knowledge graph connection.
        
        Args:
            timeout_config: Optional timeout configuration
            
        Returns:
            True if initialization successful
        """
        if self.graphiti_engine:
            return True
            
        try:
            timeout_config = timeout_config or {
                "base_timeout": 120,
                "max_timeout": 600,
                "disable_timeouts": False
            }
            
            self.graphiti_engine = GraphitiKnowledgeGraph(**timeout_config)
            success = await self.graphiti_engine.initialize()
            
            if success:
                logger.info("✅ Knowledge graph connection established")
            else:
                logger.error("❌ Failed to connect to knowledge graph")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Knowledge graph initialization failed: {e}")
            return False
    
    async def process_project(
        self,
        project_name: str,
        documents_path: Path,
        template: str = "academic",
        force_reprocess: bool = False,
        progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
    ) -> ProjectProcessingResult:
        """
        Process all documents in a project.
        
        Args:
            project_name: Name of the project
            documents_path: Path to documents directory
            template: Template to use for processing
            force_reprocess: Whether to reprocess existing documents
            progress_callback: Optional callback for progress updates
            
        Returns:
            Project processing result with statistics and status
        """
        if self._processing_active:
            raise ProcessingError("Processing already active")
            
        logger.info(f"🚀 Starting project processing: {project_name}")
        start_time = time.time()
        
        try:
            self._processing_active = True
            
            # Initialize knowledge graph
            if not await self.initialize_knowledge_graph():
                raise ProcessingError("Failed to initialize knowledge graph")
            
            # Discover documents
            pdf_files = self._discover_documents(documents_path)
            if not pdf_files:
                raise ValidationError(f"No PDF documents found in {documents_path}")
            
            # Initialize progress tracking
            self._current_progress = ProcessingProgress(
                total_documents=len(pdf_files),
                current_stage="Starting processing"
            )
            
            # Process each document
            documents_processed = []
            total_entities = 0
            total_citations = 0
            total_relationships = 0
            
            for i, pdf_file in enumerate(pdf_files):
                if progress_callback:
                    self._current_progress.current_document = pdf_file.name
                    self._current_progress.current_stage = f"Processing document {i+1}/{len(pdf_files)}"
                    progress_callback(self._current_progress)
                
                try:
                    # Check if already processed
                    if not force_reprocess and self.storage_service.is_document_processed(project_name, pdf_file):
                        logger.info(f"⏭️ Skipping {pdf_file.name} (already processed)")
                        doc_result = {
                            "filename": pdf_file.name,
                            "status": "skipped",
                            "title": self.storage_service.get_document_title(project_name, pdf_file) or pdf_file.stem
                        }
                    else:
                        # Process document
                        doc_result = await self._process_single_document(
                            pdf_file, project_name, template
                        )
                        
                        total_entities += doc_result.get("entities_created", 0)
                        total_citations += doc_result.get("citations_stored", 0)
                        total_relationships += doc_result.get("relationships_created", 0)
                    
                    documents_processed.append(doc_result)
                    
                except Exception as e:
                    error_msg = f"Failed to process {pdf_file.name}: {str(e)}"
                    logger.error(error_msg)
                    self._current_progress.errors.append(error_msg)
                    
                    documents_processed.append({
                        "filename": pdf_file.name,
                        "status": "failed",
                        "error": str(e)
                    })
                
                self._current_progress.documents_completed = i + 1
                if progress_callback:
                    progress_callback(self._current_progress)
            
            # Get knowledge graph statistics
            knowledge_graph_stats = {}
            try:
                if self.graphiti_engine:
                    knowledge_graph_stats = await self.graphiti_engine.get_knowledge_graph_stats()
            except Exception as e:
                logger.warning(f"Could not get knowledge graph stats: {e}")
            
            # Save project metadata
            await self.storage_service.save_project_metadata(
                project_name, template, documents_processed, knowledge_graph_stats
            )
            
            processing_time = time.time() - start_time
            
            result = ProjectProcessingResult(
                project_name=project_name,
                documents_processed=documents_processed,
                total_entities=total_entities,
                total_citations=total_citations,
                total_relationships=total_relationships,
                processing_time=processing_time,
                knowledge_graph_stats=knowledge_graph_stats,
                errors=self._current_progress.errors.copy()
            )
            
            logger.info(f"✅ Project processing completed in {processing_time:.2f}s")
            logger.info(f"   📄 Documents: {result.success_count} processed, {result.failure_count} failed")
            logger.info(f"   📊 Entities: {total_entities}, Citations: {total_citations}, Relationships: {total_relationships}")
            
            return result
            
        finally:
            self._processing_active = False
            self._current_progress = None
            
            # Clean up knowledge graph connection
            if self.graphiti_engine:
                await self.graphiti_engine.close()
                self.graphiti_engine = None
    
    async def _process_single_document(
        self, 
        pdf_file: Path, 
        project_name: str, 
        template: str
    ) -> Dict[str, Any]:
        """Process a single document and return result metadata."""
        logger.info(f"📄 Processing {pdf_file.name}")
        
        # Core document processing
        processing_result = self.document_processor.process_document(str(pdf_file))
        
        # Add to knowledge graph
        success = False
        if self.graphiti_engine:
            document_content = "\\n\\n".join(processing_result.enhanced_chunks)
            success = await self.graphiti_engine.add_document(
                document_content=document_content,
                document_id=f"{project_name}_{pdf_file.stem}",
                metadata={
                    "title": processing_result.document_title,
                    "project": project_name,
                    "template": template,
                    "filename": pdf_file.name,
                    "entities": processing_result.entities_created,
                    "processing_date": datetime.now().isoformat(),
                    **processing_result.metadata
                },
                source_description=f"{template} document from {project_name} project"
            )
        
        # Save local metadata
        await self.storage_service.save_document_metadata(
            project_name, pdf_file, processing_result
        )
        
        return {
            "filename": pdf_file.name,
            "document_id": f"{project_name}_{pdf_file.stem}",
            "status": "success" if success else "processed_local_only",
            "title": processing_result.document_title,
            "entities_created": processing_result.entities_created,
            "citations_stored": processing_result.citations_stored,
            "relationships_created": processing_result.relationships_created,
            "processing_time": processing_result.processing_time,
            "knowledge_graph_success": success
        }
    
    def _discover_documents(self, documents_path: Path) -> List[Path]:
        """Discover PDF documents in the given path."""
        if not documents_path.exists():
            raise ValidationError(f"Documents path does not exist: {documents_path}")
        
        pdf_files = list(documents_path.glob("*.pdf"))
        logger.info(f"📁 Discovered {len(pdf_files)} PDF documents")
        
        return pdf_files
    
    def get_current_progress(self) -> Optional[ProcessingProgress]:
        """Get current processing progress."""
        return self._current_progress
    
    def is_processing_active(self) -> bool:
        """Check if processing is currently active."""
        return self._processing_active
    
    async def cleanup(self):
        """Clean up resources."""
        if self.graphiti_engine:
            await self.graphiti_engine.close()
            self.graphiti_engine = None
        
        await self.storage_service.cleanup()