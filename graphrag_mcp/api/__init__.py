"""
GraphRAG MCP User API

This module provides the main user-facing API for the GraphRAG MCP toolkit.
Users interact with this API to create knowledge graphs and start MCP servers.
"""

from ..ui.status import ProcessingResults, ValidationResult
from .convenience import (
    get_system_status,
    quick_process,
    quick_setup,
    validate_system,
    visualize_processed_documents,
)
from .processor import GraphRAGProcessor

__all__ = [
    "GraphRAGProcessor",
    "ProcessingResults",
    "ValidationResult",
    "quick_setup",
    "quick_process",
    "validate_system",
    "get_system_status",
    "visualize_processed_documents"
]
