"""
GraphRAG MCP Error Handling

This module provides custom exceptions and error handling utilities.
"""

from typing import Any, Optional, Dict, Union


class GraphRAGError(Exception):
    """Base exception for GraphRAG MCP toolkit"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class ValidationError(GraphRAGError):
    """Raised when system validation fails"""
    pass


class ProcessingError(GraphRAGError):
    """Raised when document processing fails"""
    pass


class ConfigurationError(GraphRAGError):
    """Raised when configuration is invalid"""
    pass


class ServiceError(GraphRAGError):
    """Raised when external service is unavailable"""
    pass


class MCPError(GraphRAGError):
    """Raised when MCP server operations fail"""
    pass


def handle_processing_error(func):
    """Decorator to handle processing errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise ProcessingError(f"Error in {func.__name__}: {str(e)}", {"original_error": str(e)})
    return wrapper


def format_error_message(error: Exception) -> str:
    """Format error message for user display"""
    if isinstance(error, GraphRAGError):
        message = str(error)
        if error.details:
            message += f"\nDetails: {error.details}"
        return message
    else:
        return f"Unexpected error: {str(error)}"
