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

# Testing Core Components (NEW)
python3 test_core_components.py           # Test citation manager and query engine
python3 -c "from graphrag_mcp.core.citation_manager import CitationTracker; print('✅ Citation manager ready')"
python3 -c "from graphrag_mcp.mcp.chat_tools import ChatToolsEngine; print('✅ Chat tools ready')"
python3 -c "from graphrag_mcp.mcp.literature_tools import LiteratureToolsEngine; print('✅ Literature tools ready')"
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

### Dual-Mode GraphRAG MCP Toolkit
This is a **production-ready GraphRAG MCP Toolkit** that enables Claude to both **chat conversationally** about research content AND **write literature reviews with automatic citations**:

- **Dual-Mode Design**: Conversational chat tools + formal literature review tools
- **Universal MCP Server**: Single FastMCP server with 10+ domain-specific tools
- **Citation Management**: Comprehensive citation tracking with 4 academic styles (APA, IEEE, Nature, MLA)
- **Local Processing**: All document analysis via Ollama (privacy-first, no external APIs)
- **Template System**: Domain-specific configurations (academic template with extensible architecture)

### Core Architecture: Dual-Mode Tool System

#### Chat Tools (Conversational Mode)
Located in `graphrag_mcp/mcp/chat_tools.py`:
- `ask_knowledge_graph` - Natural Q&A with conversational responses
- `explore_topic` - Structured topic exploration with multiple scopes
- `find_connections` - Discover relationships between concepts
- `what_do_we_know_about` - Comprehensive knowledge summaries

#### Literature Review Tools (Formal Writing Mode)
Located in `graphrag_mcp/mcp/literature_tools.py`:
- `gather_sources_for_topic` - Source gathering and organization
- `get_facts_with_citations` - Citation-ready factual statements
- `verify_claim_with_sources` - Evidence-based claim verification
- `get_topic_outline` - Structured literature review outlines
- `track_citations_used` - Citation usage management
- `generate_bibliography` - Multi-style bibliography generation

### Modern Component Architecture

#### Core Package Structure (`graphrag_mcp/`)
```
graphrag_mcp/
├── cli/                       # Typer-based CLI with rich output
│   └── main.py               # Entry point: graphrag-mcp command
├── core/                     # Domain-agnostic processing engine
│   ├── analyzer.py           # AdvancedAnalyzer for enhanced document analysis
│   ├── chat_engine.py        # ChatEngine for RAG + Graph queries
│   ├── citation_manager.py   # NEW: Comprehensive citation tracking system
│   ├── document_processor.py # PDF processing and text chunking
│   ├── graphiti_engine.py    # Graphiti integration for knowledge graphs
│   ├── ollama_engine.py      # Local LLM integration layer
│   └── query_engine.py       # NEW: Enhanced NLP query processing
├── mcp/                      # MCP server generation
│   ├── chat_tools.py         # NEW: Conversational research exploration tools
│   ├── graphiti_server.py    # Graphiti-powered MCP server
│   ├── literature_tools.py   # NEW: Formal academic writing tools
│   └── server_generator.py   # Updated: FastMCP server with dual-mode tools
├── templates/                # Domain-specific configurations
│   ├── academic.py           # Updated: Literature review template with 10 tools
│   └── base.py               # Base template class
└── visualization/            # Graph visualization
    └── graphiti_yfiles.py    # yFiles professional graphs
```

### MCP Server Data Flow (Updated)
```
Documents → Processing → Knowledge Graph → Dual-Mode MCP Tools → Claude Integration
    ↓            ↓             ↓                    ↓                    ↓
  PDF/Text → Entities → Graphiti/Neo4j → Chat + Literature Tools → Research Assistant
                                              ↓
                                    Citation Tracking System
                                         (APA/IEEE/Nature/MLA)
```

**Key MCP Tools Provided (Updated):**

*Core Tools:*
- `list_templates` - Available domain templates
- `switch_template` - Change domain focus  
- `load_document_collection` - Process document sets
- `search_documents` - Semantic search across corpus

