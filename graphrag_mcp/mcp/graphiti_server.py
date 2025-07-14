"""
Graphiti-powered MCP Server
Universal MCP server using Graphiti real-time knowledge graphs instead of NetworkX
"""

import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# Graphiti components
from ..core.graphiti_engine import GraphitiKnowledgeGraph, create_graphiti_knowledge_graph
from ..templates import BaseTemplate, template_registry, AcademicTemplate

logger = logging.getLogger(__name__)


class GraphitiServerState(BaseModel):
    """State management for the Graphiti MCP server"""
    current_template: Optional[str] = None
    loaded_documents: List[str] = Field(default_factory=list)
    processed_documents: Dict[str, Any] = Field(default_factory=dict)
    active_collections: Dict[str, str] = Field(default_factory=dict)  # name -> path
    server_config: Dict[str, Any] = Field(default_factory=dict)
    knowledge_graph_stats: Dict[str, Any] = Field(default_factory=dict)


class GraphitiMCPServer:
    """
    Graphiti-powered MCP Server for real-time knowledge graphs
    
    Features:
    - Real-time document processing with Graphiti + Neo4j
    - Persistent knowledge graphs across sessions
    - AI-optimized entity extraction and relationship discovery
    - Template-based domain customization
    - Hybrid search (semantic + keyword + graph traversal)
    """
    
    def __init__(self, 
                 name: str = "GraphRAG Graphiti Assistant",
                 instructions: str = "Real-time knowledge graph assistant powered by Graphiti",
                 host: str = "localhost",
                 port: int = 8080,
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password"):
        
        self.name = name
        self.instructions = instructions
        self.host = host
        self.port = port
        
        # Graphiti configuration
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        # Initialize FastMCP server
        self.server = FastMCP(name)
        
        # Server state
        self.state = GraphitiServerState()
        
        # Graphiti knowledge graph
        self.knowledge_graph: Optional[GraphitiKnowledgeGraph] = None
        
        # Current template
        self.current_template: Optional[BaseTemplate] = None
        
        # Register core tools
        self._register_core_tools()
        
        logger.info(f"Initialized GraphitiMCPServer: {name}")
    
    async def initialize_knowledge_graph(self):
        """Initialize the Graphiti knowledge graph"""
        try:
            self.knowledge_graph = await create_graphiti_knowledge_graph(
                neo4j_uri=self.neo4j_uri,
                neo4j_user=self.neo4j_user,
                neo4j_password=self.neo4j_password
            )
            
            # Update server state
            self.state.knowledge_graph_stats = await self.knowledge_graph.get_knowledge_graph_stats()
            
            logger.info("✅ Graphiti knowledge graph initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Graphiti knowledge graph: {e}")
            return False
    
    def _register_core_tools(self):
        """Register core MCP tools for Graphiti server"""
        
        @self.server.tool
        async def server_status(ctx: Context) -> Dict[str, Any]:
            """Get comprehensive server status including Graphiti knowledge graph"""
            try:
                status = {
                    "server_name": self.name,
                    "current_template": self.state.current_template,
                    "loaded_documents": len(self.state.loaded_documents),
                    "processed_documents": len(self.state.processed_documents),
                    "active_collections": len(self.state.active_collections),
                    "neo4j_uri": self.neo4j_uri,
                    "knowledge_graph_initialized": self.knowledge_graph is not None,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add knowledge graph statistics
                if self.knowledge_graph:
                    kg_stats = await self.knowledge_graph.get_knowledge_graph_stats()
                    status["knowledge_graph_stats"] = kg_stats
                
                return status
                
            except Exception as e:
                logger.error(f"Error getting server status: {e}")
                return {"error": str(e)}
        
        @self.server.tool
        async def list_templates(ctx: Context) -> Dict[str, Any]:
            """List all available domain templates"""
            try:
                templates = {}
                for template_name, template_class in template_registry.items():
                    template_instance = template_class()
                    templates[template_name] = {
                        "name": template_instance.name,
                        "description": template_instance.description,
                        "supported_domains": template_instance.supported_domains,
                        "entity_types": list(template_instance.get_entity_schema().keys()),
                        "mcp_tools": [tool["name"] for tool in template_instance.get_mcp_tools()]
                    }
                
                return {
                    "available_templates": templates,
                    "current_template": self.state.current_template,
                    "total_templates": len(templates)
                }
                
            except Exception as e:
                logger.error(f"Error listing templates: {e}")
                return {"error": str(e)}
        
        @self.server.tool
        async def switch_template(ctx: Context, template_name: str) -> Dict[str, Any]:
            """Switch to a different domain template"""
            try:
                if template_name not in template_registry:
                    return {"error": f"Template '{template_name}' not found"}
                
                # Load new template
                template_class = template_registry[template_name]
                self.current_template = template_class()
                self.state.current_template = template_name
                
                # Register template-specific tools
                await self._register_template_tools()
                
                return {
                    "success": True,
                    "new_template": template_name,
                    "template_info": {
                        "name": self.current_template.name,
                        "description": self.current_template.description,
                        "supported_domains": self.current_template.supported_domains,
                        "entity_types": list(self.current_template.get_entity_schema().keys()),
                        "mcp_tools": [tool["name"] for tool in self.current_template.get_mcp_tools()]
                    }
                }
                
            except Exception as e:
                logger.error(f"Error switching template: {e}")
                return {"error": str(e)}
        
        @self.server.tool
        async def add_document_to_graph(ctx: Context, 
                                       document_path: str,
                                       document_id: Optional[str] = None,
                                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            """Add a document to the Graphiti knowledge graph"""
            try:
                if not self.knowledge_graph:
                    await self.initialize_knowledge_graph()
                
                # Generate document ID if not provided
                if not document_id:
                    document_id = f"doc_{len(self.state.loaded_documents) + 1}"
                
                # Read document content
                doc_path = Path(document_path)
                if not doc_path.exists():
                    return {"error": f"Document not found: {document_path}"}
                
                # Read document content (simplified - in production use proper PDF processing)
                try:
                    content = doc_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    return {"error": f"Cannot read document as text: {document_path}"}
                
                # Add to knowledge graph
                success = await self.knowledge_graph.add_document(
                    document_content=content,
                    document_id=document_id,
                    metadata=metadata or {"source": document_path},
                    source_description=f"Document from {document_path}"
                )
                
                if success:
                    # Update server state
                    self.state.loaded_documents.append(document_id)
                    self.state.processed_documents[document_id] = {
                        "path": document_path,
                        "metadata": metadata,
                        "added_at": datetime.now().isoformat()
                    }
                    
                    # Update knowledge graph stats
                    self.state.knowledge_graph_stats = await self.knowledge_graph.get_knowledge_graph_stats()
                    
                    return {
                        "success": True,
                        "document_id": document_id,
                        "document_path": document_path,
                        "knowledge_graph_stats": self.state.knowledge_graph_stats
                    }
                else:
                    return {"error": f"Failed to add document to knowledge graph"}
                
            except Exception as e:
                logger.error(f"Error adding document to graph: {e}")
                return {"error": str(e)}
        
        @self.server.tool
        async def search_knowledge_graph(ctx: Context, 
                                       query: str,
                                       max_results: int = 10) -> Dict[str, Any]:
            """Search the Graphiti knowledge graph"""
            try:
                if not self.knowledge_graph:
                    return {"error": "Knowledge graph not initialized"}
                
                # Perform search
                results = await self.knowledge_graph.search_knowledge_graph(
                    query=query,
                    max_results=max_results
                )
                
                return {
                    "query": query,
                    "results": results,
                    "total_results": len(results),
                    "max_results": max_results,
                    "search_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error searching knowledge graph: {e}")
                return {"error": str(e)}
        
        @self.server.tool
        async def get_entity_relationships(ctx: Context, 
                                         entity_name: str) -> Dict[str, Any]:
            """Get relationships for a specific entity from the knowledge graph"""
            try:
                if not self.knowledge_graph:
                    return {"error": "Knowledge graph not initialized"}
                
                relationships = await self.knowledge_graph.get_entity_relationships(entity_name)
                
                return {
                    "entity_name": entity_name,
                    "relationships": relationships,
                    "total_relationships": len(relationships),
                    "search_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error getting entity relationships: {e}")
                return {"error": str(e)}
        
        @self.server.tool
        async def get_document_summary(ctx: Context, 
                                     document_id: str) -> Dict[str, Any]:
            """Get summary information for a processed document"""
            try:
                if not self.knowledge_graph:
                    return {"error": "Knowledge graph not initialized"}
                
                summary = await self.knowledge_graph.get_document_summary(document_id)
                
                return {
                    "document_id": document_id,
                    "summary": summary,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error getting document summary: {e}")
                return {"error": str(e)}
    
    async def _register_template_tools(self):
        """Register template-specific MCP tools"""
        if not self.current_template:
            return
        
        # Get template-specific tools
        template_tools = self.current_template.get_mcp_tools()
        
        for tool_config in template_tools:
            tool_name = tool_config["name"]
            tool_description = tool_config["description"]
            tool_parameters = tool_config.get("parameters", {})
            
            # Create dynamic tool function
            async def dynamic_tool(ctx: Context, **kwargs) -> Dict[str, Any]:
                try:
                    # Use knowledge graph for template-specific queries
                    if not self.knowledge_graph:
                        return {"error": "Knowledge graph not initialized"}
                    
                    # Template-specific processing based on tool name
                    if tool_name == "query_papers":
                        query = kwargs.get("query", "")
                        results = await self.knowledge_graph.search_knowledge_graph(
                            query=query,
                            max_results=kwargs.get("max_results", 10)
                        )
                        return {
                            "tool": tool_name,
                            "query": query,
                            "results": results,
                            "template": self.current_template.name
                        }
                    
                    elif tool_name == "find_citations":
                        claim = kwargs.get("claim", "")
                        results = await self.knowledge_graph.search_knowledge_graph(
                            query=claim,
                            max_results=5
                        )
                        return {
                            "tool": tool_name,
                            "claim": claim,
                            "supporting_evidence": results,
                            "template": self.current_template.name
                        }
                    
                    elif tool_name == "research_gaps":
                        domain = kwargs.get("domain", "")
                        # Search for gaps in the knowledge graph
                        results = await self.knowledge_graph.search_knowledge_graph(
                            query=f"gaps OR limitations OR future work {domain}",
                            max_results=10
                        )
                        return {
                            "tool": tool_name,
                            "domain": domain,
                            "identified_gaps": results,
                            "template": self.current_template.name
                        }
                    
                    else:
                        # Generic template tool handling
                        return {
                            "tool": tool_name,
                            "parameters": kwargs,
                            "template": self.current_template.name,
                            "message": f"Template tool {tool_name} executed successfully"
                        }
                
                except Exception as e:
                    logger.error(f"Error in template tool {tool_name}: {e}")
                    return {"error": str(e)}
            
            # Register the dynamic tool
            self.server.tool(
                name=tool_name,
                description=tool_description
            )(dynamic_tool)
    
    async def run(self):
        """Run the Graphiti MCP server"""
        try:
            # Initialize knowledge graph
            await self.initialize_knowledge_graph()
            
            # Load default template (academic)
            if "academic" in template_registry:
                await self.switch_template(None, "academic")
            
            logger.info(f"🚀 Starting Graphiti MCP server on {self.host}:{self.port}")
            
            # Run the FastMCP server
            await self.server.run(host=self.host, port=self.port)
            
        except Exception as e:
            logger.error(f"❌ Error running Graphiti MCP server: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the server and close connections"""
        try:
            if self.knowledge_graph:
                await self.knowledge_graph.close()
            logger.info("✅ Graphiti MCP server shutdown complete")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Factory function for easy server creation
def create_graphiti_mcp_server(**kwargs) -> GraphitiMCPServer:
    """
    Create a new Graphiti MCP server instance
    
    Args:
        **kwargs: Configuration parameters for GraphitiMCPServer
        
    Returns:
        GraphitiMCPServer instance
    """
    return GraphitiMCPServer(**kwargs)


# Example usage
async def main():
    """Example usage of GraphitiMCPServer"""
    
    # Create server
    server = create_graphiti_mcp_server(
        name="Academic Research Assistant",
        instructions="Real-time knowledge graph for academic research",
        port=8080
    )
    
    # Run server
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())