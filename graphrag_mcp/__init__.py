"""
GraphRAG MCP Toolkit

An open-source platform for creating domain-specific GraphRAG MCP servers.
Transform any document collection into an intelligent AI assistant that understands
your field's unique context, terminology, and relationships.

Features:
- Domain-specific knowledge graph extraction
- Local processing with Ollama (privacy-first)
- Template-driven domain configuration
- FastMCP server generation
- Academic literature review support
- Citation-accurate responses

Built with LangChain, Graphiti, and FastMCP for professional-grade AI tools.
"""

__version__ = "0.1.0"
__author__ = "Aimie Garces"

# Core components for backwards compatibility with existing src/
# CLI interface (optional - requires typer)
try:
    from .cli.main import app as cli_app
    CLI_AVAILABLE = True
except ImportError:
    cli_app = None
    CLI_AVAILABLE = False
from .core.analyzer import AdvancedAnalyzer
from .core.chat_engine import ChatEngine
from .core.document_processor import DocumentProcessor
from .core.ollama_engine import OllamaEngine

# MCP generation
from .mcp.server_generator import (
    UniversalMCPServer,
    create_universal_server,
    run_universal_server_cli,
)
from .templates.academic import AcademicTemplate

# Template system
from .templates.base import BaseTemplate, template_registry

__all__ = [
    # Core processing components
    "DocumentProcessor",
    "ChatEngine",
    "AdvancedAnalyzer",
    "OllamaEngine",

    # CLI interface
    "cli_app",

    # Template system
    "BaseTemplate",
    "AcademicTemplate",
    "template_registry",

    # MCP generation
    "UniversalMCPServer",
    "create_universal_server",
    "run_universal_server_cli",

    # Package metadata
    "__version__",
    "__author__",
]