*Chat Tools (Conversational):*
- `ask_knowledge_graph` - Natural Q&A with research content
- `explore_topic` - Topic exploration with different detail levels
- `find_connections` - Discover concept relationships
- `what_do_we_know_about` - Comprehensive knowledge overviews

*Literature Review Tools (Formal):*
- `gather_sources_for_topic` - Organize sources for writing
- `get_facts_with_citations` - Citation-ready statements
- `verify_claim_with_sources` - Evidence-based verification
- `get_topic_outline` - Literature review structure
- `track_citations_used` - Citation management
- `generate_bibliography` - Multi-style bibliography

*Legacy Tools:*
- `query_papers` - Basic paper search
- `research_gaps` - Gap identification
- `methodology_overview` - Method comparison
- `author_analysis` - Collaboration networks
- `concept_evolution` - Concept tracking

### Key Implementation Patterns

#### Dual-Mode MCP Integration
The system provides **two complementary interfaces** for Claude:

1. **Conversational Mode**: Natural exploration and discovery
   - Claude asks questions like "What do we know about transformer architectures?"
   - Tools return conversational responses with follow-up suggestions
   - Focus on exploration and understanding

2. **Literature Review Mode**: Formal academic writing with citations
   - Claude requests "Get facts about transformers with citations for my background section"
   - Tools return formatted statements with proper citations
   - Focus on accuracy and academic standards

#### Citation Management Integration
All tools share a central `CitationTracker` that:
- Automatically tracks which papers are referenced
- Maintains citation usage context and confidence scores
- Supports 4 academic citation styles (APA, IEEE, Nature, MLA)
- Generates in-text citations and bibliographies on demand

#### Template Development Pattern (Updated)
```python
# Creating new domain templates with dual-mode tools
class NewDomainTemplate(BaseTemplate):
    def get_mcp_tools(self) -> List[MCPToolConfig]:
        return [
            # Chat tools for exploration
            MCPToolConfig(
                name="ask_domain_question",
                description="Natural questions about domain content",
                implementation="conversational_query"
            ),
            # Literature tools for formal writing
            MCPToolConfig(
                name="get_domain_facts_with_citations",
                description="Citation-ready domain facts",
                implementation="cited_facts"
            )
        ]
```

## Key Implementation Details

### Modern Development Stack (Updated)
- **Framework**: Python 3.11+, FastMCP, Typer, Pydantic
- **LLM Integration**: Ollama (llama3.1:8b, nomic-embed-text) for local privacy
- **Knowledge Graphs**: Graphiti with Neo4j persistence
- **Vector Storage**: ChromaDB for semantic search
- **Citation Management**: Custom citation tracking system with 4 academic styles
- **Code Quality**: Black, Ruff, MyPy, Pre-commit hooks
- **Testing**: Pytest with comprehensive integration tests
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

### Development Workflow (Updated)
```bash
# Setup development environment
make dev              # Install dependencies + pre-commit hooks

# Test core components (NEW)
python3 test_core_components.py  # Comprehensive integration tests

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

### Working with Citation Management
```python
# Citation tracking workflow
from graphrag_mcp.core.citation_manager import CitationTracker

citation_manager = CitationTracker()

# Add citations from document processing
citation_key = citation_manager.add_citation(
    title="Attention Is All You Need",
    authors=["Vaswani", "Shazeer"],
    year=2017,
    journal="NIPS"
)

# Track usage in tools
citation_manager.track_citation(citation_key, "Used in transformer explanation")

# Generate bibliography
bibliography = citation_manager.generate_bibliography(style="APA", used_only=True)
```

### Adding New Dual-Mode Tools
1. **Chat Tool**: Add to `graphrag_mcp/mcp/chat_tools.py`
   - Focus on conversational responses
   - Include follow-up suggestions
   - Return exploration-oriented results

2. **Literature Tool**: Add to `graphrag_mcp/mcp/literature_tools.py`
   - Integrate with citation manager
   - Return formal, citation-ready content
   - Support different academic styles

3. **Template Integration**: Update `graphrag_mcp/templates/academic.py`
   - Add tool definitions to appropriate category
   - Define parameters and implementation mappings

4. **Server Registration**: Update `graphrag_mcp/mcp/server_generator.py`
   - Add tool registration logic
   - Connect to appropriate tool engine

### MCP Server Development (Updated)
```python
# Example dual-mode MCP server usage
from graphrag_mcp.mcp.server_generator import UniversalMCPServer

