"""
Unified Storage Service

Consolidates all storage operations into a single service layer:
- Project metadata management
- Document processing results
- Knowledge graph data coordination
- File system operations

This replaces scattered storage logic across multiple wrappers.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.config import GraphRAGConfig
from ..core.enhanced_document_processor import ProcessingResult
from ..utils.error_handling import StorageError

logger = logging.getLogger(__name__)


class StorageService:
    """
    Unified storage service for all persistence operations.
    
    Handles:
    - Project configuration and metadata
    - Document processing results
    - File system organization
    - Storage validation and cleanup
    """
    
    def __init__(self, config: GraphRAGConfig = None):
        """Initialize storage service."""
        self.config = config or GraphRAGConfig()
        
        # Default storage paths
        self.base_dir = Path.home() / ".graphrag-mcp"
        self.projects_dir = self.base_dir / "projects"
        
        # Ensure directories exist
        self.base_dir.mkdir(exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)
        
        logger.info(f"💾 Storage Service initialized: {self.projects_dir}")
    
    def get_project_dir(self, project_name: str) -> Path:
        """Get project directory path."""
        return self.projects_dir / project_name
    
    def get_project_config_path(self, project_name: str) -> Path:
        """Get project configuration file path."""
        return self.get_project_dir(project_name) / "config.json"
    
    def get_processed_dir(self, project_name: str) -> Path:
        """Get processed documents directory."""
        return self.get_project_dir(project_name) / "processed"
    
    def project_exists(self, project_name: str) -> bool:
        """Check if project exists."""
        return self.get_project_dir(project_name).exists()
    
    def create_project(self, project_name: str, template: str, force: bool = False) -> bool:
        """
        Create a new project.
        
        Args:
            project_name: Name of the project
            template: Template to use
            force: Whether to overwrite existing project
            
        Returns:
            True if project created successfully
        """
        project_dir = self.get_project_dir(project_name)
        
        if project_dir.exists() and not force:
            raise StorageError(f"Project {project_name} already exists. Use --force to overwrite.")
        
        try:
            # Create project directory structure
            project_dir.mkdir(exist_ok=True)
            (project_dir / "documents").mkdir(exist_ok=True)
            (project_dir / "processed").mkdir(exist_ok=True)
            
            # Create project configuration
            config = {
                "name": project_name,
                "template": template,
                "created_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "documents_count": 0,
                "last_processed": None,
                "documents_in_graph": 0,
                "graphiti_enabled": False
            }
            
            config_path = self.get_project_config_path(project_name)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"✅ Project created: {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create project {project_name}: {e}")
            raise StorageError(f"Failed to create project: {e}")
    
    def get_project_config(self, project_name: str) -> Dict[str, Any]:
        """Get project configuration."""
        config_path = self.get_project_config_path(project_name)
        
        if not config_path.exists():
            raise StorageError(f"Project {project_name} not found")
        
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load project config: {e}")
    
    def update_project_config(self, project_name: str, updates: Dict[str, Any]) -> None:
        """Update project configuration."""
        config = self.get_project_config(project_name)
        config.update(updates)
        config["last_modified"] = datetime.now().isoformat()
        
        config_path = self.get_project_config_path(project_name)
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to update project config: {e}")
    
    def add_documents_to_project(self, project_name: str, document_paths: List[Path]) -> List[Path]:
        """
        Add documents to project.
        
        Args:
            project_name: Project name
            document_paths: List of document paths to add
            
        Returns:
            List of successfully added document paths
        """
        if not self.project_exists(project_name):
            raise StorageError(f"Project {project_name} does not exist")
        
        project_dir = self.get_project_dir(project_name)
        docs_dir = project_dir / "documents"
        
        added_files = []
        for doc_path in document_paths:
            if not doc_path.exists():
                logger.warning(f"Document not found: {doc_path}")
                continue
                
            if doc_path.suffix.lower() != '.pdf':
                logger.warning(f"Skipping non-PDF file: {doc_path}")
                continue
            
            # Copy to project documents directory
            dest = docs_dir / doc_path.name
            try:
                import shutil
                shutil.copy2(doc_path, dest)
                added_files.append(dest)
                logger.info(f"📄 Added document: {doc_path.name}")
            except Exception as e:
                logger.error(f"Failed to copy {doc_path}: {e}")
        
        # Update project config
        if added_files:
            self.update_project_config(project_name, {
                "documents_count": len(list(docs_dir.glob("*.pdf")))
            })
        
        return added_files
    
    def is_document_processed(self, project_name: str, document_path: Path) -> bool:
        """Check if document has been processed."""
        processed_dir = self.get_processed_dir(project_name)
        output_file = processed_dir / f"{document_path.stem}.json"
        return output_file.exists()
    
    def get_document_title(self, project_name: str, document_path: Path) -> Optional[str]:
        """Get document title from stored metadata."""
        processed_dir = self.get_processed_dir(project_name)
        output_file = processed_dir / f"{document_path.stem}.json"
        
        if not output_file.exists():
            return None
        
        try:
            with open(output_file) as f:
                data = json.load(f)
                return data.get("document_title")
        except Exception:
            return None
    
    async def save_document_metadata(
        self, 
        project_name: str, 
        document_path: Path, 
        processing_result: ProcessingResult
    ) -> None:
        """Save document processing metadata."""
        processed_dir = self.get_processed_dir(project_name)
        processed_dir.mkdir(exist_ok=True)
        
        output_file = processed_dir / f"{document_path.stem}.json"
        
        # Create serializable data from ProcessingResult
        processing_data = {
            "document_title": processing_result.document_title,
            "document_path": processing_result.document_path,
            "text_chunks": processing_result.text_chunks,
            "enhanced_chunks": processing_result.enhanced_chunks,
            "entities_created": processing_result.entities_created,
            "citations_stored": processing_result.citations_stored,
            "relationships_created": processing_result.relationships_created,
            "processing_time": processing_result.processing_time,
            "metadata": processing_result.metadata,
            "saved_date": datetime.now().isoformat()
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(processing_data, f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save document metadata: {e}")
    
    async def save_project_metadata(
        self,
        project_name: str,
        template: str,
        documents_processed: List[Dict[str, Any]],
        knowledge_graph_stats: Dict[str, Any]
    ) -> None:
        """Save project processing metadata."""
        project_dir = self.get_project_dir(project_name)
        metadata_file = project_dir / "processing_metadata.json"
        
        project_metadata = {
            "project_name": project_name,
            "template": template,
            "processed_date": datetime.now().isoformat(),
            "documents_processed": documents_processed,
            "graphiti_stats": knowledge_graph_stats
        }
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(project_metadata, f, indent=2)
            
            # Update project config
            successful_docs = len([d for d in documents_processed if d.get("knowledge_graph_success", False)])
            self.update_project_config(project_name, {
                "last_processed": datetime.now().isoformat(),
                "documents_in_graph": successful_docs,
                "graphiti_enabled": successful_docs > 0
            })
            
        except Exception as e:
            raise StorageError(f"Failed to save project metadata: {e}")
    
    def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Get comprehensive project status."""
        if not self.project_exists(project_name):
            raise StorageError(f"Project {project_name} does not exist")
        
        config = self.get_project_config(project_name)
        project_dir = self.get_project_dir(project_name)
        
        # Count documents
        docs_dir = project_dir / "documents"
        pdf_count = len(list(docs_dir.glob("*.pdf"))) if docs_dir.exists() else 0
        
        # Count processed documents
        processed_dir = project_dir / "processed"
        processed_count = len(list(processed_dir.glob("*.json"))) if processed_dir.exists() else 0
        
        # Load processing metadata if available
        metadata_file = project_dir / "processing_metadata.json"
        processing_metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    processing_metadata = json.load(f)
            except Exception:
                pass
        
        return {
            "project_name": project_name,
            "template": config.get("template", "unknown"),
            "created_date": config.get("created_date"),
            "last_processed": config.get("last_processed"),
            "documents_total": pdf_count,
            "documents_processed": processed_count,
            "documents_in_graph": config.get("documents_in_graph", 0),
            "graphiti_enabled": config.get("graphiti_enabled", False),
            "processing_metadata": processing_metadata
        }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects with basic information."""
        projects = []
        
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                try:
                    config = self.get_project_config(project_dir.name)
                    projects.append({
                        "name": project_dir.name,
                        "template": config.get("template", "unknown"),
                        "created_date": config.get("created_date"),
                        "documents_count": config.get("documents_count", 0),
                        "last_processed": config.get("last_processed")
                    })
                except Exception as e:
                    logger.warning(f"Could not load project {project_dir.name}: {e}")
        
        return sorted(projects, key=lambda x: x["created_date"] or "", reverse=True)
    
    async def cleanup(self):
        """Clean up storage resources."""
        # Currently no cleanup needed for file-based storage
        pass