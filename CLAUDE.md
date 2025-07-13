# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Environment Setup (REQUIRED)
```bash
# ⚠️ ALWAYS activate the virtual environment first
source langchain-env/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Verify core installation
python3 -c "from src import LangChainGraphRAG; print('✅ All dependencies installed')"

# Test visualization systems
python3 -c "from src import show_knowledge_graph; print('✅ Visualization ready')"
```

### Ollama Setup (Required)
```bash
# Install required models for local LLM processing
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

### Quick Start Tutorial System
```bash
# Complete tutorial environment setup and launch
./start_tutorial.sh

# Manual tutorial launch (alternative)
jupyter notebook tutorial/04_Building_Knowledge_Graphs.ipynb

# Clear databases for fresh start
./clear_chromadb.sh
```

### Testing and Development
```bash
# Test enhanced knowledge graph system
python3 -c "from src import LangChainGraphRAG; graph = LangChainGraphRAG(); print('✅ Enhanced GraphRAG ready')"

# Test professional visualization
python3 -c "from src.yfiles_visualization import create_yfiles_visualization; print('✅ yFiles professional viz ready')"

# Test tutorial helper functions
python3 -c "from src.tutorial_helpers import interactive_paper_chat; print('✅ Tutorial helpers ready')"

# Run enhanced analysis pipeline
python3 -c "from src import analyze_paper_with_chat; print('✅ Enhanced analysis pipeline ready')"

# Test citation tracking system
python3 -c "from src import CitationTracker; tracker = CitationTracker(); print('✅ Citation tracker ready')"
```

### Performance Testing
```bash
# Debug entity extraction if issues arise
python3 debug_entity_extraction.py

# Test basic vs enhanced extraction
python3 -c "from src import SimpleKnowledgeGraph, EnhancedKnowledgeGraph; print('✅ Both extraction systems ready')"

# Benchmark extraction performance
python3 -c "import time; from src import LangChainGraphRAG; start = time.time(); graph = LangChainGraphRAG(); print(f'✅ Init time: {time.time()-start:.1f}s')"
```

### Production Research Commands
```bash
# Build research corpus from paper collection (RTX 4090 optimized)
python3 build_research_corpus.py /path/to/papers/ --enhanced-extraction

# Start MCP server for knowledge graph access (when implemented)
python3 start_mcp_server.py /path/to/corpus/

# Test MCP integration (when implemented)
python3 test_mcp_integration.py --corpus /path/to/corpus/ --query "transformer drug discovery"
```

## Code Architecture

### System Evolution: Educational Prototype → Production Research Tool
This codebase has evolved from educational tutorials to a production literature review system:
- **Phase 1 (Complete)**: Enhanced paper analysis with GraphRAG + professional visualization + tutorial system
- **Phase 2 (Current Development)**: MCP-based architecture for literature review automation
- **Phase 3 (Planned)**: RTX 4090 corpus building + Claude Max integration for citation-accurate review writing

**Current Focus**: Building MCP server to expose knowledge graphs for LLM-powered literature synthesis (see PRD.md)

### Core Component Architecture (Layered Design)

#### Foundation Layer - Basic RAG and Knowledge Graphs
1. **`SimplePaperRAG`**: RAG implementation with Ollama embeddings and ChromaDB
2. **`SimpleKnowledgeGraph`**: NetworkX-based entity extraction (8 categories, basic relationships)

#### Enhancement Layer - Advanced Analysis
3. **`EnhancedKnowledgeGraph`**: Multi-section extraction (20+ categories, comprehensive relationships)
4. **`LangChainGraphRAG`**: LangChain-compatible GraphRAG with vector + metadata traversal
5. **`EnhancedPaperAnalyzer`**: GraphRAG-ready document analysis with rich metadata
6. **`CitationTracker`**: Multi-format citation location mapping and verification

#### Integration Layer - Unified Systems
7. **`UnifiedPaperChat`**: Intelligent routing between RAG and graph queries with smart mode detection
8. **`tutorial_helpers.py`**: Educational interfaces hiding complexity for clean learning

#### Visualization Layer - Professional Display
9. **`yfiles_visualization.py`**: Enterprise-grade interactive graphs with sidebars and search
10. **`notebook_visualization.py`**: Educational display with automatic fallbacks
11. **`standard_kg_visualization.py`**: Industry-standard export formats (GraphML, Cytoscape, D3)

#### Data Flow Architecture
```
PDF → Enhanced Analysis → LangChain GraphRAG → Professional Visualization → Tutorial System
  ↓         ↓                    ↓                     ↓                    ↓
