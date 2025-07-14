# GraphRAG MCP Toolkit Quickstart

Get up and running with GraphRAG MCP Toolkit in 5 minutes!

## 🎯 What You'll Build

By the end of this quickstart, you'll have:
- A working GraphRAG MCP server
- Processed research papers in a knowledge graph
- Claude Desktop integration for AI-powered research

## 📋 Prerequisites

- **Python 3.10+** (check with `python --version`)
- **5-10 research papers** in PDF format
- **10 minutes** of your time

## 🚀 Step 1: Install Everything

### Set Up Environment

```bash
# Create Python environment (recommended)
python -m venv graphrag-env
source graphrag-env/bin/activate  # On Windows: graphrag-env\Scripts\activate

# Or use existing environment
cd /path/to/your/project
source langchain-env/bin/activate  # Example: existing environment
```

### Install Dependencies

```bash
# Using UV (fastest)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
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

# Test core components
python3 -c "from graphrag_mcp.core import DocumentProcessor; print('✅ Core components ready')"
```

## 📄 Step 2: Start Analysis

### Quick Tutorial Setup

```bash
# Set up tutorial environment (handles everything automatically)
./start_tutorial.sh

# Or manually start Jupyter
jupyter notebook notebooks/Simple_Paper_RAG_Chat.ipynb
```

### Test with Sample Papers

```bash
# Try the main interface
python3 -c "
from graphrag_mcp.core import DocumentProcessor
processor = DocumentProcessor()
doc = processor.process_document('examples/d4sc03921a.pdf')
print('✅ Document processed successfully')
"
```

### Test MCP Server

```bash
# Start universal MCP server for testing
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio
```

## 🌐 Step 3: Connect to Claude Desktop

### Configure Claude Desktop

1. **Open Claude Desktop configuration**:
   - macOS: `~/.config/claude-desktop/config.json`
   - Windows: `%APPDATA%\Claude\config.json`

2. **Add this configuration**:
   ```json
   {
     "mcpServers": {
       "graphrag-research": {
         "command": "python3",
         "args": ["-m", "graphrag_mcp.cli.main", "serve-universal", "--template", "academic", "--transport", "stdio"],
         "cwd": "/Users/aimiegarces/Agents"
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## 🎉 Step 4: Start Researching!

### Open Claude Desktop

You should see a 🔌 icon indicating your MCP server is connected.

### Try These Commands

```
Load documents from examples directory
```

```
Search for "chemical synthesis" in the papers
```

```
Find citations for "drug discovery methods"
```

```
Show current server status
```

## 🔧 Quick Troubleshooting

### Ollama Issues

```bash
# Check if Ollama is running
ollama list

# Restart if needed
ollama serve
```

### MCP Server Issues

```bash
# Test server manually
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio

# Test core components
python3 -c "from graphrag_mcp.core import DocumentProcessor; print('✅ Working')"
```

### Claude Desktop Connection

1. Check config file path is correct
2. Restart Claude Desktop
3. Look for 🔌 icon in Claude interface

## 📈 Next Steps

### Explore More Features

- **Add more papers**: `graphrag-mcp add-documents my-research ./new-papers/`
- **Reprocess**: `graphrag-mcp process my-research --force`
- **Multiple projects**: `graphrag-mcp create project-2 --template academic`

### Advanced Usage

- **Template management**: `graphrag-mcp templates --list`
- **Server options**: `graphrag-mcp serve my-research --port 8081`
- **Batch processing**: Add multiple directories of papers

### Learn More

- **[Usage Guide](USAGE_GUIDE.md)**: Comprehensive documentation
- **[README](../README.md)**: Full feature overview
- **[Contributing](../CONTRIBUTING.md)**: Help improve the project

## 🎓 Example Research Session

Here's a complete example of using your new research assistant:

### 1. Broad Overview
```
Query papers about "transformer architectures"
```

### 2. Specific Analysis
```
Find citations for "transformers improve NLP performance"
```

### 3. Gap Analysis
```
Find research gaps in "transformer efficiency"
```

### 4. Methodology Comparison
```
Compare methodologies for "attention mechanisms"
```

### 5. Bibliography Generation
```
Generate bibliography in IEEE style
```

## 💡 Tips for Success

1. **Start with 5-10 papers** to test the system
2. **Use specific queries** for better results
3. **Organize papers by topic** for easier management
4. **Reprocess when adding new papers**
5. **Use descriptive project names**

## 🆘 Need Help?

- **Check status**: `graphrag-mcp status`
- **Verbose mode**: `graphrag-mcp --verbose status`
- **GitHub Issues**: Report problems or ask questions
- **Documentation**: See [docs/](.) for more guides

---

**Congratulations!** 🎉 You now have a working GraphRAG MCP Toolkit setup. Your research papers are transformed into an AI-powered assistant that can help you discover insights, find gaps, and manage citations.

**Ready to level up?** Check out the [Usage Guide](USAGE_GUIDE.md) for advanced features and workflows.