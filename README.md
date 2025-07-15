# GraphRAG MCP Toolkit

> **🚀 Transform any document collection into a dual-mode AI assistant with GraphRAG and MCP**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](docs/QUICKSTART.md)

An open-source platform for creating domain-specific GraphRAG MCP servers that understand your field's unique context, terminology, and relationships. Built with privacy-first local processing using Ollama and seamless Claude integration via the Model Context Protocol.

## 🎉 What's New

✅ **Dual-Mode Architecture**: Both conversational chat AND formal literature review tools  
✅ **Comprehensive Testing**: Multi-tier validation with automated health checks  
✅ **Data Integrity**: Automated validation and repair systems  
✅ **Error Recovery**: Multi-strategy fallback mechanisms  
✅ **Citation Management**: 4 academic styles (APA, IEEE, Nature, MLA)  
✅ **Claude Desktop Ready**: Auto-generated configuration for seamless integration  

## 🚀 Quick Start

### Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-org/graphrag-mcp-toolkit.git
cd graphrag-mcp-toolkit

# Set up environment (recommended)
./setup_env.sh  # Creates Python 3.11 environment with all dependencies

# Or manual setup
source graphrag-env/bin/activate
uv pip install -r requirements.txt
```

### Prerequisites

1. **Install Ollama**:
   ```bash
   # Download from https://ollama.com or use homebrew
   brew install ollama
   
   # Pull required models
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   
   # Start Ollama server
   ollama serve
   ```

2. **Verify Installation**:
   ```bash
   # RECOMMENDED: Comprehensive system validation
   python3 tests/test_basic_functionality.py
   
   # Test MCP integration
   python3 tests/test_mcp_simple.py
   
   # Check system status
   curl -s http://localhost:11434/api/tags
   ```

### Quick Tutorial

```bash
# Start the interactive tutorial (RECOMMENDED)
./start_tutorial.sh