Text    Rich Metadata +    Vector Store +       yFiles Interactive    Educational
Extract  Citations       Graph Traversal         + Export Options      Interface
```

### Tutorial System Architecture (Complete Learning Path)

#### 5-Tutorial Progressive Learning System
- **Tutorial 1**: Introduction to LLMs and Ollama (15-20 min, Complete Beginner)
- **Tutorial 2**: LangChain Fundamentals (25-30 min, Document processing)
- **Tutorial 3**: Understanding RAG (30-35 min, Vector embeddings)
- **Tutorial 4**: Building Knowledge Graphs (25-30 min, Entity extraction with real papers)
- **Tutorial 5**: Complete Paper Analysis System (35-40 min, Integration capstone)

#### Educational Design Patterns
- **Progressive Complexity**: Each tutorial builds on previous concepts
- **Real-World Examples**: Uses actual research papers (examples/d4sc03921a.pdf, d3dd00113j.pdf)
- **Clean Interfaces**: `tutorial_helpers.py` hides implementation complexity
- **Interactive Learning**: REPL-style chat, visualization, hands-on experiments

### Technical Stack Integration

#### LangChain + Ollama Integration
- **Local Privacy**: All processing via Ollama, no external API calls
- **Context Management**: Optimized for 32K token limit with intelligent chunking
- **Embedding Strategy**: nomic-embed-text for semantic similarity search
- **Model Configuration**: llama3.1:8b with temperature=0.1 for analytical consistency
- **Performance Considerations**: Enhanced extraction 20x more comprehensive but 20x slower

#### Enhanced Knowledge Graph Architecture
- **Dual Extraction Systems**: Basic (8 categories) vs Enhanced (20+ categories)
- **Multi-Section Processing**: 6000-char chunks with 1000-char overlap for comprehensive coverage
- **Advanced Entity Types**: Includes experiments, challenges, innovations, comparisons, evaluations
- **Relationship Mapping**: 15+ relationship types (uses, improves, evaluates_on, compared_with, based_on, cites)
- **Cross-Paper Linking**: Shared entities enable literature discovery and correlation

#### Professional Visualization Architecture
- **yFiles Integration**: Enterprise-grade interactive graphs with professional layouts
- **Export Ecosystem**: GraphML (Gephi), Cytoscape.js, D3.js, NetworkX formats
- **Educational Fallbacks**: Automatic detection and graceful degradation
- **Interactive Features**: Sidebar exploration, entity search, neighborhood highlighting

#### Citation Management System
- **Multi-Format Support**: Numbered [1], author-year (Smith, 2020), superscript references
- **Precise Location Tracking**: Character positions, line numbers, section mapping
- **Context Analysis**: Surrounding sentences, claim identification, evidence strength assessment
- **Verification Pipeline**: Citation accuracy scoring against evidence sources
- **Academic Standards**: Support for complex multi-line citations with mathematical notation

### Database Strategy Evolution
**Current**: ChromaDB vector store with JSON metadata for graph traversal
**Production Target**: Multi-paper corpus with MCP-exposed knowledge:
- **Batch Corpus Building**: RTX 4090 processes 20-50 papers into comprehensive knowledge graphs
- **MCP Server Integration**: Local API server exposes research knowledge via standardized protocol
- **LLM Access**: Claude Max queries knowledge graphs for citation-accurate literature review writing
- **Cross-Reference Tracking**: Entity linking across paper collections enables literature synthesis

### MCP Architecture (In Development)
**Goal**: Bridge local knowledge graphs with cloud LLM writing capabilities
- **Knowledge Graph Builder**: Offline enhanced extraction on RTX 4090 (10-15 min per paper)
- **MCP Server**: Local API exposing query_literature(), find_evidence(), generate_citations() 
- **Claude Max Integration**: Citation-accurate literature review generation via MCP protocol

## Development Patterns

### Enhanced Analysis Pattern (Production Ready)
All paper analysis follows this comprehensive pattern for literature review compatibility:
```python
# Complete enhanced analysis pipeline
chat_system = analyze_paper_with_chat(pdf_path)

# Access comprehensive knowledge graph
enhanced_entities = chat_system.kg.enhanced_entities  # 20+ categories

# Professional visualization with multiple options
visualization = chat_system.create_yfiles_visualization()

# Corpus-ready export with rich metadata
corpus_doc = export_paper_for_corpus(pdf_path)

# Citation tracking with precise locations
citations = track_citations_in_paper(content, metadata)
```

### Tutorial Development Pattern
Educational interfaces follow clean abstraction pattern:
```python
# Clean tutorial interface (hides complexity)
from src.tutorial_helpers import interactive_paper_chat
result = interactive_paper_chat(pdf_path)

