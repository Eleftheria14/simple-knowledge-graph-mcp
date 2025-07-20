#!/bin/bash

# Deploy MCP Server to Railway for HTTPS access

echo "🚀 Deploying Knowledge Graph MCP to Railway..."
echo ""
echo "📋 Prerequisites:"
echo "   1. Install Railway CLI: npm install -g @railway/cli"
echo "   2. Login to Railway: railway login"
echo "   3. Have a Railway account: https://railway.app"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install with: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI found"

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged into Railway. Run: railway login"
    exit 1
fi

echo "✅ Railway authenticated"

# Create railway project
echo "🏗️  Creating Railway project..."
railway new knowledge-graph-mcp

# Add environment variables
echo "⚙️  Setting environment variables..."
railway variables set \
    NEO4J_URI=neo4j+s://your-neo4j-aura-instance.databases.neo4j.io \
    NEO4J_USER=neo4j \
    NEO4J_PASSWORD=your-password \
    CHROMADB_PATH=/app/chroma_db

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Get your Railway URL: railway domain"
echo "   2. Use HTTPS URL in Claude Desktop connector"
echo "   3. Format: https://knowledge-graph-mcp.railway.app"