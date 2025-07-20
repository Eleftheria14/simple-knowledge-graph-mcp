#!/bin/bash

# Create public HTTPS tunnel for MCP server

echo "🌐 Creating public HTTPS tunnel for Claude Desktop..."
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok not installed. Install from: https://ngrok.com/download"
    echo "   Or: brew install ngrok"
    exit 1
fi

# Check if MCP server is running
if ! curl -f http://localhost:3001 > /dev/null 2>&1; then
    echo "❌ MCP server not running. Start with: ./scripts/docker_mcp_only.sh"
    exit 1
fi

echo "✅ MCP server detected"
echo ""
echo "🚀 Starting ngrok HTTPS tunnel..."
echo "   This creates a public URL like: https://abc123.ngrok.io"
echo ""
echo "📋 For Claude Desktop connector:"
echo "   Name: Knowledge Graph"
echo "   URL: [Use the HTTPS URL shown below]"
echo ""
echo "Press Ctrl+C to stop tunnel"
echo ""

# Start ngrok with HTTPS
ngrok http 3001