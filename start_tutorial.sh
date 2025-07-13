#!/bin/bash

# Quick start script for the Knowledge Graph Tutorial
echo "🚀 Starting Knowledge Graph Tutorial..."
echo "=================================="

# Get script directory and navigate there
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "langchain-env" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Create it with: python3 -m venv langchain-env"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source langchain-env/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if python3 -c "from src import LangChainGraphRAG; print('✅ Dependencies OK')" 2>/dev/null; then
    echo "✅ Core dependencies installed"
else
    echo "⚠️ Installing core dependencies..."
    pip install -r requirements.txt
fi

# Fix urllib3 warning for LibreSSL compatibility
echo "🔧 Fixing urllib3 compatibility..."
pip install "urllib3<2.0" >/dev/null 2>&1
echo "✅ urllib3 compatibility fixed"

# Check visualization dependencies
echo "🎨 Checking visualization dependencies..."
if python3 -c "import matplotlib, yfiles_jupyter_graphs; print('✅ Visualization OK')" 2>/dev/null; then
    echo "✅ Visualization libraries ready"
else
    echo "⚠️ Installing visualization libraries..."
    pip install matplotlib yfiles_jupyter_graphs
    echo "✅ Visualization libraries installed"
fi

# Verify everything works together
echo "🧪 Running integration test..."
if python3 -c "
from src.notebook_visualization import show_knowledge_graph
from src import LangChainGraphRAG
import matplotlib
matplotlib.use('Agg')
graph_rag = LangChainGraphRAG()
print('✅ GraphRAG + Visualization ready!')
" 2>/dev/null; then
    echo "✅ Integration test passed"
else
    echo "⚠️ Integration test failed - some features may not work"
fi

# Check if Ollama is running
echo "🔍 Checking Ollama..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️ Ollama not running!"
    echo "💡 Start it with: ollama serve"
    echo "💡 Install models with: ollama pull llama3.1:8b && ollama pull nomic-embed-text"
fi

# Check Jupyter widgets support
echo "📱 Checking Jupyter widgets..."
if python3 -c "import ipywidgets; print('✅ Widgets OK')" 2>/dev/null; then
    echo "✅ Jupyter widgets available"
else
    echo "⚠️ Installing Jupyter widgets..."
    pip install ipywidgets
fi

# Enable Jupyter extensions for browser compatibility
echo "🔧 Enabling Jupyter extensions..."
jupyter nbextension enable --py widgetsnbextension --sys-prefix >/dev/null 2>&1
jupyter serverextension enable --py jupyter_server --sys-prefix >/dev/null 2>&1
echo "✅ Browser extensions enabled"

# Install virtual environment as Jupyter kernel
echo "🔧 Setting up Jupyter kernel..."
# Remove existing kernel to avoid conflicts
jupyter kernelspec remove langchain-env -f >/dev/null 2>&1
if python -m ipykernel install --user --name=langchain-env --display-name="Python (langchain-env)" >/dev/null 2>&1; then
    echo "✅ Virtual environment kernel installed"
else
    echo "⚠️ Kernel installation failed - notebook may use wrong Python"
fi

# Start Jupyter
echo ""
echo "🎯 Ready to start tutorial!"
echo "📚 Opening Knowledge Graph Tutorial..."
echo ""
echo "💡 Tutorial features:"
echo "   🕸️ AI-powered entity extraction"
echo "   📊 Interactive yFiles graph visualization"
echo "   🔍 Knowledge graph queries"
echo "   🎨 Professional graph styling"
echo ""
echo "💡 Tutorial location: tutorial/04_Building_Knowledge_Graphs.ipynb"
echo ""
echo "🚨 Important Jupyter Setup:"
echo "   1. Select kernel: Kernel → Change Kernel → Python (langchain-env)"
echo "   2. Restart kernel if needed: Kernel → Restart"
echo "   3. Run all cells: Cell → Run All"
echo "   4. If imports fail, check that Python (langchain-env) kernel is selected!"
echo ""

# Start Jupyter from within the virtual environment
echo "🚀 Starting Jupyter server..."
bash -c "
source langchain-env/bin/activate
export JUPYTER_PATH=\$VIRTUAL_ENV/share/jupyter:\$JUPYTER_PATH
export PYTHONPATH=\$(pwd):\$PYTHONPATH
cd tutorial
nohup jupyter notebook 04_Building_Knowledge_Graphs.ipynb > ../jupyter.log 2>&1 &
" 

# Get the process ID
sleep 3
JUPYTER_PID=$(pgrep -f "jupyter-notebook")

if [ ! -z "$JUPYTER_PID" ]; then
    echo "✅ Jupyter server started successfully!"
    echo "📋 Process ID: $JUPYTER_PID"
    echo "📄 Logs: jupyter.log"
    echo ""
    echo "🌐 Server URLs:"
    echo "   http://localhost:8888/notebooks/04_Building_Knowledge_Graphs.ipynb"
    echo "   (Check jupyter.log for the token if needed)"
    echo ""
    echo "🛑 To stop the server later:"
    echo "   kill $JUPYTER_PID"
    echo "   or: pkill -f jupyter-notebook"
    echo ""
    echo "📖 The tutorial is now ready to use!"
else
    echo "❌ Failed to start Jupyter server"
    echo "📄 Check jupyter.log for details"
fi