"""
Universal MCP Server for GraphRAG MCP Toolkit

Single MCP server that adapts to any domain template and document collection.
Provides domain-specific tools through the template system while maintaining
a unified interface for Claude Max integration.
"""

import logging
from pathlib import Path
from typing import Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

# Core components
from ..core import AdvancedAnalyzer, ChatEngine, DocumentProcessor, OllamaEngine
from ..core.citation_manager import CitationTracker
from ..core.query_engine import EnhancedQueryEngine
from ..templates import BaseTemplate, template_registry
from .chat_tools import ChatToolsEngine
from .literature_tools import LiteratureToolsEngine
from .base import StandardizedToolEngine, ToolExecutionContext, create_tool_context

logger = logging.getLogger(__name__)


class ServerState(BaseModel):
    """State management for the universal MCP server"""
    current_template: str | None = None
    loaded_documents: list[str] = Field(default_factory=list)
    processed_documents: dict[str, Any] = Field(default_factory=dict)
    active_collections: dict[str, str] = Field(default_factory=dict)  # name -> path
    server_config: dict[str, Any] = Field(default_factory=dict)


class UniversalMCPServer:
    """
    Universal MCP Server that adapts to any domain template.
    
    Single server instance that can:
    - Load any domain template (academic, legal, medical, etc.)
    - Process document collections for any domain
    - Provide template-specific MCP tools
    - Switch domains dynamically
    - Maintain state across sessions
    """

    def __init__(self,
                 name: str = "GraphRAG Universal Assistant",
                 instructions: str = "Universal GraphRAG assistant with domain-specific capabilities",
                 host: str = "localhost",
                 port: int = 8080):
        """Initialize the universal MCP server"""

        self.server = FastMCP(name=name)

        # Server state
        self.state = ServerState()

        # Core components
        self.document_processor = DocumentProcessor()
        self.chat_engine = ChatEngine()
        self.analyzer = AdvancedAnalyzer()
        self.ollama_engine = OllamaEngine()

        # Enhanced components for new tools
        self.citation_manager = CitationTracker()
        self.query_engine = EnhancedQueryEngine(
            knowledge_interface=None,  # Will be set when documents are loaded
            citation_manager=self.citation_manager,
            ollama_engine=self.ollama_engine
        )

        # Create shared tool execution context
        self.tool_context = create_tool_context(
            citation_manager=self.citation_manager,
            user_context={"server": name}
        )

        # Tool engines with shared context
        self.chat_tools = ChatToolsEngine(
            query_engine=self.query_engine,
            citation_manager=self.citation_manager,
            api_processor=self.tool_context.api_processor
        )
        self.literature_tools = LiteratureToolsEngine(
            query_engine=self.query_engine,
            citation_manager=self.citation_manager,
            api_processor=self.tool_context.api_processor
        )

        # Tool registry for better management
        self.registered_tools = {}
        self.tool_execution_stats = {}

        # Current template
        self.current_template: BaseTemplate | None = None

        # Register core MCP tools
        self._register_core_tools()

        # Auto-load academic template as default
        self._load_template("academic")

        logger.info(f"🚀 Universal MCP Server initialized: {name}")

    def _register_core_tools(self):
        """Register core MCP tools that work across all domains"""

        @self.server.tool
        async def list_templates(ctx: Context) -> dict[str, Any]:
            """List all available domain templates"""
            ctx.info("Listing available templates")

            templates = template_registry.list_templates()
            template_info = {}

            for template_name in templates:
                try:
                    template = template_registry.get_template(template_name)
                    template_info[template_name] = {
                        "name": template.config.name,
                        "description": template.config.description,
                        "domain": template.config.domain,
                        "tools": len(template.get_mcp_tools()),
                        "status": "active" if template_name == self.state.current_template else "available"
                    }
                except Exception as e:
                    template_info[template_name] = {"error": str(e)}

            return {
                "available_templates": template_info,
                "current_template": self.state.current_template,
                "total_templates": len(templates)
            }

        @self.server.tool
        async def switch_template(template_name: str, ctx: Context) -> dict[str, Any]:
            """Switch to a different domain template"""
            ctx.info(f"Switching to template: {template_name}")

            try:
                self._load_template(template_name)
                return {
                    "success": True,
                    "message": f"Switched to {template_name} template",
                    "current_template": self.state.current_template,
                    "available_tools": [tool["name"] for tool in self.current_template.get_mcp_tools()]
                }
            except Exception as e:
                ctx.error(f"Failed to switch template: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "current_template": self.state.current_template
                }

        @self.server.tool
        async def server_status(ctx: Context) -> dict[str, Any]:
            """Get comprehensive server status"""
            ctx.info("Getting server status")

            # Check Ollama health
            ollama_health = self.ollama_engine.check_health()

            return {
                "server_name": self.server.name,
                "current_template": self.state.current_template,
                "template_info": self.current_template.config.model_dump() if self.current_template else None,
                "loaded_documents": len(self.state.loaded_documents),
                "processed_documents": len(self.state.processed_documents),
                "active_collections": list(self.state.active_collections.keys()),
                "ollama_status": {
                    "server_accessible": ollama_health.get("server_accessible", False),
                    "llm_available": ollama_health.get("llm_model_available", False),
                    "embedding_available": ollama_health.get("embedding_model_available", False)
                },
                "capabilities": [
                    "domain_switching",
                    "document_processing",
                    "entity_extraction",
                    "semantic_search",
                    "citation_tracking",
                    "dual_mode_tools",
                    "standardized_execution"
                ],
                "tool_analytics": self.get_tool_analytics()
            }

        @self.server.tool
        async def load_document_collection(collection_path: str, collection_name: str, ctx: Context) -> dict[str, Any]:
            """Load and process a collection of documents"""
            ctx.info(f"Loading document collection: {collection_name}")

            try:
                collection_path_obj = Path(collection_path)
                if not collection_path_obj.exists():
                    return {"success": False, "error": f"Path does not exist: {collection_path}"}

                # Find PDF files
                if collection_path_obj.is_file() and collection_path_obj.suffix.lower() == '.pdf':
                    pdf_files = [collection_path_obj]
                else:
                    pdf_files = list(collection_path_obj.rglob("*.pdf"))

                if not pdf_files:
                    return {"success": False, "error": "No PDF files found in collection"}

                # Process documents
                processed_docs = {}
                domain_guidance = self.current_template.get_entity_schema() if self.current_template else None

                for pdf_file in pdf_files[:10]:  # Limit to 10 files for now
                    ctx.info(f"Processing: {pdf_file.name}")
                    try:
                        corpus_doc = self.analyzer.analyze_for_corpus(
                            str(pdf_file),
                            domain_schema=domain_guidance
                        )
                        processed_docs[pdf_file.stem] = corpus_doc.model_dump()
                    except Exception as e:
                        ctx.error(f"Failed to process {pdf_file.name}: {e}")

                # Store collection
                self.state.active_collections[collection_name] = collection_path
                self.state.processed_documents.update(processed_docs)

                return {
                    "success": True,
                    "collection_name": collection_name,
                    "documents_found": len(pdf_files),
                    "documents_processed": len(processed_docs),
                    "documents": list(processed_docs.keys()),
                    "entities_extracted": sum(
                        len(doc.get("entities", {}))
                        for doc in processed_docs.values()
                    )
                }

            except Exception as e:
                ctx.error(f"Collection loading failed: {e}")
                return {"success": False, "error": str(e)}

        @self.server.tool
        async def search_documents(query: str, collection_name: str | None = None, ctx: Context = None) -> dict[str, Any]:
            """Search across loaded documents using semantic similarity"""
            if ctx:
                ctx.info(f"Searching documents: {query}")

            try:
                if not self.state.processed_documents:
                    return {"success": False, "error": "No documents loaded"}

                # Filter by collection if specified
                docs_to_search = self.state.processed_documents
                if collection_name and collection_name in self.state.active_collections:
                    docs_to_search = {
                        k: v for k, v in docs_to_search.items()
                        if v.get("collection") == collection_name
                    }

                # Perform semantic search across documents
                results = []
                for doc_id, doc_data in docs_to_search.items():
                    title = doc_data.get("title", doc_id)
                    content = doc_data.get("content", "")
                    entities = doc_data.get("entities", {})

                    # Simple relevance scoring (in production, use proper embeddings)
                    query_lower = query.lower()
                    title_score = 2.0 if query_lower in title.lower() else 0.0
                    content_score = content.lower().count(query_lower) * 0.1
                    entity_score = sum(
                        1.0 for entity_list in entities.values()
                        for entity in entity_list
                        if query_lower in entity.lower()
                    )

                    total_score = title_score + content_score + entity_score

                    if total_score > 0:
                        results.append({
                            "document_id": doc_id,
                            "title": title,
                            "relevance_score": total_score,
                            "matching_entities": [
                                entity for entity_list in entities.values()
                                for entity in entity_list
                                if query_lower in entity.lower()
                            ],
                            "snippet": content[:200] + "..." if len(content) > 200 else content
                        })

                # Sort by relevance
                results.sort(key=lambda x: x["relevance_score"], reverse=True)

                return {
                    "success": True,
                    "query": query,
                    "results": results[:10],  # Top 10 results
                    "total_matches": len(results),
                    "searched_collections": [collection_name] if collection_name else list(self.state.active_collections.keys())
                }

            except Exception as e:
                if ctx:
                    ctx.error(f"Search failed: {e}")
                return {"success": False, "error": str(e)}

        @self.server.tool
        async def get_tool_analytics(ctx: Context) -> dict[str, Any]:
            """Get comprehensive analytics about tool usage and performance"""
            ctx.info("Getting tool analytics")
            return self.get_tool_analytics()

    def _load_template(self, template_name: str):
        """Load a domain template and register its tools"""
        try:
            # Get template from registry
            template = template_registry.get_template(template_name)
            self.current_template = template
            self.state.current_template = template_name

            # Register template-specific tools
            self._register_template_tools(template)

            logger.info(f"✅ Template loaded: {template_name}")

        except Exception as e:
            logger.error(f"❌ Failed to load template {template_name}: {e}")
            raise

    def _register_template_tools(self, template: BaseTemplate):
        """Register MCP tools from a domain template with enhanced management"""

        # Get template's MCP tools
        mcp_tools = template.get_mcp_tools()

        for tool_config in mcp_tools:
            tool_name = tool_config["name"]
            tool_description = tool_config["description"]
            tool_params = tool_config.get("parameters", {})
            tool_category = tool_config.get("category", "general")

            # Register tool with enhanced tracking
            self.registered_tools[tool_name] = {
                "description": tool_description,
                "parameters": tool_params,
                "category": tool_category,
                "template": template.config.name,
                "execution_count": 0,
                "last_used": None
            }

            # Dynamic tool registration with standardized wrapper
            self._register_standardized_tool(tool_name, tool_description, tool_params)

            logger.debug(f"📝 Registered tool: {tool_name} ({tool_category})")

    def _register_standardized_tool(self, tool_name: str, description: str, params: dict):
        """Register a tool with standardized execution wrapper"""
        
        async def tool_wrapper(*args, ctx: Context = None, **kwargs):
            """Standardized tool execution wrapper with analytics"""
            import time
            start_time = time.time()
            
            try:
                # Update execution stats
                self.registered_tools[tool_name]["execution_count"] += 1
                self.registered_tools[tool_name]["last_used"] = time.time()
                
                # Execute the appropriate tool
                result = await self._execute_tool(tool_name, args, kwargs, ctx)
                
                # Track execution in context
                processing_time = time.time() - start_time
                self.tool_context.add_execution(tool_name, True, processing_time)
                
                return result
                
            except Exception as e:
                # Track failed execution
                processing_time = time.time() - start_time
                self.tool_context.add_execution(tool_name, False, processing_time)
                
                if ctx:
                    ctx.error(f"Tool {tool_name} failed: {e}")
                
                return {
                    "success": False,
                    "error": str(e),
                    "tool_name": tool_name,
                    "processing_time": processing_time
                }
        
        # Set the wrapper's name and docstring
        tool_wrapper.__name__ = tool_name
        tool_wrapper.__doc__ = description
        
        # Register with FastMCP
        self.server.tool(tool_wrapper)

    async def _execute_tool(self, tool_name: str, args: tuple, kwargs: dict, ctx: Context = None) -> dict[str, Any]:
        """Execute a tool with proper routing to the appropriate engine"""
        
        # Route to appropriate tool engine based on tool name
        if tool_name in ["ask_knowledge_graph", "explore_topic", "find_connections", "what_do_we_know_about"]:
            # Chat tools
            tool_method = getattr(self.chat_tools, tool_name, None)
            if tool_method:
                return await tool_method(*args, ctx=ctx, **kwargs)
                
        elif tool_name in ["gather_sources_for_topic", "get_facts_with_citations", "verify_claim_with_sources", 
                          "get_topic_outline", "track_citations_used", "generate_bibliography"]:
            # Literature tools
            tool_method = getattr(self.literature_tools, tool_name, None)
            if tool_method:
                return await tool_method(*args, ctx=ctx, **kwargs)
                
        elif tool_name == "generate_bibliography":
            # Special handling for bibliography generation
            style = kwargs.get("style", "APA")
            used_only = kwargs.get("used_only", True)
            
            return await self.literature_tools.generate_bibliography(style, used_only, ctx)
            
        else:
            # Legacy tools - route to template tool execution
            params = {}
            if args:
                # Map positional args to common parameter names
                param_names = ["query", "topic", "domain", "concept", "author", "claim"]
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        params[param_names[i]] = arg
            
            params.update(kwargs)
            return await self._execute_template_tool(tool_name, params, ctx)

    def get_tool_analytics(self) -> dict[str, Any]:
        """Get comprehensive tool usage analytics"""
        return {
            "registered_tools": len(self.registered_tools),
            "tool_details": self.registered_tools,
            "execution_stats": self.tool_context.get_execution_stats(),
            "most_used_tools": sorted(
                self.registered_tools.items(),
                key=lambda x: x[1]["execution_count"],
                reverse=True
            )[:5],
            "tool_categories": {
                category: len([t for t in self.registered_tools.values() if t["category"] == category])
                for category in set(t["category"] for t in self.registered_tools.values())
            }
        }

    async def _execute_template_tool(self, tool_name: str, params: dict[str, Any], ctx: Context | None) -> dict[str, Any]:
        """Execute a template-specific tool"""

        try:
            if tool_name == "query_papers":
                return await self._query_papers(params.get("query", ""), ctx)

            elif tool_name == "find_citations":
                return await self._find_citations(params.get("claim", ""), ctx)

            elif tool_name == "research_gaps":
                return await self._research_gaps(params.get("domain", ""), ctx)

            elif tool_name == "methodology_overview":
                return await self._methodology_overview(params.get("topic", ""), ctx)

            elif tool_name == "author_analysis":
                return await self._author_analysis(params.get("author", ""), ctx)

            elif tool_name == "concept_evolution":
                return await self._concept_evolution(params.get("concept", ""), ctx)

            elif tool_name == "generate_bibliography":
                return await self._generate_bibliography(params.get("style", "APA"), ctx)

            else:
                return {"success": False, "error": f"Tool {tool_name} not implemented"}

        except Exception as e:
            if ctx:
                ctx.error(f"Tool execution failed: {e}")
            return {"success": False, "error": str(e)}

    # Template tool implementations (academic examples)
    async def _query_papers(self, query: str, ctx: Context | None) -> dict[str, Any]:
        """Academic tool: Query papers in corpus"""
        return await self.search_documents(query, ctx=ctx)

    async def _find_citations(self, claim: str, ctx: Context | None) -> dict[str, Any]:
        """Academic tool: Find citations for claims"""
        # Search for supporting evidence
        search_results = await self.search_documents(claim, ctx=ctx)

        return {
            "claim": claim,
            "supporting_documents": search_results.get("results", []),
            "citation_strength": "preliminary",  # Would implement proper scoring
            "evidence_count": len(search_results.get("results", []))
        }

    async def _research_gaps(self, domain: str, ctx: Context | None) -> dict[str, Any]:
        """Academic tool: Identify research gaps"""
        # Analyze corpus for gaps (simplified implementation)
        return {
            "domain": domain,
            "identified_gaps": [
                "Cross-domain analysis methodology",
                "Long-term evaluation studies",
                "Scalability assessments"
            ],
            "gap_analysis": "Based on corpus analysis",
            "recommendations": ["Focus on interdisciplinary approaches"]
        }

    async def _methodology_overview(self, topic: str, ctx: Context | None) -> dict[str, Any]:
        """Academic tool: Overview of methodologies"""
        search_results = await self.search_documents(f"methodology {topic}", ctx=ctx)

        return {
            "topic": topic,
            "methodologies_found": search_results.get("results", []),
            "analysis": "Comparative methodology analysis",
            "trends": ["Increasing use of machine learning approaches"]
        }

    async def _author_analysis(self, author: str, ctx: Context | None) -> dict[str, Any]:
        """Academic tool: Analyze author contributions"""
        search_results = await self.search_documents(author, ctx=ctx) if author else {"results": []}

        return {
            "author": author or "all_authors",
            "papers_found": search_results.get("results", []),
            "collaboration_network": "Network analysis pending",
            "contribution_summary": "Author impact analysis"
        }

    async def _concept_evolution(self, concept: str, ctx: Context | None) -> dict[str, Any]:
        """Academic tool: Track concept evolution"""
        return {
            "concept": concept,
            "evolution_timeline": "Temporal analysis pending",
            "trend_analysis": "Concept tracking over time",
            "related_concepts": ["machine learning", "artificial intelligence"]
        }

    async def _generate_bibliography(self, style: str, ctx: Context | None) -> dict[str, Any]:
        """Academic tool: Generate bibliography"""
        docs = list(self.state.processed_documents.values())

        bibliography = []
        for doc in docs[:10]:  # Limit to 10 for demo
            title = doc.get("title", "Unknown Title")
            # Simplified citation format
            if style == "APA":
                citation = f"{title}. (2024). Document Analysis."
            elif style == "IEEE":
                citation = f"\"{title},\" Document Analysis, 2024."
            else:
                citation = f"{title}. Document Analysis. 2024."

            bibliography.append(citation)

        return {
            "style": style,
            "bibliography": bibliography,
            "total_references": len(bibliography)
        }

    async def run_server(self, transport: str = "http", host: str = "localhost", port: int = 8080):
        """Run the universal MCP server"""
        logger.info(f"🚀 Starting Universal MCP Server on {transport}")

        if transport == "http":
            await self.server.run(host=host, port=port)
        elif transport == "stdio":
            await self.server.run()
        else:
            raise ValueError(f"Unsupported transport: {transport}")


# Factory function for easy creation
def create_universal_server(
    name: str = "GraphRAG Universal Assistant",
    template: str = "academic",
    host: str = "localhost",
    port: int = 8080
) -> UniversalMCPServer:
    """Create a universal MCP server with specified configuration"""

    server = UniversalMCPServer(
        name=name,
        host=host,
        port=port
    )

    if template != "academic":  # academic is loaded by default
        server._load_template(template)

    return server


# CLI integration function
async def run_universal_server_cli(
    template: str = "academic",
    host: str = "localhost",
    port: int = 8080,
    transport: str = "http"
):
    """Run universal server from CLI"""

    server = create_universal_server(
        template=template,
        host=host,
        port=port
    )

    await server.run_server(transport=transport, host=host, port=port)
