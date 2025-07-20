# Prerequisites and Requirements

## 🚀 Quick Install (Most Users)

**macOS:**
```bash
# Install via Homebrew (easiest)
brew install python@3.11 docker
# Download Claude Desktop from https://claude.ai/download
```

**Windows:**
```bash
# Install via winget
winget install Python.Python.3.11 Docker.DockerDesktop
# Download Claude Desktop from https://claude.ai/download
```

**Ubuntu/Linux:**
```bash
sudo apt update && sudo apt install python3.11 docker.io
# Download Claude Desktop from https://claude.ai/download
```

**Total Download:** ~2.5GB | **Setup Time:** ~15-20 minutes

---

## Detailed System Requirements

### Operating System
- **macOS**: 10.15+ (Catalina or newer)
- **Linux**: Ubuntu 20.04+, Debian 11+, or equivalent
- **Windows**: Windows 10/11 with WSL2 (recommended) or native Windows

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended (for local embeddings)
- **Storage**: 2GB free space (databases grow with content)
- **CPU**: Modern multi-core processor (embedding generation is CPU-intensive)

### Software Prerequisites

#### 1. Python 3.11+
**Required for FastMCP compatibility**
```bash
# Check your Python version
python3 --version
# Should show 3.11.0 or higher
```

**Installation:**
- **macOS**: `brew install python@3.11` or download from python.org
- **Linux**: `sudo apt install python3.11` or use pyenv
- **Windows**: Download from python.org or use Microsoft Store

#### 2. Docker
**Required for Neo4j graph database**
```bash
# Check if Docker is installed and running
docker --version
docker info
```

**Installation:**
- **macOS**: [Docker Desktop for Mac](https://docs.docker.com/docker-for-mac/install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/docker-for-windows/install/)

**Docker Configuration:**
- Allocate at least 2GB RAM to Docker
- Ensure Docker daemon is running before setup

#### 3. Claude Desktop
**Required to use the MCP tools**
- Download from [Claude Desktop](https://claude.ai/download)
- Create Anthropic account if needed
- Ensure you can create Projects (required for document uploads)

## Python Dependencies

### Core Framework
```
fastmcp>=0.2.0          # Model Context Protocol server framework
```

### Database Drivers
```
neo4j>=5.0.0            # Neo4j graph database driver
chromadb>=0.4.0         # ChromaDB vector database
```

### Machine Learning Stack
```
sentence-transformers>=2.0.0   # Local text embeddings (no API needed)
torch>=2.0.0                   # PyTorch for ML models
numpy>=1.21.0                  # Numerical computing
```

### Utilities
```
pydantic>=2.0.0         # Data validation and serialization
python-dotenv>=1.0.0    # Environment variable management
typing-extensions>=4.0.0 # Enhanced type hints
```

## Dependency Size and Installation Time

### Total Download Size
- **Initial download**: ~2.5GB
  - PyTorch: ~800MB
  - Sentence-transformers models: ~500MB
  - Neo4j Docker image: ~600MB
  - Other dependencies: ~600MB

### Installation Time
- **Fast internet**: 10-15 minutes
- **Slow internet**: 30-45 minutes
- **First run**: Additional 2-3 minutes (model download)

## Disk Space Requirements

### Base Installation
- **Python environment**: ~2.5GB
- **Docker images**: ~600MB
- **Application code**: ~50MB

### Runtime Storage (grows with usage)
- **Neo4j database**: Starts small, grows with entities/relationships
- **ChromaDB**: Starts small, grows with text chunks and embeddings
- **Embedding cache**: ~100MB per 1000 documents processed

### Total Space Planning
- **Minimum**: 3.5GB for base installation
- **Recommended**: 10GB+ for active usage with document collections
- **Heavy usage**: 50GB+ for large document repositories

## Network Requirements

### Initial Setup
- **Internet required** for:
  - UV package manager installation
  - Python package downloads
  - Docker image pulls
  - Sentence-transformer model downloads

### Runtime Operation
- **Mostly offline**: Once installed, works without internet
- **Claude Desktop**: Requires internet for Claude API access
- **Local processing**: Embeddings generated locally (no external ML APIs)

## Development Tools (Optional)

### Code Editing
- **VS Code**: Recommended for Python development
- **PyCharm**: Alternative Python IDE
- **Vim/Emacs**: For terminal-based editing

### Database Management (Optional)
- **Neo4j Desktop**: GUI for Neo4j database exploration
- **Neo4j Browser**: Web interface (included with Docker image)

## Known Compatibility Issues

### PyTorch Installation
- **Apple Silicon Macs**: May need specific PyTorch build
- **Older CPUs**: Some sentence-transformer models require AVX2
- **Windows**: May need Visual C++ redistributables

### Docker on Different Platforms
- **Linux**: User must be in `docker` group
- **Windows**: WSL2 required for best performance
- **macOS**: File sharing performance may be slower

### Memory Constraints
- **4GB RAM systems**: May struggle with large embedding batches
- **Solution**: Reduce `EMBEDDING_BATCH_SIZE` in `.env` file

## Security Considerations

### Local Data Processing
- ✅ **No external API calls** for document processing
- ✅ **Local embeddings** via sentence-transformers
- ✅ **Local databases** (Neo4j + ChromaDB)
- ✅ **Your documents stay on your machine**

### Network Exposure
- **Neo4j**: Bound to localhost only (port 7687)
- **MCP Server**: Local socket communication with Claude Desktop
- **No external services** required after initial setup

## Environment Variables

### Required Configuration (.env file)
```bash
# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# ChromaDB Storage
CHROMADB_PATH=./chroma_db
CHROMADB_COLLECTION=knowledge_graph

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32
```

### Performance Tuning
```bash
# For systems with more RAM
EMBEDDING_BATCH_SIZE=64

# For slower systems
EMBEDDING_BATCH_SIZE=16

# Alternative embedding models
EMBEDDING_MODEL=all-mpnet-base-v2    # Better quality, slower
EMBEDDING_MODEL=all-MiniLM-L12-v2    # Balanced option
```

## Troubleshooting Common Issues

### Python Version Conflicts
```bash
# Use pyenv to manage multiple Python versions
pyenv install 3.11.7
pyenv local 3.11.7
```

### Docker Permission Issues (Linux)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Insufficient Memory
```bash
# Reduce batch size in .env
EMBEDDING_BATCH_SIZE=8
```

### Slow Embedding Generation
```bash
# Use smaller model in .env
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Verification Checklist

Before installation, verify you have:
- [ ] Python 3.11+ installed and accessible
- [ ] Docker installed and running
- [ ] Claude Desktop installed and logged in
- [ ] At least 4GB free disk space
- [ ] Stable internet connection for initial setup
- [ ] Administrator/sudo access (if needed for Docker setup)

Run this verification script:
```bash
# Check all prerequisites
python3 --version  # Should be 3.11+
docker --version   # Should show Docker version
docker info        # Should connect without errors
```

Once prerequisites are met, proceed to the main installation with `./scripts/setup.sh`.