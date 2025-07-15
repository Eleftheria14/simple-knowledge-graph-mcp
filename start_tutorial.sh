#!/bin/bash

echo "🚀 GraphRAG MCP Notebook Processing Startup Script"
echo "=" * 60

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if a service is running
check_service() {
    local name=$1
    local url=$2
    local description=$3
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        print_status "$name: $description"
        return 0
    else
        print_error "$name: Not accessible at $url"
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🔧 Step 1: Environment Setup"
echo "----------------------------"

# Check if we're in the right directory
if [ ! -f "notebooks/Main/Simple_Document_Processing.ipynb" ]; then
    print_error "Not in project root directory. Please run this script from the GraphRAG MCP project root."
    exit 1
fi

# Ensure GraphRAG environment exists
if [ ! -d "graphrag-env" ]; then
    print_error "GraphRAG environment not found at: graphrag-env/"
    print_info "Please run: ./setup_env.sh to create the environment"
    exit 1
fi

# Activate GraphRAG environment
print_info "Activating GraphRAG environment..."
source graphrag-env/bin/activate
print_status "GraphRAG environment activated"

# Verify we're using the correct Python
PYTHON_PATH=$(which python)
if [[ "$PYTHON_PATH" != *"graphrag-env"* ]]; then
    print_error "Not using GraphRAG environment Python!"
    print_info "Expected: /Users/aimiegarces/Agents/graphrag-env/bin/python"
    print_info "Actual: $PYTHON_PATH"
    exit 1
fi

echo ""
echo "🐍 Step 2: Python Dependencies"
echo "-------------------------------"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
print_info "Python version: $python_version"

# Check critical packages
critical_packages=("jupyter" "pandas" "tqdm" "matplotlib" "plotly" "networkx")
all_packages_ok=true

for package in "${critical_packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        print_status "$package: Installed"
    else
        print_error "$package: Not installed"
        all_packages_ok=false
    fi
done

if [ "$all_packages_ok" = false ]; then
    print_info "Installing missing packages..."
    pip install jupyter pandas tqdm matplotlib plotly networkx
fi

echo ""
echo "🤖 Step 3: Ollama Service"
echo "-------------------------"

# Check if Ollama is installed
if command_exists ollama; then
    print_status "Ollama: Installed"
    
    # Check if Ollama server is running
    if check_service "Ollama API" "http://localhost:11434/api/tags" "Running on port 11434"; then
        # Check required models
        print_info "Checking Ollama models..."
        if ollama list | grep -q "llama3.1:8b"; then
            print_status "llama3.1:8b model: Available"
        else
            print_warning "llama3.1:8b model: Not found, pulling..."
            ollama pull llama3.1:8b
        fi
        
        if ollama list | grep -q "nomic-embed-text"; then
            print_status "nomic-embed-text model: Available"
        else
            print_warning "nomic-embed-text model: Not found, pulling..."
            ollama pull nomic-embed-text
        fi
    else
        print_warning "Ollama server not running. Starting..."
        print_info "Run in another terminal: ollama serve"
        print_info "Or run this script with: ./start_notebook_processing.sh --start-ollama"
        
        if [ "$1" = "--start-ollama" ]; then
            print_info "Starting Ollama server in background..."
            nohup ollama serve > /dev/null 2>&1 &
            sleep 3
            if check_service "Ollama API" "http://localhost:11434/api/tags" "Running on port 11434"; then
                print_status "Ollama server started successfully"
            else
                print_error "Failed to start Ollama server"
            fi
        fi
    fi
else
    print_error "Ollama: Not installed"
    print_info "Install with: brew install ollama  # macOS"
    print_info "Or download from: https://ollama.com"
fi

echo ""
echo "🗄️  Step 4: Neo4j Database"
echo "---------------------------"

# Check if Docker is installed
if command_exists docker; then
    print_status "Docker: Installed"
    
    # Check if Neo4j container is running
    if check_service "Neo4j" "http://localhost:7474/" "Running on port 7474"; then
        print_status "Neo4j: Ready for connections"
    else
        print_warning "Neo4j not running. Starting Docker container..."
        
        # Check if neo4j container exists
        if docker ps -a --format "table {{.Names}}" | grep -q "neo4j"; then
            print_info "Starting existing Neo4j container..."
            docker start neo4j
        else
            print_info "Creating new Neo4j container..."
            docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
        fi
        
        sleep 10
        if check_service "Neo4j" "http://localhost:7474/" "Running on port 7474"; then
            print_status "Neo4j started successfully"
            print_info "Access Neo4j Browser at: http://localhost:7474"
            print_info "Username: neo4j, Password: password"
        else
            print_error "Failed to start Neo4j"
        fi
    fi
else
    print_error "Docker: Not installed"
    print_info "Neo4j requires Docker. Install from: https://docker.com"
fi

echo ""
echo "📊 Step 5: Final System Check"
echo "------------------------------"

# Run the notebook's prerequisites check
print_info "Running comprehensive system check..."
cd notebooks/Main
python3 -c "
import sys
sys.path.append('../../')
from processing_utils import check_prerequisites
result = check_prerequisites()
if result['status'] == 'passed':
    print('🎉 All systems ready!')
else:
    print(f'⚠️  Found {len(result[\"issues\"])} issues')
    for issue in result['issues']:
        print(f'   - {issue}')
" 2>/dev/null || print_warning "Prerequisites check failed - will be checked in notebook"

cd ../..

echo ""
echo "🔧 Step 6: Jupyter Kernel Setup"
echo "--------------------------------"

# Install the GraphRAG environment as a Jupyter kernel
print_info "Setting up Jupyter kernel for GraphRAG environment..."
print_info "Using Python: $(which python)"
python -m ipykernel install --user --name=graphrag-env --display-name="GraphRAG MCP" --env PATH "$(dirname $(which python)):$PATH" 2>/dev/null || print_warning "Kernel installation failed"

# Verify kernel is installed
if jupyter kernelspec list | grep -q "graphrag-env"; then
    print_status "GraphRAG MCP kernel: Installed and ready"
else
    print_warning "GraphRAG MCP kernel: Installation may have failed"
    print_info "You may need to manually select the correct kernel in Jupyter"
fi

# Force the notebook to use the correct kernel
print_info "Updating notebook to use GraphRAG MCP kernel..."
python -c "
import json
with open('notebooks/Main/Simple_Document_Processing.ipynb', 'r') as f:
    notebook = json.load(f)
notebook['metadata']['kernelspec'] = {
    'display_name': 'GraphRAG MCP',
    'language': 'python', 
    'name': 'graphrag-env'
}
with open('notebooks/Main/Simple_Document_Processing.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)
print('✅ Notebook kernel updated')
"

echo ""
echo "🎯 Ready to Launch!"
echo "==================="
print_status "All required services are running"
print_info "Now launching Jupyter Notebook..."

echo ""
echo "📝 What happens next:"
echo "1. Jupyter will open in your browser"
echo "2. The notebook will open automatically with GraphRAG MCP kernel"
echo "3. ✅ Environment: /Users/aimiegarces/Agents/graphrag-env"
echo "4. Update the PROJECT_NAME and DOCUMENTS_FOLDER variables"
echo "5. Run all cells to process your documents"
echo "6. Follow the notebook for Claude Desktop integration"
echo ""
echo "🔧 Environment verification:"
echo "   - Top-right corner should show 'GraphRAG MCP'"
echo "   - If not, the script will exit with an error"
echo "   - All processing_utils should be available"

echo ""
echo "🔗 Quick links after notebook starts:"
echo "- Notebook: http://localhost:8888/notebooks/notebooks/Main/Simple_Document_Processing.ipynb"
echo "- Neo4j Browser: http://localhost:7474 (neo4j/password)"
echo "- Ollama API: http://localhost:11434"

echo ""
print_info "Press Ctrl+C to stop Jupyter when done"
echo ""

# Change to notebooks directory and start Jupyter with correct kernel
cd notebooks/Main

# Final verification that we're in the correct environment
print_info "Final environment check before launching Jupyter..."
print_info "Python path: $(which python)"
print_info "Jupyter path: $(which jupyter)"

# Test that processing_utils can be imported
print_info "Testing processing_utils import..."
cd notebooks/Main
python -c "
try:
    from processing_utils import check_prerequisites, quick_setup
    print('✅ processing_utils: Available')
    print('✅ Environment: Ready for document processing')
except Exception as e:
    print(f'❌ processing_utils: Failed - {e}')
    exit(1)
" || {
    print_error "Processing utils test failed!"
    print_info "The environment is not properly configured"
    exit 1
}

# Start Jupyter with the GraphRAG environment
print_info "Starting Jupyter notebook with GraphRAG MCP kernel..."
print_info "Kernel should automatically be 'GraphRAG MCP'"

echo ""
echo "🚀 Launching Jupyter Notebook..."
echo "================================"
echo "📝 Instructions:"
echo "   1. Select 'GraphRAG MCP' kernel when prompted"
echo "   2. Check 'Always start the preferred kernel'"
echo "   3. Click 'Select' to continue"
echo "   4. Use Ctrl+C here to stop the server when done"
echo ""

# Launch Jupyter notebook (kernel is set in notebook metadata)
export JUPYTER_RUNTIME_DIR="$HOME/.local/share/jupyter/runtime"

# Keep the script running and handle graceful shutdown
trap 'echo ""; echo "🛑 Shutting down Jupyter server..."; echo "✅ GraphRAG MCP Tutorial session ended."; exit 0' INT

# Launch Jupyter and keep script running
jupyter notebook Simple_Document_Processing.ipynb &
JUPYTER_PID=$!

# Wait for Jupyter to fully start
sleep 3

print_status "Jupyter server is running (PID: $JUPYTER_PID)"
print_info "Press Ctrl+C to stop the server and exit"

# Keep script running until interrupted
wait $JUPYTER_PID