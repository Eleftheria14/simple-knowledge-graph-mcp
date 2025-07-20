# Scripts Reference

This folder contains all the automation scripts for the Simple Knowledge Graph MCP system.

## 🚀 **Essential Scripts (Most Users)**

### Setup & Management
- **`setup.sh`** - Complete system setup (Python, dependencies, environment)
- **`check_status.sh`** - Check if all services are running correctly
- **`start_services.sh`** - Start required services (Neo4j database)
- **`stop_services.sh`** - Stop all services cleanly

### Database Management
- **`clear_databases.sh`** - Clear all knowledge graph data (start fresh)

### Claude Desktop Integration
- **`start_mcp_for_claude.sh`** - Main script used by Claude Desktop (configured automatically)

## 🔧 **Alternative Connection Methods**

### For Other MCP Clients
- **`start_http_server.sh`** - Start HTTP server for GUI-based MCP clients
- **`start_mcp_server.sh`** - Start STDIO server for Claude Code integration

## 📋 **Typical Usage**

**First-time setup:**
```bash
./scripts/setup.sh
./scripts/start_services.sh
```

**Daily usage:**
```bash
./scripts/check_status.sh     # Verify everything is working
./scripts/clear_databases.sh  # Only if you want to start fresh
```

**Troubleshooting:**
```bash
./scripts/stop_services.sh
./scripts/start_services.sh
./scripts/check_status.sh
```

## 📝 **Notes**

- All scripts are designed to be run from the project root directory
- Scripts use UV for Python environment management
- Neo4j runs in Docker containers for isolation
- Claude Desktop automatically uses `start_mcp_for_claude.sh` when configured