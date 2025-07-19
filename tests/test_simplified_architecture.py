"""
Integration Tests for Simplified 3-Layer Architecture

Tests the new architecture that eliminates the wrapper hierarchy:
- Interface Layer tests (notebook and CLI)
- Service Layer tests (unified business logic)
- Storage Layer tests (consolidated persistence)
- End-to-end workflow tests
- Error handling and recovery tests
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import simplified architecture components
from graphrag_mcp.services.document_processing_service import DocumentProcessingService, ProcessingProgress
from graphrag_mcp.services.project_service import ProjectService
from graphrag_mcp.services.storage_service import StorageService
from graphrag_mcp.interfaces.notebook_interface import NotebookInterface
from graphrag_mcp.interfaces.cli_interface import CLIInterface
from graphrag_mcp.core.config import GraphRAGConfig
from graphrag_mcp.utils.enhanced_error_handling import (
    ValidationError, ProcessingError, StorageError, ErrorHandler
)


class TestStorageService:
    """Test the consolidated storage layer"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def storage_service(self, temp_dir):
        """Create storage service with temporary directory"""
        config = GraphRAGConfig()
        service = StorageService(config)
        # Override paths to use temp directory
        service.base_dir = temp_dir
        service.projects_dir = temp_dir / "projects"
        service.projects_dir.mkdir(exist_ok=True)
        return service
    
    def test_project_creation(self, storage_service):
        """Test project creation and configuration"""
        # Create project
        success = storage_service.create_project("test-project", "academic", force=False)
        assert success
        
        # Verify project exists
        assert storage_service.project_exists("test-project")
        
        # Verify project structure
        project_dir = storage_service.get_project_dir("test-project")
        assert project_dir.exists()
        assert (project_dir / "documents").exists()
        assert (project_dir / "processed").exists()
        
        # Verify configuration
        config = storage_service.get_project_config("test-project")
        assert config["name"] == "test-project"
        assert config["template"] == "academic"
        assert config["documents_count"] == 0
    
    def test_project_creation_duplicate(self, storage_service):
        """Test duplicate project creation handling"""
        # Create initial project
        storage_service.create_project("test-project", "academic")
        
        # Try to create duplicate without force
        with pytest.raises(StorageError):
            storage_service.create_project("test-project", "academic", force=False)
        
        # Create duplicate with force should succeed
        success = storage_service.create_project("test-project", "legal", force=True)
        assert success
        
        # Verify template was updated
        config = storage_service.get_project_config("test-project")
        assert config["template"] == "legal"
    
    def test_document_addition(self, storage_service, temp_dir):
        """Test adding documents to project"""
        # Create project
        storage_service.create_project("test-project", "academic")
        
        # Create test PDF files
        test_docs_dir = temp_dir / "test_docs"
        test_docs_dir.mkdir()
        
        pdf1 = test_docs_dir / "document1.pdf"
        pdf2 = test_docs_dir / "document2.pdf"
        pdf1.write_text("fake pdf content 1")
        pdf2.write_text("fake pdf content 2")
        
        # Add documents
        added_files = storage_service.add_documents_to_project(
            "test-project", [pdf1, pdf2]
        )
        
        assert len(added_files) == 2
        assert all(f.exists() for f in added_files)
        
        # Verify project config updated
        config = storage_service.get_project_config("test-project")
        assert config["documents_count"] == 2
    
    def test_project_status(self, storage_service):
        """Test comprehensive project status"""
        # Create project
        storage_service.create_project("test-project", "academic")
        
        # Get status
        status = storage_service.get_project_status("test-project")
        
        assert status["project_name"] == "test-project"
        assert status["template"] == "academic"
        assert status["documents_total"] == 0
        assert status["documents_processed"] == 0
        assert status["documents_in_graph"] == 0
        assert not status["graphiti_enabled"]
    
    def test_list_projects(self, storage_service):
        """Test project listing"""
        # Create multiple projects
        storage_service.create_project("project1", "academic")
        storage_service.create_project("project2", "legal")
        
        # List projects
        projects = storage_service.list_projects()
        
        assert len(projects) == 2
        project_names = [p["name"] for p in projects]
        assert "project1" in project_names
        assert "project2" in project_names


