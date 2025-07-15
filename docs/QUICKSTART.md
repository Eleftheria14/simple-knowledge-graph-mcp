# GraphRAG MCP Toolkit Quickstart

Get up and running with the **production-ready** GraphRAG MCP Toolkit in 5 minutes! Transform your research papers into a dual-mode AI assistant that both chats conversationally about your research AND writes literature reviews with perfect citations.

## 🎯 What You'll Build

By the end of this quickstart, you'll have:
- A **production-ready dual-mode GraphRAG MCP server** with enterprise-grade error handling
- Processed research papers in a persistent knowledge graph with data integrity validation
- Claude Desktop integration with **10+ specialized research tools** and comprehensive testing
- Both conversational research exploration AND formal literature review capabilities
- Automatic citation management in 4 academic styles (APA, IEEE, Nature, MLA) with validation
- **Robust error recovery** and performance monitoring for production use

## 📋 Prerequisites

- **Python 3.11+** (check with `python --version`) - Modern Python environment recommended
- **5-10 research papers** in PDF format for testing
- **10-15 minutes** of your time
- **Optional**: Neo4j for persistent knowledge graphs

## 🚀 Step 1: Install Everything

### Set Up Environment

```bash
# RECOMMENDED: Use the automated setup script
./setup_env.sh  # Creates Python 3.11 environment with all dependencies

# OR: Manual setup
python -m venv graphrag-env
source graphrag-env/bin/activate  # On Windows: graphrag-env\Scripts\activate

# OR: Use existing environment
cd /path/to/your/project
source langchain-env/bin/activate  # Example: existing environment
```

### Install Dependencies

```bash
# Using UV (fastest - recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt

# Or using make (includes dev dependencies)
make install-dev
```

### Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows - Download from https://ollama.com
```

### Download AI Models

```bash
# Download required models (this may take a few minutes)
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# Start Ollama server
ollama serve
```

### Verify Installation

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/tags

# RECOMMENDED: Run comprehensive system validation
python3 tests/test_basic_functionality.py

# Test core components with validation
python3 test_core_components.py

# Quick component test
python3 -c "from graphrag_mcp.core.citation_manager import CitationTracker; print('✅ Citation manager ready')"
python3 -c "from graphrag_mcp.mcp.chat_tools import ChatToolsEngine; print('✅ Chat tools ready')"
python3 -c "from graphrag_mcp.mcp.literature_tools import LiteratureToolsEngine; print('✅ Literature tools ready')"

# Test MCP integration
python3 tests/test_mcp_simple.py
```

## 📄 Step 2: Start Analysis

### RECOMMENDED: Interactive Tutorial Workflow

```bash
# Complete setup + launches tutorial (RECOMMENDED)
./start_tutorial.sh

# Or with Ollama startup
./start_tutorial.sh --start-ollama

# Or start services only
./start_services.sh  # Starts Ollama + Neo4j services
```

### Test with Sample Papers

```bash
# Test document processing
python3 -c "
from graphrag_mcp.core import DocumentProcessor
processor = DocumentProcessor()
doc = processor.process_document('examples/d4sc03921a.pdf')
print('✅ Document processed successfully')
"

# Test the complete workflow in notebook
cd notebooks/Main
jupyter notebook Simple_Document_Processing.ipynb
```

### Test MCP Server

```bash
# Start universal MCP server for testing
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio

# Check server status
graphrag-mcp status

# Test with specific template
graphrag-mcp serve-universal --template academic --transport stdio
```

## 🌐 Step 3: Connect to Claude Desktop

### Configure Claude Desktop

1. **RECOMMENDED: Use the auto-generated configuration**:
   ```bash
   # The system has generated a ready-to-use configuration
   cat claude_desktop_config.json
   ```

2. **Open Claude Desktop configuration**:
   - macOS: `~/.config/claude-desktop/config.json`
   - Windows: `%APPDATA%\Claude\config.json`

3. **Add the generated configuration**:
   ```json
   {
     "mcpServers": {
       "graphrag-research": {
         "command": "python3",
         "args": ["-m", "graphrag_mcp.cli.main", "serve-universal", "--template", "academic", "--transport", "stdio"],
         "cwd": "/Users/aimiegarces/Agents",
         "env": {
           "PYTHONPATH": "/Users/aimiegarces/Agents"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Verify Connection**:
   - Look for the 🔌 icon in Claude Desktop
   - Test with a simple query: "What MCP tools are available?"

## 🎉 Step 4: Start Dual-Mode Research!

### Open Claude Desktop

You should see a 🔌 icon indicating your MCP server is connected.

### 🗣️ Conversational Research Mode (Chat Tools)

Use these tools for natural exploration and discovery:

```
ask_knowledge_graph: "What are the main research themes in my documents?"
```

```
explore_topic: "machine learning applications" with scope "comprehensive"
```

```
find_connections: between "neural networks" and "optimization"
```

```
what_do_we_know_about: "drug discovery" including gaps
```

### 📝 Literature Review Mode (Literature Tools)

Use these tools for formal academic writing with citations:

```
gather_sources_for_topic: "transformer architectures" for "comprehensive" literature review
```

```
get_facts_with_citations: about "attention mechanisms" in APA style
```

```
verify_claim_with_sources: "BERT outperforms traditional NLP models"
```

```
get_topic_outline: for "transformer efficiency" literature review
```

```
generate_bibliography: in IEEE style with used citations only
```

### 🔄 Integrated Workflow

1. **Explore** with chat tools to understand the landscape
2. **Gather** sources with literature tools for formal writing
3. **Verify** claims with evidence-based tools
4. **Generate** citations and bibliography automatically

## 🔧 Quick Troubleshooting

### System Health Check

```bash
# RECOMMENDED: Comprehensive health check
python3 tests/test_basic_functionality.py

