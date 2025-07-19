"""
GraphRAG MCP Services Layer

Unified service layer that provides clean interfaces for all clients:
- CLI commands
- Jupyter notebooks  
- API endpoints
- MCP servers
- Future integrations

This eliminates the complex wrapper hierarchy with a simple 3-layer design:
1. Interface Layer - CLI/Notebook/API adapters
2. Service Layer - Business logic and orchestration
3. Storage Layer - Unified persistence operations
"""

from .document_processing_service import DocumentProcessingService
from .project_service import ProjectService
from .storage_service import StorageService

__all__ = [
    "DocumentProcessingService",
    "ProjectService", 
    "StorageService"
]