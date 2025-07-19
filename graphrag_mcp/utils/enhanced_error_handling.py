"""
Enhanced Error Handling for Simplified Architecture

Clear error propagation and handling across all layers:
- Interface Layer: User-friendly error messages
- Service Layer: Business logic error context
- Storage Layer: Data persistence error details

This replaces scattered error handling across the wrapper hierarchy.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    VALIDATION = "validation"
    PROCESSING = "processing"
    STORAGE = "storage"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    SYSTEM = "system"


@dataclass
class ErrorContext:
    """Rich error context with debugging information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    user_message: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    technical_details: Dict[str, Any] = field(default_factory=dict)
    stacktrace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "error_id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "user_message": self.user_message,
            "suggestions": self.suggestions,
            "technical_details": self.technical_details,
            "stacktrace": self.stacktrace
        }


class GraphRAGError(Exception):
    """Base exception for GraphRAG with enhanced context"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[str] = None,
        user_message: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        technical_details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        
        import uuid
        self.context = ErrorContext(
            error_id=str(uuid.uuid4())[:8],
            category=category,
            severity=severity,
            message=message,
            details=details,
            user_message=user_message or self._generate_user_message(message, category),
            suggestions=suggestions or self._generate_suggestions(category),
            technical_details=technical_details or {},
            stacktrace=traceback.format_exc() if logger.isEnabledFor(logging.DEBUG) else None
        )
    
    def _generate_user_message(self, message: str, category: ErrorCategory) -> str:
        """Generate user-friendly message based on category"""
        category_messages = {
            ErrorCategory.VALIDATION: "There's an issue with the input provided.",
            ErrorCategory.PROCESSING: "Document processing encountered an issue.",
            ErrorCategory.STORAGE: "There's a problem with data storage.",
            ErrorCategory.NETWORK: "Network connection issue detected.",
            ErrorCategory.CONFIGURATION: "Configuration problem found.",
            ErrorCategory.RESOURCE: "System resource issue encountered.",
            ErrorCategory.SYSTEM: "System error occurred."
        }
        return category_messages.get(category, "An error occurred.")
    
    def _generate_suggestions(self, category: ErrorCategory) -> List[str]:
        """Generate helpful suggestions based on category"""
        category_suggestions = {
            ErrorCategory.VALIDATION: [
                "Check that all required parameters are provided",
                "Verify file paths exist and are accessible",
                "Ensure input formats are correct"
            ],
            ErrorCategory.PROCESSING: [
                "Check that Ollama service is running: ollama serve",
                "Verify PDF files are not corrupted",
                "Ensure sufficient system resources"
            ],
            ErrorCategory.STORAGE: [
                "Check that Neo4j is running and accessible",
                "Verify database connection settings",
                "Ensure sufficient disk space"
            ],
            ErrorCategory.NETWORK: [
                "Check internet connection",
                "Verify service URLs are accessible",
                "Check firewall settings"
            ],
            ErrorCategory.CONFIGURATION: [
                "Check configuration file settings",
                "Verify environment variables",
                "Ensure all required dependencies are installed"
            ],
            ErrorCategory.RESOURCE: [
                "Check available memory and disk space",
                "Close other resource-intensive applications",
                "Consider processing fewer documents at once"
            ]
        }
        return category_suggestions.get(category, ["Check the error details above"])


class ValidationError(GraphRAGError):
    """Input validation errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class ProcessingError(GraphRAGError):
    """Document processing errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class StorageError(GraphRAGError):
    """Data storage and persistence errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.STORAGE,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class NetworkError(GraphRAGError):
    """Network and service connection errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class ConfigurationError(GraphRAGError):
    """Configuration and setup errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class ResourceError(GraphRAGError):
    """System resource errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class ErrorHandler:
    """Enhanced error handler for the simplified architecture"""
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_facing: bool = True
    ) -> ErrorContext:
        """
        Handle an error with enhanced context.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            user_facing: Whether this is a user-facing error
            
        Returns:
            ErrorContext with rich error information
        """
        if isinstance(error, GraphRAGError):
            error_context = error.context
        else:
            # Convert standard exceptions to GraphRAGError
            error_context = self._convert_standard_error(error)
        
        # Add additional context
        if context:
            error_context.technical_details.update(context)
        
        # Log the error appropriately
        self._log_error(error_context, user_facing)
        
        # Store in history for debugging
        self.error_history.append(error_context)
        
        return error_context
    
    def _convert_standard_error(self, error: Exception) -> ErrorContext:
        """Convert standard Python exceptions to ErrorContext"""
        import uuid
        
        # Map common exceptions to categories
        exception_mapping = {
            FileNotFoundError: ErrorCategory.VALIDATION,
            PermissionError: ErrorCategory.SYSTEM,
            ConnectionError: ErrorCategory.NETWORK,
            TimeoutError: ErrorCategory.NETWORK,
            MemoryError: ErrorCategory.RESOURCE,
            OSError: ErrorCategory.SYSTEM,
            ValueError: ErrorCategory.VALIDATION,
            TypeError: ErrorCategory.VALIDATION,
        }
        
        category = exception_mapping.get(type(error), ErrorCategory.SYSTEM)
        
        return ErrorContext(
            error_id=str(uuid.uuid4())[:8],
            category=category,
            severity=ErrorSeverity.ERROR,
            message=str(error),
            user_message=self._generate_user_message_for_exception(error),
            suggestions=self._generate_suggestions_for_exception(error),
            technical_details={"exception_type": type(error).__name__},
            stacktrace=traceback.format_exc() if logger.isEnabledFor(logging.DEBUG) else None
        )
    
    def _generate_user_message_for_exception(self, error: Exception) -> str:
        """Generate user-friendly messages for standard exceptions"""
        if isinstance(error, FileNotFoundError):
            return "A required file or directory was not found."
        elif isinstance(error, PermissionError):
            return "Permission denied accessing a file or resource."
        elif isinstance(error, ConnectionError):
            return "Failed to connect to a required service."
        elif isinstance(error, TimeoutError):
            return "Operation timed out waiting for a response."
        elif isinstance(error, MemoryError):
            return "Insufficient memory to complete the operation."
        else:
            return "An unexpected error occurred."
    
    def _generate_suggestions_for_exception(self, error: Exception) -> List[str]:
        """Generate helpful suggestions for standard exceptions"""
        if isinstance(error, FileNotFoundError):
            return [
                "Check that the file path is correct",
                "Ensure the file exists and is accessible",
                "Verify working directory is correct"
            ]
        elif isinstance(error, PermissionError):
            return [
                "Check file and directory permissions",
                "Run with appropriate privileges if needed",
                "Ensure the file is not in use by another process"
            ]
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return [
                "Check that required services are running",
                "Verify network connectivity",
                "Check firewall and proxy settings"
            ]
        elif isinstance(error, MemoryError):
            return [
                "Close other applications to free memory",
                "Process fewer documents at once",
                "Consider using a machine with more RAM"
            ]
        else:
            return ["Check the error details for more information"]
    
    def _log_error(self, error_context: ErrorContext, user_facing: bool):
        """Log error with appropriate level and detail"""
        log_message = f"[{error_context.error_id}] {error_context.message}"
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_context.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif error_context.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Log technical details at debug level
        if error_context.technical_details:
            logger.debug(f"Technical details: {error_context.technical_details}")
        
        if error_context.stacktrace and logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Stacktrace:\\n{error_context.stacktrace}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        if not self.error_history:
            return {"total_errors": 0, "recent_errors": []}
        
        recent_errors = self.error_history[-10:]  # Last 10 errors
        
        # Count by category
        category_counts = {}
        for error in recent_errors:
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "category_counts": category_counts,
            "most_recent": recent_errors[-1].to_dict() if recent_errors else None
        }


# Global error handler instance
error_handler = ErrorHandler()


def handle_service_error(func):
    """Decorator for service layer error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_context = error_handler.handle_error(e, {
                "function": func.__name__,
                "args": str(args)[:200],  # Truncate for logging
                "kwargs": str(kwargs)[:200]
            })
            # Re-raise with enhanced context
            raise GraphRAGError(
                error_context.message,
                category=error_context.category,
                severity=error_context.severity,
                details=error_context.details,
                user_message=error_context.user_message,
                suggestions=error_context.suggestions,
                technical_details=error_context.technical_details
            )
    return wrapper


async def handle_async_service_error(func):
    """Decorator for async service layer error handling"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_context = error_handler.handle_error(e, {
                "function": func.__name__,
                "args": str(args)[:200],
                "kwargs": str(kwargs)[:200]
            })
            # Re-raise with enhanced context
            raise GraphRAGError(
                error_context.message,
                category=error_context.category,
                severity=error_context.severity,
                details=error_context.details,
                user_message=error_context.user_message,
                suggestions=error_context.suggestions,
                technical_details=error_context.technical_details
            )
    return wrapper