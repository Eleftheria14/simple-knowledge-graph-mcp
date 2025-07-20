# Getting Started with Simple Knowledge Graph MCP

## Prerequisites
- **Python 3.11+** (required for FastMCP)
- **Docker** (for Neo4j database)
- **Claude Desktop** (to use the MCP tools)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
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

### Option 1: Easy GUI Setup (Recommended)

**1. Start HTTP Server**
```bash
./scripts/start_http_server.sh
```

**2. Add Connector in Claude Desktop**
- Open Claude Desktop → Settings → Connectors
- Click "Add custom connector"
- **Name**: `Knowledge Graph`
- **URL**: `http://localhost:3001`
- Click "Add"

**3. Restart Claude Desktop**
Close and reopen Claude Desktop application.

### Option 2: Advanced JSON Setup

**1. Edit Configuration File**
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**2. Add This Configuration**
```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/Users/aimiegarces/Agents/src/server/main.py"
      ]
    }
  }
}
```

**3. Restart Claude Desktop**
Close and reopen Claude Desktop application.

## Using the System

### 1. Start the MCP Server

**For GUI Setup (Option 1)**:
```bash
./scripts/start_http_server.sh
```

**For JSON Setup (Option 2)**:
```bash
./scripts/start_mcp_server.sh
```

Keep this running while using Claude.

### 2. In Claude Desktop
You now have 5 tools available:
- `store_entities` - Store extracted entities/relationships
- `store_vectors` - Store any content as vectors with embeddings  
- `query_knowledge_graph` - Search your knowledge base
- `generate_literature_review` - Format results for writing
- `clear_knowledge_graph` - Reset all data

### 3. Basic Workflow
1. Upload PDF to Claude Project
2. Ask Claude to extract entities: "Extract entities and relationships from this document"
3. Store text chunks: "Store the key text passages from this document"
4. Query your knowledge: "What does my knowledge graph say about [topic]?"

## Troubleshooting

**MCP server won't start:**
```bash
cd src && uv run python server/main.py
# Check for error messages
```

**Neo4j connection issues:**
```bash
docker ps
# Should show neo4j container running on port 7687
```

**Claude doesn't see tools:**
- Check config.json path is correct
- Restart Claude Desktop
- Verify MCP server is running

That's it! Your knowledge graph system is ready to use.