# Run system validation
python3 tests/test_mcp_simple.py

# Check component health
python3 -c "
from graphrag_mcp.core.citation_manager import CitationTracker
cm = CitationTracker()
print('Citation Manager Health:', cm.get_health_check()['overall_health'])
"
```

### Ollama Issues

```bash
# Check if Ollama is running
ollama list

# Restart if needed
ollama serve

# Test connectivity
curl -s http://localhost:11434/api/tags
```

### MCP Server Issues

```bash
# Test server manually with validation
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio

# Test core components with error handling
python3 -c "
try:
    from graphrag_mcp.core import DocumentProcessor
    print('✅ Document processor ready')
except Exception as e:
    print('❌ Error:', e)
"

# Check prerequisites
python3 -c "
from graphrag_mcp.utils.prerequisites import check_prerequisites
result = check_prerequisites(verbose=False)
print('Prerequisites status:', result.status)
"
```

### Claude Desktop Connection

1. **Check config file path** is correct
2. **Verify generated config**: `cat claude_desktop_config.json`
3. **Restart Claude Desktop**
4. **Look for 🔌 icon** in Claude interface
5. **Test connection**: Ask "What MCP tools are available?"
6. **Check error logs** in Claude Desktop developer tools

## 📈 Next Steps

### Explore More Features

- **Use Interactive Tutorials**: `./start_tutorial.sh` for complete workflow
- **Neo4j Integration**: `make setup-neo4j` for persistent knowledge graphs
- **Template Management**: `graphrag-mcp templates --list` and `--info academic`
- **Advanced Analysis**: Try the comprehensive test in `test_core_components.py`

### Advanced Usage

- **Quality Control**: `make quality` for comprehensive code analysis
- **Development Mode**: `make dev` for complete development environment
- **Batch Processing**: Process multiple document collections
- **Custom Templates**: Create domain-specific templates

### Learn More

- **[Usage Guide](USAGE_GUIDE.md)**: Comprehensive dual-mode documentation
- **[API Reference](API_REFERENCE.md)**: Complete API documentation
- **[README](../README.md)**: Full feature overview and architecture
- **[Contributing](../CONTRIBUTING.md)**: Help improve the project

## 🎓 Example Dual-Mode Research Session

Here's a complete example demonstrating both conversational and formal modes:

### Phase 1: Exploration (Chat Tools)
```
ask_knowledge_graph: "What are the main themes in transformer research?"
explore_topic: "attention mechanisms" with scope "detailed"
find_connections: between "transformers" and "computational efficiency"
what_do_we_know_about: "BERT variants" including gaps
```

### Phase 2: Formal Writing (Literature Tools)
```
gather_sources_for_topic: "transformer architectures" for "introduction" section
get_facts_with_citations: about "attention mechanisms" in APA style
verify_claim_with_sources: "Transformers outperform RNNs on long sequences"
get_topic_outline: for "transformer efficiency" literature review
track_citations_used: ["vaswani2017", "devlin2018", "brown2020"]
generate_bibliography: in IEEE style with used citations only
```

### Phase 3: Quality Control
```
track_citations_used: Check citation distribution
verify_claim_with_sources: Double-check key claims
generate_bibliography: Final bibliography in required style
```

## 💡 Tips for Success

1. **Start with the tutorial workflow** - `./start_tutorial.sh` for best experience
2. **Use dual-mode approach** - Explore with chat tools, then write with literature tools
3. **Test core components** - Run `python3 test_core_components.py` to verify setup
4. **Use specific queries** for better results in both modes
5. **Track citations consistently** - Use `track_citations_used` throughout your writing
6. **Organize papers by topic** for easier management
7. **Choose appropriate citation styles** - APA, IEEE, Nature, or MLA based on your field

## 🆘 Need Help?

- **Check status**: `graphrag-mcp status`
- **Test components**: `python3 test_core_components.py`
- **Check services**: `curl -s http://localhost:11434/api/tags` (Ollama)
- **Verbose mode**: `graphrag-mcp --verbose status`
- **Interactive tutorial**: `./start_tutorial.sh` for guided workflow
- **GitHub Issues**: Report problems or ask questions
- **Documentation**: See [docs/](.) for comprehensive guides

---

**Congratulations!** 🎉 You now have a production-ready dual-mode GraphRAG MCP Toolkit setup. Your research papers are transformed into an AI-powered assistant that can both chat conversationally about your research AND write formal literature reviews with perfect citations.

**Ready to level up?** Check out the [Usage Guide](USAGE_GUIDE.md) for advanced dual-mode workflows and the [API Reference](API_REFERENCE.md) for complete documentation.