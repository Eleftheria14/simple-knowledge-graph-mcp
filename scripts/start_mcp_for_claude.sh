#!/bin/bash
# Simple MCP Server Startup Script for Claude Desktop

# Change to project directory
cd "/Users/aimiegarces/Agents"

# Set up Python path and run server using full path to UV
export PYTHONPATH="/Users/aimiegarces/Agents/src"
/Users/aimiegarces/.local/bin/uv run python -c "import sys; sys.path.insert(0, 'src'); from server.main import mcp; mcp.run()"