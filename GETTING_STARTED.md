# Getting Started with Simple Knowledge Graph MCP

⏱️ **Setup Time:** ~15-20 minutes  
💻 **Skill Level:** Beginner (copy-paste commands)

## Prerequisites
- **Python 3.11+** (required for FastMCP)
- **Docker** (for Neo4j database)  
- **Claude Desktop** (to use the MCP tools)

**Need help installing these?** → [Full Prerequisites Guide](PREREQUISITES.md)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Eleftheria14/simple-knowledge-graph-mcp.git
cd simple-knowledge-graph-mcp
```

### 2. Run Setup Script
```bash
./scripts/setup.sh
```
This automatically:
- Installs UV package manager if needed
- Creates Python 3.11 environment
- Installs all dependencies
- Creates `.env` configuration file
- Tests all imports

### 3. Start Database Services
```bash
./scripts/start_services.sh
```
This starts Neo4j in Docker and validates connections.

### 4. Verify Everything Works
```bash
./scripts/check_status.sh
```
Should show all green checkmarks.

## Configure Claude Desktop

**Important**: Claude Desktop uses STDIO (not HTTP) for MCP server connections via a configuration file.

### Step 1: Create Configuration File

**macOS:**
```bash
# Create the configuration directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude

# Create the configuration file (replace YOUR_PROJECT_PATH)
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-c",
        "import sys; sys.path.insert(0, 'YOUR_PROJECT_PATH/src'); from server.main import mcp; mcp.run()"
      ],
      "env": {
        "PYTHONPATH": "YOUR_PROJECT_PATH/src"
      }
    }
  }
}
EOF

# Alternative (Simpler): Use the provided startup script
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "YOUR_PROJECT_PATH/scripts/start_mcp_for_claude.sh",
      "args": []
    }
  }
}
EOF
```

**Windows:**
```bash
# Create at %APPDATA%\Claude\claude_desktop_config.json
# Use same JSON but with Windows paths (use forward slashes in JSON)
```

### Step 2: Test Configuration
1. **Restart Claude Desktop** completely (quit and reopen)
2. **Check for MCP indicator** - look for ⚡ slider icon in bottom left
3. **Test connection**: Ask Claude "What MCP tools do you have available?"

**✅ Success indicators:**
- ⚡ icon appears in Claude Desktop input box
- Claude responds with 8+ tools including: `store_entities`, `store_vectors`, `query_knowledge_graph`, `generate_literature_review`, `clear_knowledge_graph`, and text processing tools

## Using the System

### 1. Ensure Services Are Running
```bash
# Start Neo4j and other required services
./scripts/start_services.sh

# Verify everything is working
./scripts/check_status.sh
```

**Note**: You don't need to manually start the MCP server - Claude Desktop will launch it automatically using the configuration file.

### 2. In Claude Desktop
You now have 8+ tools available:

**Core Knowledge Graph Tools:**
- `store_entities` - Store extracted entities/relationships
- `store_vectors` - Store any content as vectors with embeddings  
- `query_knowledge_graph` - Search your knowledge base
- `generate_literature_review` - Format results for writing
- `clear_knowledge_graph` - Reset all data

**Text Processing Tools:**
- `generate_systematic_chunks` - Automatically chunk papers for complete coverage
- `estimate_chunking_requirements` - Plan optimal chunking strategy
- `validate_text_coverage` - Verify research-grade text coverage

### 3. Basic Workflow
1. Upload PDF to Claude Project
2. Ask Claude to extract entities: "Extract entities and relationships from this document"
3. Store text chunks: "Store the key text passages from this document"
4. Query your knowledge: "What does my knowledge graph say about [topic]?"

## Troubleshooting

**Claude Desktop doesn't show MCP tools:**
1. Check config file exists: `ls ~/Library/Application\ Support/Claude/claude_desktop_config.json`
2. Validate JSON syntax using an online JSON validator
3. Ensure paths in config are absolute and correct
4. Restart Claude Desktop completely (quit and reopen)
5. Look for ⚡ icon in bottom left of input box

**Test MCP server manually:**
```bash
# Test server can start (from project root)
uv run python -c "import sys; sys.path.insert(0, 'src'); from server.main import mcp; print('✅ Server loads successfully')"
```

**Neo4j connection issues:**
```bash
docker ps
# Should show neo4j container running on port 7687
./scripts/check_status.sh
# Should show all green checkmarks
```

**Check Claude Desktop logs (macOS):**
```bash
# View logs for connection errors
tail -f ~/Library/Logs/Claude/claude-desktop.log
```

That's it! Your knowledge graph system is ready to use.