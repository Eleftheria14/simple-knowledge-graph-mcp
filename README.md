# Scientific Paper Literature Review System

An intelligent system for analyzing scientific papers and building comprehensive literature reviews. Features enhanced paper analysis, knowledge graph extraction, citation tracking, and GraphRAG integration for cross-paper discovery and citation-accurate writing.

Built with LangChain, LangGraph, and Ollama for local, private analysis.

## 🎯 Key Features

### 📄 Enhanced Paper Analysis
- **Deep Content Extraction**: Comprehensive metadata including authors, year, domain, research type
- **Section Structure Analysis**: Precise mapping of document sections with line numbers
- **Citation Tracking**: Location-aware citation extraction and verification
- **Entity & Relationship Mapping**: Knowledge graph construction with NetworkX

### 🕸️ Literature Review Capabilities  
- **GraphRAG Integration**: Cross-paper discovery using LangChain GraphRAG
- **Corpus Management**: Store and index analyzed papers for literature reviews
- **Citation-Accurate Writing**: Maintain precise source traceability for every claim
- **Theme Discovery**: Identify research trends and gaps across paper collections

### 🤖 Interactive Analysis
- **RAG Chat Interface**: Ask natural language questions about papers
- **Smart Retrieval**: Semantic similarity search with context preservation
- **Knowledge Graph Exploration**: Discover relationships between concepts and methods
- **Local Privacy**: Complete analysis using Ollama - no external API calls

## 🚀 Quick Start

### Prerequisites

1. **Ollama** with required models:
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ollama serve
   ```

2. **Python Environment**:
   ```bash
   source langchain-env/bin/activate
   pip install -r requirements.txt
   ```

### Basic Paper Analysis

```python
from src import analyze_paper_with_chat

# Analyze a single paper
chat_system = analyze_paper_with_chat("path/to/paper.pdf")

# Ask questions
response = chat_system.chat("What are the main findings?")
print(response['answer'])

# Explore entities
entities = chat_system.get_entities()
print(f"Authors: {entities['authors']}")
print(f"Methods: {entities['methods']}")
```

### Literature Review Preparation

```python
from src import export_paper_for_corpus, track_citations_in_paper

# Export paper for corpus inclusion
corpus_doc = export_paper_for_corpus("path/to/paper.pdf")

# Track citations with precise locations
citations = track_citations_in_paper(
    corpus_doc['content'], 
    corpus_doc['metadata']
)

print(f"Found {len(citations['inline_citations'])} citations")
print(f"Document ready for GraphRAG: {corpus_doc['document_id']}")
```

## 📊 System Architecture

```
Papers → Enhanced Analysis → Corpus Database → GraphRAG → Literature Reviews
   ↓          ↓                   ↓             ↓           ↓
Single     Rich Metadata      Vector Store   Cross-Paper  Citation-Rich
Paper      + Citations        + Graph        Discovery    Reviews
```

### Core Components

1. **`EnhancedPaperAnalyzer`**: GraphRAG-compatible document analysis
2. **`CitationTracker`**: Precise citation location mapping  
3. **`UnifiedPaperChat`**: Interactive paper exploration
4. **`SimplePaperRAG`**: Semantic search and retrieval
5. **`SimpleKnowledgeGraph`**: Entity and relationship extraction

## 📁 Project Structure

```
├── src/                          # Core system components
│   ├── enhanced_paper_analyzer.py   # GraphRAG-compatible analysis
│   ├── citation_tracker.py          # Citation location mapping
│   ├── unified_paper_chat.py        # Chat interface + corpus export
│   ├── simple_paper_rag.py          # RAG implementation
│   └── simple_knowledge_graph.py    # Knowledge graph extraction
├── notebooks/                    # Jupyter interfaces
│   └── Simple_Paper_RAG_Chat.ipynb  # Main analysis notebook
├── examples/                     # Sample papers
├── docs/                        # Documentation
└── requirements.txt             # Dependencies
```

## 🔬 Analysis Capabilities

### Paper Metadata Extraction
- **Publication Details**: Authors, year, domain, research type
- **Content Analysis**: Word count, section structure, citation density
- **Quality Indicators**: Abstract presence, methodology detection
- **Domain Classification**: Chemistry, biology, computer science, etc.

### Citation & Reference Management
- **Inline Citations**: [1], (Smith, 2020), superscript references
- **Reference Lists**: Parsed with author, title, journal extraction
- **Location Mapping**: Precise character positions and line numbers
- **Context Analysis**: Surrounding sentences and claim identification

### Knowledge Graph Features
- **Entity Types**: Authors, institutions, methods, concepts, technologies
- **Relationship Mapping**: Uses, improves, evaluates, compares
- **Graph Analytics**: Centrality measures, connected components
- **Cross-Paper Linking**: Shared entities across document collection

## 📚 Usage Examples

### Research Paper Understanding
```python
# Load and analyze paper
chat = analyze_paper_with_chat("transformer_chemistry.pdf")

# Understand methodology
response = chat.chat("What methods were used?")

# Explore relationships
authors = chat.explore_entity("BERT")
print(f"BERT connections: {authors['connections']}")
```

### Literature Review Preparation
```python
# Analyze multiple papers for corpus
papers = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]
corpus_docs = []

for pdf in papers:
    doc = export_paper_for_corpus(pdf)
    corpus_docs.append(doc)
    print(f"Processed: {doc['metadata']['title']}")

# Ready for GraphRAG and literature review writing
```

### Citation Verification
```python
# Verify citations in written content
section_text = "BERT achieves 89% accuracy [Smith et al., 2020]..."
evidence = [corpus_doc1, corpus_doc2, corpus_doc3]

verification = verify_citation_accuracy(section_text, evidence)
print(f"Citation accuracy: {verification['accuracy_score']:.1%}")
```

## 🔧 Advanced Configuration

### Custom Analysis Focus
```python
# Domain-specific analysis
analyzer = EnhancedPaperAnalyzer()
analyzer.domain_keywords = {
    'materials': ['polymer', 'crystal', 'synthesis'],
    'ai': ['neural', 'learning', 'algorithm']
}
```

### Citation Style Customization
```python
# Different citation formats
tracker = CitationTracker()
tracker.citation_patterns.update({
    'numbered_brackets': [r'\[(\d+)\]'],
    'author_year': [r'\(([A-Za-z]+,\s*\d{4})\)']
})
```

## 🚀 Next Steps: Complete Literature Review System

**Phase 2 (Planned)**: Corpus Management & GraphRAG
- Multi-paper corpus database
- LangChain GraphRAG implementation  
- Cross-paper entity linking

**Phase 3 (Planned)**: Automated Review Writing
- Literature review planning system
- Section-by-section writing with citations
- Evidence synthesis and narrative generation

## 🤝 Contributing

This is a personal research tool, but feedback and suggestions are welcome! 

## 📄 License

Open source for research and educational use.

---

**🎉 Start analyzing papers with AI today!**
Transform how you read, understand, and synthesize scientific literature with intelligent automation and precise citation tracking.