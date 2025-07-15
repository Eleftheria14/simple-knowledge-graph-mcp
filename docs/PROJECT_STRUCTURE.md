# GraphRAG MCP Toolkit - Project Structure

## 📁 Project Organization

```
graphrag-mcp-toolkit/
├── 📄 README.md                     # Main project documentation
├── 🔧 pyproject.toml               # Python project configuration
├── 📋 requirements.txt             # Python dependencies
├── 📄 LICENSE                      # MIT License
├── 📝 CHANGELOG.md                 # Version history
├── 🤖 CLAUDE.md                    # Claude Code instructions
├── 🤝 CONTRIBUTING.md              # Contribution guidelines
├── 🔗 docs_links.md                # External documentation links
├── 🏗️ Makefile                     # Build and development commands
│
├── 🧠 graphrag_mcp/                # Main package
│   ├── 📄 __init__.py
│   ├── 💻 cli/                     # Command-line interface
│   │   ├── 📄 __init__.py
│   │   └── 🎯 main.py              # CLI entry point
│   ├── 🔧 core/                    # Core processing engine
│   │   ├── 📄 __init__.py
│   │   ├── 🔍 analyzer.py          # Document analysis
│   │   ├── 💬 chat_engine.py       # Chat processing
│   │   ├── 📚 citation_manager.py  # Citation tracking
│   │   ├── 📄 document_processor.py # Document processing
│   │   ├── 🕸️ graphiti_engine.py   # Knowledge graph engine
│   │   ├── 🦙 ollama_engine.py     # Ollama integration
│   │   └── 🔎 query_engine.py      # Enhanced query processing
│   ├── 🛠️ mcp/                     # MCP server components
│   │   ├── 📄 __init__.py
│   │   ├── 💭 chat_tools.py        # Conversational tools
│   │   ├── 🕸️ graphiti_server.py   # Graphiti MCP server
│   │   ├── 📝 literature_tools.py  # Literature review tools
│   │   └── 🌐 server_generator.py  # Universal MCP server
│   ├── 📋 templates/               # Domain templates
│   │   ├── 📄 __init__.py
│   │   ├── 🎓 academic.py          # Academic template
│   │   └── 🏗️ base.py              # Base template class
│   └── 📊 visualization/           # Graph visualization
│       ├── 📄 __init__.py
│       └── 🌐 graphiti_yfiles.py   # yFiles integration
│
├── 📚 docs/                        # Documentation
│   ├── 📖 API_REFERENCE.md         # API documentation
│   ├── 🏗️ ARCHITECTURE_FLOW.md     # Architecture overview
│   ├── 🔗 COMPONENT_INTERACTIONS.md # Component interactions
│   ├── 📈 DATA_FLOW_VISUALIZATION.md # Data flow diagrams
│   ├── 🚀 QUICKSTART.md            # Quick start guide
│   ├── 📋 PRD.md                   # Product requirements
│   ├── 📖 USAGE_GUIDE.md           # Usage documentation
│   └── 📝 IMPLEMENTATION_PLAN.md   # Implementation history
│
├── 🧪 tests/                       # Test suite
│   ├── 📄 __init__.py
│   ├── 🔗 test_graphiti_connection.py
│   ├── 🧪 test_integration.py
│   └── 📊 test_viz_* files
│
├── 📓 notebooks/                   # Jupyter notebooks
│   ├── 🌐 Google CoLab/           # Google Colab versions
│   ├── 🏠 Main/                   # Primary notebooks
│   │   ├── 📓 Simple_Document_Processing.ipynb
│   │   └── 🔧 processing_utils.py
│   └── 📁 Other/                  # Additional notebooks
│
├── 🎓 tutorial/                    # Learning materials
│   ├── 01_Introduction_to_LLMs_and_Ollama.ipynb
│   ├── 02_LangChain_Fundamentals.ipynb
│   ├── 03_Understanding_RAG.ipynb
│   ├── 04_Building_Knowledge_Graphs.ipynb
│   └── 05_Your_First_Paper_Analysis_System.ipynb
│
├── 📁 examples/                    # Sample data and outputs
│   ├── 📄 Test File.pdf
│   └── 📊 sample_analysis_outputs/
│
├── 🔧 Shell Scripts
│   ├── 🚀 activate_graphrag_env.sh # Environment activation
│   ├── 🧹 clear_chromadb.sh       # Database cleanup
│   ├── ⚙️ setup_env.sh            # Environment setup
│   └── 🎯 start_tutorial.sh       # Tutorial launcher
│
└── 📄 Sample Papers               # Test documents
    ├── d3dd00113j.pdf
    └── d4sc03921a.pdf
```

## 🚀 Key Features

### Dual-Mode Architecture
- **Chat Mode**: Conversational exploration of research content
- **Literature Review Mode**: Formal writing with automatic citations

### 10 MCP Tools
**Chat Tools (4):**
- `ask_knowledge_graph` - Natural Q&A
- `explore_topic` - Topic exploration
- `find_connections` - Concept relationships
- `what_do_we_know_about` - Knowledge summaries

**Literature Review Tools (6):**
- `gather_sources_for_topic` - Source organization
- `get_facts_with_citations` - Citation-ready facts
- `verify_claim_with_sources` - Evidence verification
- `get_topic_outline` - Review outlines
- `track_citations_used` - Citation management
- `generate_bibliography` - Multi-style bibliographies

### Technical Stack
- **Python 3.11+** with modern type hints
- **FastMCP** for MCP server implementation
- **Ollama** for local LLM processing
- **Graphiti** for knowledge graph management
- **Pydantic** for data validation
- **4 Academic Citation Styles**: APA, IEEE, Nature, MLA

## 🔧 Development Commands

```bash
# Environment setup
make dev                    # Complete development setup
source graphrag-env/bin/activate  # Activate environment

# Code quality
make format                 # Format code
make lint                   # Check code quality
make test                   # Run tests

# Usage
graphrag-mcp status        # Check system status
graphrag-mcp serve-universal --template academic --transport stdio
```

## 📚 Documentation

- **Quick Start**: `docs/QUICKSTART.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **Architecture**: `docs/ARCHITECTURE_FLOW.md`
- **Usage Guide**: `docs/USAGE_GUIDE.md`
- **Claude Instructions**: `CLAUDE.md`

## 🌟 Production Ready

This project is **production-ready** with:
- ✅ Comprehensive test coverage
- ✅ Proper error handling
- ✅ Documentation and examples
- ✅ Code quality checks
- ✅ Type hints and validation
- ✅ MCP integration
- ✅ Citation management

Ready for immediate use with Claude Desktop via MCP integration.