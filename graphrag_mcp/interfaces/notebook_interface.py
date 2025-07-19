"""
Direct Notebook Interface for GraphRAG MCP

This replaces the subprocess CLI calls in notebooks with direct service calls.
Provides a clean, notebook-friendly interface with:
- Progress tracking with visual feedback
- Error handling with clear messages  
- Interactive features for Jupyter environments
- No subprocess or CLI wrapper overhead
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import time

# Jupyter/IPython imports (optional)
try:
    from IPython.display import display, clear_output
    from tqdm.notebook import tqdm
    JUPYTER_AVAILABLE = True
except ImportError:
    from tqdm import tqdm
    JUPYTER_AVAILABLE = False

from ..services.document_processing_service import DocumentProcessingService, ProcessingProgress
from ..services.project_service import ProjectService
from ..core.config import GraphRAGConfig
from ..utils.error_handling import ValidationError, ProcessingError

logger = logging.getLogger(__name__)


@dataclass
class NotebookResult:
    """Result object optimized for notebook display"""
    success: bool
    message: str
    data: Dict[str, Any]
    errors: List[str]
    
    def display(self):
        """Display result in notebook with formatting"""
        if JUPYTER_AVAILABLE:
            from IPython.display import HTML, display
            
            if self.success:
                html = f"""
                <div style="padding: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; border-radius: 5px;">
                    <strong>✅ Success:</strong> {self.message}
                </div>
                """
            else:
                error_details = "\\n".join(f"• {error}" for error in self.errors) if self.errors else "No details available"
                html = f"""
                <div style="padding: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; border-radius: 5px;">
                    <strong>❌ Error:</strong> {self.message}<br>
                    <details><summary>Error Details</summary><pre>{error_details}</pre></details>
                </div>
                """
            
            display(HTML(html))
        else:
            # Fallback for non-Jupyter environments
            status = "✅ Success" if self.success else "❌ Error"
            print(f"{status}: {self.message}")
            if self.errors:
                for error in self.errors:
                    print(f"  • {error}")


class NotebookInterface:
    """
    Direct notebook interface that bypasses CLI completely.
    
    This provides a clean, notebook-friendly API for all GraphRAG operations:
    - Project management
    - Document processing  
    - Progress tracking
    - Error handling
    - Results visualization
    """
    
    def __init__(self, config: GraphRAGConfig = None):
        """Initialize notebook interface."""
        self.config = config or GraphRAGConfig()
        self.project_service = ProjectService(self.config)
        self.processing_service = DocumentProcessingService(self.config)
        
        # Notebook state
        self._current_progress_bar: Optional[tqdm] = None
        
        logger.info("📓 Notebook Interface initialized")
    
    def check_prerequisites(self) -> NotebookResult:
        """
        Check system prerequisites for GraphRAG processing.
        
        Returns:
            Result with system status and any issues found
        """
        print("🔍 Checking system prerequisites...")
        
        issues = []
        
        # Check Ollama
        try:
            import subprocess
            result = subprocess.run(
                "curl -s http://localhost:11434/api/tags", 
                shell=True, capture_output=True, timeout=10
            )
            if result.returncode != 0:
                issues.append("Ollama not accessible at http://localhost:11434")
        except Exception as e:
            issues.append(f"Failed to check Ollama: {e}")
        
        # Check Neo4j
        try:
            result = subprocess.run(
                "curl -f -s http://localhost:7474/", 
                shell=True, capture_output=True, timeout=10
            )
            if result.returncode != 0:
                issues.append("Neo4j not accessible at http://localhost:7474")
        except Exception as e:
            issues.append(f"Failed to check Neo4j: {e}")
        
        # Check Python packages
        required_packages = ["ollama", "neo4j", "chromadb", "langchain_ollama"]
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                issues.append(f"Required package not found: {package}")
        
        if issues:
            return NotebookResult(
                success=False,
                message="System prerequisites check failed",
                data={"issues": issues},
                errors=issues
            )
        else:
            return NotebookResult(
                success=True,
                message="All system prerequisites are ready",
                data={"status": "ready"},
                errors=[]
            )
    
    def create_project(
        self, 
        name: str, 
        template: str = "academic", 
        force: bool = False
    ) -> NotebookResult:
        """
        Create a new GraphRAG project.
        
        Args:
            name: Project name
            template: Template to use (academic, legal, medical, business, research)
            force: Whether to overwrite existing project
            
        Returns:
            Creation result with project details
        """
        print(f"🚀 Creating project: {name}")
        
        try:
            result = self.project_service.create_project(name, template, force)
            
            return NotebookResult(
                success=result["status"] == "success",
                message=result["message"],
                data=result,
                errors=[] if result["status"] == "success" else [result["message"]]
            )
            
        except Exception as e:
            return NotebookResult(
                success=False,
                message=f"Failed to create project: {str(e)}",
                data={},
                errors=[str(e)]
            )
    
    def add_documents(
        self, 
        project_name: str, 
        documents_path: str, 
        recursive: bool = False
    ) -> NotebookResult:
        """
        Add documents to a project.
        
        Args:
            project_name: Project name
            documents_path: Path to documents or directory
            recursive: Whether to search recursively for PDFs
            
        Returns:
            Addition result with file counts
        """
        print(f"📄 Adding documents to project: {project_name}")
        
        try:
            path = Path(documents_path)
            result = self.project_service.add_documents(project_name, path, recursive)
            
            return NotebookResult(
                success=result["status"] in ["success", "warning"],
                message=result["message"],
                data=result,
                errors=[] if result["status"] != "failed" else [result["message"]]
            )
            
        except Exception as e:
            return NotebookResult(
                success=False,
                message=f"Failed to add documents: {str(e)}",
                data={},
                errors=[str(e)]
            )
    
    def discover_documents(self, documents_path: str) -> NotebookResult:
        """
        Discover PDF documents in a directory.
        
        Args:
            documents_path: Path to search for documents
            
        Returns:
            Discovery result with document list and metadata
        """
        print(f"🔍 Scanning for PDF documents in: {documents_path}")
        
        try:
            path = Path(documents_path)
            if not path.exists():
                return NotebookResult(
                    success=False,
                    message=f"Path does not exist: {documents_path}",
                    data={},
                    errors=[f"Path not found: {documents_path}"]
                )
            
            pdf_files = list(path.glob("*.pdf"))
            
            if pdf_files:
                total_size = sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)  # MB
                
                documents_info = []
                for pdf_file in pdf_files:
                    size_mb = pdf_file.stat().st_size / (1024 * 1024)
                    documents_info.append({
                        "name": pdf_file.name,
                        "size_mb": round(size_mb, 1),
                        "path": str(pdf_file)
                    })
                
                # Estimate processing time (3 minutes per document)
                est_minutes = len(pdf_files) * 3
                
                return NotebookResult(
                    success=True,
                    message=f"Found {len(pdf_files)} PDF documents ({total_size:.1f} MB total)",
                    data={
                        "documents": documents_info,
                        "count": len(pdf_files),
                        "total_size_mb": round(total_size, 1),
                        "estimated_processing_minutes": est_minutes
                    },
                    errors=[]
                )
            else:
                return NotebookResult(
                    success=False,
                    message=f"No PDF documents found in {documents_path}",
                    data={"count": 0},
                    errors=["No PDF files found"]
                )
                
        except Exception as e:
            return NotebookResult(
                success=False,
                message=f"Failed to discover documents: {str(e)}",
                data={},
                errors=[str(e)]
            )
    
    async def process_project(
        self, 
        project_name: str, 
        documents_path: str,
        template: str = "academic",
        force_reprocess: bool = False,
        show_progress: bool = True
    ) -> NotebookResult:
        """
        Process all documents in a project with progress tracking.
        
        Args:
            project_name: Project name
            documents_path: Path to documents directory
            template: Processing template
            force_reprocess: Whether to reprocess existing documents
            show_progress: Whether to show progress bar
            
        Returns:
            Processing result with statistics
        """
        print(f"🦙 Processing project: {project_name}")
        print("📊 This will:")
        print("   1. 📄 Extract text from PDFs")
        print("   2. 📝 Create text chunks") 
        print("   3. 🧠 Extract entities with LLM")
        print("   4. 📚 Parse citations")
        print("   5. 🔗 Build relationships")
        print("   6. 💾 Store in Neo4j + ChromaDB")
        print()
        
        def progress_callback(progress: ProcessingProgress):
            """Update progress bar with current status"""
            if self._current_progress_bar and show_progress:
                self._current_progress_bar.set_description(
                    f"{progress.current_stage} - {progress.current_document}"
                )
                self._current_progress_bar.n = progress.documents_completed
                self._current_progress_bar.refresh()
        
        try:
            # Setup progress bar
            if show_progress:
                # Get document count first
                path = Path(documents_path)
                pdf_files = list(path.glob("*.pdf"))
                total_docs = len(pdf_files)
                
                self._current_progress_bar = tqdm(
                    total=total_docs,
                    desc="Initializing...",
                    unit="docs"
                )
            
            # Process project
            result = await self.processing_service.process_project(
                project_name=project_name,
                documents_path=Path(documents_path),
                template=template,
                force_reprocess=force_reprocess,
                progress_callback=progress_callback if show_progress else None
            )
            
            return NotebookResult(
                success=result.failure_count == 0,
                message=f"Processing completed: {result.success_count} succeeded, {result.failure_count} failed",
                data={
                    "project_name": result.project_name,
                    "documents_processed": result.success_count,
                    "documents_failed": result.failure_count,
                    "total_entities": result.total_entities,
                    "total_citations": result.total_citations,
                    "total_relationships": result.total_relationships,
                    "processing_time": result.processing_time,
                    "knowledge_graph_stats": result.knowledge_graph_stats
                },
                errors=result.errors
            )
            
        except Exception as e:
            return NotebookResult(
                success=False,
                message=f"Processing failed: {str(e)}",
                data={},
                errors=[str(e)]
            )
        finally:
            # Clean up progress bar
            if self._current_progress_bar:
                self._current_progress_bar.close()
                self._current_progress_bar = None
    
    def get_project_status(self, project_name: str) -> NotebookResult:
        """
        Get comprehensive project status.
        
        Args:
            project_name: Project name
            
        Returns:
            Status result with all project information
        """
        try:
            result = self.project_service.get_project_status(project_name)
            
            return NotebookResult(
                success=result["status"] == "success",
                message=f"Project status retrieved for: {project_name}",
                data=result.get("project_status", {}),
                errors=[] if result["status"] == "success" else [result.get("message", "Unknown error")]
            )
            
        except Exception as e:
            return NotebookResult(
                success=False,
                message=f"Failed to get project status: {str(e)}",
                data={},
                errors=[str(e)]
            )
    
    def list_projects(self) -> NotebookResult:
        """
        List all projects.
        
        Returns:
            List result with project information
        """
        try:
            result = self.project_service.list_projects()
            
            return NotebookResult(
                success=result["status"] == "success",
                message=f"Found {result.get('total_projects', 0)} projects",
                data=result,
                errors=[] if result["status"] == "success" else [result.get("message", "Unknown error")]
            )
            
        except Exception as e:
            return NotebookResult(
                success=False,
                message=f"Failed to list projects: {str(e)}",
                data={},
                errors=[str(e)]
            )
    
    def get_available_templates(self) -> NotebookResult:
        """
        Get available processing templates.
        
        Returns:
            Templates result with available options
        """
        try:
            templates = self.project_service.get_available_templates()
            
            template_details = {}
            for template in templates:
                info = self.project_service.get_template_info(template)
                if info["status"] == "success":
                    template_details[template] = info["template"]
            
            return NotebookResult(
                success=True,
                message=f"Found {len(templates)} available templates",
                data={
                    "templates": templates,
                    "template_details": template_details
                },
                errors=[]
            )
            
        except Exception as e:
            return NotebookResult(
                success=False,
                message=f"Failed to get templates: {str(e)}",
                data={},
                errors=[str(e)]
            )
    
    async def cleanup(self):
        """Clean up notebook interface resources."""
        await self.processing_service.cleanup()


# Convenience function for notebook users
def create_graphrag_interface(config: GraphRAGConfig = None) -> NotebookInterface:
    """
    Create a GraphRAG interface for notebook use.
    
    Args:
        config: Optional configuration
        
    Returns:
        Notebook interface ready for use
    """
    return NotebookInterface(config)