"""
Simplified CLI Interface

This replaces the complex CLI wrapper hierarchy with a thin interface
that directly calls the service layer. No more nested async wrappers
or subprocess complexity.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ..services.document_processing_service import DocumentProcessingService, ProcessingProgress
from ..services.project_service import ProjectService
from ..core.config import GraphRAGConfig
from ..utils.error_handling import ValidationError, ProcessingError

logger = logging.getLogger(__name__)


class CLIInterface:
    """
    Simplified CLI interface that wraps the service layer.
    
    This replaces the complex CLI command implementations with thin
    wrappers around the service layer, eliminating the wrapper hierarchy.
    """
    
    def __init__(self, config: GraphRAGConfig = None):
        """Initialize CLI interface."""
        self.config = config or GraphRAGConfig()
        self.console = Console()
        
        # Initialize services
        self.project_service = ProjectService(self.config)
        self.processing_service = DocumentProcessingService(self.config)
        
        logger.info("🖥️ CLI Interface initialized")
    
    def create_project(
        self,
        name: str,
        template: str = "academic",
        force: bool = False
    ) -> bool:
        """
        Create a new project.
        
        Args:
            name: Project name
            template: Template to use
            force: Whether to overwrite existing project
            
        Returns:
            True if successful
        """
        self.console.print(f"🚀 Creating new assistant: [bold blue]{name}[/bold blue]")
        
        try:
            result = self.project_service.create_project(name, template, force)
            
            if result["status"] == "success":
                self.console.print(f"✅ {result['message']}")
                self.console.print(f"📁 Project location: {result['project_path']}")
                self.console.print(f"🎓 Template: {result['template']}")
                return True
            else:
                self.console.print(f"❌ {result['message']}", style="red")
                return False
                
        except Exception as e:
            self.console.print(f"❌ Project creation failed: {str(e)}", style="red")
            return False
    
    def add_documents(
        self,
        project_name: str,
        documents_path: str,
        recursive: bool = False
    ) -> bool:
        """
        Add documents to a project.
        
        Args:
            project_name: Project name
            documents_path: Path to documents
            recursive: Whether to search recursively
            
        Returns:
            True if successful
        """
        self.console.print(f"📥 Adding documents to project: [bold blue]{project_name}[/bold blue]")
        
        try:
            path = Path(documents_path)
            result = self.project_service.add_documents(project_name, path, recursive)
            
            if result["status"] in ["success", "warning"]:
                self.console.print(f"✅ {result['message']}")
                
                if result.get("added_files"):
                    self.console.print("📋 Added documents:")
                    for filename in result["added_files"]:
                        self.console.print(f"  📄 {filename}")
                
                return True
            else:
                self.console.print(f"❌ {result['message']}", style="red")
                return False
                
        except Exception as e:
            self.console.print(f"❌ Failed to add documents: {str(e)}", style="red")
            return False
    
    async def process_project(
        self,
        project_name: str,
        force: bool = False,
        graphiti_only: bool = False
    ) -> bool:
        """
        Process documents in a project.
        
        Args:
            project_name: Project name
            force: Whether to reprocess existing documents
            graphiti_only: Only populate Graphiti, skip local JSON
            
        Returns:
            True if successful
        """
        self.console.print(f"⚙️ Processing project: [bold blue]{project_name}[/bold blue]")
        
        try:
            # Get project configuration
            status_result = self.project_service.get_project_status(project_name)
            if status_result["status"] != "success":
                self.console.print(f"❌ Project not found: {project_name}", style="red")
                return False
            
            project_status = status_result["project_status"]
            template = project_status["template"]
            
            # Get project directory and documents
            project_dir = self.project_service.storage_service.get_project_dir(project_name)
            docs_dir = project_dir / "documents"
            
            if not docs_dir.exists():
                self.console.print("❌ No documents directory found. Add documents first.", style="red")
                return False
            
            pdf_files = list(docs_dir.glob("*.pdf"))
            if not pdf_files:
                self.console.print("❌ No PDF documents found. Add documents first.", style="red")
                return False
            
            self.console.print(f"📋 Template: {template}")
            self.console.print(f"📁 Documents: {len(pdf_files)} PDF files")
            self.console.print("🧠 Knowledge Graph: Persistent Graphiti/Neo4j")
            
            # Progress tracking
            progress_data = {}
            
            def progress_callback(progress: ProcessingProgress):
                """Update progress display"""
                if "task" not in progress_data:
                    return
                
                task = progress_data["task"]
                progress_data["progress"].update(
                    task,
                    description=f"{progress.current_stage} - {progress.current_document}",
                    completed=progress.documents_completed
                )
            
            # Start processing with progress display
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
            ) as progress:
                
                progress_data["progress"] = progress
                progress_data["task"] = progress.add_task(
                    "Processing documents...",
                    total=len(pdf_files)
                )
                
                # Process project
                result = await self.processing_service.process_project(
                    project_name=project_name,
                    documents_path=docs_dir,
                    template=template,
                    force_reprocess=force,
                    progress_callback=progress_callback
                )
                
                if result.failure_count == 0:
                    self.console.print()
                    self.console.print(Panel.fit(
                        f"[green]🎉 Processing Complete![/green]\\n\\n"
                        f"📄 Documents: {result.success_count} processed\\n"
                        f"👥 Entities: {result.total_entities}\\n"
                        f"📚 Citations: {result.total_citations}\\n"
                        f"🔗 Relationships: {result.total_relationships}\\n"
                        f"🧠 Knowledge Graph: Populated in Neo4j\\n"
                        f"⏱️ Time: {result.processing_time:.2f}s\\n\\n"
                        f"[dim]Next step:[/dim]\\n"
                        f"  Start MCP server: [code]graphrag-mcp serve {project_name}[/code]",
                        title="✅ Success",
                        border_style="green"
                    ))
                    return True
                else:
                    self.console.print()
                    self.console.print(Panel.fit(
                        f"[yellow]⚠️ Processing Completed with Issues[/yellow]\\n\\n"
                        f"📄 Successful: {result.success_count}\\n"
                        f"❌ Failed: {result.failure_count}\\n"
                        f"👥 Entities: {result.total_entities}\\n"
                        f"📚 Citations: {result.total_citations}\\n\\n"
                        f"[dim]Check errors above for details[/dim]",
                        title="⚠️ Partial Success",
                        border_style="yellow"
                    ))
                    return result.success_count > 0
                
        except Exception as e:
            self.console.print(f"❌ Processing failed: {str(e)}", style="red")
            logger.error(f"Processing failed: {e}")
            return False
    
    def get_project_status(self, project_name: str) -> bool:
        """
        Get project status.
        
        Args:
            project_name: Project name
            
        Returns:
            True if successful
        """
        try:
            result = self.project_service.get_project_status(project_name)
            
            if result["status"] == "success":
                status = result["project_status"]
                
                self.console.print(f"📊 Project Status: [bold blue]{project_name}[/bold blue]")
                self.console.print(f"📁 Template: {status['template']}")
                self.console.print(f"📄 Documents: {status['documents_processed']}/{status['documents_total']} processed")
                self.console.print(f"🧠 Knowledge Graph: {status['documents_in_graph']} documents")
                self.console.print(f"🔧 Graphiti: {'Enabled' if status['graphiti_enabled'] else 'Disabled'}")
                self.console.print(f"📅 Created: {status.get('created_date', 'Unknown')}")
                self.console.print(f"📅 Last Processed: {status.get('last_processed', 'Never')}")
                self.console.print(f"🔄 Status: {status['processing_status']}")
                self.console.print(f"💡 Next Step: {status['next_step']}")
                
                return True
            else:
                self.console.print(f"❌ {result['message']}", style="red")
                return False
                
        except Exception as e:
            self.console.print(f"❌ Failed to get status: {str(e)}", style="red")
            return False
    
    def list_projects(self) -> bool:
        """
        List all projects.
        
        Returns:
            True if successful
        """
        try:
            result = self.project_service.list_projects()
            
            if result["status"] == "success":
                projects = result["projects"]
                
                if projects:
                    self.console.print(f"📋 Found {len(projects)} projects:")
                    self.console.print()
                    
                    for project in projects:
                        self.console.print(f"  📁 [bold]{project['name']}[/bold]")
                        self.console.print(f"     🎓 Template: {project['template']}")
                        self.console.print(f"     📄 Documents: {project['documents_count']}")
                        self.console.print(f"     📅 Created: {project.get('created_date', 'Unknown')}")
                        if project.get('last_processed'):
                            self.console.print(f"     ⚙️ Last Processed: {project['last_processed']}")
                        self.console.print()
                else:
                    self.console.print("📋 No projects found")
                    self.console.print("💡 Create a project with: graphrag-mcp create <name>")
                
                return True
            else:
                self.console.print(f"❌ {result['message']}", style="red")
                return False
                
        except Exception as e:
            self.console.print(f"❌ Failed to list projects: {str(e)}", style="red")
            return False
    
    def list_templates(self) -> bool:
        """
        List available templates.
        
        Returns:
            True if successful
        """
        try:
            templates = self.project_service.get_available_templates()
            
            self.console.print("📋 Available templates:")
            self.console.print()
            
            for template in templates:
                try:
                    info_result = self.project_service.get_template_info(template)
                    if info_result["status"] == "success":
                        info = info_result["template"]
                        self.console.print(f"  🎓 [bold]{info['name']}[/bold]")
                        self.console.print(f"     📝 {info['description']}")
                        self.console.print(f"     🔧 Features: {', '.join(info['features'])}")
                        self.console.print(f"     🎯 Domains: {', '.join(info['domains'])}")
                        self.console.print()
                except Exception:
                    self.console.print(f"  🎓 [bold]{template}[/bold]")
                    self.console.print(f"     📝 Template for {template} domain")
                    self.console.print()
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Failed to list templates: {str(e)}", style="red")
            return False
    
    async def cleanup(self):
        """Clean up CLI interface resources."""
        await self.processing_service.cleanup()