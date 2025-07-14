# Examples

This directory contains example files and scripts for the Scientific Paper Analyzer.

## Files

### `d4sc03921a.pdf`
Example research paper: "A review of large language models and autonomous agents in chemistry" 
- **Authors**: Mayk Caldas Ramos, Christopher J. Collison, Andrew D. White
- **Journal**: Chemical Science
- **Year**: 2024
- **DOI**: 10.1039/d4sc03921a

This paper is used for testing citation extraction and analysis functionality.

### `sample_analysis_outputs/`
Directory containing example outputs from the GraphRAG MCP analysis system showing:
- Natural knowledge graph discovery
- Comprehensive paper analysis
- Multiple export formats (GraphML, JSON, Markdown)
- Processing metadata and statistics

## Usage Examples

### Basic Paper Analysis with GraphRAG MCP
```python
from graphrag_mcp.core.analyzer import analyze_paper_with_chat

# Analyze paper with interactive chat interface
chat_system = analyze_paper_with_chat("examples/d4sc03921a.pdf")
response = chat_system.chat("What are the main findings?")
entities = chat_system.get_entities()
```

### Graphiti Knowledge Graph Creation
```python
from graphrag_mcp.core.graphiti_engine import create_graphiti_knowledge_graph
import asyncio

# Create Graphiti-powered knowledge graph
asyncio.run(create_graphiti_knowledge_graph())
```

### Export for Corpus Building
```python
from graphrag_mcp.core.analyzer import export_paper_for_corpus

# Export paper for GraphRAG corpus
corpus_doc = export_paper_for_corpus("examples/d4sc03921a.pdf")
print(f"Extracted {len(corpus_doc['entities'])} entities")
```

## Testing Your Own Papers

1. Place your PDF files in this directory
2. Update the file path in the examples
3. Run the GraphRAG MCP analysis:

```python
from graphrag_mcp.core.analyzer import analyze_paper_with_chat

# Analyze your own paper
chat_system = analyze_paper_with_chat("examples/your_paper.pdf")
response = chat_system.chat("What are the main contributions?")
```

## Expected Output

When running GraphRAG MCP analysis on the example paper, you should see:

```
🔄 Loading paper: d4sc03921a.pdf
✅ Document processed successfully
🔄 Building knowledge graph...
✅ Knowledge graph created with entities and relationships
🔄 Initializing chat system...
✅ Chat system ready

📊 Paper Analysis Results:
- Title: A review of large language models and autonomous agents in chemistry
- Authors: Mayk Caldas Ramos, Christopher J. Collison, Andrew D. White
- Entities extracted: 20+ (methods, concepts, technologies)
- Citations tracked: Multiple format support
- Knowledge graph: Graphiti-powered (NetworkX legacy support)
```

## Integration with Current System

The examples work with the current GraphRAG MCP architecture:
- **Core Engine**: Ollama + ChromaDB + Graphiti
- **Analysis**: Enhanced entity extraction with 20+ categories
- **Chat Interface**: Interactive exploration of paper content
- **Export**: GraphRAG-compatible corpus documents
- **Visualization**: yFiles professional graphs