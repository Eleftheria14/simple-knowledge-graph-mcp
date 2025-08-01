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

### n8n Workflow Automation
```bash
# Start n8n for batch processing workflows
./scripts/n8n_manager.sh start

# Start n8n MCP documentation server (Claude Code integration)
./scripts/n8n_mcp_server.sh start

# Check n8n status
./scripts/n8n_manager.sh status

# View n8n logs
./scripts/n8n_manager.sh logs

# Stop n8n
./scripts/n8n_manager.sh stop

# Access n8n web interface at http://localhost:5678
# Login: admin / password123

# Manage Claude Code MCP integration
claude mcp list                    # List configured MCP servers
claude mcp add-json <name> <json>   # Add MCP server configuration
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
uv run python -c "from neo4j import GraphDatabase; import chromadb; print('✅ DB libraries work')"
```

### Testing and Validation
```bash
# Test import structure
cd src && uv run python -c "
from storage.neo4j import Neo4jStorage, Neo4jQuery
from storage.chroma import ChromaDBStorage, ChromaDBQuery  
from tools.storage.entity_storage import register_entity_tools
from server.main import mcp
print('✅ All imports successful')
"

# Test MCP tools registration
cd src && uv run python -c "from server.main import mcp; print(f'MCP server has {len(mcp._tools)} tools registered')"
```

## System Architecture

### Dual-Mode Knowledge Graph MCP System
This is a **modular FastMCP server** that provides 5 core tools for building and querying knowledge graphs from documents. The system uses two complementary storage backends:

- **Neo4j**: Graph database for entities, relationships, and semantic connections
- **ChromaDB**: Vector database for any content with local embeddings (sentence-transformers)

### Core MCP Tools Available
1. `store_entities` - Store entities and relationships in Neo4j graph database
2. `store_vectors` - Store any content as vectors with embeddings in ChromaDB
3. `query_knowledge_graph` - Query both databases for comprehensive research results
4. `generate_literature_review` - Format results for academic writing with citations
5. `clear_knowledge_graph` - Clear all data from both databases

### Modular Architecture Pattern

#### Storage Layer (`src/storage/`)
```
storage/
├── neo4j/           # Graph database operations
│   ├── storage.py   # Entity and relationship storage
│   └── query.py     # Graph queries and traversal
├── chroma/          # Vector database operations  
│   ├── storage.py   # Text storage with embeddings
│   └── query.py     # Semantic search and retrieval
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
chromadb_storage = ChromaDBStorage()

# Register tools from modules
register_entity_tools(mcp, neo4j_storage)
register_text_tools(mcp, chromadb_storage)
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
The system uses separate storage and query classes for each database:

**Neo4j Pattern**:
- `Neo4jStorage` - Handles entity and relationship persistence
- `Neo4jQuery` - Handles graph queries and relationship traversal

**ChromaDB Pattern**:
- `ChromaDBStorage` - Handles text storage with automatic embedding generation
- `ChromaDBQuery` - Handles semantic search and citation retrieval

Both share the `EmbeddingService` for consistent vector generation.

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
- Environment variables in `.env` (created from `.env.example`)
- Database URIs configurable via `NEO4J_URI`, `CHROMADB_PATH`
- Embedding model configurable via `EMBEDDING_MODEL`
- Citation styles: APA, IEEE, Nature, MLA (in `config.CITATION_STYLES`)

### Local-First Design
- **No external API dependencies** - All LLM processing via Claude Desktop/ChatGPT
- **Local embeddings** - sentence-transformers for privacy
- **Local databases** - Neo4j via Docker, ChromaDB as files
- **Zero API keys required** - Complete offline operation capability

## Common Development Patterns

### Adding New MCP Tools
1. Create tool function in appropriate module (`tools/storage/` or `tools/query/`)
2. Follow the `register_*_tools(mcp, *managers)` pattern
3. Import and register in `src/server/main.py`
4. Use absolute imports within `src/`

### Database Manager Development
1. Separate storage and query operations into different classes
2. Share common dependencies (like `EmbeddingService`) between related classes
3. Use dependency injection pattern in tool registration

### Testing New Components
```bash
# Test individual storage components
cd src && uv run python -c "from storage.neo4j import Neo4jStorage; print('Neo4j ready')"

# Test tool registration
cd src && uv run python -c "from tools.storage.entity_storage import register_entity_tools; print('Tools ready')"

# Test full server
./scripts/start_mcp_server.sh

# Test n8n MCP integration
claude mcp list  # Verify n8n-docs server is configured
```

### n8n Workflow Development
```bash
# Import workflow template into n8n
# 1. Open http://localhost:5678
# 2. Menu (3 dots) → Import from File
# 3. Select n8n_hello_world_workflow.json

# Test MCP community node in n8n workflows
# Configure MCP node with:
# Transport: stdio
# Command: uv
# Args: ["run", "python", "src/server/main.py"]
# Working Directory: /Users/[user]/Agents
```

## n8n Batch Processing Integration

### Dual-Mode Operation
The system now operates in two complementary modes:

1. **Interactive Mode (Claude Desktop)**: Manual document processing via MCP tools
2. **Batch Mode (n8n Workflows)**: Automated batch processing of multiple documents

### n8n MCP Integration Architecture
```
Interactive: Claude Desktop ←→ Knowledge Graph MCP ←→ Neo4j + ChromaDB
Batch:       n8n Workflows ←→ MCP Community Node ←→ Knowledge Graph MCP ←→ Neo4j + ChromaDB
```

### Key n8n Integration Components
- **n8n MCP Documentation Server**: Provides Claude Code with expert n8n knowledge
- **n8n MCP Community Node**: Enables n8n workflows to call your MCP tools directly
- **Batch Processing Workflows**: Automated PDF processing, entity extraction, and knowledge graph building

### Branch Structure
- **main**: Stable interactive MCP system
- **feature/n8n-batch-processing**: n8n integration development (current)

### Workflow Templates
Pre-built n8n workflow files available:
- `n8n_hello_world_workflow.json`: Basic test workflow
- Comprehensive batch processing workflow in planning docs

## Entity Extraction System

### AI-Driven Flexible Schema
The system uses **Claude-determined entity extraction** rather than rigid schemas:

- **Adaptive categorization**: No fixed entity types - Claude determines relevance
- **Cross-domain compatibility**: Works for chemistry, CS, biology, literature, etc.
- **Confidence scoring**: All entities and relationships include confidence metrics (0.5-1.0)
- **Contextual relationships**: Include source text fragments for verification
- **Complete citation requirements**: Mandatory bibliographic data for academic papers

### Extraction Process
Follows the comprehensive prompt in `ENTITY_EXTRACTION_PROMPT.md`:
1. **Citation entity creation** (mandatory first step)
2. **Entity identification** with descriptive IDs
3. **Relationship mapping** with contextual evidence
4. **Complete text storage** with systematic chunking
5. **Validation** of entity-relationship consistency

## Project Context

This is a **production-ready MCP toolkit** for building knowledge graphs from documents using Claude Desktop or n8n workflows. The system enables researchers to:

1. **Interactive Processing**: Upload PDFs to Claude Desktop for immediate analysis
2. **Batch Processing**: Use n8n workflows for automated processing of document collections
3. **Dual Storage**: Store in both graph (Neo4j) and vector (ChromaDB) databases
4. **Intelligent Querying**: Query knowledge base for research insights and connections
5. **Academic Output**: Generate formatted literature reviews with proper citations

The architecture emphasizes **simplicity, modularity, and local privacy** while providing both interactive and automated research capabilities through comprehensive MCP protocol integration.