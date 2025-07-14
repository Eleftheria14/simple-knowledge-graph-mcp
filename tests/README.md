# Tests

This directory contains test files for the GraphRAG MCP system.

## Test Files

### `test_graphiti_connection.py`
**Primary System Test** - Tests the complete GraphRAG MCP system with Graphiti integration.

**Features:**
- Tests GraphRAG MCP module imports
- Tests Graphiti core integration (if available)
- Tests Neo4j connection and database operations
- Tests Ollama LLM integration
- Tests knowledge graph creation and search

**Usage:**
```bash
# Prerequisites
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
ollama serve
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# Run test
python3 tests/test_graphiti_connection.py
```

### Visualization Test Files

#### `test_viz_graphiti.json`
Standard JSON format for knowledge graph visualization testing.

#### `test_viz_graphiti_cytoscape.json`
Cytoscape.js compatible format for web-based graph visualization.

#### `test_viz_graphiti.graphml`
GraphML format for external graph analysis tools (Gephi, yFiles, etc.).

## Test Data

All test files use a sample "ML for Drug Discovery" document with:
- **Document ID**: viz_test_001
- **Node Count**: 1 (document node)
- **Edge Count**: 0 (minimal test case)
- **Metadata**: Processing timestamp, document properties

## Integration Testing

The tests are designed to work with the current GraphRAG MCP architecture:

### System Components Tested
- **Core Engine**: Ollama + ChromaDB + Graphiti
- **Knowledge Graph**: Entity extraction and relationship mapping
- **Visualization**: Multiple export formats
- **Database**: Neo4j integration with Graphiti backend

### Expected Dependencies
- **Python 3.11+**: Core runtime
- **Neo4j**: Graph database (Docker container)
- **Ollama**: Local LLM server (llama3.1:8b, nomic-embed-text)
- **GraphRAG MCP**: Local module imports

## Running Tests

### Full System Test
```bash
# 1. Start services
docker start neo4j
ollama serve

# 2. Run comprehensive test
python3 tests/test_graphiti_connection.py
```

### Expected Output
```
🔄 Testing GraphRAG MCP system with Graphiti...
✅ GraphRAG MCP imports successful
✅ Graphiti core imports successful
🔄 Testing GraphRAG MCP knowledge graph creation...
✅ GraphRAG MCP knowledge graph created successfully
🔄 Testing Graphiti core integration...
✅ Graphiti initialized successfully
🔄 Building indices and constraints...
✅ Neo4j indices and constraints created
🔄 Adding test episode...
✅ Test episode added successfully
🔄 Testing search functionality...
✅ Search returned X results
🎉 GraphRAG MCP system test completed!
📊 System ready for paper analysis with Graphiti backend
```

## Troubleshooting

### Common Issues
- **Neo4j not running**: Start Docker container
- **Ollama not responding**: Check `ollama serve` status
- **Import errors**: Verify GraphRAG MCP module installation
- **Connection errors**: Check Neo4j credentials (neo4j/password)

### Test Environment Setup
```bash
# Environment activation
source graphiti-env/bin/activate

# Service startup
docker start neo4j
ollama serve

# Model availability
ollama list  # Should show llama3.1:8b and nomic-embed-text
```

## Future Test Additions

Planned test extensions:
- **Unit tests** for individual GraphRAG MCP components
- **Integration tests** for paper analysis workflow
- **Performance tests** for large document processing
- **MCP server tests** for template generation
- **Visualization tests** for different graph formats

## Test Data Management

The test files use minimal synthetic data to avoid:
- Large file dependencies
- Complex setup requirements
- External service dependencies
- Sensitive research content

All test data is self-contained and represents realistic but simplified use cases.