class TestProjectService:
    """Test the project management service"""
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def project_service(self, temp_dir):
        config = GraphRAGConfig()
        service = ProjectService(config)
        # Override storage paths
        service.storage_service.base_dir = temp_dir
        service.storage_service.projects_dir = temp_dir / "projects"
        service.storage_service.projects_dir.mkdir(exist_ok=True)
        return service
    
    def test_create_project_validation(self, project_service):
        """Test project creation validation"""
        # Test empty name
        result = project_service.create_project("")
        assert result["status"] == "failed"
        assert "empty" in result["message"].lower()
        
        # Test invalid characters
        result = project_service.create_project("invalid@name!")
        assert result["status"] == "failed"
        assert "letters" in result["message"].lower()
        
        # Test invalid template
        result = project_service.create_project("valid-name", template="invalid")
        assert result["status"] == "failed"
        assert "template" in result["message"].lower()
    
    def test_create_project_success(self, project_service):
        """Test successful project creation"""
        result = project_service.create_project("test-project", "academic")
        
        assert result["status"] == "success"
        assert result["project_name"] == "test-project"
        assert result["template"] == "academic"
        assert "project_path" in result
    
    def test_add_documents_validation(self, project_service, temp_dir):
        """Test document addition validation"""
        # Test non-existent project
        result = project_service.add_documents("nonexistent", temp_dir)
        assert result["status"] == "failed"
        assert "does not exist" in result["message"]
        
        # Create project
        project_service.create_project("test-project", "academic")
        
        # Test non-existent path
        result = project_service.add_documents("test-project", Path("/nonexistent"))
        assert result["status"] == "failed"
        assert "does not exist" in result["message"]
    
    def test_get_available_templates(self, project_service):
        """Test template listing"""
        templates = project_service.get_available_templates()
        
        assert isinstance(templates, list)
        assert "academic" in templates
        assert "legal" in templates
        assert len(templates) > 0
    
    def test_get_template_info(self, project_service):
        """Test template information retrieval"""
        result = project_service.get_template_info("academic")
        
        assert result["status"] == "success"
        template = result["template"]
        assert template["name"] == "academic"
        assert "description" in template
        assert "features" in template
        assert "domains" in template


class TestDocumentProcessingService:
    """Test the unified document processing service"""
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def processing_service(self, temp_dir):
        config = GraphRAGConfig()
        service = DocumentProcessingService(config)
        # Override storage paths
        service.storage_service.base_dir = temp_dir
        service.storage_service.projects_dir = temp_dir / "projects"
        service.storage_service.projects_dir.mkdir(exist_ok=True)
        return service
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_initialization(self, processing_service):
        """Test knowledge graph connection initialization"""
        # Mock the graphiti engine to avoid real Neo4j dependency
        with patch('graphrag_mcp.services.document_processing_service.GraphitiKnowledgeGraph') as mock_graphiti:
            mock_instance = AsyncMock()
            mock_instance.initialize.return_value = True
            mock_graphiti.return_value = mock_instance
            
            success = await processing_service.initialize_knowledge_graph()
            assert success
            assert processing_service.graphiti_engine is not None
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_initialization_failure(self, processing_service):
        """Test knowledge graph connection failure handling"""
        with patch('graphrag_mcp.services.document_processing_service.GraphitiKnowledgeGraph') as mock_graphiti:
            mock_instance = AsyncMock()
            mock_instance.initialize.return_value = False
            mock_graphiti.return_value = mock_instance
            
            success = await processing_service.initialize_knowledge_graph()
            assert not success
    
    def test_discover_documents(self, processing_service, temp_dir):
        """Test document discovery"""
        # Create test documents
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()
        
        pdf1 = docs_dir / "doc1.pdf"
        pdf2 = docs_dir / "doc2.pdf"
        txt_file = docs_dir / "doc3.txt"  # Should be ignored
        
        pdf1.write_text("pdf content 1")
        pdf2.write_text("pdf content 2")
        txt_file.write_text("text content")
        
        # Discover documents
        pdf_files = processing_service._discover_documents(docs_dir)
        
        assert len(pdf_files) == 2
        assert all(f.suffix == ".pdf" for f in pdf_files)
        
    def test_discover_documents_empty(self, processing_service, temp_dir):
        """Test document discovery with empty directory"""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        pdf_files = processing_service._discover_documents(empty_dir)
        assert len(pdf_files) == 0
    
    def test_discover_documents_nonexistent(self, processing_service, temp_dir):
        """Test document discovery with non-existent directory"""
        nonexistent_dir = temp_dir / "nonexistent"
        
        with pytest.raises(ValidationError):
            processing_service._discover_documents(nonexistent_dir)
    
    def test_processing_state_management(self, processing_service):
        """Test processing state tracking"""
        assert not processing_service.is_processing_active()
        assert processing_service.get_current_progress() is None
        
        # Simulate active processing
        processing_service._processing_active = True
        processing_service._current_progress = ProcessingProgress(
            total_documents=5,
            current_stage="Testing"
        )
        
        assert processing_service.is_processing_active()
        progress = processing_service.get_current_progress()
        assert progress is not None
        assert progress.total_documents == 5


