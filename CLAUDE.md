# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Environment Setup
```bash
# Modern UV-based setup (RECOMMENDED - Python 3.11+)
./scripts/setup.sh

# Activate UV environment for manual commands
uv run python <command>
```

### Service Management
```bash
# Start required services (Neo4j)
./scripts/start_services.sh

# Check system status and connections
./scripts/check_status.sh

# Stop all services
./scripts/stop_services.sh
```

### MCP Server Operations
```bash
# Start HTTP MCP server (easy GUI setup)
./scripts/start_http_server.sh

# Start STDIO MCP server (advanced JSON config)
./scripts/start_mcp_server.sh

# Test specific components
uv run python -c "import sys; sys.path.insert(0, 'src'); from server.main import mcp; print('✅ Server imports work')"

# Manual server startup (for development)
cd src && uv run python server/main.py
cd src && uv run python server/main.py --http  # HTTP mode
```

### Database Management
```bash
# Clear all data (fresh start)
./scripts/clear_databases.sh

# Test database connections
uv run python -c "from neo4j import GraphDatabase; print('✅ Neo4j library works')"
```

### Testing and Validation
```bash
# Test import structure (Neo4j-only system)
cd src && uv run python -c "
from storage.neo4j import Neo4jStorage, Neo4jQuery
from tools.storage.entity_storage import register_entity_tools
from server.main import mcp
print('✅ All imports successful')
"

# Test MCP tools registration
cd src && uv run python -c "from server.main import mcp; print(f'MCP server has {len(mcp._tools)} tools registered')"

# Test LangChain ecosystem (if implementing document processor)
uv run python -c "from langchain_groq import ChatGroq; from langgraph.prebuilt import create_react_agent; print('✅ LangChain stack ready')"
```

## System Architecture

### Neo4j-Only Knowledge Graph MCP System
This is a **modular FastMCP server** that provides 5 core tools for building and querying knowledge graphs from documents. The system uses a unified Neo4j storage backend:

- **Neo4j**: Graph database for entities, relationships, and vector storage with local embeddings (sentence-transformers)

### Core MCP Tools Available
1. `store_entities` - Store entities and relationships in Neo4j graph database
2. `store_vectors` - Store any content as vectors with embeddings in Neo4j
3. `query_knowledge_graph` - Query Neo4j for both graph and vector search results
4. `generate_literature_review` - Format results for academic writing with citations
5. `clear_knowledge_graph` - Clear all data from Neo4j database

### Modular Architecture Pattern

#### Storage Layer (`src/storage/`)
```
storage/
├── neo4j/           # Graph database operations
│   ├── storage.py   # Entity, relationship, and vector storage
│   └── query.py     # Graph queries and traversal
└── embedding/       # Local embedding generation
    └── service.py   # sentence-transformers integration
```

#### Tools Layer (`src/tools/`)
```
tools/
├── storage/         # Data persistence tools
│   ├── entity_storage.py      # register_entity_tools()
│   ├── text_storage.py        # register_text_tools()  
│   └── database_management.py # register_management_tools()
└── query/           # Data retrieval tools
    ├── knowledge_search.py     # register_search_tools()
    └── literature_generation.py # register_literature_tools()
```

#### Server Layer (`src/server/`)
- `main.py` - FastMCP server orchestration and tool registration

#### Configuration (`src/config/`)
- `settings.py` - Environment variables and database configuration

### Tool Registration Pattern
Each tool module follows this pattern:
```python
def register_*_tools(mcp: FastMCP, *managers):
    @mcp.tool()
    def tool_name(params) -> Dict[str, Any]:
        # Tool implementation
        pass
```

The main server imports and registers all tools:
```python
# Initialize storage managers
neo4j_storage = Neo4jStorage()
neo4j_query = Neo4jQuery()

# Register tools from modules
register_entity_tools(mcp, neo4j_storage)
register_text_tools(mcp, neo4j_storage)  # Now uses Neo4j for vectors too
register_search_tools(mcp, neo4j_query, neo4j_storage)
```

### Import Structure Requirements
**Critical**: All imports within `src/` use absolute imports from the package root:
```python
# Correct
from storage.neo4j import Neo4jStorage
from tools.storage.entity_storage import register_entity_tools
import config

# Incorrect (relative imports cause issues)
from ..storage.neo4j import Neo4jStorage
from ...tools.storage.entity_storage import register_entity_tools
```

### Database Integration Pattern
The system uses separate storage and query classes for Neo4j operations:

**Neo4j Pattern**:
- `Neo4jStorage` - Handles entity, relationship, and vector storage with automatic embedding generation
- `Neo4jQuery` - Handles graph queries and relationship traversal

Both share the `EmbeddingService` for consistent vector generation across all storage types.

### Entity Extraction Philosophy
The system uses **flexible, AI-driven entity extraction** rather than rigid schemas:

1. **Claude determines relevance** - No fixed entity types or constraints
2. **Adaptive to document types** - Works across domains (chemistry, CS, biology, etc.)
3. **Confidence scoring** - All entities and relationships include confidence metrics
4. **Contextual relationships** - Relationships include source context for verification

