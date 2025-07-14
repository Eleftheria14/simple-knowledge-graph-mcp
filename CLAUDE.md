# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Environment Setup
```bash
# Modern Python 3.11+ environment (RECOMMENDED)
source graphiti-env/bin/activate

# Legacy Python 3.9 environment (for compatibility)
source langchain-env/bin/activate

# Install dependencies with UV (faster)
uv pip install -r requirements.txt

# Development setup with all tools
make install-dev
make dev  # Complete development environment setup
```

### Build System Commands (Makefile)
```bash
# Installation
make install          # Production install
make install-dev      # Development install with all dependencies

# Code Quality
make lint            # Run ruff, black, mypy
make format          # Format code with black, ruff, isort
make check-format    # Check formatting without changes
make type-check      # Run mypy type checking
make security        # Run bandit and safety checks
make pre-commit      # Run all pre-commit hooks
make quality         # Run all quality checks (lint + type-check + security)

# Testing
make test            # Run tests with coverage
make test-quick      # Quick test run without coverage

# Single test commands
uv run pytest tests/test_specific.py -v              # Run specific test file
uv run pytest tests/test_specific.py::test_func -v  # Run specific test function
uv run pytest tests/ -k "test_pattern" -v           # Run tests matching pattern
uv run pytest tests/ -m "unit" -v                   # Run tests with specific marker

# Environment Setup
make setup-ollama    # Install Ollama models (llama3.1:8b, nomic-embed-text)
make setup-neo4j     # Start Neo4j Docker container
make clear-db        # Clear all ChromaDB databases
make tutorial        # Start tutorial system

# Documentation & Build
make docs            # Build documentation with mkdocs
make docs-serve      # Serve documentation locally
make build           # Build package with uv
make publish         # Publish to PyPI
make publish-test    # Publish to test PyPI
make clean           # Clean build artifacts

# Development Workflow
make dev             # Complete development setup (install-dev + pre-commit-install)
make ci              # Simulate CI pipeline (clean + install-dev + quality + test)
```

### CLI Commands (graphrag-mcp)
```bash
# Primary MCP Server Commands
graphrag-mcp serve-universal --template academic --transport stdio  # Universal MCP server
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio

# Template Management
graphrag-mcp templates --list              # List available templates
graphrag-mcp templates --info academic     # Get template details

# Status & Health
graphrag-mcp status                        # System status
curl -s http://localhost:11434/api/tags    # Check Ollama status
curl -f http://localhost:7474/             # Check Neo4j status

# Testing Commands
python3 -c "from graphrag_mcp.core import DocumentProcessor; print('✅ Core ready')"
python3 -c "from graphrag_mcp.core.graphiti_engine import create_graphiti_knowledge_graph; import asyncio; asyncio.run(create_graphiti_knowledge_graph())"
```

### Required Services Setup
```bash
# Ollama Setup (Required)
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve

# Verify Ollama is running
curl -s http://localhost:11434/api/tags

# Neo4j Setup (Required for Graphiti)
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

# Verify Neo4j is running
curl -f http://localhost:7474/
# Access Neo4j Browser: http://localhost:7474 (neo4j/password)
```

### MCP Integration Testing
```bash
# Claude Desktop Configuration Example
# Add to ~/.config/claude-desktop/config.json:
{
  "mcpServers": {
    "graphrag-research": {
      "command": "python3",
      "args": ["-m", "graphrag_mcp.cli.main", "serve-universal", "--template", "academic", "--transport", "stdio"],
      "cwd": "/path/to/project"
    }
  }
}

# Test MCP server manually
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio

# Database Reset
./clear_chromadb.sh
```

## System Architecture

### Core Architecture: Universal MCP Server with Template System
This is a **GraphRAG MCP Toolkit** that provides domain-specific AI capabilities to Claude via the Model Context Protocol:

- **Universal MCP Server**: Single FastMCP server that adapts to different domains via templates
- **Template System**: Domain-specific configurations (academic, legal, medical, financial, etc.)
- **Local Processing**: All document analysis via Ollama (privacy-first, no external APIs)
- **Knowledge Graphs**: Graphiti integration for real-time graph construction and Neo4j persistence

### Modern Component Architecture

#### Core Package Structure (`graphrag_mcp/`)
```
graphrag_mcp/
├── cli/                       # Typer-based CLI with rich output
│   └── main.py               # Entry point: graphrag-mcp command
├── core/                     # Domain-agnostic processing engine
│   ├── analyzer.py           # AdvancedAnalyzer for enhanced document analysis
│   ├── chat_engine.py        # ChatEngine for RAG + Graph queries
│   ├── document_processor.py # PDF processing and text chunking
│   ├── graphiti_engine.py    # Graphiti integration for knowledge graphs
│   └── ollama_engine.py      # Local LLM integration layer
├── mcp/                      # MCP server generation
│   ├── graphiti_server.py    # Graphiti-powered MCP server
│   └── server_generator.py   # FastMCP server builder
├── templates/                # Domain-specific configurations
│   ├── academic.py           # Literature review template
│   └── base.py               # Base template class
└── visualization/            # Graph visualization
    └── graphiti_yfiles.py    # yFiles professional graphs
```

#### Legacy Components (Migration in Progress)
- **`src/`**: Original research components being refactored into `graphrag_mcp/`
- **`notebooks/`**: Interactive Jupyter interfaces for development and testing
- **`tutorial/`**: 5-part tutorial system for learning the platform

### MCP Server Data Flow
```
Documents → Processing → Knowledge Graph → MCP Tools → Claude Integration
    ↓            ↓             ↓              ↓              ↓
  PDF/Text → Entities → Graphiti/Neo4j → Template Tools → Claude Assistant
```

