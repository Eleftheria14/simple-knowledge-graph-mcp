"""
GraphRAG MCP Interface Layer

Clean interfaces for all client types:
- Jupyter notebooks
- CLI commands  
- API endpoints
- MCP servers

Each interface is a thin wrapper around the service layer.
"""

from .notebook_interface import NotebookInterface
from .cli_interface import CLIInterface

__all__ = [
    "NotebookInterface", 
    "CLIInterface"
]