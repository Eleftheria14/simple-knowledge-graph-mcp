"""Shared tool registry for both MCP and LangChain usage"""
from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from fastmcp import FastMCP

# Import dual-purpose tools (work for both MCP and LangChain)
from tools.storage.enhanced_entity_storage import extract_and_store_entities, register_enhanced_entity_tools
from tools.storage.neo4j_vector_storage import store_vectors, register_vector_storage_tools

# Import PDF processing tools
from processor.tools.grobid_tool import grobid_extract

# Import MCP-only tools
from tools.query.knowledge_search import register_search_tools
from tools.query.literature_generation import register_literature_tools
from tools.storage.database_management import register_management_tools

# Storage managers
from storage.neo4j import Neo4jStorage, Neo4jQuery

class SharedToolRegistry:
    """Registry of tools that work for both MCP and LangChain"""
    
    @staticmethod
    def get_all_tools() -> List[BaseTool]:
        """Get all tools for LangChain agent use"""
        return [
            grobid_extract,         # Academic PDF processing (GROBID)
            extract_and_store_entities,
            store_vectors,
        ]
    
    @staticmethod
    def get_storage_tools() -> List[BaseTool]:
        """Get storage-focused tools"""
        return [
            extract_and_store_entities,
            store_vectors,
        ]
    
    @staticmethod
    def get_query_tools() -> List[BaseTool]:
        """Get query-focused tools"""
        # TODO: Add enhanced query tools
        return []
    
    @staticmethod
    def get_extraction_tools() -> List[BaseTool]:
        """Get extraction-focused tools"""
        return [extract_and_store_entities]
    
    @staticmethod
    def register_with_mcp(mcp: FastMCP, neo4j_storage: Neo4jStorage, neo4j_query: Neo4jQuery):
        """Register all tools with MCP server"""
        print("📋 Registering shared tools with MCP server...")
        
        # Register dual-purpose tools (work for both MCP and LangChain)
        register_enhanced_entity_tools(mcp, neo4j_storage)
        register_vector_storage_tools(mcp, neo4j_storage)
        
        # Register MCP-only tools
        register_search_tools(mcp, neo4j_query, neo4j_storage)
        register_literature_tools(mcp, neo4j_query, neo4j_storage)
        register_management_tools(mcp, neo4j_storage)
        
        print("✅ All tools registered with MCP server")

    @staticmethod
    def get_tool_summary() -> Dict[str, Any]:
        """Get summary of available tools"""
        all_tools = SharedToolRegistry.get_all_tools()
        
        return {
            "total_shared_tools": len(all_tools),
            "storage_tools": len(SharedToolRegistry.get_storage_tools()),
            "query_tools": len(SharedToolRegistry.get_query_tools()),
            "extraction_tools": len(SharedToolRegistry.get_extraction_tools()),
            "tool_names": [tool.name for tool in all_tools],
            "capabilities": {
                "entity_extraction": True,
                "text_storage": True,  # Neo4j vector storage
                "knowledge_search": False,  # TODO: Enhance
                "literature_review": False,  # TODO: Enhance
            }
        }

# Convenience functions for easy import
def get_langchain_tools() -> List[BaseTool]:
    """Get all tools for LangChain agent use"""
    return SharedToolRegistry.get_all_tools()

def register_all_mcp_tools(mcp: FastMCP, neo4j_storage: Neo4jStorage, neo4j_query: Neo4jQuery):
    """Register all tools with MCP server"""
    SharedToolRegistry.register_with_mcp(mcp, neo4j_storage, neo4j_query)

# Test function
def test_shared_registry():
    """Test the shared tool registry"""
    print("Testing Shared Tool Registry...")
    
    # Test getting tools
    all_tools = SharedToolRegistry.get_all_tools()
    storage_tools = SharedToolRegistry.get_storage_tools()
    
    print(f"✅ Found {len(all_tools)} shared tools")
    print(f"✅ Found {len(storage_tools)} storage tools")
    
    # Test tool summary
    summary = SharedToolRegistry.get_tool_summary()
    print("📊 Tool Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Test individual tools
    if all_tools:
        test_tool = all_tools[0]
        print(f"🔧 Testing tool: {test_tool.name}")
        print(f"   Description: {test_tool.description}")
    
    print("✅ Shared registry test completed")

if __name__ == "__main__":
    test_shared_registry()