#!/bin/bash

# Start Ngrok Tunnel for MCP Server
# Creates a public URL like https://abc123.ngrok.io

set -e

echo "🌐 Creating public tunnel for Knowledge Graph MCP..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok not installed. Install from: https://ngrok.com/download"
    echo "   Or: brew install ngrok"
    exit 1
fi

# Check if MCP server is running
if ! curl -f http://localhost:3001 > /dev/null 2>&1; then
    echo "❌ MCP server not running on localhost:3001"
    echo "   Please start it first with: ./scripts/docker_mcp_only.sh"
    exit 1
fi

echo "✅ MCP server detected on localhost:3001"
echo ""
echo "🚀 Starting ngrok tunnel..."
echo "   This will create a public URL like: https://abc123.ngrok.io"
echo "   Press Ctrl+C to stop the tunnel"
echo ""

# Start ngrok tunnel
ngrok http 3001