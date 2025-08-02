# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Environment Setup
```bash
# Modern UV-based setup (RECOMMENDED - Python 3.11+)
./scripts/setup.sh

# Start required services (Neo4j + GROBID)
./scripts/start_services.sh

# Start GROBID service for academic PDF processing
docker run -d --name grobid -p 8070:8070 lfoppiano/grobid:0.8.0

# Activate UV environment for manual commands
uv run python <command>
```

### Academic Document Processing
```bash
# Process PDFs using GROBID for superior academic extraction
python process_literature.py

# Test GROBID service status
curl http://localhost:8070/api/isalive

# Test GROBID extraction on single PDF
uv run python -c "
import sys; sys.path.insert(0, 'src')
from processor.tools.grobid_tool import grobid_extract
result = grobid_extract.invoke({'file_path': 'Literature/test.pdf'})
print('Success:', result.get('success'))
print('Authors:', len(result.get('metadata', {}).get('authors', [])))
"
```

### MCP Server Operations  
```bash
# Start HTTP MCP server (easy GUI setup)
./scripts/start_http_server.sh

# Start STDIO MCP server (advanced JSON config)
./scripts/start_mcp_server.sh

# Test MCP server with current tools
cd src && uv run python -c "from server.main import mcp; print(f'MCP server has {len(mcp._tools)} tools registered')"

# Manual server startup (for development)
cd src && uv run python server/main.py
cd src && uv run python server/main.py --http  # HTTP mode
```

### Database Management
```bash
# Clear all data (fresh start)
./scripts/clear_databases.sh

# Check Neo4j data
uv run python -c "
import sys; sys.path.insert(0, 'src')
from neo4j import GraphDatabase; import config
driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD))
with driver.session() as session:
    result = session.run('MATCH (n) RETURN labels(n) as labels, count(*) as count ORDER BY count DESC LIMIT 5')
    for record in result: print(f'{record[\"labels\"]}: {record[\"count\"]} nodes')
driver.close()
"
```

### System Validation
```bash
# Test core imports and tool registry
cd src && uv run python -c "
from tools.shared_registry import SharedToolRegistry
tools = SharedToolRegistry.get_all_tools()
print(f'✅ Available tools: {[t.name for t in tools]}')
"

# Test LangGraph document pipeline
uv run python -c "from langchain_groq import ChatGroq; from langgraph.prebuilt import create_react_agent; print('✅ LangChain stack ready')"

# Validate Neo4j and GROBID integration  
uv run python -c "
import sys; sys.path.insert(0, 'src')
from storage.neo4j import Neo4jStorage, Neo4jQuery
from processor.tools.grobid_tool import GrobidProcessor
print('✅ Neo4j storage:', Neo4jStorage())
print('✅ GROBID service:', GrobidProcessor().is_alive())
"
```

## System Architecture

### GROBID-Powered Academic Knowledge Graph System
This is a **dual-mode MCP system** combining interactive knowledge graph tools with automated academic document processing. The system uses Neo4j for unified storage and GROBID for superior academic PDF extraction.

**Core Components:**
- **Neo4j**: Graph database for entities, relationships, and vector storage with local embeddings
- **GROBID**: Academic PDF processing service (Docker) for extracting structured research data
- **LangGraph**: Intelligent document orchestration for automated processing workflows
- **FastMCP**: Server providing 5 core tools for Claude Desktop integration

### Current MCP Tools Available
1. `extract_and_store_entities` - Enhanced entity extraction with academic focus
2. `store_vectors` - Store text chunks as vectors with embeddings in Neo4j
3. `query_knowledge_graph` - Search both graph and vector data for comprehensive results
4. `generate_literature_review` - Format academic results with proper citations
5. `clear_knowledge_graph` - Reset all data for fresh start

### Academic Processing Pipeline
```
PDF → GROBID → Structured Academic Data → LangGraph Agent → Neo4j Storage
```
- **Authors/Affiliations**: Extracted with institutional relationships
- **Citations/References**: Parsed bibliographic networks  
- **Academic Structure**: Sections, abstracts, methodologies preserved
- **Tables/Figures**: Content with captions and context

### Modular Architecture Pattern

#### Storage Layer (`src/storage/`)
```
storage/
├── neo4j/           # Unified graph and vector database
│   ├── storage.py   # Entities, relationships, and vector storage
│   └── query.py     # Graph queries and semantic search
└── embedding/       # Local embedding generation
    └── service.py   # sentence-transformers integration (privacy-focused)
```

