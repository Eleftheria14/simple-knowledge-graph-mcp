"""
GraphRAG MCP Base Components

This module provides standardized base classes and utilities for MCP tools.
"""

import asyncio
import time
from typing import Any, Dict, Optional, List, Callable
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, Field
try:
    from mcp.server.fastmcp import Context
except ImportError:
    try:
        from fastmcp import Context
    except ImportError:
        # Fallback for when MCP is not available
        Context = None

from ..utils.error_handling import ProcessingError, ValidationError
from ..ui.status import ValidationResult


class MCPToolType(str, Enum):
    """MCP tool categories"""
    CHAT = "chat"
    LITERATURE = "literature"
    CORE = "core"
    UTILITY = "utility"


@dataclass
class MCPMetadata:
    """Metadata for MCP tool responses"""
    tool_name: str
    tool_type: MCPToolType
    processing_time: float
    confidence_score: Optional[float] = None
    citations_used: List[str] = field(default_factory=list)
    follow_up_suggestions: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    additional_info: Dict[str, Any] = field(default_factory=dict)


class MCPResponse(BaseModel):
    """Standardized MCP tool response format"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[MCPMetadata] = None
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary for MCP response"""
        result = super().model_dump(**kwargs)
        
        # Convert metadata dataclass to dict if present
        if self.metadata:
            result["metadata"] = {
                "tool_name": self.metadata.tool_name,
                "tool_type": self.metadata.tool_type.value,
                "processing_time": self.metadata.processing_time,
                "confidence_score": self.metadata.confidence_score,
                "citations_used": self.metadata.citations_used,
                "follow_up_suggestions": self.metadata.follow_up_suggestions,
                "data_sources": self.metadata.data_sources,
                "additional_info": self.metadata.additional_info
            }
        
        return result


class StandardizedToolEngine:
    """Base class for standardized MCP tool engines"""
    
    def __init__(self, api_processor=None, citation_manager=None):
        """Initialize with optional API processor and citation manager"""
        self.api_processor = api_processor
        self.citation_manager = citation_manager
        self.tool_registry = {}
        
    def validate_environment(self) -> ValidationResult:
        """Validate environment before tool execution"""
        if self.api_processor:
            return self.api_processor.validate_environment(verbose=False)
        else:
            # Fallback validation
            return ValidationResult(
                status="passed",
                issues=[],
                details={"validation": "basic"}
            )
    
    def track_citation(self, citation_key: str, context: str = ""):
        """Track citation usage across tools"""
        if self.citation_manager:
            self.citation_manager.track_citation(citation_key, context)
    
    def get_citations_used(self) -> List[str]:
        """Get all citations used during processing"""
        if self.citation_manager:
            return list(self.citation_manager.used_citations)
        return []
    
    def register_tool(self, tool_name: str, tool_type: MCPToolType, handler: Callable):
        """Register a tool with the engine"""
        self.tool_registry[tool_name] = {
            "handler": handler,
            "type": tool_type
        }


