"""
MCP server generation module

Generates FastMCP servers from domain templates, enabling AI assistants to access
domain-specific knowledge through the Model Context Protocol.

Components:
- ServerGenerator: Creates deployable MCP servers
- ToolsBuilder: Generates domain-specific tool functions
- ConfigManager: Handles server configuration and deployment
"""

from .server_generator import UniversalMCPServer, create_universal_server, run_universal_server_cli

__all__ = [
    "UniversalMCPServer",
    "create_universal_server", 
    "run_universal_server_cli",
]