# Create server with integrated citation management
server = UniversalMCPServer()

# Citation manager is shared across all tools
assert server.chat_tools.citation_manager is server.literature_tools.citation_manager
assert server.chat_tools.citation_manager is server.citation_manager
```

### Error Handling and Debugging
```bash
# Common debugging commands
curl -s http://localhost:11434/api/tags || echo "Start ollama: ollama serve"
curl -f http://localhost:7474/ || echo "Start Neo4j: make setup-neo4j"

# Test core components
python3 test_core_components.py

# Database reset for conflicts
./clear_chromadb.sh

# Python environment issues
source graphiti-env/bin/activate
uv pip install -r requirements.txt

# Pre-commit hook issues
make pre-commit-install
```

## Project Context and Vision

### Current Status: Dual-Mode Research Assistant
This is a **production-ready dual-mode GraphRAG MCP Toolkit** that enables Claude to both explore research content conversationally AND write formal literature reviews with automatic citations. The system represents a major advancement from basic document search to sophisticated research assistance.

### Primary Use Case: Comprehensive Research Workflows
Enable Claude to support complete research workflows:

1. **Exploration Phase**: Use chat tools to explore topics, find connections, understand the landscape
2. **Writing Phase**: Use literature review tools to gather sources, verify claims, generate citations
3. **Citation Management**: Automatic tracking and formatting throughout both phases

### Key Innovations (Updated)
1. **Dual-Mode Architecture**: First MCP toolkit with both conversational and formal writing modes
2. **Integrated Citation Management**: Automatic citation tracking with 4 academic styles
3. **Enhanced Query Processing**: NLP-based intent classification and entity extraction
4. **Template-Based Architecture**: Universal system supports any professional domain
5. **Local Privacy-First**: All processing via Ollama, no external API dependencies
6. **Production MCP Integration**: Seamless connection to Claude Desktop and other AI assistants

### Development Philosophy
- **Dual-Mode Design**: Support both exploration and formal writing workflows
- **Citation-First**: Proper academic attribution built into every tool
- **Local Privacy**: All processing local via Ollama
- **Community-Driven**: Open-source with contribution-friendly architecture
- **Production-Ready**: Comprehensive testing, documentation, and deployment tools
- **Research-Grounded**: Built on proven academic research foundations

### Performance Characteristics (Updated)
- **Setup Time**: <30 minutes from install to working dual-mode MCP server
- **Processing Speed**: 2-10 minutes per document with modern hardware
- **Query Response**: <3 seconds for both chat and literature queries
- **Citation Accuracy**: >95% citation extraction and formatting accuracy
- **Tool Count**: 10+ MCP tools across chat and literature review modes
- **Citation Styles**: 4 academic styles with proper formatting

### Sample Data for Testing
- **Academic Papers**: `examples/d4sc03921a.pdf`, `examples/d3dd00113j.pdf`
- **Integration Tests**: `test_core_components.py` with real-world research scenarios
- **Tutorial Materials**: `tutorial/` with 5-part learning system
- **Test Data**: `tests/` with comprehensive integration testing

### Latest Implementation Achievement
The recent major implementation added:
- **10 new MCP tools** organized in chat and literature review categories
- **Comprehensive citation management** with 4 academic citation styles
- **Enhanced query engine** with NLP processing and intent classification
- **Real-world validation** through comprehensive integration testing
- **Production-ready architecture** with shared state management across all tools

This represents the transformation from a research prototype to a production-ready dual-mode research assistant that can both chat about research content and write formal literature reviews with perfect citations.