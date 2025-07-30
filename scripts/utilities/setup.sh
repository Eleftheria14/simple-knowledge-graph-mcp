#!/bin/bash

# UV-based environment setup for Simple Knowledge Graph MCP
# Requires Python 3.11+ for FastMCP compatibility

set -e  # Exit on any error

echo "🚀 Setting up Simple Knowledge Graph MCP Environment with UV..."
echo ""

# Check if UV is available
echo "📦 Checking UV..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "   ✅ Found UV: $UV_VERSION"
else
    echo "   ❌ UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.cargo/env
    echo "   ✅ UV installed"
fi

# Check if Docker is available  
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo "   ✅ Docker is running"
    else
        echo "   ❌ Docker is installed but not running. Please start Docker."
        exit 1
    fi
else
    echo "   ❌ Docker not found. Please install Docker to run Neo4j."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Create UV project with Python 3.11
echo "🐍 Creating Python 3.11 environment with UV..."
if [ ! -f "pyproject.toml" ]; then
    uv init --python 3.11
    echo "   ✅ UV project initialized with Python 3.11"
else
    echo "   ✅ UV project already exists"
fi

# Install dependencies with UV
echo "📚 Installing dependencies with UV..."
uv add $(cat requirements.txt | grep -v '^#' | grep -v '^$' | tr '\n' ' ')
echo "   ✅ Dependencies installed"

# Create .env file if it doesn't exist
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✅ Created .env file from template"
    echo "   💡 You can customize database settings in .env"
else
    echo "   ✅ .env file already exists"
fi

# Test imports
echo "🧪 Testing Python imports..."
uv run python -c "import sentence_transformers, neo4j, chromadb, fastmcp; print('   ✅ All imports successful')" || {
    echo "   ❌ Import test failed. Please check dependencies."
    exit 1
}

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/start_services.sh (to start Neo4j)"
echo "2. Run: uv run python src/server/main.py (to start the MCP server)"
echo "3. Configure Claude Desktop with this MCP server"
echo "4. Upload PDFs to Claude and start building your knowledge graph!"
echo ""
echo "💡 Use 'uv run python <script>' to run Python commands with dependencies"