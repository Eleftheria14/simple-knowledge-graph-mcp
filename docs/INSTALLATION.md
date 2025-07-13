# Installation Guide

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Eleftheria14/scientific-paper-analyzer.git
cd scientific-paper-analyzer
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment (required)
python3 -m venv langchain-env
source langchain-env/bin/activate  # Windows: langchain-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Ollama
```bash
# Install Ollama (visit https://ollama.ai for installation)
# Then download required models
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# Start Ollama server
ollama serve
```

### 4. Quick Test
```bash
# Test the system
python3 -c "from src import analyze_paper_for_corpus; print('✅ System ready!')"
```

## Detailed Installation

### Prerequisites
- Python 3.9+ (3.11 recommended)
- Ollama (for local LLM processing)
- 8GB+ RAM recommended
- 10GB+ free disk space

### Virtual Environment Setup (Required)
```bash
# Create the required virtual environment
python3 -m venv langchain-env
source langchain-env/bin/activate

# Verify you're in the virtual environment
which python  # Should show path with langchain-env
```

### Dependency Installation
```bash
# Install all required packages
pip install -r requirements.txt

# Key dependencies installed:
# - langchain + langchain-ollama (LLM integration)
# - chromadb (vector storage)
# - networkx (knowledge graphs)
# - yfiles-jupyter-graphs (professional visualization)
# - jupyter + notebook (interface)
```

### Ollama Setup (Required)

**Install Ollama:**
- macOS: Download from https://ollama.ai
- Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
- Windows: Download installer from https://ollama.ai

**Download Models:**
```bash
# Main LLM for analysis (4.7GB)
ollama pull llama3.1:8b

# Embedding model for semantic search (274MB)
ollama pull nomic-embed-text

# Verify models are installed
ollama list
```

**Start Ollama Server:**
```bash
# Start the server (keep running)
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

## Interface Options

### Option 1: Tutorial Interface (Recommended for Learning)
```bash
# Quick start script
./start_tutorial.sh

# Or manually
source langchain-env/bin/activate
jupyter notebook tutorial/04_Building_Knowledge_Graphs.ipynb
```

### Option 2: Main Interface (For Research Use)
```bash
source langchain-env/bin/activate
jupyter notebook notebooks/Simple_Paper_RAG_Chat.ipynb
```

### Option 3: Advanced Interface (Optimized System)
```bash
source langchain-env/bin/activate
jupyter notebook notebooks/Enhanced_Literature_Review_System.ipynb
```

## System Architecture

### Local Privacy-First Design
- **LLM Processing**: Local Ollama (no cloud APIs)
- **Vector Storage**: Local ChromaDB (no external databases)
- **Knowledge Graphs**: Local NetworkX processing
- **Data**: Everything stays on your machine

### Current Technology Stack
- **Backend**: Python + LangChain + ChromaDB
- **LLM**: Ollama (llama3.1:8b for analysis, nomic-embed-text for embeddings)
- **Storage**: ChromaDB vector database (local files)
- **Graphs**: NetworkX + yFiles Jupyter Graphs
- **Interface**: Jupyter notebooks

### Data Storage Locations
```
scientific-paper-analyzer/
├── chroma_graph_db/          # Vector embeddings (auto-created)
├── examples/                 # Sample papers for testing
├── tutorial/chroma_db/       # Tutorial database (auto-created)
└── notebooks/               # Analysis interfaces
```

## Verification

### Test Core System
```bash
# Activate environment
source langchain-env/bin/activate

# Test paper analysis
python3 -c "
from src import analyze_paper_for_corpus
result = analyze_paper_for_corpus('examples/d4sc03921a.pdf')
print(f'✅ Analysis successful: {result[\"metadata\"][\"title\"]}')
"
```

### Test Visualization
```bash
# Test knowledge graph visualization
python3 -c "
from src import show_knowledge_graph
print('✅ Visualization system ready')
"
```

### Test Jupyter Integration
```bash
# Launch tutorial interface
jupyter notebook tutorial/04_Building_Knowledge_Graphs.ipynb
```

## Common Issues & Solutions

### Import Errors
```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to your shell profile (~/.bashrc, ~/.zshrc)
echo 'export PYTHONPATH="${PYTHONPATH}:'"$(pwd)"'"' >> ~/.bashrc
```

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Check available models
ollama list
```

### ChromaDB Permission Issues
```bash
# Clear and recreate database
./clear_chromadb.sh

# Or manually remove
rm -rf chroma_graph_db/ tutorial/chroma_db/
```

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf langchain-env/
python3 -m venv langchain-env
source langchain-env/bin/activate
pip install -r requirements.txt
```

### Jupyter Kernel Issues
```bash
# Install kernel in virtual environment
source langchain-env/bin/activate
python -m ipykernel install --user --name=langchain-env --display-name="Python (langchain-env)"

# Select the correct kernel in Jupyter:
# Kernel → Change Kernel → Python (langchain-env)
```

## System Requirements

### Minimum Requirements
- **CPU**: 2+ cores
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **OS**: macOS, Linux, Windows with WSL

### Recommended Specifications
- **CPU**: 4+ cores (M1/M2 Mac or modern Intel/AMD)
- **RAM**: 16GB+ (for better LLM performance)
- **Storage**: SSD with 20GB+ free space
- **Network**: Internet for initial model downloads

### Model Storage Requirements
- **llama3.1:8b**: ~4.7GB
- **nomic-embed-text**: ~274MB
- **ChromaDB data**: Varies by papers analyzed (~10-50MB per paper)

## Getting Started

Once installation is complete:

1. **Start with tutorials**: `./start_tutorial.sh`
2. **Analyze sample papers**: Use papers in `examples/` folder
3. **Explore visualizations**: Try different knowledge graph views
4. **Add your papers**: Upload PDFs for analysis
5. **Build knowledge base**: Add multiple papers to see connections

## Advanced Setup

### Custom Model Configuration
```python
# In your notebooks, you can configure different models
from src.simple_paper_rag import SimplePaperRAG

# Use different embedding model (if available)
rag = SimplePaperRAG(
    embedding_model="your-custom-embed-model",
    llm_model="your-custom-llm-model"
)
```

### Performance Optimization
```bash
# For faster processing on Apple Silicon
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2

# For systems with limited RAM
export OLLAMA_HOST=127.0.0.1:11434
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure virtual environment is activated
4. Check Ollama is running and models are downloaded
5. Review the tutorial notebooks for examples

---

**You're now ready to analyze scientific papers with AI! 🚀**