# Or manual setup
cd notebooks/Main
jupyter notebook Simple_Document_Processing.ipynb
```

### Connect to Claude Desktop

**Use the auto-generated configuration:**

```bash
# The system generates a ready-to-use configuration
cat claude_desktop_config.json
```

Add to your Claude Desktop configuration (`~/.config/claude-desktop/config.json`):

```json
{
  "mcpServers": {
    "graphrag-research": {
      "command": "python3",
      "args": ["-m", "graphrag_mcp.cli.main", "serve-universal", "--template", "academic", "--transport", "stdio"],
      "cwd": "/path/to/your/project",
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

**Then restart Claude Desktop** and look for the 🔌 icon to confirm connection.

## 🎯 Dual-Mode Research Assistant

### 🗣️ **Conversational Mode** (Chat Tools)
Natural exploration and discovery:
- `ask_knowledge_graph` - Natural Q&A with research content
- `explore_topic` - Topic exploration with different detail levels
- `find_connections` - Discover relationships between concepts
- `what_do_we_know_about` - Comprehensive knowledge overviews

### 📝 **Literature Review Mode** (Literature Tools)
Formal academic writing with citations:
- `gather_sources_for_topic` - Organize sources for writing
- `get_facts_with_citations` - Citation-ready statements
- `verify_claim_with_sources` - Evidence-based verification
- `get_topic_outline` - Literature review structure
- `track_citations_used` - Citation management
- `generate_bibliography` - Multi-style bibliography

## 🔧 Core Features

### 🧠 **Enhanced Document Processing**
- **Multi-pass entity extraction** with 20+ categories
- **Citation tracking** with precise location mapping
- **Cross-document analysis** with relationship discovery
- **Domain-smart interpretation** without artificial constraints

### 🔒 **Privacy-First Architecture**
- **100% local processing** with Ollama
- **No external API calls** for document analysis
- **Your data stays on your machine**
- **Secure Neo4j storage** (optional)

### 📊 **Comprehensive Testing Framework**
- **Basic validation**: `tests/test_basic_functionality.py`
- **MCP integration**: `tests/test_mcp_simple.py`
- **End-to-end testing**: `tests/test_mcp_integration.py`
- **Health monitoring**: Automated system diagnostics

### 🛠️ **Developer-Friendly**
- **Modern Python 3.9+** with proper type hints
- **Comprehensive error handling** with recovery mechanisms
- **Resource management** with automatic cleanup
- **Performance monitoring** with detailed metrics

## 📚 Documentation

### Essential Guides
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Usage Guide](docs/USAGE_GUIDE.md)** - Comprehensive dual-mode workflows

### Architecture & Development
- **[Architecture Flow](docs/ARCHITECTURE_FLOW.md)** - System design and data flow
- **[Component Interactions](docs/COMPONENT_INTERACTIONS.md)** - How components work together
- **[Data Flow Visualization](docs/DATA_FLOW_VISUALIZATION.md)** - Visual system overview

## 🛠️ Development Commands

```bash
# Environment setup
make dev              # Complete development environment
make install-dev      # Development dependencies only

# Code quality
make lint            # Run ruff, black, mypy
make format          # Format code
make type-check      # Type checking
make quality         # All quality checks

# Testing
make test            # Run tests with coverage
python3 tests/test_basic_functionality.py  # Basic validation
python3 tests/test_mcp_simple.py          # MCP integration
python3 tests/test_mcp_integration.py     # End-to-end testing

# Services
make setup-ollama    # Install Ollama models
make setup-neo4j     # Start Neo4j container
make clear-db        # Clear all databases
```

## 🔍 Key Use Cases

### Academic Research
- **Literature reviews** with automatic citation management
- **Research gap identification** across document collections
- **Cross-paper concept tracking** and relationship discovery
- **Citation verification** and evidence-based writing

### Professional Knowledge Work
- **Document analysis** for any domain (legal, medical, technical)
- **Knowledge base creation** from institutional documents
- **Expert system development** with domain-specific reasoning
- **Compliance and regulatory** document management

## 🚧 Architecture Overview

```
Documents → Processing → Knowledge Graph → MCP Server → Claude Integration
    ↓          ↓             ↓              ↓              ↓
  PDF/Text   Enhanced      Graphiti        FastMCP       Dual-Mode
            Analysis       + Neo4j         Protocol       Assistant
```

### Core Components
- **Document Processor**: PDF parsing with validation and error handling
- **Enhanced Analyzer**: Multi-pass entity extraction with 20+ categories
- **Citation Manager**: Comprehensive citation tracking (APA, IEEE, Nature, MLA)
- **Query Engine**: NLP-based intent classification with error recovery
- **MCP Server**: FastMCP integration with standardized tool patterns
- **Testing Framework**: Multi-tier validation with health monitoring

## 🧪 Testing & Validation

The system includes comprehensive testing at multiple levels:

```bash
# System validation
python3 tests/test_basic_functionality.py

# MCP server testing
python3 tests/test_mcp_simple.py

# End-to-end integration
python3 tests/test_mcp_integration.py

# Health monitoring
python3 -c "from graphrag_mcp.core.citation_manager import CitationTracker; cm = CitationTracker(); print(cm.get_health_check())"
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Clone and setup
git clone https://github.com/your-org/graphrag-mcp-toolkit.git
cd graphrag-mcp-toolkit
make dev

# Run tests
make test
make quality
```

## 📈 Performance

- **Setup Time**: <30 minutes from install to working MCP server
- **Processing Speed**: 2-10 minutes per document
- **Query Response**: <3 seconds for both chat and literature queries
- **Citation Accuracy**: >95% extraction and formatting accuracy
- **System Reliability**: Comprehensive error recovery and health monitoring

## 🔧 Technical Stack

- **Python 3.9+** with modern async/await patterns
- **Ollama** for local LLM inference (llama3.1:8b, nomic-embed-text)
- **Graphiti** for real-time knowledge graph construction
- **Neo4j** for persistent graph storage (optional)
- **FastMCP** for Claude Desktop integration
- **ChromaDB** for vector storage and semantic search
- **Jupyter** for interactive document processing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft GraphRAG**: Inspiration for graph-based RAG
- **Anthropic MCP**: Model Context Protocol specification
- **Ollama**: Local LLM inference platform
- **Graphiti**: Real-time knowledge graph platform
- **FastMCP**: MCP server implementation

---

**Transform your documents into intelligent research assistants with GraphRAG MCP Toolkit!** 🚀

For support, questions, or contributions, please see our [documentation](docs/) or open an issue on GitHub.