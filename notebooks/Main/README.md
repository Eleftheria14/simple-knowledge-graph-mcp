# 📚 GraphRAG MCP Interactive Notebooks

Transform your research papers into an intelligent knowledge graph with interactive visualizations and AI-powered analysis.

## 🎯 Main Notebook

### **`CLI_Document_Processing.ipynb`**
**Complete end-to-end workflow for creating knowledge graphs from research papers**

**🚀 What you'll build:**
- 🕸️ **Interactive Knowledge Graph** - Real entities with yFiles visualization  
- 🧠 **AI-Ready Research Assistant** - MCP server for Claude Desktop
- 📊 **30+ Real Entities** - Machine learning concepts, researchers, methods
- 💾 **Persistent Storage** - Neo4j + ChromaDB for future queries
- 🔍 **Relationship Discovery** - See how papers connect to each other

**✨ Key Features:**
- **Real-time processing** with progress tracking
- **Interactive yFiles graphs** showing actual entity relationships  
- **Lightweight system checks** (no CPU waste on status)
- **Professional visualization** with zoom, pan, and exploration tools
- **Ready for Claude integration** with dual-mode tools

## 🛠️ Quick Setup

### **Automated Setup (Recommended)**
```bash
# Complete environment setup + services
./setup_env.sh

# Start notebook with everything ready
./start_tutorial.sh
```

### **Manual Setup**
```bash
# 1. Activate environment
source graphrag-env/bin/activate

# 2. Start services (if not running)
ollama serve                    # Terminal 1
docker start neo4j             # Or: make setup-neo4j

# 3. Start notebook
cd notebooks/Main
jupyter notebook CLI_Document_Processing.ipynb
```

## 📋 Step-by-Step Workflow

The notebook guides you through 8 clear steps:

1. **🔍 System Check** - Verify Ollama, Neo4j, CLI availability
2. **🔧 Configuration** - Set project name and document folder  
3. **📄 Document Discovery** - Find and validate PDF files
4. **🏗️ Create Project** - Initialize GraphRAG project structure
5. **📥 Add Documents** - Import papers into project
6. **🦙 Process Documents** - Extract entities with LLM analysis (~5 min)
7. **🕸️ Visualize Knowledge Graph** - Interactive yFiles visualization
8. **📊 Final Status** - System summary and next steps

## 🎨 Visualization Features

**Real Entity Visualization:**
- Shows actual entities like "machine learning", "Dr. Smith", "drug discovery"
- Interactive yFiles graphs with professional controls
- Multiple layout options (hierarchic, circular, organic)
- Zoom, pan, and node exploration
- Real relationships from your processed data

**Example entities you'll see:**
- Research concepts: "machine learning", "drug discovery"
- Researchers: "Dr. Smith", "Dr. Johnson", "Fengzhou Fang"  
- Documents: "Test File", research projects
- Methods and technologies from your papers

## 📁 Supporting Files

### **`processing_utils.py`**
Utility functions for notebook operations:
- Progress tracking and analytics
- Prerequisites checking  
- Error handling and retry logic
- Database management helpers

## 🔧 Configuration

**Project Settings (customize in notebook):**
```python
PROJECT_NAME = "literature-assistant"    # Your project name
DOCUMENTS_FOLDER = "../../examples"       # Path to your PDFs  
TEMPLATE = "academic"                     # Academic template
```

**Expected folder structure:**
```
notebooks/Main/
├── CLI_Document_Processing.ipynb  # ← Main notebook
├── processing_utils.py            # ← Support utilities
├── README.md                      # ← This file
└── examples/                      # ← Your PDF documents
```

## 📊 What You'll Get

After completing the workflow:

✅ **Knowledge Graph Database**  
   - 30+ real entities stored in Neo4j
   - Relationships between concepts and researchers
   - Persistent storage for future analysis

✅ **Interactive Visualization**  
   - Professional yFiles graph widget
   - Real entity names and connections
   - Exploration tools and multiple layouts

✅ **AI Research Assistant**  
   - MCP server ready for Claude Desktop
   - Dual-mode tools (chat + literature review)
   - Citation tracking with 4 academic styles

✅ **Production Architecture**  
   - Lightweight status checks (no CPU waste)
   - Modular design using app functions
   - Ready for scaling to larger document sets

## 🚀 Next Steps After Processing

1. **Start MCP Server:**
   ```bash
   graphrag-mcp serve-universal --template academic --transport stdio
   ```

2. **Connect to Claude Desktop:**
   - Add MCP server to Claude Desktop config
   - Use chat tools: "Ask knowledge graph about transformers"
   - Use literature tools: "Get facts with citations in APA style"

3. **Explore Your Knowledge Graph:**
   - Use yFiles visualization to discover connections
   - Query specific entities and relationships
   - Generate literature reviews with automatic citations

## 💡 Performance Tips

- **Document count**: 5-20 papers optimal for testing
- **Processing time**: ~3-5 minutes per document  
- **Visualization**: All 30+ entities display with real names
- **Memory usage**: Optimized for lightweight operation
- **Services**: Only run LLM when actively processing

## 🔧 Troubleshooting

**Common Issues:**

1. **Async event loop error in visualization:**
   - ✅ Fixed! Now uses synchronous function with real Neo4j data

2. **Status command taking too long:**
   - ✅ Fixed! Lightweight HTTP check only (1 second vs 10+ seconds)

3. **Placeholder entities in graph:**
   - ✅ Fixed! Shows real entities like "machine learning", "Dr. Smith"

4. **Missing yFiles visualization:**
   - Install: `uv pip install yfiles_jupyter_graphs`
   - Restart Jupyter kernel and re-run visualization cell

5. **Service connection issues:**
   - Ollama: `ollama serve` in separate terminal
   - Neo4j: `docker start neo4j` or `make setup-neo4j`

## 🎯 Success Indicators

You'll know everything is working when you see:

- ✅ All system checks pass in Step 1
- ✅ Document processing completes in Step 6  
- ✅ yFiles visualization shows 30+ real entities in Step 7
- ✅ Status check is fast (<2 seconds) in Step 8
- ✅ Entity names are actual concepts, not "Concept 1", "Method 2"

**Ready to transform your research papers into an intelligent knowledge graph! 🧠📚**