#### Tools Layer (`src/tools/`)
```
tools/
├── storage/         # Data persistence tools
│   ├── enhanced_entity_storage.py   # Academic entity extraction
│   ├── neo4j_vector_storage.py      # Vector storage in Neo4j
│   └── database_management.py       # Database operations
├── query/           # Data retrieval tools
│   ├── knowledge_search.py          # Graph + vector search
│   └── literature_generation.py     # Academic formatting
└── shared_registry.py               # Dual MCP/LangChain tool registry
```

#### Academic Processing Layer (`src/processor/`)
```  
processor/
├── document_pipeline.py        # LangGraph orchestrator
├── tools/
│   ├── grobid_tool.py          # GROBID academic PDF extraction
│   └── storage_tool.py         # Neo4j integration for pipeline
├── config.py                   # Processing configuration
├── orchestrator_config.py      # Workflow definitions
└── entity_extractor_config.py  # Academic extraction settings
```

#### Server Layer (`src/server/`)
- `main.py` - FastMCP server with all MCP tools registered

#### Configuration (`src/config/`)
- `settings.py` - Environment variables and database configuration

### Dual Tool Registry Pattern
The system supports both MCP and LangChain tools through a shared registry:

```python
# Shared registry for both MCP and LangChain usage
from tools.shared_registry import SharedToolRegistry

# Get tools for LangChain agents (document processing)
langchain_tools = SharedToolRegistry.get_all_tools()
# Returns: [grobid_extract, extract_and_store_entities, store_vectors]

# Register tools with MCP server (Claude Desktop integration)
SharedToolRegistry.register_with_mcp(mcp, neo4j_storage, neo4j_query)
```

**Tool Architecture Benefits:**
```python
@tool  # LangChain decorator
def grobid_extract(file_path: str) -> Dict[str, Any]:
    """Extract academic content using GROBID"""
    # Works in both LangGraph agents AND as MCP tool
    return grobid_processor.process_fulltext(file_path)
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
**Required Environment Variables (`.env` file):**
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` - Neo4j database connection
- `GROQ_API_KEY` - Required for LLM-based entity extraction and orchestration

**Optional Configurations:**
- `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` - LangSmith monitoring
- `EMBEDDING_MODEL` - Local embedding model (default: all-MiniLM-L6-v2)
- Citation styles: APA, IEEE, Nature, MLA (in `config.CITATION_STYLES`)

**Academic Processing Configs (`configs/`):**
- `orchestrator_grobid.yaml` - GROBID-powered document processing workflows
- `entity_extractor_academic.yaml` - Academic entity extraction settings

### Architecture Design Principles
- **Academic-focused** - GROBID provides superior research paper understanding vs generic PDF tools
- **Dual-mode operation** - Interactive MCP tools + automated LangGraph processing
- **Privacy-first** - Local embeddings, self-hosted GROBID, no external APIs for PDF processing  
- **Unified storage** - Neo4j handles both graph entities and vector embeddings
- **Zero API costs** - GROBID replaces expensive services like LlamaParse

## Recommended Icon Libraries

### For Web/UI Development
**Primary Recommendations:**
1. **Lucide** - Clean outlined icons, 1000+ icons, excellent React/Vue support
2. **Heroicons** - Tailwind's official set, outline/solid variants, web-optimized
3. **Phosphor Icons** - Largest collection (7000+), multiple weights, great variety
4. **Tabler Icons** - 4000+ free SVG icons, consistent design system
5. **Feather Icons** - Minimalist outlined icons, lightweight and simple

**Comprehensive Collections:**
6. **React Icons** - Meta-library combining FontAwesome, Feather, Material, etc.
7. **Material Design Icons** - Google's comprehensive system, familiar UX patterns
8. **Remix Icon** - 2000+ neutral-style icons, good for business apps
9. **Bootstrap Icons** - 1800+ icons, works well with Bootstrap framework
10. **Iconify** - Unified access to 100+ icon sets, massive selection

**Platform-Specific:**
- **SF Symbols** - Apple's system icons (macOS/iOS apps)
- **Fluent UI Icons** - Microsoft's design system
- **Ant Design Icons** - For Ant Design React projects

**Selection Criteria:** Consider your framework (React/Vue/vanilla), design style (outlined/filled), bundle size requirements, and whether you need academic/technical specific icons.

**For Academic Projects:** Lucide or Heroicons provide the cleanest, most professional appearance that complements research-focused interfaces.

## Common Development Patterns

### Adding Dual-Purpose Tools (MCP + LangChain)
1. Create tool with `@tool` decorator in appropriate module
2. Add to `SharedToolRegistry.get_all_tools()` for LangChain access
3. Register with MCP via `SharedToolRegistry.register_with_mcp()`
4. Test both modes: LangGraph agents and MCP server

