"""
CLI module for GraphRAG MCP Toolkit

Provides the command-line interface for creating, managing, and deploying
GraphRAG MCP servers across different domains.

Main commands:
- create: Create new domain-specific assistant
- templates: Manage domain templates
- add-documents: Add PDFs to project
- process: Process documents into knowledge graphs
- serve: Start MCP server for AI integration
- status: Check system and project health
"""

from .main import app

# For backwards compatibility
cli_app = app

__all__ = ["app", "cli_app"]