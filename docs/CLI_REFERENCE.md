# GraphRAG MCP Toolkit CLI Reference

This document provides a complete reference for the **GraphRAG MCP Toolkit command-line interface**. The CLI is the primary interface for most users, providing all functionality needed to create, manage, and deploy GraphRAG MCP servers.

## 🚀 Overview

The GraphRAG MCP Toolkit CLI provides **11 commands** covering the complete workflow:

- **Project Management** - Create, configure, and manage projects
- **Document Processing** - Add and process documents into knowledge graphs
- **Server Management** - Start and manage MCP servers
- **System Tools** - Validation, visualization, and status checking
- **Quick Setup** - One-command workflows for common use cases

## 📋 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Global Options](#global-options)
3. [Project Management Commands](#project-management-commands)
4. [Document Processing Commands](#document-processing-commands)
5. [Server Management Commands](#server-management-commands)
6. [System Tools Commands](#system-tools-commands)
7. [Quick Setup Commands](#quick-setup-commands)
8. [Common Workflows](#common-workflows)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)

## 🛠️ Installation & Setup

### Prerequisites

```bash
# Ensure Python 3.11+ is installed
python3 --version

# Install the GraphRAG MCP Toolkit
pip install graphrag-mcp-toolkit

# Start required services
ollama serve  # In separate terminal

# Optional: Start Neo4j for advanced features
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### Basic Usage

```bash
# Get help
graphrag-mcp --help

# Get help for specific command
graphrag-mcp create --help

# Enable verbose output
graphrag-mcp --verbose status
```

## 🌐 Global Options

These options work with all commands:

```bash
graphrag-mcp [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Available Global Options

- `--verbose, -v`: Enable verbose output and debug logging
- `--config-dir PATH`: Custom configuration directory (default: `~/.graphrag-mcp`)
- `--help`: Show help message and exit

### Examples

```bash
# Verbose mode for debugging
graphrag-mcp --verbose create my-project

# Custom config directory
graphrag-mcp --config-dir ./custom-config status

# Get help
graphrag-mcp --help
```

## 📁 Project Management Commands

### create

Create a new GraphRAG project with specified template.

```bash
graphrag-mcp create [OPTIONS] PROJECT_NAME
```

**Arguments:**
- `PROJECT_NAME`: Name of the project to create

**Options:**
- `--template, -t TEXT`: Domain template to use (default: "academic")
- `--directory, -d PATH`: Project directory (default: `~/.graphrag-mcp/projects`)
- `--force, -f`: Overwrite existing project without confirmation

**Examples:**
```bash
# Create academic research project
graphrag-mcp create literature-review

# Create project with specific template
graphrag-mcp create legal-analysis --template legal

# Create in custom directory
graphrag-mcp create my-research --directory ./projects

# Force overwrite existing project
graphrag-mcp create existing-project --force
```

**Output:**
```
🚀 Creating new assistant: literature-review
✅ Assistant 'literature-review' created successfully!

📁 Location: /Users/username/.graphrag-mcp/projects/literature-review
🎯 Template: academic

Next steps:
  1. Add documents: graphrag-mcp add-documents literature-review ./papers/
  2. Process corpus: graphrag-mcp process literature-review
  3. Start server: graphrag-mcp serve literature-review
```

### templates

Manage and view available domain templates.

```bash
graphrag-mcp templates [OPTIONS]
```

**Options:**
- `--list, -l`: List available templates (default)
- `--info, -i TEXT`: Show detailed information about a template
- `--install PATH`: Install template from URL or path (planned)

**Examples:**
```bash
# List all available templates
graphrag-mcp templates --list

# Get detailed info about academic template
graphrag-mcp templates --info academic

# Install custom template (planned)
graphrag-mcp templates --install ./my-template.json
```

**Output:**
```
📋 Available Templates

┌─────────────┬──────────────────────────────────────────┬─────────────┐
│ Template    │ Description                              │ Status      │
├─────────────┼──────────────────────────────────────────┼─────────────┤
│ academic    │ Literature review and research analysis  │ ✅ Available │
│ legal       │ Legal document analysis (planned)        │ 🚧 Planned   │
│ medical     │ Clinical guidelines and protocols        │ 🚧 Planned   │
│ financial   │ Financial document analysis (planned)    │ 🚧 Planned   │
│ engineering │ Technical specifications (planned)       │ 🚧 Planned   │
└─────────────┴──────────────────────────────────────────┴─────────────┘
```

### status

Show project status and system health information.

```bash
graphrag-mcp status [PROJECT_NAME]
```

**Arguments:**
- `PROJECT_NAME`: Optional project name for specific status

**Examples:**
```bash
# Show all projects status
graphrag-mcp status

# Show specific project status
graphrag-mcp status my-project
```

**Output:**
```
📊 GraphRAG MCP Toolkit Status

🔧 System Health
✅ Ollama server: Online
✅ LLM model (llama3.1:8b): Available
✅ Embedding model (nomic-embed-text): Available

📁 Projects
┌─────────────┬──────────┬───────────┬───────────┬─────────────────┐
│ Project     │ Template │ Documents │ Processed │ Status          │
├─────────────┼──────────┼───────────┼───────────┼─────────────────┤
│ my-research │ academic │ 5         │ 5         │ ✅ Ready         │
│ legal-docs  │ legal    │ 3         │ 0         │ 🔄 Needs processing │
└─────────────┴──────────┴───────────┴───────────┴─────────────────┘
```

## 📄 Document Processing Commands

### add-documents

Add documents to a project for processing.

```bash
graphrag-mcp add-documents [OPTIONS] PROJECT_NAME PATHS...
```

**Arguments:**
- `PROJECT_NAME`: Name of the project
- `PATHS`: Document paths to add (files or directories)

**Options:**
- `--recursive, -r`: Scan directories recursively

**Examples:**
```bash
# Add single document
graphrag-mcp add-documents my-project ./paper.pdf

# Add multiple documents
graphrag-mcp add-documents my-project ./paper1.pdf ./paper2.pdf

# Add all PDFs from directory
graphrag-mcp add-documents my-project ./papers/

# Add recursively from directory tree
graphrag-mcp add-documents my-project ./research/ --recursive
```

**Output:**
```
📄 Adding documents to project: my-project
✅ Added 5 documents:
  📄 attention_paper.pdf
  📄 transformer_survey.pdf
  📄 bert_paper.pdf
  📄 gpt_paper.pdf
  📄 t5_paper.pdf
```

### process

Process documents into knowledge graphs with citations.

```bash
graphrag-mcp process [OPTIONS] PROJECT_NAME
```

**Arguments:**
- `PROJECT_NAME`: Name of the project to process

**Options:**
- `--force, -f`: Reprocess existing documents
- `--graphiti-only`: Only populate knowledge graph, skip JSON export

**Examples:**
```bash
# Process all documents in project
graphrag-mcp process my-project

# Force reprocessing of all documents
graphrag-mcp process my-project --force

# Only update knowledge graph
graphrag-mcp process my-project --graphiti-only
```

**Output:**
```
⚙️ Processing project: my-project
📋 Template: academic
📁 Documents: 5 PDF files
🧠 Knowledge Graph: Persistent Neo4j

🔌 Connecting to Neo4j...
✅ Connected to knowledge graph

Processing Documents:
📄 Processing attention_paper.pdf...
   ✅ Added to knowledge graph: attention_paper.pdf
📄 Processing transformer_survey.pdf...
   ✅ Added to knowledge graph: transformer_survey.pdf
📄 Processing bert_paper.pdf...
   ✅ Added to knowledge graph: bert_paper.pdf

📊 Knowledge Graph Stats: 245 nodes, 189 relationships

🎉 Processing Complete!
📄 Documents: 5 processed
🧠 Knowledge Graph: Populated in Neo4j
📁 Metadata: Saved to processed/

Next step:
  Start MCP server: graphrag-mcp serve my-project
```

## 🚀 Server Management Commands

### serve

Start MCP server for a processed project.

```bash
graphrag-mcp serve [OPTIONS] PROJECT_NAME
```

**Arguments:**
- `PROJECT_NAME`: Name of the project to serve

**Options:**
- `--port, -p INTEGER`: Server port (default: 8080)
- `--host TEXT`: Server host (default: "localhost")
- `--transport, -t TEXT`: Transport method - "http" or "stdio" (default: "http")
- `--background, -b`: Run in background (planned)

**Examples:**
```bash
# Start HTTP server on default port
graphrag-mcp serve my-project

# Start on specific port
graphrag-mcp serve my-project --port 8081

# Start with stdio transport for Claude Desktop
graphrag-mcp serve my-project --transport stdio

# Start HTTP server on custom host/port
graphrag-mcp serve my-project --host 0.0.0.0 --port 9000
```

**Output:**
```
🚀 Starting MCP server for: my-project
📋 Server: localhost:8080 (http)
🎯 Template: academic
🧠 Knowledge Graph: Neo4j
📊 Documents in Graph: 5/5
📈 Graph Stats: 245 nodes, 189 relationships

🔌 Connecting to knowledge graph...
✅ Connected to knowledge graph

🚀 MCP Server Running!
📡 Endpoint: localhost:8080
🧠 Knowledge Graph: Connected to Neo4j
📋 Project: my-project (academic template)
📊 Documents: 5 in knowledge graph

Claude Desktop Integration:
{"mcpServers": {"graphrag-my-project": {"command": "graphrag-mcp", "args": ["serve", "my-project", "--transport", "stdio"]}}}

Stop server: Ctrl+C
```

### serve-universal

Start universal MCP server without a specific project.

```bash
graphrag-mcp serve-universal [OPTIONS]
```

**Options:**
- `--template, -t TEXT`: Domain template to use (default: "academic")
- `--port, -p INTEGER`: Server port (default: 8080)
- `--host TEXT`: Server host (default: "localhost")
- `--transport TEXT`: Transport method - "http" or "stdio" (default: "http")

**Examples:**
```bash
# Start universal server with academic template
graphrag-mcp serve-universal

# Start with different template
graphrag-mcp serve-universal --template legal

# Start with stdio transport for Claude Desktop
graphrag-mcp serve-universal --template academic --transport stdio
```

**Output:**
```
🚀 Starting Universal MCP Server
📋 Server: localhost:8080 (http)
🎯 Template: academic
📄 No documents loaded (use load_document_collection tool)

🚀 Universal MCP Server Running!
📡 Endpoint: localhost:8080
🎯 Template: academic
📄 Use load_document_collection tool to add documents
🛠️ All MCP tools available for Claude integration
```

### serve-graphiti

Start Graphiti-powered MCP server with real-time knowledge graphs.

```bash
graphrag-mcp serve-graphiti [OPTIONS]
```

**Options:**
- `--template, -t TEXT`: Domain template to use (default: "academic")
- `--port, -p INTEGER`: Server port (default: 8080)
- `--host TEXT`: Server host (default: "localhost")
- `--neo4j-uri TEXT`: Neo4j connection URI (default: "bolt://localhost:7687")
- `--neo4j-user TEXT`: Neo4j username (default: "neo4j")
- `--neo4j-password TEXT`: Neo4j password (default: "password")

**Examples:**
```bash
# Start Graphiti server with defaults
graphrag-mcp serve-graphiti

# Start with custom Neo4j connection
graphrag-mcp serve-graphiti --neo4j-uri bolt://remote:7687 --neo4j-user admin --neo4j-password secret

# Start with legal template
graphrag-mcp serve-graphiti --template legal
```

**Output:**
```
🚀 Starting Graphiti MCP Server
📋 Server: localhost:8080
🎯 Template: academic
🗃️ Neo4j: bolt://localhost:7687
🧠 Backend: Graphiti + Neo4j

🔍 Checking Neo4j connection...
🚀 Starting Graphiti MCP Server...
📊 Real-time knowledge graph capabilities enabled
🔗 Use add_document_to_graph tool to add documents
🔍 Use search_knowledge_graph tool for semantic search
```

## 🔧 System Tools Commands

### visualize

Show knowledge graph visualization using Graphiti + yFiles.

```bash
graphrag-mcp visualize [OPTIONS] PROJECT_NAME
```

**Arguments:**
- `PROJECT_NAME`: Name of the project to visualize

**Options:**
- `--max-nodes INTEGER`: Maximum nodes to display (default: 50)
- `--interactive / --static`: Interactive vs static visualization (default: interactive)
- `--output PATH`: Save visualization to file

**Examples:**
```bash
# Create interactive visualization
graphrag-mcp visualize my-project

# Create with more nodes
graphrag-mcp visualize my-project --max-nodes 100

# Save to file
graphrag-mcp visualize my-project --output graph.html

# Create static visualization
graphrag-mcp visualize my-project --static
```

**Output:**
```
🕸️ Visualizing knowledge graph for: my-project
🔍 Creating knowledge graph visualization...
✅ Knowledge graph visualization created successfully!
📄 Interactive visualization opened in browser
```

### validate

Validate system prerequisites and configuration.

```bash
graphrag-mcp validate [OPTIONS]
```

**Options:**
- `--verbose, -v`: Show detailed validation information
- `--fix`: Attempt to fix common issues automatically

**Examples:**
```bash
# Basic validation
graphrag-mcp validate

# Detailed validation with verbose output
graphrag-mcp validate --verbose

# Validation with automatic fixes
graphrag-mcp validate --fix
```

**Output:**
```
🔍 System Validation

✅ Python version: 3.11+ (recommended)
✅ Ollama server: Connected and working
✅ LLM model (llama3.1:8b): Available
⚠️ Neo4j connection: Optional (for advanced features)
✅ ChromaDB: Available

🎉 System validation passed!
✅ All components are working correctly
```

## ⚡ Quick Setup Commands

### quick-setup

Create project, add documents, and optionally process them in one command.

```bash
graphrag-mcp quick-setup [OPTIONS] PROJECT_NAME DOCUMENTS_PATH
```

**Arguments:**
- `PROJECT_NAME`: Name of the project to create
- `DOCUMENTS_PATH`: Path to documents folder or file

**Options:**
- `--template, -t TEXT`: Domain template to use (default: "academic")
- `--auto-process / --no-process`: Automatically process documents (default: auto-process)
- `--auto-serve`: Start MCP server after processing

**Examples:**
```bash
# Quick setup with processing
graphrag-mcp quick-setup research-project ./papers/

# Quick setup with custom template
graphrag-mcp quick-setup legal-analysis ./contracts/ --template legal

# Quick setup with auto-serve
graphrag-mcp quick-setup my-research ./docs/ --auto-serve

# Quick setup without processing
graphrag-mcp quick-setup draft-project ./papers/ --no-process
```

**Output:**
```
🚀 Quick Setup: research-project

📁 Step 1: Creating project...
✅ Project created successfully

📄 Step 2: Adding documents...
✅ Added 8 documents

⚙️ Step 3: Processing documents...
✅ Documents processed successfully

🚀 Step 4: Starting MCP server...
💡 Use Ctrl+C to stop the server

🎉 Quick Setup Complete!
📁 Project: research-project
📄 Documents: 8 added
🎯 Template: academic
```

## 🔄 Common Workflows

### Complete Project Workflow

```bash
# 1. Validate system
graphrag-mcp validate

# 2. Create project
graphrag-mcp create my-research --template academic

# 3. Add documents
graphrag-mcp add-documents my-research ./papers/ --recursive

# 4. Process documents
graphrag-mcp process my-research

# 5. Visualize results
graphrag-mcp visualize my-research --max-nodes 50

# 6. Start MCP server
graphrag-mcp serve my-research --transport stdio
```

### Quick Start Workflow

```bash
# All-in-one command
graphrag-mcp quick-setup my-research ./papers/ --auto-serve

# Or with validation first
graphrag-mcp validate --fix
graphrag-mcp quick-setup my-research ./papers/ --auto-serve
```

### Development Workflow

```bash
# Check system status
graphrag-mcp status

# Create development project
graphrag-mcp create dev-project --template academic

# Add test documents
graphrag-mcp add-documents dev-project ./test-papers/

# Process with force refresh
graphrag-mcp process dev-project --force

# Start universal server for testing
graphrag-mcp serve-universal --template academic --transport stdio
```

### Production Workflow

```bash
# System validation
graphrag-mcp validate --verbose

# Create production project
graphrag-mcp create prod-system --template academic

# Add production documents
graphrag-mcp add-documents prod-system ./production-docs/ --recursive

# Process documents
graphrag-mcp process prod-system

# Start production server
graphrag-mcp serve prod-system --host 0.0.0.0 --port 8080
```

## ⚙️ Configuration

### Configuration Files

The CLI uses these configuration files:

```
~/.graphrag-mcp/
├── config.json          # Global configuration
├── projects/            # Project directories
│   ├── my-project/
│   │   ├── config.json  # Project configuration
│   │   ├── documents/   # Source documents
│   │   ├── processed/   # Processed metadata
│   │   └── README.md    # Project documentation
│   └── ...
└── templates/           # Custom templates
```

### Environment Variables

```bash
# Model configuration
export GRAPHRAG_LLM_MODEL="llama3.1:8b"
export GRAPHRAG_EMBEDDING_MODEL="nomic-embed-text"
export GRAPHRAG_TEMPERATURE="0.1"

# Storage configuration
export GRAPHRAG_CHROMADB_PATH="chroma_graph_db"
export GRAPHRAG_NEO4J_URI="bolt://localhost:7687"
export GRAPHRAG_NEO4J_USER="neo4j"
export GRAPHRAG_NEO4J_PASSWORD="password"

# Processing configuration
export GRAPHRAG_CHUNK_SIZE="1000"
export GRAPHRAG_CHUNK_OVERLAP="200"
export GRAPHRAG_CITATION_STYLE="APA"

# MCP configuration
export GRAPHRAG_MCP_SERVER_NAME="GraphRAG Research Assistant"
```

### Project Configuration

Each project has a `config.json` file:

```json
{
  "name": "my-research",
  "template": "academic",
  "created_date": "2024-01-15T10:30:00Z",
  "version": "0.1.0",
  "documents": [],
  "last_processed": "2024-01-15T11:00:00Z",
  "documents_in_graph": 5,
  "graphiti_enabled": true,
  "mcp_server": {
    "port": 8080,
    "host": "localhost",
    "enabled": true
  }
}
```

## 🆘 Troubleshooting

### Common Issues

#### "Command not found: graphrag-mcp"

```bash
# Check installation
pip show graphrag-mcp-toolkit

# Reinstall if needed
pip install --upgrade graphrag-mcp-toolkit

# Check PATH
echo $PATH
```

#### "Ollama server not accessible"

```bash
# Start Ollama
ollama serve

# Check if running
curl -s http://localhost:11434/api/tags

# Validate with CLI
graphrag-mcp validate --verbose
```

#### "No documents found"

```bash
# Check document path
ls -la ./papers/

# Check supported formats
graphrag-mcp add-documents --help

# Add documents explicitly
graphrag-mcp add-documents my-project ./papers/document.pdf
```

#### "Neo4j connection failed"

```bash
# Start Neo4j
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

# Check connection
curl -f http://localhost:7474/

# Use without Neo4j
graphrag-mcp process my-project --graphiti-only
```

#### "Processing failed"

```bash
# Check logs with verbose mode
graphrag-mcp --verbose process my-project

# Try force reprocessing
graphrag-mcp process my-project --force

# Check document format
file ./papers/document.pdf
```

### Debug Commands

```bash
# System validation
graphrag-mcp validate --verbose --fix

# Check status
graphrag-mcp status

# Test configuration
python3 -c "from graphrag_mcp.core.config import GraphRAGConfig; print(GraphRAGConfig())"

# Check project structure
ls -la ~/.graphrag-mcp/projects/my-project/
```

### Performance Tips

1. **Use --force sparingly** - Only reprocess when necessary
2. **Monitor memory usage** - Process large collections in batches
3. **Use appropriate chunk sizes** - Adjust for your document types
4. **Enable Neo4j** - For better performance with large knowledge graphs
5. **Use stdio transport** - For Claude Desktop integration

### Getting Help

```bash
# General help
graphrag-mcp --help

# Command-specific help
graphrag-mcp create --help
graphrag-mcp process --help
graphrag-mcp serve --help

# Verbose mode for debugging
graphrag-mcp --verbose [command]
```

## 📚 Advanced Usage

### Custom Templates

Create custom domain templates:

```bash
# Copy academic template
cp ~/.graphrag-mcp/templates/academic.json ~/.graphrag-mcp/templates/medical.json

# Edit template
nano ~/.graphrag-mcp/templates/medical.json

# Use custom template
graphrag-mcp create medical-project --template medical
```

### Batch Processing

Process multiple projects:

```bash
# Process multiple projects
for project in research-1 research-2 research-3; do
    graphrag-mcp process $project --force
done

# Start multiple servers
graphrag-mcp serve research-1 --port 8080 &
graphrag-mcp serve research-2 --port 8081 &
graphrag-mcp serve research-3 --port 8082 &
```

### Integration Scripts

Create shell scripts for common workflows:

```bash
#!/bin/bash
# setup-research.sh
PROJECT_NAME=$1
DOCS_PATH=$2

graphrag-mcp validate --fix
graphrag-mcp create $PROJECT_NAME --template academic
graphrag-mcp add-documents $PROJECT_NAME $DOCS_PATH --recursive
graphrag-mcp process $PROJECT_NAME
graphrag-mcp visualize $PROJECT_NAME --max-nodes 100
```

### Docker Integration

Use with Docker:

```bash
# Build container with GraphRAG
docker build -t my-graphrag .

# Run with mounted documents
docker run -v ./papers:/papers my-graphrag graphrag-mcp quick-setup research /papers
```

---

This CLI reference provides complete documentation for all GraphRAG MCP Toolkit commands. For Python API usage, see [API_REFERENCE.md](API_REFERENCE.md). For MCP tools, see [MCP_TOOLS.md](MCP_TOOLS.md).