# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Environment Setup (REQUIRED)
```bash
# ⚠️ ALWAYS activate the virtual environment first
source langchain-env/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "from src import LangChainGraphRAG; print('✅ All dependencies installed')"
```

### Ollama Setup (Required)
```bash
# Install required models for local LLM processing
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

### Testing and Development
```bash
# Test GraphRAG system
python3 -c "from src import LangChainGraphRAG; graph = LangChainGraphRAG(); print('✅ GraphRAG system ready')"

# Test yFiles visualization
python3 -c "from src import create_yfiles_visualization, LangChainGraphRAG; print('✅ Visualization system ready')"

# Quick knowledge graph tutorial
jupyter notebook tutorial/04_Building_Knowledge_Graphs.ipynb

# Run main notebook interface  
jupyter notebook notebooks/Simple_Paper_RAG_Chat.ipynb

# Legacy tests (still functional)
python3 -c "from src import analyze_paper_for_corpus; print('✅ Legacy analyzer ready')"
python3 -c "from src import CitationTracker; tracker = CitationTracker(); print('✅ Citation tracker ready')"
```

## Code Architecture

### System Evolution: Single Paper → Literature Review System
This codebase has evolved from simple paper analysis to a comprehensive literature review system:
- **Phase 1 (Current)**: Enhanced paper analysis with GraphRAG compatibility
- **Phase 2 (Planned)**: Corpus management and cross-paper GraphRAG
- **Phase 3 (Planned)**: Automated literature review writing

### Core Component Architecture

#### Analysis Pipeline
1. **`SimplePaperRAG`**: RAG implementation with semantic search and Ollama embeddings
2. **`SimpleKnowledgeGraph`**: NetworkX-based entity extraction and relationship mapping
3. **`UnifiedPaperChat`**: Intelligent routing between RAG and graph queries
4. **`EnhancedPaperAnalyzer`**: GraphRAG-compatible document analysis with rich metadata
5. **`CitationTracker`**: Precise citation location mapping and verification

#### Data Flow Architecture
```
PDF → EnhancedPaperAnalyzer → GraphRAG Document → Corpus Database → Literature Review
  ↓         ↓                      ↓                ↓               ↓
Text    Metadata +          Vector Store +      Cross-Paper    Citation-Rich
Extract Citations           Embeddings          Discovery       Reviews
```

### Technical Stack Integration

#### LangChain + Ollama Integration
- **Local Privacy**: All processing via Ollama, no external API calls
- **Context Management**: Optimized for 32K token limit with intelligent chunking
- **Embedding Strategy**: nomic-embed-text for semantic similarity search
- **Model Configuration**: llama3.1:8b with temperature=0.1 for analytical consistency

#### Knowledge Graph Architecture  
- **NetworkX Backend**: Graph construction and analysis
- **Entity Types**: Authors, institutions, methods, concepts, technologies, metrics, datasets
- **Relationship Mapping**: Uses, improves, evaluates_on, compared_with, based_on, cites
- **Cross-Paper Linking**: Shared entities enable literature discovery

#### Citation Management System
- **Multi-Format Support**: Numbered [1], author-year (Smith, 2020), superscript
- **Location Tracking**: Character positions, line numbers, section mapping
- **Context Analysis**: Surrounding sentences, claim identification, evidence strength
- **Verification**: Citation accuracy scoring against evidence sources

### Database Strategy
Currently in-memory for single papers, designed for future corpus database:
- **Document Storage**: GraphRAG-compatible metadata with precise citations
- **Vector Integration**: ChromaDB for semantic search capabilities  
- **Cross-Reference Tracking**: Entity linking across paper collections

## Development Patterns

### Enhanced Analysis Pattern
All paper analysis follows this enhanced pattern for literature review compatibility:
```python
# Single paper analysis
chat_system = analyze_paper_with_chat(pdf_path)

# Corpus-ready analysis with citations
corpus_doc = export_paper_for_corpus(pdf_path)

# Citation tracking with locations
citations = track_citations_in_paper(content, metadata)
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
System designed for future automated review writing:
- **Evidence mapping** from claims to source papers
- **Citation verification** against available documents
- **Narrative flow planning** based on cross-paper themes
- **Section-by-section synthesis** with maintained provenance

## Testing Strategy

### Manual Verification Approach
No automated test suite - testing via:
- **Notebook execution** with sample papers in examples/
- **Citation accuracy checks** against known paper formats
- **Entity extraction validation** through manual review
- **Cross-paper compatibility** testing with multiple documents

### Performance Benchmarks
- **Processing Time**: ~30-60 seconds per paper analysis
- **Token Efficiency**: Optimized chunking for 32K context window
- **Memory Usage**: In-memory processing suitable for single papers
- **Accuracy Metrics**: Citation extraction >90% accuracy on academic papers