def standard_mcp_tool(tool_name: str, tool_type: MCPToolType, require_validation: bool = True):
    """
    Decorator for standardizing MCP tool implementations
    
    Args:
        tool_name: Name of the tool
        tool_type: Type of tool (chat, literature, core, utility)
        require_validation: Whether to validate environment before execution
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, ctx: Optional[Context] = None, **kwargs):
            start_time = time.time()
            
            try:
                # Environment validation if required
                if require_validation and hasattr(self, 'validate_environment'):
                    validation = self.validate_environment()
                    if not validation.is_valid:
                        return MCPResponse(
                            success=False,
                            error="Environment validation failed",
                            error_code="ENV_VALIDATION_FAILED",
                            metadata=MCPMetadata(
                                tool_name=tool_name,
                                tool_type=tool_type,
                                processing_time=time.time() - start_time,
                                additional_info={"validation_issues": validation.issues}
                            )
                        ).model_dump()
                
                # Execute the tool function
                result = await func(self, *args, ctx=ctx, **kwargs)
                
                # Get processing time
                processing_time = time.time() - start_time
                
                # Get citations used during processing
                citations_used = []
                if hasattr(self, 'get_citations_used'):
                    citations_used = self.get_citations_used()
                
                # Create metadata
                metadata = MCPMetadata(
                    tool_name=tool_name,
                    tool_type=tool_type,
                    processing_time=processing_time,
                    citations_used=citations_used
                )
                
                # Handle different return types
                if isinstance(result, dict):
                    # If result already has success/error structure, preserve it
                    if "success" in result:
                        response = MCPResponse(
                            success=result.get("success", True),
                            data=result.get("data"),
                            error=result.get("error"),
                            error_code=result.get("error_code"),
                            metadata=metadata
                        )
                    else:
                        # Wrap data in success response
                        response = MCPResponse(
                            success=True,
                            data=result,
                            metadata=metadata
                        )
                else:
                    # Direct data response
                    response = MCPResponse(
                        success=True,
                        data=result,
                        metadata=metadata
                    )
                
                return response.model_dump()
                
            except ValidationError as e:
                return MCPResponse(
                    success=False,
                    error=str(e),
                    error_code="VALIDATION_ERROR",
                    metadata=MCPMetadata(
                        tool_name=tool_name,
                        tool_type=tool_type,
                        processing_time=time.time() - start_time,
                        additional_info={"validation_error": e.context}
                    )
                ).model_dump()
                
            except ProcessingError as e:
                return MCPResponse(
                    success=False,
                    error=str(e),
                    error_code="PROCESSING_ERROR",
                    metadata=MCPMetadata(
                        tool_name=tool_name,
                        tool_type=tool_type,
                        processing_time=time.time() - start_time,
                        additional_info={"processing_error": e.context}
                    )
                ).model_dump()
                
            except Exception as e:
                return MCPResponse(
                    success=False,
                    error=f"Unexpected error: {str(e)}",
                    error_code="UNEXPECTED_ERROR",
                    metadata=MCPMetadata(
                        tool_name=tool_name,
                        tool_type=tool_type,
                        processing_time=time.time() - start_time,
                        additional_info={"exception_type": type(e).__name__}
                    )
                ).model_dump()
        
        return wrapper
    return decorator


class ToolExecutionContext:
    """Context for tool execution with shared state"""
    
    def __init__(self, api_processor=None, citation_manager=None, user_context=None):
        self.api_processor = api_processor
        self.citation_manager = citation_manager
        self.user_context = user_context or {}
        self.execution_history = []
        
    def add_execution(self, tool_name: str, success: bool, processing_time: float):
        """Track tool execution for analytics"""
        self.execution_history.append({
            "tool_name": tool_name,
            "success": success,
            "processing_time": processing_time,
            "timestamp": time.time()
        })
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for e in self.execution_history if e["success"])
        total_time = sum(e["processing_time"] for e in self.execution_history)
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "total_processing_time": total_time,
            "average_processing_time": total_time / total_executions if total_executions > 0 else 0
        }


def create_tool_context(api_processor=None, citation_manager=None, user_context=None) -> ToolExecutionContext:
    """Create a standardized tool execution context"""
    return ToolExecutionContext(
        api_processor=api_processor,
        citation_manager=citation_manager,
        user_context=user_context
    )


# Response format helpers
def success_response(data: Any, metadata: Optional[MCPMetadata] = None) -> Dict[str, Any]:
    """Create a standardized success response"""
    return MCPResponse(success=True, data=data, metadata=metadata).model_dump()


def error_response(error: str, error_code: str = "GENERIC_ERROR", 
                  metadata: Optional[MCPMetadata] = None) -> Dict[str, Any]:
    """Create a standardized error response"""
    return MCPResponse(
        success=False, 
        error=error, 
        error_code=error_code, 
        metadata=metadata
    ).model_dump()


def validation_error_response(error: str, issues: List[str] = None) -> Dict[str, Any]:
    """Create a standardized validation error response"""
    return MCPResponse(
        success=False,
        error=error,
        error_code="VALIDATION_ERROR",
        metadata=MCPMetadata(
            tool_name="validation",
            tool_type=MCPToolType.UTILITY,
            processing_time=0.0,
            additional_info={"issues": issues or []}
        )
    ).model_dump()