class TestNotebookInterface:
    """Test the direct notebook interface"""
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def notebook_interface(self, temp_dir):
        config = GraphRAGConfig()
        interface = NotebookInterface(config)
        # Override storage paths
        interface.project_service.storage_service.base_dir = temp_dir
        interface.project_service.storage_service.projects_dir = temp_dir / "projects"
        interface.project_service.storage_service.projects_dir.mkdir(exist_ok=True)
        return interface
    
    @patch('subprocess.run')
    def test_check_prerequisites_success(self, mock_subprocess, notebook_interface):
        """Test successful prerequisite check"""
        # Mock successful service checks
        mock_subprocess.return_value.returncode = 0
        
        result = notebook_interface.check_prerequisites()
        
        assert result.success
        assert "ready" in result.message.lower()
        assert len(result.errors) == 0
    
    @patch('subprocess.run')
    def test_check_prerequisites_failure(self, mock_subprocess, notebook_interface):
        """Test failed prerequisite check"""
        # Mock failed service checks
        mock_subprocess.return_value.returncode = 1
        
        result = notebook_interface.check_prerequisites()
        
        assert not result.success
        assert len(result.errors) > 0
    
    def test_create_project_notebook(self, notebook_interface):
        """Test project creation through notebook interface"""
        result = notebook_interface.create_project("test-project", "academic")
        
        assert result.success
        assert result.data["project_name"] == "test-project"
    
    def test_discover_documents_notebook(self, notebook_interface, temp_dir):
        """Test document discovery through notebook interface"""
        # Create test documents
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()
        
        pdf1 = docs_dir / "doc1.pdf"
        pdf1.write_bytes(b"fake pdf content")
        
        result = notebook_interface.discover_documents(str(docs_dir))
        
        assert result.success
        assert result.data["count"] == 1
        assert "estimated_processing_minutes" in result.data
    
    def test_discover_documents_empty_notebook(self, notebook_interface, temp_dir):
        """Test document discovery with empty directory"""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        result = notebook_interface.discover_documents(str(empty_dir))
        
        assert not result.success
        assert result.data["count"] == 0


class TestCLIInterface:
    """Test the simplified CLI interface"""
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cli_interface(self, temp_dir):
        config = GraphRAGConfig()
        interface = CLIInterface(config)
        # Override storage paths
        interface.project_service.storage_service.base_dir = temp_dir
        interface.project_service.storage_service.projects_dir = temp_dir / "projects"
        interface.project_service.storage_service.projects_dir.mkdir(exist_ok=True)
        return interface
    
    def test_create_project_cli(self, cli_interface):
        """Test project creation through CLI interface"""
        success = cli_interface.create_project("test-project", "academic")
        assert success
    
    def test_create_project_cli_failure(self, cli_interface):
        """Test project creation failure through CLI interface"""
        # Invalid template should fail
        success = cli_interface.create_project("test-project", "invalid-template")
        assert not success
    
    def test_list_projects_cli(self, cli_interface):
        """Test project listing through CLI interface"""
        # Create test projects
        cli_interface.create_project("project1", "academic")
        cli_interface.create_project("project2", "legal")
        
        success = cli_interface.list_projects()
        assert success
    
    def test_list_templates_cli(self, cli_interface):
        """Test template listing through CLI interface"""
        success = cli_interface.list_templates()
        assert success