### GROBID Integration Pattern
```python
from processor.tools.grobid_tool import GrobidProcessor

# Check service availability
processor = GrobidProcessor()
if not processor.is_alive():
    # Start GROBID: docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0
    
# Process academic PDFs
result = processor.process_fulltext(pdf_path)
# Returns: structured academic data (authors, citations, content)
```

### Academic Workflow Configuration
```yaml
# configs/orchestrator_grobid.yaml
tools:
  enabled_tools:
    - grobid_extract              # Academic PDF processing  
    - extract_and_store_entities  # Entity extraction
    - store_vectors              # Vector storage
```

### Testing Academic Processing
```bash
# Test GROBID extraction
uv run python -c "
import sys; sys.path.insert(0, 'src')
from processor.tools.grobid_tool import grobid_extract
result = grobid_extract.invoke({'file_path': 'Literature/test.pdf'})
print('Title:', result.get('metadata', {}).get('title', 'Unknown'))
print('Authors:', len(result.get('metadata', {}).get('authors', [])))
"

# Test complete academic workflow  
python process_literature.py

# Verify Neo4j data storage
uv run python -c "
import sys; sys.path.insert(0, 'src')
from neo4j import GraphDatabase; import config
driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD))
with driver.session() as session:
    result = session.run('MATCH (tv:TextVector) RETURN count(*) as count')
    print('TextVectors stored:', result.single()['count'])
driver.close()
"
```

## GROBID-Powered Document Processing 

### Academic Processing Architecture
The system uses LangGraph for intelligent academic document orchestration:

```
PDF → GROBID (Docker) → Structured Academic Data → LangGraph Agent → Neo4j Storage
```

### Modern Academic Processing Stack
- **GROBID**: Self-hosted academic PDF parsing (87-90% F1-score accuracy)
- **LangGraph**: Stateful orchestration with intelligent academic workflows
- **Groq**: Fast LLM inference (Llama 3.1 8B) for entity extraction decisions
- **Neo4j**: Unified storage for both graph entities and vector embeddings
- **Local Embeddings**: sentence-transformers for complete privacy

### Current Dependencies
```toml
# Core LangChain Ecosystem
"langchain>=0.3.0"        # Core framework
"langgraph>=0.2.0"        # Stateful orchestration  
"langchain-groq>=0.2.0"   # Groq LLM integration
"langsmith>=0.1.0"        # Production monitoring

# Academic Processing (GROBID-based)
"requests>=2.31.0"        # GROBID API communication
"watchdog>=3.0.0"         # Folder monitoring
```

### Academic Agent Pattern
```python
# GROBID-powered LangGraph agent
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from tools.shared_registry import SharedToolRegistry

agent = create_react_agent(
    model=ChatGroq(model="llama-3.1-8b-instant"),
    tools=SharedToolRegistry.get_all_tools(),  # [grobid_extract, extract_and_store_entities, store_vectors]
    checkpointer=MemorySaver()
)
```

### Processing Workflow
1. **GROBID Extraction**: Structured academic data (authors, citations, abstracts)  
2. **Entity Analysis**: LLM extracts academic relationships and concepts
3. **Vector Storage**: Text chunks with academic context preserved
4. **Knowledge Graph**: Authors, papers, and concepts linked in Neo4j

## Project Context

This is a **GROBID-powered academic research toolkit** that transforms research papers into queryable knowledge graphs via Claude Desktop. The system specializes in academic document processing and provides superior citation network analysis.

### Core Capabilities
1. **Academic PDF Processing**: GROBID extracts structured data (authors, affiliations, citations) with 87-90% accuracy
2. **Interactive MCP Mode**: Upload PDFs to Claude Desktop for immediate academic analysis  
3. **Automated Processing**: LangGraph workflows for batch academic document processing
4. **Knowledge Graph Storage**: Authors, papers, concepts, and citations stored in Neo4j
5. **Semantic Search**: Vector embeddings enable cross-paper concept discovery
6. **Literature Reviews**: Generate formatted academic reviews with proper citations

### Academic Focus
- **Research Paper Optimization**: Built specifically for academic papers vs generic documents
- **Citation Network Analysis**: Maps author collaborations and paper relationships  
- **Institutional Tracking**: University and research organization affiliations
- **Zero API Costs**: Self-hosted GROBID eliminates expensive PDF processing fees
- **Privacy-First**: Local processing ensures research data stays confidential

The system transforms academic document collections into intelligent, queryable knowledge bases that reveal hidden connections and research patterns across papers, authors, and institutions.