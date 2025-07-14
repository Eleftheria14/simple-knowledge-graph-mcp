# GraphRAG MCP Toolkit Usage Guide

This comprehensive guide covers everything you need to know to use the GraphRAG MCP Toolkit effectively.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [CLI Reference](#cli-reference)
3. [Academic Template Guide](#academic-template-guide)
4. [MCP Server Configuration](#mcp-server-configuration)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## 🚀 Quick Start

### Installation and Setup

```bash
# Set up environment
python -m venv graphrag-env
source graphrag-env/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Install Ollama and models
brew install ollama
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve

# Verify installation
python3 -c "from graphrag_mcp.core import DocumentProcessor; print('✅ Ready')"
```

### Your First Analysis

```bash
# Set up tutorial environment
./start_tutorial.sh

# Or manually test components
python3 -c "
from graphrag_mcp.core import DocumentProcessor
processor = DocumentProcessor()
doc = processor.process_document('examples/d4sc03921a.pdf')
print('✅ Document processed')
"

# Test MCP server
python3 -m graphrag_mcp.cli.main serve-universal --template academic --transport stdio
```

## 🔧 Core Components Reference

### Document Processing

#### Using DocumentProcessor

```python
from graphrag_mcp.core import DocumentProcessor

# Initialize processor
processor = DocumentProcessor()

# Process document
doc_data = processor.process_document('examples/d4sc03921a.pdf')
print(f"Processed: {doc_data.title}")
```

#### Using AdvancedAnalyzer

```python
from graphrag_mcp.core import AdvancedAnalyzer

# Initialize analyzer
analyzer = AdvancedAnalyzer()

# Analyze for corpus
corpus_doc = analyzer.analyze_for_corpus('examples/d4sc03921a.pdf')
print(f"Entities: {len(corpus_doc.entities)}")
```

#### `graphrag-mcp add-documents`
Adds documents to a project for processing.

```bash
graphrag-mcp add-documents <project> <paths> [OPTIONS]

Options:
  --recursive, -r   Scan directories recursively
```

**Examples:**
```bash
# Add single document
graphrag-mcp add-documents research-assistant ./paper.pdf

# Add multiple documents
graphrag-mcp add-documents research-assistant ./doc1.pdf ./doc2.pdf

# Add directory recursively
graphrag-mcp add-documents research-assistant ./papers/ --recursive
```

#### `graphrag-mcp process`
Processes documents into knowledge graphs.

```bash
graphrag-mcp process <project> [OPTIONS]

Options:
  --force, -f   Reprocess existing documents
```

**Examples:**
```bash
# Process all documents
graphrag-mcp process research-assistant

# Force reprocessing
graphrag-mcp process research-assistant --force
```

#### `graphrag-mcp serve`
Starts MCP server for a project.

```bash
graphrag-mcp serve <project> [OPTIONS]

Options:
  --port, -p        Server port [default: 8080]
  --host            Server host [default: localhost]
  --transport, -t   Transport method [default: http]
  --background, -b  Run in background
```

**Examples:**
```bash
# Basic server
graphrag-mcp serve research-assistant

# Custom port
graphrag-mcp serve research-assistant --port 8081

# STDIO transport for Claude Desktop
graphrag-mcp serve research-assistant --transport stdio
```

#### `graphrag-mcp serve-universal`
Starts universal server for testing without a project.

```bash
graphrag-mcp serve-universal [OPTIONS]

Options:
  --template, -t    Domain template [default: academic]
  --port, -p        Server port [default: 8080]
  --host            Server host [default: localhost]
  --transport       Transport method [default: http]
```

**Examples:**
```bash
# Test server
graphrag-mcp serve-universal --template academic

# STDIO for Claude Desktop testing
graphrag-mcp serve-universal --transport stdio
```

### Management Commands

#### `graphrag-mcp templates`
Manages domain templates.

```bash
graphrag-mcp templates [OPTIONS]

Options:
  --list, -l        List available templates
  --info, -i        Show template info
  --install         Install template from URL/path
```

**Examples:**
```bash
# List templates
graphrag-mcp templates --list

# Template details
graphrag-mcp templates --info academic

# Install custom template (planned)
graphrag-mcp templates --install ./custom-template.json
```

#### `graphrag-mcp status`
Shows system and project status.

```bash
graphrag-mcp status [project]

Arguments:
  project   Specific project to check (optional)
```

**Examples:**
```bash
# System overview
graphrag-mcp status

# Project-specific status
graphrag-mcp status research-assistant
```

## 📚 Academic Template Guide

The academic template is optimized for literature reviews and research analysis.

### MCP Tools Available

#### `query_papers`
Semantic search across your document corpus.

```json
{
  "query": "string",
  "entity_filter": "string (optional)",
  "limit": "integer (default: 10)"
}
```

**Usage in Claude:**
```
Query papers about "transformer architectures in NLP"
```

#### `find_citations`
Finds supporting evidence for claims.

```json
{
  "claim": "string",
  "context": "string (optional)"
}
```

**Usage in Claude:**
```
Find citations for "BERT outperforms traditional NLP models"
```

#### `research_gaps`
Identifies unexplored research areas.

```json
{
  "domain": "string",
  "depth": "surface | deep (default: surface)"
}
```

**Usage in Claude:**
```
Find research gaps in "neural machine translation"
```

#### `methodology_overview`
Compares research methodologies.

```json
{
  "topic": "string",
  "include_evolution": "boolean (default: true)"
}
```

**Usage in Claude:**
```
Compare methodologies for "sentiment analysis"
```

#### `author_analysis`
Analyzes author contributions and collaborations.

```json
{
  "author": "string (optional)",
  "institution": "string (optional)"
}
```

**Usage in Claude:**
```
Analyze contributions by "Yoshua Bengio"
```

#### `concept_evolution`
Tracks concept development over time.

```json
{
  "concept": "string",
  "time_range": "string (optional)"
}
```

**Usage in Claude:**
```
Track evolution of "attention mechanisms"
```

#### `generate_bibliography`
Creates formatted bibliography.

```json
{
  "style": "APA | IEEE | Nature (default: APA)",
  "filter_used": "boolean (default: true)"
}
```

**Usage in Claude:**
```
Generate APA style bibliography
```

### Academic Workflow Examples

#### Literature Review Workflow

1. **Setup Project**
   ```bash
   graphrag-mcp create literature-review --template academic
   ```

2. **Add Papers**
   ```bash
   graphrag-mcp add-documents literature-review ./papers/ --recursive
   ```

3. **Process Corpus**
   ```bash
   graphrag-mcp process literature-review
   ```

4. **Start Server**
   ```bash
   graphrag-mcp serve literature-review --transport stdio
   ```

5. **Use in Claude**
   ```
   Query papers about "deep learning in drug discovery"
   Find research gaps in "molecular property prediction"
   Generate bibliography in APA style
   ```

#### Research Analysis Workflow

1. **Initial Overview**
   ```
   Query papers about "my research topic"
   ```

2. **Methodology Analysis**
   ```
   Compare methodologies for "my research area"
   ```

3. **Gap Identification**
   ```
   Find research gaps in "my field"
   ```

4. **Citation Support**
   ```
   Find citations for "my key claim"
   ```

5. **Bibliography Generation**
   ```
   Generate bibliography in IEEE style
   ```

## 🌐 MCP Server Configuration

### Claude Desktop Integration

Add to `~/.config/claude-desktop/config.json`:

```json
{
  "mcpServers": {
    "graphrag-research": {
      "command": "python3",
      "args": ["-m", "graphrag_mcp.cli.main", "serve-universal", "--template", "academic", "--transport", "stdio"],
      "cwd": "/Users/aimiegarces/Agents",
      "env": {
        "OLLAMA_HOST": "localhost:11434"
      }
    }
  }
}
```

### Multiple Projects

```json
{
  "mcpServers": {
    "literature-review": {
      "command": "graphrag-mcp",
      "args": ["serve", "literature-review", "--transport", "stdio"]
    },
    "research-analysis": {
      "command": "graphrag-mcp", 
      "args": ["serve", "research-analysis", "--transport", "stdio"]
    }
  }
}
```

### Universal Server for Testing

```json
{
  "mcpServers": {
    "graphrag-universal": {
      "command": "graphrag-mcp",
      "args": ["serve-universal", "--template", "academic", "--transport", "stdio"]
    }
  }
}
```

## 🔧 Advanced Usage

### Environment Variables

```bash
# Ollama configuration
export OLLAMA_HOST=localhost:11434
export OLLAMA_LLM_MODEL=llama3.1:8b
export OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# MCP server settings
export GRAPHRAG_MCP_PORT=8080
export GRAPHRAG_MCP_HOST=localhost

# Project settings
export GRAPHRAG_MCP_CONFIG_DIR=~/.graphrag-mcp
```

### Custom Project Configuration

Edit `~/.graphrag-mcp/projects/my-project/config.json`:

```json
{
  "name": "my-project",
  "template": "academic",
  "created_date": "2024-01-01",
  "version": "0.1.0",
  "documents": [],
  "mcp_server": {
    "port": 8080,
    "host": "localhost",
    "enabled": true
  },
  "processing": {
    "max_entities": 100,
    "citation_extraction": true,
    "entity_linking": true
  }
}
```

### Batch Processing

```bash
# Process multiple projects
for project in research-1 research-2 research-3; do
  graphrag-mcp process "$project" --force
done

# Add documents to multiple projects
find ./papers -name "*.pdf" | while read paper; do
  graphrag-mcp add-documents research-assistant "$paper"
done
```

### Performance Optimization

```bash
# Monitor processing
graphrag-mcp process research-assistant --verbose

# Check system resources
graphrag-mcp status --verbose

# Optimize Ollama
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Ollama Connection Error

**Problem:** `❌ Ollama server: Offline`

**Solution:**
```bash
# Check Ollama status
ollama list

# Restart Ollama
ollama serve

# Check models
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

#### 2. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'graphrag_mcp'`

**Solution:**
```bash
# Reinstall package
uv sync

# Check installation
uv run graphrag-mcp --help
```

#### 3. MCP Server Fails to Start

**Problem:** `❌ Server failed to start`

**Solution:**
```bash
# Check project exists
graphrag-mcp status my-project

# Verify documents processed
ls ~/.graphrag-mcp/projects/my-project/processed/

# Test universal server
graphrag-mcp serve-universal --template academic
```

#### 4. Template Not Found

**Problem:** `❌ Template 'custom' not found`

**Solution:**
```bash
# List available templates
graphrag-mcp templates --list

# Use existing template
graphrag-mcp create my-project --template academic
```

### Debug Mode

```bash
# Enable verbose logging
export GRAPHRAG_MCP_DEBUG=1

# Run with debug
graphrag-mcp --verbose status

# Check logs
tail -f ~/.graphrag-mcp/logs/graphrag-mcp.log
```

## 📈 Best Practices

### Document Management

1. **Organize Papers**
   ```bash
   mkdir -p papers/{arxiv,conferences,journals}
   graphrag-mcp add-documents research papers/arxiv/ --recursive
   ```

2. **Naming Conventions**
   ```bash
   # Use descriptive project names
   graphrag-mcp create nlp-survey-2024 --template academic
   graphrag-mcp create drug-discovery-analysis --template academic
   ```

3. **Version Control**
   ```bash
   # Track project configurations
   git add ~/.graphrag-mcp/projects/my-project/config.json
   git commit -m "Add research project configuration"
   ```

### Performance Optimization

1. **Batch Processing**
   ```bash
   # Process multiple documents at once
   graphrag-mcp add-documents research ./papers/ --recursive
   graphrag-mcp process research
   ```

2. **Resource Management**
   ```bash
   # Monitor system resources
   graphrag-mcp status --verbose
   
   # Optimize Ollama settings
   export OLLAMA_MAX_LOADED_MODELS=1
   ```

3. **Storage Optimization**
   ```bash
   # Clean up old processed files
   find ~/.graphrag-mcp/projects/*/processed -name "*.json" -older +30d -delete
   ```

### Claude Integration

1. **Effective Queries**
   ```
   # Be specific in queries
   "Find papers about transformer attention mechanisms in computer vision"
   
   # Use context
   "Find citations for the claim about BERT's performance, focusing on NLP benchmarks"
   ```

2. **Iterative Research**
   ```
   # Start broad, then narrow
   1. Query papers about "machine learning in healthcare"
   2. Find research gaps in "medical image analysis"
   3. Compare methodologies for "diagnostic AI systems"
   ```

3. **Citation Management**
   ```
   # Always verify citations
   Find citations for "specific claim"
   Generate bibliography in APA style
   ```

### Project Organization

1. **Multiple Projects**
   ```bash
   # Domain-specific projects
   graphrag-mcp create ml-survey --template academic
   graphrag-mcp create nlp-research --template academic
   graphrag-mcp create cv-analysis --template academic
   ```

2. **Template Selection**
   ```bash
   # Choose appropriate templates
   graphrag-mcp create legal-research --template legal    # When available
   graphrag-mcp create medical-study --template medical   # When available
   ```

3. **Backup Strategy**
   ```bash
   # Regular backups
   tar -czf graphrag-backup-$(date +%Y%m%d).tar.gz ~/.graphrag-mcp/
   ```

---

**Need more help?** Check out the [README](../README.md) for quick reference or [CONTRIBUTING](../CONTRIBUTING.md) for development setup.