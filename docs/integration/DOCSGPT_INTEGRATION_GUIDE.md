# DocsGPT + Knowledge Graph Integration Guide

## 🎯 Overview

This integration combines **DocsGPT's professional UI** with our **superior n8n + MCP knowledge graph system**, giving you the best of both worlds:

- ✅ **Professional document management** with upload, organization, and search
- ✅ **Advanced entity extraction** and relationship mapping  
- ✅ **Batch document processing** capabilities
- ✅ **Graph-based question answering** with source citations
- ✅ **Local embeddings** for privacy (no external API dependencies)

## 🚀 Quick Start

### 1. **Start the Integrated System**
```bash
./scripts/start_integrated_docsgpt.sh
```

### 2. **Import n8n Workflow** 
```bash
./scripts/import_docsgpt_workflow.sh
```
Follow the instructions to import the workflow via n8n's web interface.

### 3. **Access the Interfaces**
- **DocsGPT UI**: http://localhost:5173 - Main document processing interface
- **n8n Admin**: http://localhost:5678 - Workflow management (admin/password123)
- **Neo4j Browser**: http://localhost:7474 - Graph database (neo4j/password123)

### 4. **Test the Integration**
```bash
python3 test_docsgpt_integration.py
```

## 📚 Key Features

### 🗂️ **Enhanced Document Library**
- Upload documents with automatic knowledge graph processing
- View extracted entities and relationship counts per document  
- Entity preview tags showing key concepts from each document
- Real-time processing status updates

### ⚡ **Batch Processing**
- Process multiple documents simultaneously
- Progress tracking with real-time status updates
- Detailed results showing entities extracted per document
- Drag-and-drop interface for easy file selection

### 🧠 **Knowledge Graph Integration**  
- All queries use our Neo4j + ChromaDB backend instead of DocsGPT's default RAG
- Entity and relationship extraction via Claude/GPT
- Source attribution and citations maintained
- Graph-based answer generation

### 🔌 **API Endpoints**
New knowledge graph endpoints available:
- `GET /api/entities/top` - Get frequently mentioned entities
- `GET /api/graph/search?query=<query>` - Search knowledge graph
- `GET /api/graph/stats` - Get graph statistics  
- `GET /api/knowledge/health` - Check integration health

## 🏗️ Architecture

```
DocsGPT UI → DocsGPT Backend → Knowledge Graph Retriever → n8n Webhook → MCP Tools → Neo4j + ChromaDB
```

### **Core Components:**
1. **DocsGPT UI** - Professional React frontend with document management
2. **Modified Backend** - DocsGPT Flask app using our KnowledgeGraphRetriever
3. **n8n Workflows** - Process documents and handle API requests 
4. **MCP Server** - Bridge to Claude Desktop for entity extraction
5. **Neo4j** - Graph database for entities and relationships
6. **ChromaDB** - Vector database for semantic search

## 📖 Usage Guide

