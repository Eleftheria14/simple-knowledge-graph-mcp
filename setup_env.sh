#!/bin/bash

# GraphRAG MCP Toolkit Environment Setup Script
# This script sets up a complete development environment with UV

set -e  # Exit on any error

echo "🚀 Setting up GraphRAG MCP Toolkit Environment"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    print_error "UV is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

print_status "UV is installed: $(uv --version)"

# Remove existing virtual environment if it exists
if [ -d "graphrag-env" ]; then
    print_warning "Removing existing graphrag-env virtual environment..."
    rm -rf graphrag-env
fi

# Create new virtual environment with Python 3.11
print_info "Creating new virtual environment with Python 3.11..."
uv venv graphrag-env --python 3.11

# Activate the virtual environment
print_info "Activating virtual environment..."
source graphrag-env/bin/activate

# Verify Python version
PYTHON_VERSION=$(python --version)
print_status "Python version: $PYTHON_VERSION"

# Install core dependencies from pyproject.toml
print_info "Installing core dependencies..."
uv pip install -e .

# Install development dependencies (includes Jupyter)
print_info "Installing development dependencies..."
uv pip install -e ".[dev]"

# Install additional packages needed for the notebook
print_info "Installing additional notebook dependencies..."
uv pip install tqdm pandas matplotlib plotly networkx seaborn ipywidgets

# Install Graphiti dependencies (skip if not available)
print_info "Installing Graphiti dependencies..."
uv pip install neo4j || print_warning "Neo4j client installation failed"
# Note: graphiti-ai may need to be installed separately or from source

# Verify key imports
print_info "Verifying key package imports..."
python -c "
import sys
print(f'Python path: {sys.executable}')

# Test core GraphRAG MCP imports
try:
    from graphrag_mcp.core.document_processor import DocumentProcessor
    print('✅ GraphRAG MCP core imports: OK')
except ImportError as e:
    print(f'❌ GraphRAG MCP core imports failed: {e}')

# Test notebook dependencies
packages = ['pandas', 'matplotlib', 'plotly', 'networkx', 'seaborn', 'tqdm', 'jupyter']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}: OK')
    except ImportError as e:
        print(f'❌ {pkg}: Failed - {e}')

# Test LangChain imports
try:
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print('✅ LangChain imports: OK')
except ImportError as e:
    print(f'❌ LangChain imports failed: {e}')

# Test Graphiti imports (optional)
try:
    from graphiti import Graphiti
    print('✅ Graphiti imports: OK')
except ImportError as e:
    print(f'⚠️  Graphiti imports failed (may need separate installation): {e}')
"

# Create activation script
print_info "Creating convenient activation script..."
cat > activate_graphrag_env.sh << 'EOF'
#!/bin/bash
# Convenient script to activate GraphRAG MCP environment
source graphrag-env/bin/activate
echo "🚀 GraphRAG MCP environment activated!"
echo "📁 Python: $(which python)"
echo "🐍 Version: $(python --version)"
echo ""
echo "💡 To start Jupyter notebook:"
echo "   jupyter notebook"
echo ""
echo "💡 To run the processing notebook:"
echo "   cd notebooks/Main && jupyter notebook Simple_Document_Processing.ipynb"
EOF

chmod +x activate_graphrag_env.sh

print_status "Environment setup complete!"
echo ""
echo "🎉 GraphRAG MCP Toolkit is ready!"
echo "================================="
echo ""
echo "📋 Next steps:"
echo "1. Activate environment: source graphrag-env/bin/activate"
echo "   Or use: ./activate_graphrag_env.sh"
echo ""
echo "2. Start required services:"
echo "   • Ollama: ollama serve"
echo "   • Neo4j: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest"
echo ""
echo "3. Install Ollama models:"
echo "   • ollama pull llama3.1:8b"
echo "   • ollama pull nomic-embed-text"
echo ""
echo "4. Start Jupyter notebook:"
echo "   cd notebooks/Main && jupyter notebook Simple_Document_Processing.ipynb"
echo ""
echo "✨ Happy researching!"