See `src/prompts/entity_extraction.md` for detailed guidance patterns.

### Development Workflow
1. **Code changes**: Work within the `src/` directory structure
2. **Test imports**: Use `uv run python` from project root with `sys.path.insert(0, 'src')`
3. **Server testing**: Always test from `src/` directory: `cd src && uv run python server/main.py`
4. **Production deployment**: Use `./scripts/start_mcp_server.sh` which handles paths correctly

### Configuration Management
- Environment variables in `.env` file
- Required: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- Required for document processor: `GROQ_API_KEY`, `LLAMAPARSE_API_KEY`
- Optional: `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` (for LangSmith monitoring)
- Embedding model configurable via `EMBEDDING_MODEL`
- Citation styles: APA, IEEE, Nature, MLA (in `config.CITATION_STYLES`)

### Architecture Design
- **Core MCP tools** - Interactive knowledge graph operations via Claude Desktop
- **Document processor** - Automated PDF processing pipeline (planned)
- **Local embeddings** - sentence-transformers for privacy
- **Unified storage** - Neo4j for both graph and vectors
- **Extensible** - Add new processors or storage backends easily

## Common Development Patterns

### Adding New MCP Tools
1. Create tool function in appropriate module (`tools/storage/` or `tools/query/`)
2. Follow the `register_*_tools(mcp, *managers)` pattern
3. Import and register in `src/server/main.py`
4. Use absolute imports within `src/`

### Database Manager Development
1. Neo4j storage handles both graph operations and vector storage
2. Share `EmbeddingService` between storage and query classes  
3. Use dependency injection pattern in tool registration
4. Vector storage uses `TextVector` nodes with embedding arrays

### Testing New Components
```bash
# Test individual storage components
cd src && uv run python -c "from storage.neo4j import Neo4jStorage; print('Neo4j ready')"

# Test tool registration
cd src && uv run python -c "from tools.storage.entity_storage import register_entity_tools; print('Tools ready')"

# Test full server
./scripts/start_mcp_server.sh

# Test vector storage
cd src && uv run python -c "from storage.neo4j import Neo4jStorage; s = Neo4jStorage(); print('Vector storage ready')"
```

## LangGraph Document Processing Pipeline

### Architecture Overview
The system includes an intelligent document processing orchestrator using LangGraph:

```
Watch Folder → LangGraph Agent → LlamaParse → Entity/Citation Extraction → Neo4j Storage
```

### Modern LangChain Stack
The document processor uses the modern LangChain ecosystem:
- **LangGraph**: Stateful orchestration with intelligent decision-making
- **Groq**: Fast AI inference (Llama 3.1 70B) for orchestration decisions
- **LangSmith**: Production monitoring, tracing, and cost analysis
- **LlamaParse**: Premium PDF processing for complex documents

### Tech Stack Dependencies
```toml
# Core LangChain Ecosystem
"langchain>=0.3.0"        # Core framework
"langgraph>=0.2.0"        # Stateful orchestration  
"langchain-groq>=0.2.0"   # Groq LLM integration
"langsmith>=0.1.0"        # Production monitoring

# Document Processing
"llamaparse>=0.5.0"       # Premium PDF extraction
"watchdog>=3.0.0"         # Folder monitoring
```

### Agent Architecture Pattern
```python
# Modern LangGraph pattern
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

agent = create_react_agent(
    model=ChatGroq(model="llama-3.1-70b-versatile"),
    tools=[llamaparse_pdf, extract_citations, store_in_neo4j],
    checkpointer=MemorySaver()
)
```

### Processing Tools Structure
```
src/processor/
├── document_pipeline.py    # LangGraph orchestrator
├── tools/
│   ├── llamaparse_tool.py  # PDF processing tool
│   ├── citation_tool.py    # Citation extraction
│   └── storage_tool.py     # Neo4j integration
└── folder_watcher.py       # File system monitoring
```

### Key Design Decisions
- **LLM-driven orchestration**: Agent makes intelligent processing decisions rather than linear workflows
- **Reuse existing Neo4j storage** from MCP tools
- **Streaming processing**: Real-time feedback via LangGraph
- **Comprehensive monitoring**: LangSmith tracks all operations, costs, and performance
- **Tool integration**: Document processor tools integrate seamlessly with MCP tools

## Project Context

This is a **production-ready MCP toolkit** for building knowledge graphs from documents using Claude Desktop. The system enables researchers to:

1. **Interactive mode**: Upload PDFs to Claude Desktop for immediate analysis
2. **Automated mode**: Watch folders for automatic document processing (planned)
3. Extract entities and relationships via natural language
4. Store everything in Neo4j (both graph and vector data)
5. Query the knowledge base for research insights and connections
6. Generate formatted literature reviews with citations

The architecture emphasizes **simplicity, modularity, and unified storage** while providing both interactive and automated research capabilities through comprehensive MCP protocol integration.