### **Uploading Documents**
1. Go to DocsGPT UI (http://localhost:5173)
2. Click "Upload" or go to Settings → Documents
3. Drag & drop or select files (PDF, DOCX, TXT, MD supported)
4. Documents are processed by both DocsGPT and our knowledge graph system
5. View extracted entities and relationships in the document library

### **Batch Processing**
1. Go to Settings → Batch Processing
2. Drag multiple files to the upload area
3. Click "Process X Files" to start batch processing
4. Monitor progress and view results in real-time
5. Each document shows entity count and processing time

### **Querying Knowledge** 
1. Use the chat interface as normal
2. All queries now use our knowledge graph backend
3. Answers include source citations and entity relationships
4. More accurate responses due to graph-based context understanding

### **Exploring the Graph**
1. Open Neo4j Browser: http://localhost:7474
2. Login: neo4j/password123
3. Run queries like: `MATCH (n) RETURN n LIMIT 25`
4. Visualize relationships between entities

## 🛠️ Development

### **File Structure**
```
docsgpt-source/
├── application/
│   ├── integrations/           # NEW: Our integration code
│   │   ├── docsgpt_bridge.py  # Knowledge graph retriever
│   │   └── __init__.py
│   ├── api/knowledge/          # NEW: Knowledge graph API
│   │   ├── routes.py          # API endpoints  
│   │   └── __init__.py
│   └── ...                    # Original DocsGPT code
├── frontend/src/
│   ├── components/
│   │   └── BatchProcessor.tsx  # NEW: Batch processing UI
│   └── ...                    # Original DocsGPT UI
└── deployment/
    └── docker-compose.yaml    # UPDATED: Added Neo4j + n8n
```

### **Key Integration Points**

#### **1. Retriever Replacement**
`application/retriever/retriever_creator.py` - Always returns our `KnowledgeGraphRetriever`

#### **2. Document Upload Enhancement**  
`frontend/src/upload/Upload.tsx` - Added knowledge graph processing to upload success callback

#### **3. API Endpoints**
`application/api/knowledge/routes.py` - New endpoints for graph data and statistics

#### **4. Enhanced UI**
`frontend/src/settings/Documents.tsx` - Shows entity counts and relationship previews

### **Making Changes**

#### **Modify Knowledge Graph Logic**
Edit `src/integrations/docsgpt_bridge.py` to change how DocsGPT interfaces with n8n

#### **Update n8n Workflows**  
1. Open n8n: http://localhost:5678
2. Edit the "DocsGPT Integration" workflow
3. Changes take effect immediately

#### **Add New API Endpoints**
Add routes to `application/api/knowledge/routes.py` - they're automatically registered

#### **Customize UI**
Modify components in `frontend/src/` - React dev server will hot reload

## 🧪 Testing

### **Integration Tests**
```bash
python3 test_docsgpt_integration.py
```
Tests all components: DocsGPT, n8n, Neo4j, webhooks, API endpoints

### **Individual Component Tests**
```bash
# Test DocsGPT backend
curl http://localhost:7091/api/config

# Test knowledge graph API
curl http://localhost:7091/api/entities/top

# Test n8n webhook
curl -X POST http://localhost:5678/webhook/docsgpt-integration \
  -H "Content-Type: application/json" \
  -d '{"action": "test", "query": "hello"}'

# Test Neo4j
curl http://localhost:7474
```

### **Debug Mode**
Add debug logging to any component:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

## 🚨 Troubleshooting

### **Services Not Starting**
```bash
# Check service status
docker-compose -f docsgpt-source/deployment/docker-compose.yaml ps

# View logs
docker-compose -f docsgpt-source/deployment/docker-compose.yaml logs -f

# Restart specific service
docker-compose -f docsgpt-source/deployment/docker-compose.yaml restart n8n
```

### **n8n Workflow Issues**
1. Check workflow is imported: http://localhost:5678
2. Ensure workflow is activated (toggle switch)
3. Test webhook endpoint directly
4. Check n8n execution logs in the interface

### **Knowledge Graph Not Working**
1. Verify n8n workflow is active
2. Check webhook endpoints return 200, not 404
3. Ensure Neo4j is accessible at http://localhost:7474
4. Run integration tests to identify specific issues

### **Document Upload Fails**
1. Check DocsGPT logs: `docker logs docsgpt-oss-backend-1`
2. Verify file types are supported (PDF, DOCX, TXT, MD)
3. Check n8n webhook for document processing
4. Ensure sufficient disk space and memory

### **API Errors**
1. Check DocsGPT backend logs for Python errors
2. Verify n8n service is running and accessible
3. Test individual endpoints with curl
4. Check Flask app registration of knowledge blueprint

## 🔧 Configuration

### **Environment Variables**
```bash
# DocsGPT Core
API_KEY=your_anthropic_or_openai_key
LLM_PROVIDER=anthropic
LLM_NAME=claude-3-sonnet-20240229

# Knowledge Graph Integration  
N8N_BASE_URL=http://localhost:5678
KNOWLEDGE_GRAPH_ENABLED=true
MCP_SERVER_URL=http://localhost:3001

# Database URLs
MONGO_URI=mongodb://localhost:27017/docsgpt
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

### **Scaling Configuration**
For production deployments:
- Increase Neo4j memory: `NEO4J_dbms_memory_heap_initial_size=1G`
- Scale n8n workers: Add multiple n8n containers with load balancing
- Use external databases: Configure MongoDB and Neo4j clusters
- Add Redis caching: Configure Redis for API response caching

## 📊 Monitoring

### **Health Endpoints**
- DocsGPT: `http://localhost:7091/api/config`
- Knowledge Graph: `http://localhost:7091/api/knowledge/health`  
- n8n: `http://localhost:5678/healthz`
- Neo4j: `http://localhost:7474`

### **Metrics**
- Document processing success rate
- Entity extraction counts
- Graph query response times
- Memory and CPU usage per service

### **Logging**
All services log to Docker stdout. View with:
```bash
docker-compose -f docsgpt-source/deployment/docker-compose.yaml logs -f [service_name]
```

## 🎉 Success!

You now have a **production-ready document processing system** that combines:
- DocsGPT's polished UI and document management
- Our advanced knowledge graph capabilities  
- Batch processing for handling multiple papers
- Local embeddings for privacy
- Comprehensive API access

Perfect for academic research, technical documentation, and any scenario requiring intelligent document analysis with relationship mapping!

## 📞 Support

If you encounter issues:
1. Run the integration tests: `python3 test_docsgpt_integration.py`
2. Check service logs for specific error messages
3. Verify all environment variables are set correctly
4. Ensure Docker has sufficient resources allocated

The integration is designed to be robust and provide helpful error messages to guide troubleshooting.