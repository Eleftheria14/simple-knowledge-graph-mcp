"""
Project Management Service

Handles all project-related operations:
- Project creation and configuration
- Document management within projects
- Project status and metadata
- Template management

This consolidates project management logic from CLI and other interfaces.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .storage_service import StorageService
from ..core.config import GraphRAGConfig
from ..utils.error_handling import ValidationError, StorageError

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Unified project management service.
    
    Provides high-level project operations for all interfaces:
    - CLI commands
    - Jupyter notebooks
    - API endpoints
    - MCP servers
    """
    
    def __init__(self, config: GraphRAGConfig = None):
        """Initialize project service."""
        self.config = config or GraphRAGConfig()
        self.storage_service = StorageService(self.config)
        
        logger.info("📁 Project Service initialized")
    
    def create_project(
        self,
        name: str,
        template: str = "academic",
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            template: Template to use
            force: Whether to overwrite existing project
            
        Returns:
            Project creation result with status and details
        """
        if not name or not name.strip():
            raise ValidationError("Project name cannot be empty")
        
        # Validate project name
        if not name.replace("-", "").replace("_", "").isalnum():
            raise ValidationError("Project name must contain only letters, numbers, hyphens, and underscores")
        
        # Validate template
        available_templates = self.get_available_templates()
        if template not in available_templates:
            raise ValidationError(f"Unknown template: {template}. Available: {', '.join(available_templates)}")
        
        logger.info(f"🚀 Creating project: {name} with template: {template}")
        
        try:
            success = self.storage_service.create_project(name, template, force)
            
            if success:
                project_dir = self.storage_service.get_project_dir(name)
                return {
                    "status": "success",
                    "project_name": name,
                    "template": template,
                    "project_path": str(project_dir),
                    "message": f"Project '{name}' created successfully"
                }
            else:
                return {
                    "status": "failed",
                    "message": "Project creation failed"
                }
                
        except Exception as e:
            logger.error(f"❌ Project creation failed: {e}")
            return {
                "status": "failed", 
                "message": str(e)
            }
    
    def add_documents(
        self,
        project_name: str,
        documents_path: Path,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Add documents to a project.
        
        Args:
            project_name: Project name
            documents_path: Path to documents or directory
            recursive: Whether to search recursively
            
        Returns:
            Document addition result with counts and status
        """
        if not self.storage_service.project_exists(project_name):
            raise ValidationError(f"Project '{project_name}' does not exist")
        
        if not documents_path.exists():
            raise ValidationError(f"Documents path does not exist: {documents_path}")
        
        # Discover documents
        document_paths = []
        if documents_path.is_file() and documents_path.suffix.lower() == '.pdf':
            document_paths = [documents_path]
        elif documents_path.is_dir():
            if recursive:
                document_paths = list(documents_path.rglob("*.pdf"))
            else:
                document_paths = list(documents_path.glob("*.pdf"))
        
        if not document_paths:
            return {
                "status": "warning",
                "message": f"No PDF documents found in {documents_path}",
                "documents_added": 0,
                "documents_found": 0
            }
        
        logger.info(f"📄 Adding {len(document_paths)} documents to project: {project_name}")
        
        try:
            added_files = self.storage_service.add_documents_to_project(project_name, document_paths)
            
            return {
                "status": "success",
                "message": f"Added {len(added_files)} documents to project '{project_name}'",
                "documents_added": len(added_files),
                "documents_found": len(document_paths),
                "added_files": [f.name for f in added_files]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add documents: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """
        Get comprehensive project status.
        
        Args:
            project_name: Project name
            
        Returns:
            Project status with all relevant information
        """
        if not self.storage_service.project_exists(project_name):
            raise ValidationError(f"Project '{project_name}' does not exist")
        
        try:
            status = self.storage_service.get_project_status(project_name)
            
            # Add processing status indicators
            if status["documents_total"] == 0:
                status["processing_status"] = "no_documents"
                status["next_step"] = "Add documents with: graphrag-mcp add-documents"
            elif status["documents_processed"] == 0:
                status["processing_status"] = "ready_to_process"
                status["next_step"] = "Process documents with: graphrag-mcp process"
            elif status["documents_processed"] < status["documents_total"]:
                status["processing_status"] = "partially_processed"
                status["next_step"] = "Complete processing with: graphrag-mcp process --force"
            else:
                status["processing_status"] = "fully_processed"
                status["next_step"] = "Start MCP server with: graphrag-mcp serve"
            
            return {
                "status": "success",
                "project_status": status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get project status: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    def list_projects(self) -> Dict[str, Any]:
        """
        List all projects.
        
        Returns:
            List of projects with basic information
        """
        try:
            projects = self.storage_service.list_projects()
            
            return {
                "status": "success",
                "projects": projects,
                "total_projects": len(projects)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to list projects: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    def delete_project(self, project_name: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Delete a project.
        
        Args:
            project_name: Project name
            confirm: Whether deletion is confirmed
            
        Returns:
            Deletion result
        """
        if not confirm:
            return {
                "status": "confirmation_required",
                "message": f"Are you sure you want to delete project '{project_name}'? This action cannot be undone."
            }
        
        if not self.storage_service.project_exists(project_name):
            raise ValidationError(f"Project '{project_name}' does not exist")
        
        try:
            import shutil
            project_dir = self.storage_service.get_project_dir(project_name)
            shutil.rmtree(project_dir)
            
            logger.info(f"🗑️ Project deleted: {project_name}")
            
            return {
                "status": "success",
                "message": f"Project '{project_name}' deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to delete project: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available templates.
        
        Returns:
            List of template names
        """
        # For now, return hardcoded templates
        # In the future, this could scan a templates directory
        return ["academic", "legal", "medical", "business", "research"]
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get information about a specific template.
        
        Args:
            template_name: Template name
            
        Returns:
            Template information
        """
        templates_info = {
            "academic": {
                "name": "academic",
                "description": "Template for academic research and literature review",
                "features": ["Citation management", "Entity extraction", "Research connections"],
                "domains": ["Scientific research", "Literature review", "Academic writing"]
            },
            "legal": {
                "name": "legal",
                "description": "Template for legal document analysis",
                "features": ["Case law extraction", "Legal entity recognition", "Citation tracking"],
                "domains": ["Legal research", "Case analysis", "Contract review"]
            },
            "medical": {
                "name": "medical",
                "description": "Template for medical and healthcare research",
                "features": ["Medical entity extraction", "Drug interaction analysis", "Clinical data"],
                "domains": ["Medical research", "Healthcare", "Clinical studies"]
            },
            "business": {
                "name": "business",
                "description": "Template for business document analysis",
                "features": ["Financial entity extraction", "Business relationship mapping", "Market analysis"],
                "domains": ["Business analysis", "Financial research", "Market intelligence"]
            },
            "research": {
                "name": "research",
                "description": "General research template for various domains",
                "features": ["Flexible entity extraction", "General relationship mapping", "Research synthesis"],
                "domains": ["General research", "Cross-domain analysis", "Knowledge synthesis"]
            }
        }
        
        if template_name not in templates_info:
            raise ValidationError(f"Unknown template: {template_name}")
        
        return {
            "status": "success",
            "template": templates_info[template_name]
        }