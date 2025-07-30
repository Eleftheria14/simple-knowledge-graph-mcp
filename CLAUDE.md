# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### System Management
```bash
# Complete system startup (recommended for development)
./scripts/start_system.sh

# System health and status check
./scripts/status_system.sh

# Complete system shutdown
./scripts/stop_system.sh

# Environment setup with UV package manager
./scripts/utilities/setup.sh
```

### MCP Server Operations
```bash
# Start MCP server for Claude Desktop integration
./scripts/mcp/start_mcp_for_claude.sh

# Start HTTP MCP server (web-based setup)
./scripts/mcp/start_http_server.sh

# Test MCP server functionality
cd src && uv run python server/main.py
cd src && uv run python server/main.py --http  # HTTP mode
```

### Database Management
```bash
# Clear all databases (fresh start)
./scripts/database/clear_databases.sh

# Start required services (Neo4j, Redis, MongoDB)
./scripts/system/start_services.sh

# Check database connections
./scripts/status_system.sh
```

### DocsGPT Integration
```bash
# Start complete DocsGPT system with knowledge graph
cd docsgpt-source/deployment && docker compose up -d

# Development mode (frontend + backend)
cd docsgpt-source/frontend && npm run dev  # Port 5173
cd docsgpt-source/application && python app.py  # Port 7091
```

### Testing and Validation
```bash
# Test import structure
cd src && uv run python -c "
from storage.neo4j import Neo4jStorage
from storage.chroma import ChromaDBStorage  
from server.main import mcp
print('✅ All imports successful')
"

# Test MCP tools registration
cd src && uv run python -c "from server.main import mcp; print(f'MCP server has {len(mcp._tools)} tools registered')"

# Test database connections
uv run python -c "from neo4j import GraphDatabase; import chromadb; print('✅ DB libraries work')"
```

## High-Level Architecture

### System Purpose
This is a **comprehensive document processing and knowledge graph system** designed to solve Claude Desktop conversation length limits when processing multiple research papers. It provides unlimited batch processing capabilities through multiple interfaces while maintaining complete local privacy.

### Multi-Interface Architecture
```
Claude Desktop ↔ MCP Server ↔ Knowledge Graph Tools ↔ Neo4j + ChromaDB
DocsGPT UI (5173) ↔ Flask Backend (7091) ↔ Knowledge Graph Bridge ↔ Storage Layer
n8n Workflows (5678) ↔ MCP Community Node ↔ Knowledge Graph MCP ↔ Databases
```

### Core Components

#### **MCP Knowledge Graph Server (`src/`)**
- **FastMCP Server**: `src/server/main.py` - Main orchestration with 8+ registered tools
- **Storage Layer**: Dual database strategy with Neo4j (graph) + ChromaDB (vector)
  - `src/storage/neo4j/` - Entity and relationship storage/queries
  - `src/storage/chroma/` - Vector storage with local embeddings
  - `src/storage/embedding/` - sentence-transformers integration
- **Tools Layer**: MCP tool implementations in `src/tools/`
  - `storage/` modules - Data persistence tools
  - `query/` modules - Data retrieval and literature generation tools

#### **DocsGPT Integration (`docsgpt-source/`)**
Professional document management UI with enhanced knowledge graph capabilities:
- **Custom Retriever**: `application/integrations/knowledge_graph_bridge.py`
- **Modified RAG Pipeline**: Bypasses default FAISS for Neo4j + ChromaDB queries
- **Batch Processing**: No conversation length limits for document collections

#### **Workflow Automation**
- **n8n Integration**: Community node enables workflow access to MCP tools
- **Batch Processing**: `workflows/` directory contains pre-built processing pipelines
- **Management Scripts**: Organized in `scripts/` by functionality (system, MCP, database, utilities)

### Technology Stack

#### **Core Technologies**
- **Python 3.11+** with UV package manager for fast dependency resolution
- **FastMCP** for Model Context Protocol server implementation
- **Neo4j** (Docker) for graph database storage
- **ChromaDB** for vector database with local sentence-transformers embeddings
- **Docker** for multi-service orchestration

#### **DocsGPT Stack**
- **React + TypeScript** frontend with Vite build system
- **Flask** RESTful API backend with Celery background processing
- **Redis** for caching and message broker
- **MongoDB** for user data and conversation storage