# Behind the scenes: full system integration
# - Enhanced knowledge graph extraction
# - Professional visualization
# - Intelligent query routing
# - Error handling and progress display
```

### GraphRAG Preparation Pattern
Documents are structured for future GraphRAG integration:
- **Rich Metadata**: Authors, methods, concepts as edge connectors
- **Section Mapping**: Precise content location for citation accuracy
- **Cross-Paper Compatibility**: Standardized entity extraction for linking

### Error Handling Strategy
- **Graceful LLM Failures**: Fallback entity structures when extraction fails
- **PDF Processing Resilience**: Multiple extraction strategies for different formats
- **Citation Parsing Robustness**: Multiple regex patterns for various citation styles

## External Dependencies

### Required Services
- **Ollama Server**: Must be running locally with specified models
- **Jupyter Environment**: For interactive notebook interface
- **NetworkX**: For knowledge graph construction and analysis

### Model Requirements
- **llama3.1:8b**: Primary analysis model (32,768 token context)
- **nomic-embed-text**: Embedding model for semantic search
- **Temperature 0.1**: Consistent analytical outputs
- **Context Preservation**: Intelligent chunking within token limits

## Key Implementation Details

### Citation Processing Innovation
Advanced regex patterns handle complex academic citations:
- **Multi-line titles** with special characters and mathematical notation
- **Complex author lists** with superscripts and affiliations  
- **Reference list parsing** with DOI and URL extraction
- **Context-aware positioning** for literature review writing

### Knowledge Graph Enhancement
Beyond simple entity extraction:
- **Hierarchical clustering** of related concepts
- **Relationship strength scoring** based on co-occurrence
- **Cross-paper entity resolution** for literature connections
- **Graph analytics** including centrality and community detection

### Literature Review Preparation
System designed for MCP-based automated review writing:
- **Evidence mapping** from claims to source papers via MCP queries
- **Citation verification** against corpus through MCP server
- **Claude Max integration** for professional literature synthesis
- **Section-by-section synthesis** with maintained citation provenance

### MCP Development Roadmap
**Current Status**: Foundation components complete, MCP server in development
**Next Steps** (see PRD.md for full timeline):
1. **Batch Corpus Builder**: Process paper collections with enhanced extraction
2. **MCP Server Implementation**: Expose knowledge graphs via standardized protocol
3. **Claude Max Integration**: Literature review generation with citation accuracy

## Testing Strategy

### Manual Verification Approach
No automated test suite - testing via:
- **Notebook execution** with sample papers in examples/
- **Citation accuracy checks** against known paper formats
- **Entity extraction validation** through manual review
- **Cross-paper compatibility** testing with multiple documents

### Performance Benchmarks and Hardware Considerations

#### Processing Time (Per Paper Analysis)
- **Basic Extraction**: ~30-60 seconds (8 entity categories, single LLM call)
- **Enhanced Extraction**: ~10-60 minutes depending on hardware and paper complexity
  - **M4 MacBook Pro (efficiency cores)**: ~55-66 minutes for comprehensive extraction
  - **M4 MacBook Pro (performance cores)**: ~15-25 minutes (with proper scheduling)
  - **RTX 4090 + CUDA**: ~10-18 minutes (estimated with Ollama CUDA acceleration)
  - **Google Colab T4**: ~20-30 minutes (free tier)

#### Hardware Optimization Notes
- **M4 Core Scheduling**: Ollama may default to efficiency cores (much slower)
- **CUDA Acceleration**: RTX 4090 provides 4-7x speedup over M4 efficiency cores
- **Memory Requirements**: 24GB recommended for llama3.1:8b, enhanced extraction
- **Token Efficiency**: Optimized chunking for 32K context window with intelligent overlap

#### Accuracy and Quality Metrics
- **Citation Extraction**: >90% accuracy on academic papers
- **Entity Extraction**: Enhanced system finds 5-20x more entities than basic
- **Cross-Paper Linking**: Shared entity detection enables literature discovery
- **Visualization Quality**: Professional yFiles graphs vs educational displays

## Important Utilities and Scripts

### Database Management
```bash
# Clear all ChromaDB databases for fresh start
./clear_chromadb.sh

# Check what's in current databases
python3 -c "from src import LangChainGraphRAG; graph = LangChainGraphRAG(); print(graph.get_graph_summary())"
```

### Tutorial System
```bash
# Complete setup and launch tutorial environment
./start_tutorial.sh

# Manual tutorial launch
source langchain-env/bin/activate && jupyter notebook tutorial/
```

### Debugging and Diagnostics
```bash
# Debug entity extraction issues
python3 debug_entity_extraction.py

# Test LLM connection and JSON generation
python3 -c "from src.enhanced_knowledge_graph import EnhancedKnowledgeGraph; kg = EnhancedKnowledgeGraph(); print('LLM ready')"
```

### Sample Data
- **examples/d4sc03921a.pdf**: Primary research paper for testing enhanced extraction
- **examples/d3dd00113j.pdf**: Secondary paper for cross-paper linking tests
- **tutorial/sample_text.txt**: Legacy simple text for basic testing

### Key Configuration Files
- **requirements.txt**: Dependencies including yFiles, LangChain, ChromaDB
- **PRD.md**: Complete product requirements for MCP-based literature review system
- **start_tutorial.sh**: Complete environment setup with Jupyter kernel configuration
- **clear_chromadb.sh**: Database cleanup utility for fresh starts

## Important Project Files

### Planning and Documentation
- **PRD.md**: Comprehensive product requirements document for production research tool
- **README.md**: Project overview and quick start guide
- **CLAUDE.md**: Development guidance (this file)

### Research Examples
- **examples/d4sc03921a.pdf**: Primary research paper for testing enhanced extraction
- **examples/d3dd00113j.pdf**: Secondary paper for cross-paper linking tests

### Production Development Focus
**Current Priority**: Implementing MCP server architecture per PRD.md specifications
**Target Architecture**: RTX 4090 knowledge building → MCP server → Claude Max literature writing
**Success Metric**: Generate citation-accurate literature review sections in minutes vs weeks