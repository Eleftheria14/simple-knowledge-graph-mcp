# DocsGPT + Knowledge Graph Integration System

**Professional document processing with advanced knowledge graph capabilities - now with unlimited batch processing!**

## 🎯 **What This System Solves**

**Problem**: Claude Desktop conversations get too long after processing just 1-2 research papers, limiting your ability to analyze large document collections.

**Solution**: A comprehensive integration that combines:
- **DocsGPT's professional UI** for document management and chat interface
- **Your superior knowledge graph system** (Neo4j + ChromaDB + MCP) for intelligent entity extraction
- **Batch processing capabilities** to handle unlimited documents without conversation limits
- **Local processing** for complete privacy (no external API dependencies)

## 🚀 **Quick Start**

### **1. Start the System**
```bash
./scripts/start_integrated_docsgpt.sh
```

### **2. Access the Interface**
- **DocsGPT UI**: http://localhost:5173 (main document interface)
- **Neo4j Browser**: http://localhost:7474 (graph visualization)
- **n8n Workflows**: http://localhost:5678 (automation management)

### **3. Test Integration**
```bash
python3 test_docsgpt_integration.py
```

## 🏗️ **System Architecture**

```
User → DocsGPT UI → DocsGPT Backend → KnowledgeGraphRetriever → n8n → MCP Tools → Neo4j + ChromaDB
```

### **Core Components**
1. **DocsGPT Frontend** (React) - Professional document management UI
2. **DocsGPT Backend** (Flask) - Modified to use your knowledge graph
3. **Knowledge Graph Bridge** - Connects DocsGPT to your n8n + MCP system
4. **n8n Workflows** - Automates document processing and entity extraction
5. **MCP Tools** - Your existing tools for Claude Desktop integration
6. **Dual Database System** - Neo4j (graphs) + ChromaDB (vectors)

## 📁 **Project Structure**

```
/Users/aimiegarces/Agents/
├── docs/                           # 📚 Complete documentation
│   ├── integration/                # DocsGPT integration guides
│   ├── mcp/                       # MCP system documentation
│   └── workflows/                 # n8n workflow documentation
├── scripts/                       # 🔧 Management scripts
│   ├── start_integrated_docsgpt.sh # ⭐ Main startup script
│   ├── stop_integrated_system.sh  # Stop all services
│   └── status_integrated_system.sh # Check system health
├── src/                          # 🧠 Your original MCP knowledge graph system
│   ├── storage/                  # Neo4j + ChromaDB integrations
│   ├── tools/                    # MCP tools for entity extraction
│   └── server/                   # MCP server
├── docsgpt-source/               # 🌐 DocsGPT integration
│   ├── application/integrations/ # Bridge to your knowledge graph
│   ├── frontend/src/components/  # Enhanced UI components
│   └── deployment/              # Docker orchestration
├── workflows/                    # 🔄 n8n workflow definitions
├── chroma_db/                   # 💾 Vector database storage
└── archive/                     # 📦 Development artifacts
```

## ✨ **Key Features**

### **🗂️ Professional Document Management**
- Upload documents via drag-and-drop interface
- View extracted entities and relationship counts per document
- Batch processing with real-time progress tracking
- Support for PDF, DOCX, TXT, MD formats

### **🧠 Graph-Enhanced Intelligence**
- All queries use your Neo4j + ChromaDB system (not DocsGPT's default RAG)
- Entity and relationship extraction via Claude/GPT integration
- Cross-document relationship discovery
- Source attribution and citations maintained

### **⚡ Batch Processing**
- Process unlimited documents without conversation limits
- Real-time status updates during processing
- Detailed results showing entities extracted per document
- Automated workflow processing via n8n

### **🔒 Privacy-First Design**
- All processing happens locally on your machine
- Local embeddings using sentence-transformers
- No external API dependencies for core functionality
- Complete control over your data

## 📖 **Documentation**

### **Essential Guides**
- **[Integration Guide](docs/integration/DOCSGPT_INTEGRATION_GUIDE.md)** - Complete setup and usage
- **[MCP Tools Reference](docs/mcp/MCP_TOOLS.md)** - Available tools and usage
- **[Scripts Reference](scripts/README.md)** - Management commands

### **Quick References**
- **[Batch Processing Plan](docs/integration/BATCH_PROCESSING_PLAN.md)** - Implementation details
- **[Entity Extraction Guide](docs/mcp/ENTITY_EXTRACTION_PROMPT.md)** - Prompt engineering
- **[Workflow Diagrams](docs/workflows/N8N_WORKFLOW_DIAGRAM.md)** - n8n architecture

## 🛠️ **Development**

### **Requirements**
- Python 3.11+ with UV package manager
- Docker with 8GB+ memory recommended
- Ports 5173, 7091, 7474, 5678, 3001 available

### **Environment Setup**
```bash
./scripts/setup.sh                    # Install dependencies
./scripts/start_integrated_docsgpt.sh # Start all services
```

### **API Key Setup**
Add your Anthropic or OpenAI API key to `docsgpt-source/application/.env`:
```bash
API_KEY=your_actual_api_key_here
```

## 🌐 **Service URLs**

When the system is running:
- **DocsGPT Interface**: http://localhost:5173
- **DocsGPT API**: http://localhost:7091
- **Neo4j Browser**: http://localhost:7474 (neo4j/password123)
- **n8n Workflows**: http://localhost:5678 (admin/password123)
- **n8n MCP Server**: http://localhost:3001

## 🎉 **Success!**

You now have a **production-ready document processing system** that:
- ✅ Solves Claude Desktop conversation length limits
- ✅ Provides professional document management UI
- ✅ Maintains your superior knowledge graph RAG system
- ✅ Enables unlimited batch processing of research papers
- ✅ Preserves complete privacy with local processing

Perfect for academic research, technical documentation, and any scenario requiring intelligent document analysis with relationship mapping!

## 🔧 **Support**

- **System Status**: `./scripts/status_integrated_system.sh`
- **Integration Tests**: `python3 test_docsgpt_integration.py`  
- **Documentation**: Check [`docs/`](docs/) directory
- **Troubleshooting**: See integration guide troubleshooting section