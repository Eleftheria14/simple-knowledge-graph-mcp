# GraphRAG MCP Toolkit Usage Guide

This comprehensive guide covers everything you need to know to use the GraphRAG MCP Toolkit effectively. The toolkit provides a production-ready dual-mode GraphRAG MCP system that enables Claude to both **chat conversationally** about research content AND **write literature reviews with automatic citations**.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Dual-Mode Architecture](#dual-mode-architecture)
3. [CLI Reference](#cli-reference)
4. [Academic Template Guide](#academic-template-guide)
5. [MCP Server Configuration](#mcp-server-configuration)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## 🚀 Quick Start

### Installation and Setup

```bash
# RECOMMENDED: Use automated setup
./setup_env.sh  # Creates Python 3.11 environment with all dependencies

# OR: Manual setup
source graphrag-env/bin/activate
uv pip install -r requirements.txt

# Install Ollama and models
brew install ollama
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve

# Optional: Install Neo4j for persistent knowledge graphs
make setup-neo4j

# Verify installation (comprehensive check)
python3 test_core_components.py

# Quick component verification
python3 -c "from graphrag_mcp.core.citation_manager import CitationTracker; print('✅ Citation manager ready')"
python3 -c "from graphrag_mcp.mcp.chat_tools import ChatToolsEngine; print('✅ Chat tools ready')"
python3 -c "from graphrag_mcp.mcp.literature_tools import LiteratureToolsEngine; print('✅ Literature tools ready')"
```

### Your First Analysis

```bash
# RECOMMENDED: Interactive tutorial workflow
./start_tutorial.sh

# Or use notebook processing (complete workflow)
cd notebooks/Main
jupyter notebook Simple_Document_Processing.ipynb

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

## 🔄 Dual-Mode Architecture

The GraphRAG MCP Toolkit provides a sophisticated dual-mode architecture that enables Claude to support complete research workflows:

### 🗣️ Chat Tools - Conversational Research Exploration
Natural, exploratory tools for research discovery and understanding optimized for conversational interaction:

- **ask_knowledge_graph**: Natural Q&A with conversational responses
- **explore_topic**: Structured topic exploration with multiple scopes
- **find_connections**: Discover relationships between concepts
- **what_do_we_know_about**: Comprehensive knowledge summaries

### 📝 Literature Review Tools - Formal Academic Writing
Citation-aware tools for systematic literature review and formal academic writing with integrated citation management:

- **gather_sources_for_topic**: Source gathering and organization
- **get_facts_with_citations**: Citation-ready factual statements
- **verify_claim_with_sources**: Evidence-based claim verification
- **get_topic_outline**: Structured literature review outlines
- **track_citations_used**: Citation usage management
- **generate_bibliography**: Multi-style bibliography generation

### 🔗 Integrated Citation Management
Both tool sets share a central **CitationTracker** that:
- Automatically tracks which papers are referenced
- Maintains citation usage context and confidence scores
- Supports 4 academic citation styles (APA, IEEE, Nature, MLA)
- Generates in-text citations and bibliographies on demand

### 🔄 Workflow Integration
1. **Exploration Phase**: Use chat tools to explore topics, find connections, understand the landscape
2. **Writing Phase**: Use literature review tools to gather sources, verify claims, generate citations
3. **Citation Management**: Automatic tracking and formatting throughout both phases

## 📚 Academic Template Guide

The academic template demonstrates the full power of the dual-mode system with **16 MCP tools** organized into three categories:

### 🗣️ Chat Tools (4 tools) - Conversational Exploration
Natural exploration and discovery tools with enhanced query processing:

#### `ask_knowledge_graph`
Natural Q&A interface with conversational responses.

```json
{
  "question": "string",
  "depth": "quick | detailed (default: quick)"
}
```

**Usage in Claude:**
```
ask_knowledge_graph: "What are the main research themes in transformer architectures?"
```

#### `explore_topic`
Structured topic exploration with different detail levels.

```json
{
  "topic": "string",
  "scope": "overview | detailed | comprehensive (default: overview)"
}
```

**Usage in Claude:**
```
explore_topic: "attention mechanisms" with scope "comprehensive"
```

#### `find_connections`
Discover relationships between concepts using graph traversal.

```json
{
  "concept_a": "string",
  "concept_b": "string",
  "connection_types": "array[string] (optional)"
}
```

**Usage in Claude:**
```
find_connections: between "neural networks" and "optimization algorithms"
```

#### `what_do_we_know_about`
Comprehensive knowledge summaries with optional gap analysis.

```json
{
  "topic": "string",
  "include_gaps": "boolean (default: true)"
}
```

**Usage in Claude:**
```
what_do_we_know_about: "BERT variants" including gaps
```

### 📝 Literature Review Tools (6 tools) - Formal Writing
Citation-aware tools for systematic literature review and formal academic writing:

#### `gather_sources_for_topic`
Systematic source collection and organization for literature reviews.

```json
{
  "topic": "string",
  "scope": "focused | comprehensive (default: comprehensive)",
  "sections": "array[string] (optional)"
}
```

**Usage in Claude:**
```
gather_sources_for_topic: "transformer architectures" for "comprehensive" literature review
```

#### `get_facts_with_citations`
Citation-ready factual statements for academic writing.

```json
{
  "topic": "string",
  "section": "string (optional)",
  "citation_style": "APA | IEEE | Nature | MLA (default: APA)"
}
```

**Usage in Claude:**
```
get_facts_with_citations: about "attention mechanisms" in APA style
```

#### `verify_claim_with_sources`
Evidence-based claim verification with supporting/contradicting evidence.

```json
{
  "claim": "string",
  "evidence_strength": "weak | medium | strong (default: strong)"
}
```

**Usage in Claude:**
```
verify_claim_with_sources: "Transformers outperform RNNs on long sequences"
```

#### `get_topic_outline`
Structured literature review outlines and section organization.

```json
{
  "topic": "string",
  "outline_type": "introduction | methods | results | discussion | comprehensive (default: comprehensive)"
}
```

**Usage in Claude:**
```
get_topic_outline: for "transformer efficiency" literature review
```

#### `track_citations_used`
Citation usage management and tracking.

```json
{
  "citation_keys": "array[string]",
  "context": "string (optional)"
}
```

**Usage in Claude:**
```
track_citations_used: ["vaswani2017", "devlin2018", "brown2020"]
```

#### `generate_bibliography`
Multi-style bibliography generation with usage statistics.

```json
{
  "style": "APA | IEEE | Nature | MLA (default: APA)",
  "used_only": "boolean (default: true)",
  "sort_by": "author | year | title (default: author)"
}
```

**Usage in Claude:**
```
generate_bibliography: in IEEE style with used citations only
```

### 🔍 Legacy/Core Tools (6 tools) - Backwards Compatibility
Existing tools maintained for specialized analytical functions:

### Core Tools

#### `list_templates`
Browse available domain templates.

#### `switch_template`
Change domain focus dynamically.

#### `load_document_collection`
Process document sets into knowledge graphs.

#### `search_documents`
Semantic search across document corpus.

### Legacy Tools

#### `query_papers`
Basic semantic search across your document corpus.

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

#### `research_gaps`
Identifies unexplored research areas.

#### `methodology_overview`
Compares research methodologies.

#### `author_analysis`
Analyzes author contributions and collaborations.

#### `concept_evolution`
Tracks concept development over time.

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