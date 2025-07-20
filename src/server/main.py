#!/usr/bin/env python3
"""
Simple Knowledge Graph MCP Server

A modular FastMCP server that registers tools from separate modules for building
and querying knowledge graphs. This server orchestrates storage and query tools
to provide a complete research assistant interface.

Architecture:
- Storage tools: Entity and text storage in Neo4j and ChromaDB
- Query tools: Knowledge graph search and literature review generation  
- Management tools: Database utilities and cleanup operations

The server initializes storage managers and registers all tools from their
respective modules, providing a clean separation of concerns.
"""

from fastmcp import FastMCP

# Import our storage managers
from storage.neo4j import Neo4jStorage, Neo4jQuery
from storage.chroma import ChromaDBStorage, ChromaDBQuery
import config

# Import tool registration functions
from tools.storage.entity_storage import register_entity_tools
from tools.storage.text_storage import register_text_tools
from tools.storage.database_management import register_management_tools
from tools.query.knowledge_search import register_search_tools
from tools.query.literature_generation import register_literature_tools
from tools.processing.text_processing import register_text_processing_tools

# Initialize MCP server
mcp = FastMCP("Knowledge Graph Research Assistant")

# Initialize storage managers
neo4j_storage = Neo4jStorage()
neo4j_query = Neo4jQuery()
chromadb_storage = ChromaDBStorage()
chromadb_query = ChromaDBQuery()

# Register all tools from separate modules
register_entity_tools(mcp, neo4j_storage)
register_text_tools(mcp, chromadb_storage)
register_management_tools(mcp, neo4j_storage, chromadb_storage)
register_search_tools(mcp, neo4j_query, chromadb_query)
register_literature_tools(mcp, neo4j_query, chromadb_query)
register_text_processing_tools(mcp)


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