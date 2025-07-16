# GraphRAG MCP Toolkit API Reference

This document provides comprehensive API documentation for the **GraphRAG MCP Toolkit** - a system that enables Claude to both **chat conversationally** about research content AND **write literature reviews with automatic citations**.

## 🚀 Key Features

- **Citation Management**: Automatic citation tracking with 4 academic styles (APA, IEEE, Nature, MLA)
- **Knowledge Graph Integration**: Real-time knowledge graphs with Neo4j
- **Three User Interfaces**: CLI, Python API, and MCP tools
- **Local Privacy-First**: All processing via Ollama, no external API dependencies
- **Production MCP Integration**: 10+ MCP tools for Claude Desktop

## 📋 Table of Contents

1. [Python API](#python-api)
2. [Configuration](#configuration)
3. [Enhanced Document Processing](#enhanced-document-processing)
4. [Citation Management](#citation-management)
5. [CLI Interface](#cli-interface)
6. [MCP Tools](#mcp-tools)
7. [Error Handling](#error-handling)

## 🐍 Python API

### Quick Setup API

Convenience functions for common workflows:

```python
from graphrag_mcp.api import quick_setup, quick_process, validate_system

# One-line project setup
processor = quick_setup(
    project_name="research-project",
    documents_folder="./papers/",
    template="academic"
)

# One-line document processing
processor = await quick_process(
    project_name="research-project", 
    documents_folder="./papers/",
    template="academic"
)

# System validation
is_ready = validate_system()
```

### GraphRAGProcessor Class

Main user-facing API for document processing:

```python
from graphrag_mcp.api import GraphRAGProcessor

# Initialize processor
processor = GraphRAGProcessor(
    project_name="my-research",
    template="academic"
)

# Validate environment
validation = processor.validate_environment()
if not validation.is_valid:
    print(f"Issues: {validation.issues}")

# Discover documents
documents = processor.discover_documents("./papers/")

# Process documents
results = await processor.process_documents(documents)
print(f"Processed: {results.success}, Failed: {results.failed}")

# Start MCP server
await processor.start_mcp_server(port=8080)
```

### System Status API

```python
from graphrag_mcp.api import get_system_status

# Get detailed system status
status = get_system_status()
print(f"System ready: {status['ready']}")
print(f"Validation: {status['validation']}")
print(f"System info: {status['system_info']}")
```

## ⚙️ Configuration

### Simple Configuration System

```python
from graphrag_mcp.core.config import GraphRAGConfig

# Default configuration
config = GraphRAGConfig()

# Access nested settings
print(f"LLM Model: {config.model.llm_model}")
print(f"Chunk Size: {config.processing.chunk_size}")
print(f"ChromaDB Path: {config.storage.chromadb.persist_directory}")
print(f"Neo4j URI: {config.storage.neo4j.uri}")

# Environment-based configuration
config = GraphRAGConfig.from_env()
```

### Configuration Structure

```python
class GraphRAGConfig:
    model: ModelConfig              # LLM and embedding settings
    storage: StorageConfig          # ChromaDB and Neo4j settings
    processing: ProcessingConfig    # Text processing settings
    default_citation_style: str     # APA, IEEE, Nature, MLA
    mcp_server_name: str           # MCP server identification
```

### Environment Variables

```bash
# Model settings
export GRAPHRAG_LLM_MODEL="llama3.1:8b"
export GRAPHRAG_EMBEDDING_MODEL="nomic-embed-text"
export GRAPHRAG_TEMPERATURE="0.1"

# Storage settings
export GRAPHRAG_CHROMADB_PATH="chroma_graph_db"
export GRAPHRAG_NEO4J_URI="bolt://localhost:7687"
export GRAPHRAG_NEO4J_USER="neo4j"
export GRAPHRAG_NEO4J_PASSWORD="password"

# Processing settings
export GRAPHRAG_CHUNK_SIZE="1000"
export GRAPHRAG_CHUNK_OVERLAP="200"
export GRAPHRAG_CITATION_STYLE="APA"
```

## 📄 Enhanced Document Processing

### EnhancedDocumentProcessor

Sequential processing architecture with comprehensive analysis:

```python
from graphrag_mcp.core import EnhancedDocumentProcessor, GraphRAGConfig

# Initialize processor
config = GraphRAGConfig()
processor = EnhancedDocumentProcessor(config)

# Process document
result = processor.process_document("/path/to/document.pdf")

# Access results
print(f"Title: {result.document_title}")
print(f"Entities: {result.entities_created}")
print(f"Citations: {result.citations_stored}")
print(f"Relationships: {result.relationships_created}")
print(f"Processing time: {result.processing_time:.2f}s")

# Enhanced content chunks
enhanced_content = "\n\n".join(result.enhanced_chunks)
```

### ProcessingResult Structure

```python
@dataclass
class ProcessingResult:
    document_title: str
    document_path: str
    text_chunks: List[str]
    enhanced_chunks: List[str]          # Context-enriched chunks
    embeddings: np.ndarray             # Context-aware embeddings
    entities_created: int              # Number of entities extracted
    citations_stored: int              # Number of citations stored
    relationships_created: int         # Number of relationships created
    processing_time: float             # Processing duration
    analysis_result: AnalysisResult    # Detailed analysis results
    metadata: Dict[str, Any]           # Additional metadata
```

## 📚 Citation Management

### ChromaDBCitationManager

Persistent citation storage with multiple academic styles:

```python
from graphrag_mcp.core.chromadb_citation_manager import ChromaDBCitationManager

# Initialize citation manager
citation_manager = ChromaDBCitationManager(
    collection_name="research_citations",
    persist_directory="chroma_graph_db"
)

# Add citation
citation_key = citation_manager.add_citation(
    title="Attention Is All You Need",
    authors=["Vaswani, A.", "Shazeer, N."],
    year=2017,
    journal="NIPS",
    linked_entities=["transformer", "attention"]
)

# Track citation usage
citation_manager.track_citation(
    citation_key=citation_key,
    context_text="The transformer architecture revolutionized NLP",
    section="background",
    confidence=0.95
)

# Generate bibliography
bibliography = citation_manager.generate_bibliography(
    style="APA",
    used_only=True
)

# Get citation statistics
stats = citation_manager.get_citation_stats()
print(f"Total citations: {stats['total_citations']}")
```

### Supported Citation Styles

- **APA**: American Psychological Association
- **IEEE**: Institute of Electrical and Electronics Engineers  
- **Nature**: Nature Publishing Group
- **MLA**: Modern Language Association

## 🖥️ CLI Interface

### Available Commands

```bash
# Create new project
graphrag-mcp create my-project --template academic

# Add documents
graphrag-mcp add-documents my-project ./papers/ --recursive

# Process documents
graphrag-mcp process my-project

# Serve MCP server
graphrag-mcp serve my-project --port 8080

# Universal MCP server
graphrag-mcp serve-universal --template academic --transport stdio

# NEW: Visualize knowledge graph
graphrag-mcp visualize my-project --max-nodes 100 --interactive

# NEW: Validate system
graphrag-mcp validate --verbose --fix

# NEW: Quick setup
graphrag-mcp quick-setup research-project ./papers/ --auto-process --auto-serve

# Check status
graphrag-mcp status my-project

# List templates
graphrag-mcp templates --list
```

### Command Examples

```bash
# Complete workflow
graphrag-mcp create research-project --template academic
graphrag-mcp add-documents research-project ./papers/ --recursive
graphrag-mcp process research-project
graphrag-mcp visualize research-project --max-nodes 50
graphrag-mcp serve research-project --transport stdio

# Quick setup (single command)
graphrag-mcp quick-setup research-project ./papers/ --auto-process --auto-serve

# System validation
graphrag-mcp validate --verbose
```

## 🛠️ MCP Tools

### Chat Tools (Conversational Mode)

Tools for natural exploration and discovery:

```python
# Available via MCP protocol
ask_knowledge_graph(query: str) -> ChatResponse
explore_topic(topic: str, scope: str) -> TopicExploration  
find_connections(entity1: str, entity2: str) -> ConnectionAnalysis
what_do_we_know_about(topic: str) -> KnowledgeSummary
```

### Literature Review Tools (Formal Writing Mode)

Tools for formal academic writing with citations:

```python
# Available via MCP protocol
gather_sources_for_topic(topic: str) -> SourceCollection
get_facts_with_citations(topic: str, style: str) -> CitedFacts
verify_claim_with_sources(claim: str) -> ClaimVerification
get_topic_outline(topic: str) -> LiteratureOutline
track_citations_used() -> CitationUsage
generate_bibliography(style: str, used_only: bool) -> Bibliography
```

### Core Tools

```python
# Available via MCP protocol
list_templates() -> List[str]
switch_template(template_name: str) -> bool
load_document_collection(path: str) -> ProcessingResults
search_documents(query: str) -> SearchResults
```

## 🚨 Error Handling

### Exception Types

```python
from graphrag_mcp.utils.error_handling import (
    ProcessingError,
    ValidationError,
    ConfigurationError
)

try:
    result = processor.process_document("document.pdf")
except ProcessingError as e:
    print(f"Processing failed: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Error Recovery

```python
# Graceful error handling
try:
    processor = EnhancedDocumentProcessor(config)
    result = processor.process_document("document.pdf")
except Exception as e:
    logger.error(f"Processing failed: {e}")
    # Fallback to basic processing
    result = create_fallback_result(document_path)
```

## 📊 Status and Progress Tracking

### Document Status

```python
from graphrag_mcp.ui.status import DocumentStatus

# Track document processing
doc_status = DocumentStatus(
    path=Path("document.pdf"),
    name="document.pdf",
    size_mb=2.5,
    status="processing",
    entities_found=45,
    citations_found=12
)

# Check processing speed
print(f"Processing speed: {doc_status.processing_speed:.1f} pages/min")
```

### Processing Results

```python
from graphrag_mcp.ui.status import ProcessingResults

# Get overall results
results = ProcessingResults(
    total=10,
    success=8,
    failed=2,
    total_time=300.5,
    documents=processed_documents
)

print(f"Success rate: {results.success_rate:.1f}%")
print(f"Average time: {results.average_time:.1f}s per document")
```

## 🔍 Validation and Testing

### System Validation

```python
from graphrag_mcp.api import validate_system

# Quick validation
is_ready = validate_system()

# Detailed validation
from graphrag_mcp.utils.prerequisites import check_prerequisites
validation_result = check_prerequisites(verbose=True)

if validation_result.is_valid:
    print("✅ System ready")
else:
    print(f"❌ Issues: {validation_result.issues}")
```

### Health Monitoring

```python
# Check Ollama connection
config = GraphRAGConfig()
llm_engine = LLMAnalysisEngine(config.model.llm_model)
test_result = llm_engine.analyze_text_chunk("test", "test_doc")

# Check ChromaDB
citation_manager = ChromaDBCitationManager("test", "test_db")
stats = citation_manager.get_citation_stats()
```

## 📈 Performance and Monitoring

### Processing Statistics

```python
# Get processing statistics
stats = processor.get_processing_statistics()
print(f"Documents processed: {stats['documents_processed']}")
print(f"Average processing time: {stats['average_processing_time']:.2f}s")
print(f"Total entities: {stats['total_entities_created']}")
print(f"Total citations: {stats['total_citations_stored']}")
```

### Resource Management

```python
# Cleanup resources
processor.cleanup()

# Monitor memory usage
import psutil
memory_percent = psutil.virtual_memory().percent
print(f"Memory usage: {memory_percent}%")
```

## 🔧 Advanced Usage

### Custom Templates

```python
from graphrag_mcp.templates.base import BaseTemplate

class CustomTemplate(BaseTemplate):
    def get_entity_schema(self):
        return {
            "custom_entity": "Custom domain entity",
            "custom_relationship": "Custom relationship type"
        }
    
    def get_mcp_tools(self):
        return [
            # Define custom MCP tools
        ]
```

### Integration with External Systems

```python
# Neo4j integration
from graphrag_mcp.core.neo4j_entity_manager import Neo4jEntityManager

entity_manager = Neo4jEntityManager(
    uri="bolt://localhost:7687",
    auth=("neo4j", "password")
)

# Graphiti integration
from graphrag_mcp.core.graphiti_engine import GraphitiKnowledgeGraph

graphiti_engine = GraphitiKnowledgeGraph()
await graphiti_engine.initialize()
```

## 📝 Migration Guide

### From Legacy Architecture

```python
# OLD: AdvancedAnalyzer
from graphrag_mcp.core.analyzer import AdvancedAnalyzer
analyzer = AdvancedAnalyzer()
result = analyzer.analyze_for_corpus("document.pdf")

# NEW: EnhancedDocumentProcessor
from graphrag_mcp.core.enhanced_document_processor import EnhancedDocumentProcessor
processor = EnhancedDocumentProcessor(config)
result = processor.process_document("document.pdf")
```

### Configuration Migration

```python
# OLD: Complex nested config
config = ComplexConfig(
    models=ModelConfig(...),
    storage=StorageConfig(...),
    # ... many nested levels
)

# NEW: Simplified config
config = GraphRAGConfig()
# Access with: config.model.llm_model, config.storage.chromadb.persist_directory
```

## 🎯 Best Practices

1. **Use EnhancedDocumentProcessor** for all document processing
2. **Leverage ChromaDBCitationManager** for citation tracking
3. **Validate system** before processing with `validate_system()`
4. **Use appropriate citation styles** for your domain
5. **Monitor processing statistics** for performance optimization
6. **Implement error handling** for production systems
7. **Use the CLI** for most common operations
8. **Utilize MCP tools** for Claude Desktop integration

## 🆘 Troubleshooting

### Common Issues

1. **Import errors**: Check that dependencies are installed
2. **Ollama connection**: Ensure Ollama is running (`ollama serve`)
3. **ChromaDB permissions**: Check file permissions for database directory
4. **Neo4j connection**: Verify Neo4j is running and accessible
5. **Memory issues**: Monitor memory usage during processing

### Debug Commands

```bash
# Validate system
graphrag-mcp validate --verbose

# Check status
graphrag-mcp status

# Test configuration
python -c "from graphrag_mcp.core.config import GraphRAGConfig; print(GraphRAGConfig())"
```

---

This API reference covers the simplified GraphRAG MCP Toolkit architecture. For CLI usage, see [CLI_REFERENCE.md](CLI_REFERENCE.md). For MCP tools, see [MCP_TOOLS.md](MCP_TOOLS.md).