**Key MCP Tools Provided:**
- `list_templates` - Available domain templates
- `switch_template` - Change domain focus  
- `load_document_collection` - Process document sets
- `search_documents` - Semantic search across corpus
- `query_papers` (academic) - Literature search
- `find_citations` (academic) - Citation discovery
- `research_gaps` (academic) - Gap identification

### Key Implementation Patterns

#### MCP Server as Domain Bridge
The system acts as a **bridge between Claude and domain-specific knowledge**:
1. **Document Processing**: PDF → Chunks → Entities → Knowledge Graph
2. **Template Application**: Domain-specific entity extraction and tool configuration  
3. **MCP Tool Registration**: FastMCP server exposes domain tools to Claude
4. **Real-time Interaction**: Claude calls tools, server returns structured data
5. **Knowledge Synthesis**: Claude processes tool results into final outputs

#### Template Development Pattern
```python
# Creating new domain templates
class NewDomainTemplate(BaseTemplate):
    def get_entity_schema(self) -> Dict[str, str]:
        # Domain guidance for entity extraction
        
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        # Define domain-specific MCP tools
```

## Key Implementation Details

### Modern Development Stack
- **Framework**: Python 3.11+, FastMCP, Typer, Pydantic
- **LLM Integration**: Ollama (llama3.1:8b, nomic-embed-text) for local privacy
- **Knowledge Graphs**: Graphiti with Neo4j persistence
- **Vector Storage**: ChromaDB for semantic search
- **Code Quality**: Black, Ruff, MyPy, Pre-commit hooks
- **Testing**: Pytest with coverage reporting
- **Documentation**: MkDocs with Material theme

### Database Management
```bash
# Clear all ChromaDB databases (fresh start)
./clear_chromadb.sh

# Database locations:
# - chroma_graph_db/          # Main GraphRAG database
# - tutorial/chroma_*_db/     # Tutorial databases  
# - notebooks/chroma_db/      # Notebook databases
```

### Development Workflow
```bash
# Setup development environment
make dev              # Install dependencies + pre-commit hooks

# Development cycle
make format           # Format code (black, ruff, isort)
make lint            # Check code quality (ruff, black, mypy)
make type-check      # Type checking (mypy)
make test            # Run tests with coverage
make pre-commit      # Run all pre-commit hooks

# Quality assurance
make quality         # Run lint + type-check + security
make ci              # Full CI simulation
```

## Common Development Patterns

### Adding New Domain Templates
1. **Create template class**: Inherit from `BaseTemplate` in `templates/`
2. **Define entity types**: Specify domain-specific entities and relationships
3. **Configure extraction**: Set up LLM prompts for domain knowledge
4. **Add MCP tools**: Define domain-specific functions for the MCP server
5. **Test and validate**: Verify template works with sample documents

### MCP Server Development
```python
# Example domain-specific MCP server
from graphrag_mcp.mcp.server_generator import create_mcp_server
from graphrag_mcp.templates.academic import AcademicTemplate

# Generate server for academic domain
server = create_mcp_server(
    template=AcademicTemplate(),
    knowledge_graph=graph,
    port=8081
)
```

### Error Handling and Debugging
```bash
# Common debugging commands
curl -s http://localhost:11434/api/tags || echo "Start ollama: ollama serve"
curl -f http://localhost:7474/ || echo "Start Neo4j: make setup-neo4j"

# Database reset for conflicts
./clear_chromadb.sh

# Python environment issues
source graphiti-env/bin/activate
uv pip install -r requirements.txt

# Pre-commit hook issues
make pre-commit-install
```

## Project Context and Vision

### Current Status: Production MCP Toolkit
This is a **production-ready GraphRAG MCP Toolkit** that enables domain professionals to create specialized AI assistants for Claude. The system provides a universal MCP server that adapts to different professional domains through templates.

### Primary Use Case: Domain-Specific Claude Integration
Enable Claude to access and reason over domain-specific document collections through MCP tools. Example: Academic researchers can load papers into the server, then ask Claude questions about literature gaps, methodologies, and citations - Claude gets real-time access to the knowledge through MCP tool calls.

### Key Innovations
1. **Template-Based Architecture**: Universal system supports any professional domain
2. **Enhanced Entity Extraction**: 20+ categories with domain-specific customization
3. **Local Privacy-First**: All processing via Ollama, no external API dependencies
4. **MCP Integration**: Seamless connection to Claude Max and other AI assistants
5. **Professional Visualization**: yFiles integration for publication-ready graphs

### Development Philosophy
- **Universal Design**: Template system enables any professional domain
- **Local Privacy**: All processing local via Ollama
- **Community-Driven**: Open-source with contribution-friendly architecture
- **Production-Ready**: Comprehensive testing, documentation, and deployment tools
- **Research-Grounded**: Built on proven academic research foundations

### Performance Characteristics
- **Setup Time**: <30 minutes from install to working MCP server
- **Processing Speed**: 2-10 minutes per document with modern hardware
- **Query Response**: <3 seconds for domain-specific queries
- **Accuracy**: >90% citation extraction, >85% entity extraction
- **Scalability**: 100+ document collections efficiently processed

### Sample Data for Testing
- **Academic Papers**: `examples/d4sc03921a.pdf`, `examples/d3dd00113j.pdf`
- **Sample Outputs**: `examples/sample_analysis_outputs/` with complete analysis examples
- **Tutorial Materials**: `tutorial/` with 5-part learning system
- **Test Data**: `tests/` with visualization and connection tests