class TestErrorHandling:
    """Test enhanced error handling across the architecture"""
    
    def test_error_context_creation(self):
        """Test error context creation and serialization"""
        from graphrag_mcp.utils.enhanced_error_handling import ValidationError, ErrorCategory, ErrorSeverity
        
        error = ValidationError(
            "Test validation error",
            details="Detailed error information",
            suggestions=["Fix input", "Try again"]
        )
        
        assert error.context.category == ErrorCategory.VALIDATION
        assert error.context.severity == ErrorSeverity.ERROR
        assert error.context.message == "Test validation error"
        assert len(error.context.suggestions) == 2
        
        # Test serialization
        error_dict = error.context.to_dict()
        assert isinstance(error_dict, dict)
        assert error_dict["category"] == "validation"
        assert error_dict["severity"] == "error"
    
    def test_error_handler_standard_exceptions(self):
        """Test error handler with standard Python exceptions"""
        from graphrag_mcp.utils.enhanced_error_handling import ErrorHandler
        
        handler = ErrorHandler()
        
        # Test FileNotFoundError
        error = FileNotFoundError("File not found")
        context = handler.handle_error(error)
        
        assert "file" in context.user_message.lower()
        assert len(context.suggestions) > 0
        assert context.category.value == "validation"
    
    def test_error_handler_history(self):
        """Test error handler history tracking"""
        from graphrag_mcp.utils.enhanced_error_handling import ErrorHandler
        
        handler = ErrorHandler()
        
        # Generate some errors
        handler.handle_error(ValueError("Error 1"))
        handler.handle_error(FileNotFoundError("Error 2"))
        handler.handle_error(ConnectionError("Error 3"))
        
        summary = handler.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert summary["recent_errors"] == 3
        assert len(summary["category_counts"]) > 0
        assert summary["most_recent"] is not None


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def notebook_interface(self, temp_dir):
        config = GraphRAGConfig()
        interface = NotebookInterface(config)
        # Override storage paths
        interface.project_service.storage_service.base_dir = temp_dir
        interface.project_service.storage_service.projects_dir = temp_dir / "projects"
        interface.project_service.storage_service.projects_dir.mkdir(exist_ok=True)
        return interface
    
    def test_complete_notebook_workflow(self, notebook_interface, temp_dir):
        """Test complete workflow through notebook interface"""
        # Step 1: Create project
        create_result = notebook_interface.create_project("workflow-test", "academic")
        assert create_result.success
        
        # Step 2: Create test documents
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()
        pdf1 = docs_dir / "test1.pdf"
        pdf1.write_bytes(b"fake pdf content 1")
        
        # Step 3: Discover documents
        discover_result = notebook_interface.discover_documents(str(docs_dir))
        assert discover_result.success
        assert discover_result.data["count"] == 1
        
        # Step 4: Add documents to project
        add_result = notebook_interface.add_documents("workflow-test", str(docs_dir))
        assert add_result.success
        assert add_result.data["documents_added"] == 1
        
        # Step 5: Get project status
        status_result = notebook_interface.get_project_status("workflow-test")
        assert status_result.success
        assert status_result.data["documents_total"] == 1
        
        # Step 6: List projects
        list_result = notebook_interface.list_projects()
        assert list_result.success
        assert list_result.data["total_projects"] == 1
    
    def test_error_recovery_workflow(self, notebook_interface, temp_dir):
        """Test error handling and recovery in workflows"""
        # Try to create project with invalid template
        create_result = notebook_interface.create_project("test", "invalid-template")
        assert not create_result.success
        assert len(create_result.errors) > 0
        
        # Recover with valid template
        create_result = notebook_interface.create_project("test", "academic")
        assert create_result.success
        
        # Try to add documents from non-existent path
        add_result = notebook_interface.add_documents("test", "/nonexistent/path")
        assert not add_result.success
        
        # Try to get status of non-existent project
        status_result = notebook_interface.get_project_status("nonexistent")
        assert not status_result.success


if __name__ == "__main__":
    pytest.main([__file__])