#### **AI/ML Components**
- **Local Embeddings**: sentence-transformers (privacy-first, no external APIs)
- **LlamaParse** for advanced PDF processing with premium parsing modes
- **Multi-LLM Support**: OpenAI, Anthropic, Google, Groq, local models

### Development Patterns

#### **Modular Tool Registration**
All MCP tools follow this pattern in `src/tools/`:
```python
def register_*_tools(mcp: FastMCP, *managers):
    @mcp.tool()
    def tool_name(params) -> Dict[str, Any]:
        # Tool implementation using injected managers
        pass
```

#### **Storage Abstraction**
- **Separate Classes**: Storage and query operations split (e.g., `Neo4jStorage` + `Neo4jQuery`)
- **Shared Dependencies**: `EmbeddingService` used across both Neo4j and ChromaDB
- **Dependency Injection**: Managers passed to tool registration functions

#### **Import Structure Requirements**
**Critical**: All imports within `src/` use absolute imports from package root:
```python
# Correct
from storage.neo4j import Neo4jStorage
from tools.storage.entity_storage import register_entity_tools

# Incorrect - causes import failures
from ..storage.neo4j import Neo4jStorage
```

### Configuration Management

#### **Environment Variables**
Primary configuration in `.env` (created from `.env.example`):
```bash
# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
CHROMADB_PATH=/path/to/chroma_db

# AI Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Local model, no API needed
LLAMAPARSE_API_KEY=llx-...  # Optional for advanced PDF processing
GROQ_API_KEY=gsk_...  # Optional for fast AI inference
```

#### **Service Dependencies**
**Required Services**:
- **Neo4j** (port 7474/7687): Graph database for entities and relationships
- **Redis** (port 6379): Caching, session storage, Celery broker
- **MongoDB** (port 27017): User data, conversations, document metadata

**Optional Services**:
- **n8n** (port 5678): Workflow automation platform
- **DocsGPT Frontend** (port 5173): Web UI for document management
- **DocsGPT Backend** (port 7091): Flask API server

### Entity Extraction Philosophy
The system uses **AI-driven flexible entity extraction** rather than rigid schemas:
- **Claude determines relevance** - No fixed entity types, adaptive to document domains
- **Confidence scoring** - All entities and relationships include confidence metrics (0.5-1.0)
- **Cross-domain compatibility** - Works for chemistry, computer science, biology, literature
- **Contextual relationships** - Include source text fragments for verification

### Privacy-First Design
- **Local embeddings** using sentence-transformers (no external API calls)
- **Local databases** via Docker containers or file-based storage
- **Zero API keys required** for core functionality
- **Optional external APIs** only for enhanced features (LlamaParse, LLM providers)
- **Complete offline operation** capability for document processing

### Multi-Mode Operation

#### **Interactive Mode (Claude Desktop)**
- Direct MCP integration with 8+ tools available
- Real-time document processing and knowledge graph queries
- HTTP and STDIO transport modes supported

#### **Batch Mode (n8n Workflows)**
- Automated processing of document collections
- No conversation length limits
- Pre-built workflows in `workflows/` directory

#### **Web UI Mode (DocsGPT)**
- Professional document management interface
- Custom retriever for knowledge graph integration
- Multi-user support with authentication

### Development Workflow

#### **Initial Setup**
1. Run `./scripts/utilities/setup.sh` for UV environment setup
2. Configure `.env` from `.env.example` template
3. Start services with `./scripts/start_system.sh`
4. Choose interface: Claude Desktop MCP, DocsGPT UI, or n8n workflows

#### **Adding New MCP Tools**
1. Create tool function in appropriate `src/tools/` module
2. Follow `register_*_tools(mcp, *managers)` pattern
3. Import and register in `src/server/main.py`
4. Test with component validation scripts

#### **Database Schema Evolution**
- **Neo4j**: Graph schema is dynamic, determined by AI entity extraction
- **ChromaDB**: Vector collections are automatically managed
- **Document metadata**: Stored with complete citation information for academic use

The system emphasizes **modularity, privacy, and extensibility** while providing both interactive and automated research capabilities through comprehensive MCP protocol integration.