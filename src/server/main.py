#!/usr/bin/env python3
"""
Simple Knowledge Graph MCP Server

A modular FastMCP server that registers tools from separate modules for building
and querying knowledge graphs. This server orchestrates storage and query tools
to provide a complete research assistant interface.

Architecture:
- Storage tools: Entity and text storage in Neo4j (with vector search)
- Query tools: Knowledge graph search and literature review generation  
- Management tools: Database utilities and cleanup operations

The server initializes storage managers and registers all tools from their
respective modules, providing a clean separation of concerns.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from fastmcp import FastMCP

# Import our storage managers
from storage.neo4j import Neo4jStorage, Neo4jQuery
import config

# Import shared tool registry
from tools.shared_registry import register_all_mcp_tools

# Initialize MCP server
mcp = FastMCP("Knowledge Graph Research Assistant")

# Initialize Neo4j storage managers
neo4j_storage = Neo4jStorage()
neo4j_query = Neo4jQuery()

# Register all tools using shared registry
register_all_mcp_tools(mcp, neo4j_storage, neo4j_query)


if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        # Run as HTTP server for easy GUI setup
        print("🌐 Starting HTTP MCP server at http://localhost:3001")
        print("   Add this URL in Claude Desktop connector settings")
        print("   Try both: http://localhost:3001 and http://localhost:3001/mcp")
        mcp.run(
            transport="http", 
            host="0.0.0.0",  # Accept connections from any interface
            port=3001,
            log_level="debug"
        )
    else:
        # Run as STDIO for advanced JSON config
        mcp.run()