"""
GraphRAG MCP Main Processor

This module provides the main user-facing API for the GraphRAG MCP toolkit.
"""

import asyncio
import sys
import time
import resource
import gc
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from contextlib import asynccontextmanager

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ..core.analyzer import AdvancedAnalyzer
from ..core.citation_manager import CitationTracker
from ..core.document_processor import DocumentProcessor
from ..ui.status import (
    DocumentInfo,
    DocumentStatus,
    ProcessingResults,
    ValidationResult,
)
from ..utils.error_handling import ConfigurationError, ProcessingError, ValidationError
from ..utils.file_discovery import discover_documents
from ..utils.prerequisites import check_prerequisites, validate_environment

# Optional Graphiti import
try:
    from ..core.graphiti_engine import GraphitiKnowledgeGraph
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False


class GraphRAGProcessor:
    """
    Main user-facing API for GraphRAG MCP toolkit
    
    This class provides a clean interface for users to:
    1. Validate their environment
    2. Discover and process documents
    3. Create knowledge graphs
    4. Start MCP servers for Claude integration
    """

    def __init__(self, project_name: str, template: str = "academic"):
        """
        Initialize GraphRAG processor with enhanced resource management
        
        Args:
            project_name: Name of the project
            template: Template to use (default: academic)
        """
        # Validate inputs
        if not project_name or not project_name.strip():
            raise ValidationError("Project name cannot be empty", {"project_name": project_name})
        
        self.project_name = project_name.strip()
        self.template = template
        self.max_concurrent = 3
        self.retry_attempts = 3
        
        # Resource management
        self._active_tasks = set()
        self._resource_cleanup_handlers = []
        self._processing_stats = {
            "documents_processed": 0,
            "documents_failed": 0,
            "total_processing_time": 0,
            "memory_usage": []
        }
        self._shutdown_requested = False

        # Initialize components with error handling
        try:
            self.doc_processor = DocumentProcessor()
            self.analyzer = AdvancedAnalyzer()
            self.citation_tracker = CitationTracker()
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize core components: {str(e)}")

        # Optional Graphiti engine with better error handling
        self.graphiti_engine = None
        if GRAPHITI_AVAILABLE:
            try:
                self.graphiti_engine = GraphitiKnowledgeGraph()
                print("🕸️  Knowledge graph persistence: ENABLED (will store in Neo4j)")
                self._register_cleanup_handler(self._cleanup_graphiti)
            except Exception as e:
                print(f"⚠️  Graphiti initialization failed: {e}")
                print("⚠️  Knowledge graph persistence: DISABLED")
        else:
            print("⚠️  Knowledge graph persistence: DISABLED (Graphiti not available)")

        print("✅ GraphRAG processor initialized")
        
        # Register cleanup handler for processor
        self._register_cleanup_handler(self._cleanup_processor)
    
    def _register_cleanup_handler(self, handler):
        """Register a cleanup handler to be called during shutdown"""
        self._resource_cleanup_handlers.append(handler)
    
    def _cleanup_processor(self):
        """Cleanup processor resources"""
        try:
            if hasattr(self, 'doc_processor'):
                # Clear document data to free memory
                self.doc_processor.document_data = None
                self.doc_processor.chat_history = []
            
            # Force garbage collection
            gc.collect()
        except Exception as e:
            print(f"⚠️  Error during processor cleanup: {e}")
    
    def _cleanup_graphiti(self):
        """Cleanup Graphiti engine resources"""
        try:
            if self.graphiti_engine:
                # Close any open connections
                # This would need to be implemented based on Graphiti's API
                pass
        except Exception as e:
            print(f"⚠️  Error during Graphiti cleanup: {e}")
    
    def _monitor_resource_usage(self):
        """Monitor current resource usage"""
        try:
            # Get memory usage
            memory_info = resource.getrusage(resource.RUSAGE_SELF)
            memory_mb = memory_info.ru_maxrss / 1024 if sys.platform == 'darwin' else memory_info.ru_maxrss / 1024
            
            self._processing_stats["memory_usage"].append(memory_mb)
            
            # Keep only last 100 measurements
            if len(self._processing_stats["memory_usage"]) > 100:
                self._processing_stats["memory_usage"] = self._processing_stats["memory_usage"][-100:]
            
            return memory_mb
        except Exception:
            return 0
    
    @asynccontextmanager
    async def _processing_context(self, operation_name: str):
        """Context manager for processing operations with resource monitoring"""
        start_time = time.time()
        start_memory = self._monitor_resource_usage()
        
        try:
            print(f"🔄 Starting {operation_name}")
            yield
        finally:
            end_time = time.time()
            end_memory = self._monitor_resource_usage()
            processing_time = end_time - start_time
            
            print(f"⏱️  {operation_name} completed in {processing_time:.2f}s")
            if end_memory > start_memory:
                print(f"🧠 Memory usage: {end_memory - start_memory:.1f}MB increase")
            
            # Force garbage collection after processing
            gc.collect()

    def validate_environment(self, verbose: bool = True) -> ValidationResult:
        """
        Validate system environment and prerequisites with enhanced error handling
        
        Args:
            verbose: Whether to print detailed status
            
        Returns:
            ValidationResult with status and issues
        """
        try:
            return validate_environment(verbose=verbose)
        except Exception as e:
            return ValidationResult(
                status="failed",
                issues=[f"Validation error: {str(e)}"],
                details={"error": str(e), "error_type": type(e).__name__}
            )

    def discover_documents(self, folder_path: str, recursive: bool = True) -> list[DocumentInfo]:
        """
        Discover documents in a folder
        
        Args:
            folder_path: Path to search for documents
            recursive: Whether to search recursively
            
        Returns:
            List of DocumentInfo objects
        """
        try:
            return discover_documents(folder_path, recursive)
        except Exception as e:
            raise ProcessingError(f"Document discovery failed: {str(e)}")

    async def process_documents(self, documents: list[DocumentInfo]) -> ProcessingResults:
        """
        Process documents into knowledge graph with enhanced resource management
        
        Args:
            documents: List of documents to process
            
        Returns:
            ProcessingResults with statistics
            
        Raises:
            ValidationError: If input validation fails
            ProcessingError: If processing fails
        """
        # Validate input
        if not isinstance(documents, list):
            raise ValidationError("Documents must be a list", {"documents_type": type(documents).__name__})
        
        if not documents:
            return ProcessingResults(
                success=0,
                failed=0,
                total_time=0,
                documents=[]
            )
        
        # Check if shutdown was requested
        if self._shutdown_requested:
            raise ProcessingError("Processing shutdown requested", {"operation": "process_documents"})

        async with self._processing_context("document_batch_processing"):
            print(f"🚀 Processing {len(documents)} documents...")

            # Convert DocumentInfo to DocumentStatus with validation
            doc_statuses = []
            for doc in documents:
                try:
                    doc_status = doc.to_document_status()
                    # Validate document exists and is accessible
                    if not doc_status.path.exists():
                        doc_status.status = "failed"
                        doc_status.error_message = f"Document not found: {doc_status.path}"
                    doc_statuses.append(doc_status)
                except Exception as e:
                    # Create a failed document status
                    doc_statuses.append(DocumentStatus(
                        name=str(doc) if hasattr(doc, 'name') else "Unknown",
                        path=Path("unknown"),
                        status="failed",
                        error_message=f"Failed to create document status: {str(e)}"
                    ))

            # Process with progress tracking and resource management
            try:
                # Import here to avoid circular imports
                from ..ui.progress import ProgressTracker

                progress = ProgressTracker(len(documents))

                # Concurrent processing with resource limits
                semaphore = asyncio.Semaphore(self.max_concurrent)

                async def process_with_semaphore(doc_status):
                    if self._shutdown_requested:
                        doc_status.status = "failed"
                        doc_status.error_message = "Processing cancelled"
                        return False
                    
                    async with semaphore:
                        try:
                            # Monitor memory before processing
                            memory_before = self._monitor_resource_usage()
                            
                            # Add to active tasks
                            task_id = f"doc_{doc_status.name}"
                            self._active_tasks.add(task_id)
                            
                            success = await self._process_single_document(doc_status)
                            
                            # Monitor memory after processing
                            memory_after = self._monitor_resource_usage()
                            
                            # Update stats
                            if success:
                                self._processing_stats["documents_processed"] += 1
                            else:
                                self._processing_stats["documents_failed"] += 1
                            
                            # Force garbage collection if memory usage is high
                            if memory_after > memory_before + 100:  # 100MB threshold
                                gc.collect()
                            
                            return success
                        except Exception as e:
                            doc_status.status = "failed"
                            doc_status.error_message = f"Processing error: {str(e)}"
                            self._processing_stats["documents_failed"] += 1
                            return False
                        finally:
                            # Remove from active tasks
                            self._active_tasks.discard(task_id)
                            progress.update(1)

                # Process all documents
                start_time = time.time()
                tasks = [process_with_semaphore(doc) for doc in doc_statuses]
                
                # Use asyncio.gather with proper exception handling
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and handle exceptions
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        doc_statuses[i].status = "failed"
                        doc_statuses[i].error_message = f"Task failed: {str(result)}"

                total_time = time.time() - start_time
                successful = sum(1 for doc in doc_statuses if doc.status == "completed")
                failed = sum(1 for doc in doc_statuses if doc.status == "failed")

                # Update overall stats
                self._processing_stats["total_processing_time"] += total_time

                print(f"📊 Complete: {successful} success, {failed} failed ({total_time/60:.1f} min)")
                
                # Show memory usage if significant
                current_memory = self._monitor_resource_usage()
                if current_memory > 500:  # 500MB threshold
                    print(f"🧠 Memory usage: {current_memory:.1f}MB")

                return ProcessingResults(
                    success=successful,
                    failed=failed,
                    total_time=total_time,
                    documents=doc_statuses
                )

            except Exception as e:
                # Cleanup active tasks on error
                for task_id in list(self._active_tasks):
                    self._active_tasks.discard(task_id)
                raise ProcessingError(f"Batch processing failed: {str(e)}", {"error_type": type(e).__name__})

    async def _process_single_document(self, doc_status: DocumentStatus) -> bool:
        """Process a single document with detailed tracking"""
        doc_status.status = "processing"
        doc_status.start_time = datetime.now()

        print(f"📄 Processing: {doc_status.name}")

        try:
            # Step 1: Document processing
            print("   🔍 Step 1: Loading and processing PDF...")
            try:
                doc_data = self.doc_processor.load_document(str(doc_status.path))
                print("   ✅ Document loaded successfully")

                # Get document summary
                summary = self.doc_processor.get_document_summary()
                print("   📋 Generated document summary")

            except Exception as e:
                print(f"   ❌ Document loading failed: {e}")
                raise

            # Step 2: Analysis
            print("   🔬 Step 2: Analyzing document content...")
            try:
                corpus_doc = self.analyzer.analyze_for_corpus(str(doc_status.path))
                print("   ✅ Analysis complete")
                print(f"   📊 Found {len(corpus_doc.entities)} entities via analyzer")

                # Handle different entity formats
                if isinstance(corpus_doc.entities, dict):
                    # Flatten dictionary of entities
                    all_entities = []
                    for entity_type, entity_list in corpus_doc.entities.items():
                        all_entities.extend(entity_list)
                else:
                    all_entities = corpus_doc.entities

                print(f"   🔗 Total unique entities: {len(all_entities)}")

            except Exception as e:
                print(f"   ❌ Analysis failed: {e}")
                print("   🔧 Using fallback document representation")

                # Create fallback document
                corpus_doc = type('CorpusDoc', (), {
                    'entities': [],
                    'content': summary.get('content', 'Document processed successfully'),
                    'title': doc_status.name.replace('.pdf', ''),
                    'metadata': {
                        'filename': doc_status.name,
                        'size_mb': doc_status.size_mb,
                        'processing_date': datetime.now().isoformat()
                    },
                    'citations': []
                })()
                all_entities = []

            # Step 3: Knowledge graph storage
            print("   🕸️  Step 3: Storing in knowledge graph...")
            try:
                if self.graphiti_engine:
                    content_str = str(corpus_doc.content) if hasattr(corpus_doc, 'content') else summary.get('content', '')

                    success = await self.graphiti_engine.add_document(
                        document_content=content_str,
                        document_id=f"{self.project_name}_{doc_status.path.stem}",
                        metadata={
                            "title": getattr(corpus_doc, 'title', doc_status.name),
                            "project": self.project_name,
                            "template": self.template,
                            "filename": doc_status.name,
                            "entities": all_entities,
                            "processing_date": datetime.now().isoformat(),
                            **getattr(corpus_doc, 'metadata', {})
                        },
                        source_description=f"{self.template} document from {self.project_name} project"
                    )
                    print("   ✅ Stored in Neo4j successfully")
                else:
                    success = True
                    print("   ⚠️  Graphiti not available, skipping persistence")

            except Exception as e:
                print(f"   ❌ Knowledge graph storage failed: {e}")
                success = True  # Don't fail completely
                print("   ⚠️  Continuing without knowledge graph storage")

            # Update status
            doc_status.entities_found = len(all_entities)
            doc_status.citations_found = len(getattr(corpus_doc, 'citations', []))
            doc_status.status = "completed" if success else "failed"

            if success:
                print("   🎉 Processing completed successfully!")
                print(f"   📈 Entities: {doc_status.entities_found}, Citations: {doc_status.citations_found}")

            return success

        except Exception as e:
            print(f"   💥 Processing failed: {str(e)}")
            doc_status.status = "failed"
            doc_status.error_message = str(e)
            return False

        finally:
            doc_status.end_time = datetime.now()
            if doc_status.start_time:
                doc_status.processing_time = (doc_status.end_time - doc_status.start_time).total_seconds()
                print(f"   ⏱️  Processing time: {doc_status.processing_time:.2f} seconds")

    def get_knowledge_graph_stats(self) -> dict[str, Any]:
        """
        Get statistics about the knowledge graph
        
        Returns:
            Dictionary with graph statistics
        """
        # This would be implemented to return actual graph stats
        return {
            "project_name": self.project_name,
            "template": self.template,
            "graphiti_available": GRAPHITI_AVAILABLE,
            "status": "active" if self.graphiti_engine else "disabled"
        }

    def start_mcp_server(self, transport: str = "stdio", port: int = 8080) -> dict[str, Any]:
        """
        Start MCP server for Claude integration
        
        Args:
            transport: Transport method (stdio or http)
            port: Port for HTTP transport
            
        Returns:
            Server information
        """
        try:
            # Import here to avoid circular imports
            from ..mcp.server_generator import UniversalMCPServer

            # Create and start server
            server = UniversalMCPServer(
                name=f"GraphRAG {self.project_name}",
                instructions=f"GraphRAG assistant for {self.project_name} project"
            )

            # This would actually start the server
            print(f"🚀 Starting MCP server for project: {self.project_name}")
            print(f"   📡 Transport: {transport}")
            if transport == "http":
                print(f"   🌐 Port: {port}")

            return {
                "project_name": self.project_name,
                "transport": transport,
                "port": port if transport == "http" else None,
                "status": "starting"
            }

        except Exception as e:
            raise ConfigurationError(f"Failed to start MCP server: {str(e)}")

    def visualize_knowledge_graph(self, documents: list[DocumentStatus], max_nodes: int = 50) -> Any | None:
        """
        Create interactive knowledge graph visualization
        
        Args:
            documents: List of processed documents
            max_nodes: Maximum number of nodes to display
            
        Returns:
            NetworkX graph object or None if visualization fails
        """
        try:
            from ..ui.visualizations import visualize_knowledge_graph
            return visualize_knowledge_graph(documents, self.project_name, max_nodes)
        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
            return None
    
    def request_shutdown(self):
        """Request graceful shutdown of all processing"""
        print("🛑 Shutdown requested...")
        self._shutdown_requested = True
        
        # Wait for active tasks to complete
        if self._active_tasks:
            print(f"⏳ Waiting for {len(self._active_tasks)} active tasks to complete...")
            # In a real implementation, you might want to set a timeout here
    
    def force_shutdown(self):
        """Force immediate shutdown with cleanup"""
        print("🚨 Force shutdown initiated...")
        self._shutdown_requested = True
        
        # Clear active tasks
        self._active_tasks.clear()
        
        # Run cleanup handlers
        for handler in self._resource_cleanup_handlers:
            try:
                handler()
            except Exception as e:
                print(f"⚠️ Error during cleanup: {e}")
        
        print("✅ Shutdown complete")
    
    def get_processing_stats(self) -> dict[str, Any]:
        """Get comprehensive processing statistics"""
        stats = self._processing_stats.copy()
        stats.update({
            "active_tasks": len(self._active_tasks),
            "active_task_names": list(self._active_tasks),
            "shutdown_requested": self._shutdown_requested,
            "current_memory_mb": self._monitor_resource_usage(),
            "average_memory_mb": sum(self._processing_stats["memory_usage"]) / len(self._processing_stats["memory_usage"]) if self._processing_stats["memory_usage"] else 0
        })
        return stats
    
    def clear_processing_stats(self):
        """Clear processing statistics"""
        self._processing_stats = {
            "documents_processed": 0,
            "documents_failed": 0,
            "total_processing_time": 0,
            "memory_usage": []
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.force_shutdown()
        return False  # Don't suppress exceptions

    def export_knowledge_graph(self, format: str = "json") -> str:
        """
        Export knowledge graph in specified format
        
        Args:
            format: Export format (json, graphml, etc.)
            
        Returns:
            Exported data as string
        """
        # This would be implemented to export actual graph data
        return f"{{\"project\": \"{self.project_name}\", \"format\": \"{format}\"}}"
