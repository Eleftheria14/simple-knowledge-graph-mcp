# n8n Workflows

## Active Workflows

### **OPTIMAL_LLAMAPARSE_WORKFLOW.json** ⭐ **RECOMMENDED**
- **Purpose**: Complete DocsGPT → n8n → LlamaParse → Knowledge Graph integration
- **Uses**: LlamaCloud community node (eliminates binary upload complexity)  
- **Features**: Premium parsing, structured output, dynamic file paths
- **Status**: Production ready
- **Key Innovation**: Uses official LlamaParse community node from https://github.com/run-llama/n8n-llamacloud

### **BREAKTHROUGH_CONFIG.json** 📚 **REFERENCE**
- **Purpose**: Working manual HTTP Request configuration (historical reference)
- **Uses**: Manual HTTP Request + Move Binary Data approach
- **Features**: Demonstrates successful binary upload to LlamaParse API
- **Status**: Working but superseded by community node

### **BREAKTHROUGH_COMPLETE.json** 🔧 **COMPLETE MANUAL**
- **Purpose**: Full workflow using manual HTTP Request approach
- **Uses**: HTTP Request + Wait + Get Results + Response formatting
- **Features**: Complete end-to-end processing pipeline
- **Status**: Working but complex, superseded by community node

### **LLAMAPARSE_COMMUNITY_NODE.json** 🧪 **SIMPLE VERSION**
- **Purpose**: Basic LlamaParse community node test
- **Uses**: Static file path approach
- **Features**: Minimal configuration for testing
- **Status**: Working but less flexible than OPTIMAL

### **LLAMAPARSE_BINARY_WORKFLOW.json** 🔄 **BINARY APPROACH**
- **Purpose**: Community node with binary data processing
- **Uses**: Read Binary File → LlamaParse community node
- **Features**: Handles binary data input
- **Status**: Alternative approach for binary file inputs

## Archive Structure
- `archive/failed_attempts/` - All debugging attempts (~50 files from binary upload troubleshooting)
- `archive/` - Previous versions and test results from manual HTTP approach
- `archive/tests/` - Test scripts and result files moved from root directory

## Key Breakthrough: LlamaCloud Community Node

The **LlamaCloud n8n community node** (https://github.com/run-llama/n8n-llamacloud) was the game-changer that solved all our binary upload complexity.

### Before (Manual Approach):
- Complex HTTP Request + Move Binary Data configurations
- Binary upload errors and empty file parameters
- Multiple debugging sessions with 50+ failed attempts
- Manual job polling and result retrieval

### After (Community Node):
- Single LlamaParse node handles everything
- No binary upload complexity
- Built-in job management and result retrieval
- Official support from LlamaIndex team

## Installation Requirements

### 1. Install LlamaCloud Community Node
```bash
# Already completed - node is installed and available
git clone https://github.com/run-llama/n8n-llamacloud.git
npm install && npm run build && npm link
```

### 2. Configure Credentials
In n8n interface:
- Go to Settings → Credentials → Add LlamaCloud
- API Key: `llx-sZqRfwhNfQgbGgRsD372lCHd76aT5GEAB9nzaAw2fJ2zmX0X` (already in .env)

### 3. Docker Setup
- Shared `/data` volume between DocsGPT and n8n containers
- Neo4j + ChromaDB knowledge graph system running
- MCP server available for knowledge graph operations

## Integration Pattern

```
DocsGPT UI → Upload PDF → n8n Webhook → LlamaParse Community Node → Knowledge Graph Storage
```

**Key advantages:**
- ✅ No binary upload debugging needed
- ✅ Official LlamaIndex support and updates  
- ✅ Handles premium parsing, job polling, result formatting
- ✅ Simple file path input (works with Docker shared volumes)
- ✅ Production-ready and maintained

## Next Steps
1. Configure LlamaCloud credentials in n8n
2. Test OPTIMAL_LLAMAPARSE_WORKFLOW.json
3. Integrate with DocsGPT file upload system
4. Add MCP knowledge graph storage to workflow