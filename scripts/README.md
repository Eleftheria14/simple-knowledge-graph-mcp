# Scripts Reference

Organized automation scripts for the **DocsGPT + Knowledge Graph Integration System**.

## 🚀 **Quick Start Commands**

### **Essential Operations**
```bash
./scripts/start_system.sh          # ⭐ Start complete integrated system
./scripts/stop_system.sh           # 🛑 Stop all services cleanly  
./scripts/status_system.sh         # 📊 Check system health
./scripts/utilities/setup.sh       # 🔧 Initial environment setup
```

### **Testing & Verification**
```bash
python3 test_docsgpt_integration.py                # Test integration
./scripts/database/visualize_chromadb.py          # Explore vector data
./scripts/utilities/import_docsgpt_workflow.sh    # Import n8n workflow
```

## 📁 **Organized Script Structure**

```
scripts/
├── 🏠 CONVENIENCE WRAPPERS (Use These!)
│   ├── start_system.sh            # → integrated/start_integrated_docsgpt.sh
│   ├── stop_system.sh             # → integrated/stop_integrated_system.sh  
│   └── status_system.sh           # → integrated/status_integrated_system.sh
│
├── 🔧 integrated/                 # Main DocsGPT + Knowledge Graph system
│   ├── start_integrated_docsgpt.sh   # Complete system startup with health checks
│   ├── stop_integrated_system.sh     # Clean shutdown of all services
│   └── status_integrated_system.sh   # Health monitoring and diagnostics
│
├── 🗂️ system/                    # Legacy/backwards compatibility
│   ├── start_services.sh             # Redirects to integrated system
│   ├── stop_services.sh              # Redirects to integrated system  
│   └── check_status.sh               # Individual service checks
│
├── 🧠 mcp/                       # MCP server variants
│   ├── start_mcp_for_claude.sh       # STDIO MCP for Claude Desktop
│   ├── start_mcp_server.sh           # Advanced STDIO MCP configuration
│   ├── start_http_server.sh          # HTTP MCP for GUI clients
│   └── n8n_mcp_server.sh             # n8n MCP bridge server
│
├── 💾 database/                  # Data management
│   ├── clear_databases.sh            # Clear all knowledge graph data
│   ├── chromadb_dashboard.py         # ChromaDB exploration interface
│   └── visualize_chromadb.py         # Vector database visualization
│
└── ⚙️ utilities/                 # Setup and workflow management
    ├── setup.sh                      # Environment setup (UV, dependencies)
    ├── n8n_manager.sh                # n8n Docker container management
    └── import_docsgpt_workflow.sh    # Import workflow definitions
```

## 📋 **Common Workflows**

### **🆕 First-Time Setup**
```bash
# 1. Install dependencies and setup environment
./scripts/utilities/setup.sh

# 2. Start the complete integrated system
./scripts/start_system.sh

# 3. Import workflow for document processing
./scripts/utilities/import_docsgpt_workflow.sh

# 4. Test everything is working
python3 test_docsgpt_integration.py

# 5. Access the system
# - DocsGPT UI: http://localhost:5173
# - Neo4j Browser: http://localhost:7474 (neo4j/password123)
# - n8n Interface: http://localhost:5678 (admin/password123)
```

### **📝 Daily Usage**
```bash
# Check system health
./scripts/status_system.sh

# Access DocsGPT UI for document processing
# → http://localhost:5173

# Upload papers, build knowledge graphs, query with AI
```

### **🔧 Development & Debugging**
```bash
# Start system with full output
./scripts/start_system.sh

# Monitor specific services
./scripts/system/check_status.sh

# Explore vector database
./scripts/database/visualize_chromadb.py

# Clear data for fresh start
./scripts/database/clear_databases.sh
```

### **🧠 Claude Desktop Integration**
```bash
# For standalone Claude Desktop MCP usage
./scripts/mcp/start_mcp_for_claude.sh

# For HTTP-based MCP clients
./scripts/mcp/start_http_server.sh
```

## 🌐 **Service Architecture**

```
User → DocsGPT UI (5173) → Backend (7091) → Knowledge Graph Bridge → n8n (5678) → MCP Tools (3001) → Neo4j (7474) + ChromaDB
```

## 🎯 **Key Benefits of Organization**

### **✅ Simplified Usage**
- **One command startup**: `./scripts/start_system.sh`
- **Clear categorization**: Find the right script quickly
- **Backwards compatibility**: Legacy scripts still work

### **✅ Maintenance-Friendly**
- **Logical grouping**: Related scripts together
- **Clear dependencies**: Understand what each script does
- **Easy troubleshooting**: Targeted debugging scripts

### **✅ Development-Ready**
- **Modular design**: Add new scripts to appropriate categories
- **Testing support**: Dedicated testing and visualization tools
- **Multiple deployment modes**: Integrated, standalone, or legacy

## 🛠️ **Environment Requirements**

- **Python 3.11+** with UV package manager
- **Docker** with 8GB+ memory recommended  
- **Available Ports**: 5173, 7091, 7474, 5678, 3001
- **API Key**: Add to `docsgpt-source/application/.env`

## 📝 **Important Notes**

### **Data Persistence**
- **Neo4j**: Docker volume `docsgpt-oss_neo4j_data`
- **MongoDB**: Docker volume `docsgpt-oss_mongodb_data_container`  
- **n8n**: Docker volume `docsgpt-oss_n8n_data`
- **ChromaDB**: Local `./chroma_db/` directory

### **Script Execution**
- **Always run from**: `/Users/aimiegarces/Agents/` (project root)
- **Use convenience wrappers**: Prefer `start_system.sh` over nested paths
- **Check status first**: Use `status_system.sh` before troubleshooting

### **System Integration**
- **DocsGPT**: Professional document management UI
- **Knowledge Graph**: Superior entity extraction vs. default RAG
- **Batch Processing**: No conversation length limits
- **Privacy**: Complete local processing, no external APIs

## 🎉 **Success!**

Your scripts are now organized for:
- ✅ **Easy daily use** with convenience wrappers
- ✅ **Clear categorization** by functionality  
- ✅ **Backwards compatibility** with existing workflows
- ✅ **Development flexibility** with modular organization
- ✅ **Professional deployment** with integrated system focus