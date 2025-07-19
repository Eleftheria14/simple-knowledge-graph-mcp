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

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Neo4j will not be started automatically."
    print_info "To install Docker, visit: https://docs.docker.com/get-docker/"
    DOCKER_AVAILABLE=false
else
    print_status "Docker is available: $(docker --version)"
    DOCKER_AVAILABLE=true
fi

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

# Install Graphiti dependencies
print_info "Installing Graphiti dependencies..."
uv pip install neo4j || print_warning "Neo4j client installation failed"
uv pip install graphiti-core || print_warning "Graphiti core installation failed"

# Start Ollama if available
if command -v ollama &> /dev/null; then
    print_info "Starting Ollama service..."
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_status "Ollama is already running"
    else
        print_info "Starting Ollama in background..."
        ollama serve &
        sleep 3
        
        # Check if Ollama started successfully
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_status "Ollama started successfully at http://localhost:11434"
        else
            print_warning "Ollama may still be starting up. Check http://localhost:11434 in a few moments."
        fi
    fi
else
    print_warning "Ollama not found - skipping Ollama startup"
    print_info "Install Ollama from: https://ollama.ai"
fi

# Start Neo4j if Docker is available
if [ "$DOCKER_AVAILABLE" = true ]; then
    print_info "Starting Neo4j database..."
    if docker ps -q -f name=neo4j | grep -q .; then
        print_status "Neo4j container is already running"
    else
        # Check if container exists but is stopped
        if docker ps -a -q -f name=neo4j | grep -q .; then
            print_info "Starting existing Neo4j container..."
            docker start neo4j
        else
            print_info "Creating and starting new Neo4j container..."
            docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
        fi
        
        # Wait a moment for Neo4j to start
        print_info "Waiting for Neo4j to start..."
        sleep 5
        
        # Check if Neo4j is accessible
        if curl -f -s http://localhost:7474/ > /dev/null 2>&1; then
            print_status "Neo4j is running and accessible at http://localhost:7474"
        else
            print_warning "Neo4j may still be starting up. Check http://localhost:7474 in a few moments."
        fi
    fi
else
    print_warning "Docker not available - skipping Neo4j startup"
    print_info "You can manually start Neo4j with:"
    echo "docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest"
fi

# Verify key imports
print_info "Verifying key package imports..."
python -c "
import sys
print(f'Python path: {sys.executable}')

# Test core GraphRAG MCP imports
try:
    from graphrag_mcp.core.enhanced_document_processor import EnhancedDocumentProcessor
    from graphrag_mcp.core.llm_analysis_engine import LLMAnalysisEngine
    from graphrag_mcp.core.config import GraphRAGConfig
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
    from graphiti_core import Graphiti
    print('✅ Graphiti core imports: OK')
except ImportError as e:
    print(f'⚠️  Graphiti core imports failed: {e}')
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

# Final service status check
print_info "Final service status:"
if curl -f -s http://localhost:7474/ > /dev/null 2>&1; then
    print_status "Neo4j: Running at http://localhost:7474"
else
    print_warning "Neo4j: Not accessible (may need manual start)"
fi

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_status "Ollama: Running at http://localhost:11434"
else
    print_warning "Ollama: Not running (start with: ollama serve)"
fi

echo ""
echo "📋 Next steps:"
echo "1. Activate environment: source graphrag-env/bin/activate"
echo "   Or use: ./activate_graphrag_env.sh"
echo ""
echo "2. Start Jupyter notebook:"
echo "   cd notebooks/Main && jupyter notebook CLI_Document_Processing.ipynb"
echo ""
echo "3. If services aren't running, restart them:"
echo "   • Ollama: ollama serve"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "   • Neo4j: docker start neo4j"
else
    echo "   • Neo4j: docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest"
fi
echo ""
echo "4. Install Ollama models (if not already installed):"
echo "   • ollama pull llama3.1:8b"
echo "   • ollama pull nomic-embed-text"
echo ""
echo "✨ Happy researching!"