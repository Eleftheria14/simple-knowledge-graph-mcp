# GraphRAG MCP Configuration System

The GraphRAG MCP Toolkit includes a comprehensive configuration system that manages all aspects of the system including document processing, storage backends, LLM models, citation management, and knowledge graph settings.

## Table of Contents

- [Overview](#overview)
- [Configuration Classes](#configuration-classes)
- [Environment Profiles](#environment-profiles)
- [Usage Examples](#usage-examples)
- [Configuration Persistence](#configuration-persistence)
- [Validation and Error Handling](#validation-and-error-handling)
- [System Requirements](#system-requirements)
- [Best Practices](#best-practices)

## Overview

The configuration system is built on Pydantic v2 and provides:

- **Hierarchical Configuration**: Organized into logical components
- **Environment Profiles**: Development, production, and testing profiles
- **Validation**: Comprehensive validation with helpful error messages
- **Persistence**: Save and load configurations from JSON files
- **Environment Variables**: Support for .env files and environment variables
- **Type Safety**: Full type checking and IDE support

## Configuration Classes

### Main Configuration Classes

#### `GraphRAGConfig`
The main configuration class that combines all component configurations.

```python
from graphrag_mcp.core.config import GraphRAGConfig

config = GraphRAGConfig()
print(f"System: {config.system_name} v{config.version}")
```

#### `ProcessingConfig`
Configuration for document processing:

```python
from graphrag_mcp.core.config import ProcessingConfig

processing = ProcessingConfig(
    processing_mode="parallel",
    max_concurrent_documents=5,
    chunk_size=1000,
    chunk_overlap=100,
    validation_enabled=True,
    error_handling_mode="lenient"
)
```

Key settings:
- `processing_mode`: "sequential", "parallel", or "adaptive"
- `chunk_size`: Text chunk size (100-4000)
- `chunk_overlap`: Overlap between chunks
- `max_file_size_mb`: Maximum file size (1-500 MB)
- `validation_enabled`: Enable validation
- `error_handling_mode`: "strict", "lenient", or "skip"

#### `StorageConfig`
Configuration for storage backends:

```python
from graphrag_mcp.core.config import StorageConfig

storage = StorageConfig(
    chromadb_enabled=True,
    neo4j_enabled=True,
    backup_enabled=True,
    backup_interval_hours=24
)
```

Includes:
- `ChromaDBConfig`: Vector database settings
- `Neo4jConfig`: Graph database settings
- Backup and recovery settings

#### `ModelConfig`
Configuration for LLM and embedding models:

```python
from graphrag_mcp.core.config import ModelConfig

model = ModelConfig(
    llm_model="llama3.1:8b",
    embedding_model="nomic-embed-text",
    temperature=0.1,
    max_context=32768,
    enable_cache=True
)
```

Key settings:
- `llm_model`: Primary LLM model
- `embedding_model`: Embedding model
- `temperature`: Model temperature (0.0-1.0)
- `max_context`: Maximum context length
- `ollama_base_url`: Ollama server URL

#### `CitationConfig`
Configuration for citation management:

```python
from graphrag_mcp.core.config import CitationConfig

citation = CitationConfig(
    default_style="APA",
    supported_styles=["APA", "IEEE", "Nature", "MLA"],
    validate_citations=True,
    track_usage=True
)
```

Features:
- Multiple citation styles
- Citation validation
- Usage tracking
- Fuzzy matching

#### `KnowledgeGraphConfig`
Configuration for knowledge graph extraction:

```python
from graphrag_mcp.core.config import KnowledgeGraphConfig

kg = KnowledgeGraphConfig(
    entity_extraction_enabled=True,
    relationship_extraction_enabled=True,
    min_entity_confidence=0.7,
    entity_types=["PERSON", "ORGANIZATION", "CONCEPT"],
    enable_graph_validation=True
)
```

## Environment Profiles

The system supports three environment profiles:

### Development Profile
```python
config = GraphRAGConfig()
dev_config = config.get_profile("development")
```

Characteristics:
- Debug mode enabled
- Strict error handling
- Comprehensive validation
- No automatic backups
- Detailed logging

### Production Profile
```python
config = GraphRAGConfig()
prod_config = config.get_profile("production")
```

Characteristics:
- Debug mode disabled
- Lenient error handling
- Automatic backups enabled
- Performance optimizations
- Production logging

### Testing Profile
```python
config = GraphRAGConfig()
test_config = config.get_profile("testing")
```

Characteristics:
- Debug mode enabled
- Minimal validation
- Skip error handling
- No monitoring
- Fast execution

## Usage Examples

### Basic Usage

```python
from graphrag_mcp.core.config import GraphRAGConfig

# Create default configuration
config = GraphRAGConfig()

# Access component configurations
print(f"LLM Model: {config.model.llm_model}")
print(f"Chunk Size: {config.processing.chunk_size}")
print(f"Citation Style: {config.citation.default_style}")
```

### Custom Configuration

```python
from graphrag_mcp.core.config import create_config

# Create custom configuration with overrides
config = create_config(
    profile="development",
    system_name="My Research Assistant",
    **{
        "processing.chunk_size": 1200,
        "processing.processing_mode": "parallel",
        "model.temperature": 0.2,
        "citation.default_style": "IEEE"
    }
)
```

### Component Configuration

```python
from graphrag_mcp.core.config import (
    GraphRAGConfig, ProcessingConfig, ModelConfig
)

# Create custom components
processing = ProcessingConfig(
    processing_mode="parallel",
    max_concurrent_documents=10,
    chunk_size=1500
)

model = ModelConfig(
    llm_model="llama3.1:8b",
    temperature=0.15,
    max_context=16384
)

# Combine into main config
config = GraphRAGConfig(
    processing=processing,
    model=model
)
```

## Configuration Persistence

### Save Configuration

```python
from graphrag_mcp.core.config import GraphRAGConfig
from pathlib import Path

config = GraphRAGConfig()

# Save to default location
config.save_config()

# Save to custom location
config.save_config(Path("my_config.json"))
```

### Load Configuration

```python
from graphrag_mcp.core.config import GraphRAGConfig
from pathlib import Path

# Load from default location
config = GraphRAGConfig.load_config()

# Load from custom location
config = GraphRAGConfig.load_config(Path("my_config.json"))
```

### Environment Variables

Create a `.env` file:

```bash
# GraphRAG Configuration
GRAPHRAG_ENVIRONMENT=production
GRAPHRAG_DEBUG=false
GRAPHRAG_LOG_LEVEL=INFO

# Model Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1:8b
EMBEDDING_MODEL=nomic-embed-text

# Storage Configuration
CHROMADB_ENABLED=true
NEO4J_ENABLED=true
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

## Validation and Error Handling

### Validation Features

- **Range Validation**: Numeric values within acceptable ranges
- **Format Validation**: Proper formats for URLs, paths, etc.
- **Consistency Validation**: Cross-component consistency checks
- **Path Validation**: Automatic directory creation

### Error Examples

```python
from graphrag_mcp.core.config import ProcessingConfig

try:
    # This will fail validation
    config = ProcessingConfig(
        chunk_size=50,  # Too small
        temperature=1.5,  # Too high
        chunk_overlap=1000  # Larger than chunk_size
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Custom Validation

```python
from graphrag_mcp.core.config import GraphRAGConfig

config = GraphRAGConfig()

# This will fail consistency validation
config.storage.chromadb_enabled = True
config.model.embedding_model = ""  # Empty model
```

## System Requirements

### Validate System Requirements

```python
from graphrag_mcp.core.config import validate_system_requirements

config = GraphRAGConfig()
results = validate_system_requirements(config)

print(f"Status: {results['status']}")
print(f"Requirements: {results['requirements']}")

if results['errors']:
    print("Errors:")
    for error in results['errors']:
        print(f"  - {error}")
```

### Setup Environment

```python
from graphrag_mcp.core.config import setup_environment

config = GraphRAGConfig()
setup_environment(config)
```

This will:
- Configure logging
- Create necessary directories
- Set environment variables
- Initialize monitoring

## Best Practices

### 1. Use Environment Profiles

```python
# Development
dev_config = create_config(profile="development")

# Production
prod_config = create_config(profile="production")
```

### 2. Validate System Requirements

```python
from graphrag_mcp.core.config import validate_system_requirements

config = GraphRAGConfig()
results = validate_system_requirements(config)

if results['status'] != 'success':
    print("System not ready!")
    exit(1)
```

### 3. Use Configuration Factories

```python
from graphrag_mcp.core.config import create_config

# Better than manual construction
config = create_config(
    profile="production",
    system_name="My System",
    auto_save_config=True
)
```

### 4. Separate Configuration Files

```python
# Different environments
dev_config = GraphRAGConfig.load_config("config/development.json")
prod_config = GraphRAGConfig.load_config("config/production.json")
```

### 5. Version Your Configuration

```python
config = GraphRAGConfig(
    system_name="My System",
    version="1.2.0",  # Version your configuration
    auto_save_config=True
)
```

### 6. Monitor Configuration Changes

```python
import logging

# Configuration changes are logged
logging.basicConfig(level=logging.INFO)

config = GraphRAGConfig()
config.save_config()  # This will log the save operation
```

## Common Patterns

### Research Project Setup

```python
research_config = create_config(
    profile="development",
    system_name="Literature Review Assistant",
    **{
        "processing.chunk_size": 1200,
        "processing.processing_mode": "parallel",
        "citation.default_style": "APA",
        "citation.track_usage": True,
        "knowledge_graph.min_entity_confidence": 0.8
    }
)
```

### Production Deployment

```python
production_config = create_config(
    profile="production",
    system_name="GraphRAG Production",
    **{
        "processing.error_handling_mode": "lenient",
        "storage.backup_enabled": True,
        "model.enable_cache": True,
        "citation.validate_citations": True
    }
)
```

### Testing Environment

```python
test_config = create_config(
    profile="testing",
    system_name="Test System",
    **{
        "processing.validation_enabled": False,
        "storage.backup_enabled": False,
        "model.enable_cache": False
    }
)
```

## Troubleshooting

### Common Issues

1. **Validation Errors**: Check parameter ranges and formats
2. **Path Issues**: Ensure directories exist and are writable
3. **Consistency Errors**: Verify cross-component settings
4. **System Requirements**: Run validation before deployment

### Debug Mode

```python
config = GraphRAGConfig(debug=True, log_level="DEBUG")
setup_environment(config)
```

This provides detailed logging for troubleshooting.

## API Reference

For complete API documentation, see the docstrings in `/Users/aimiegarces/Agents/graphrag_mcp/core/config.py`.

Key classes:
- `GraphRAGConfig`: Main configuration class
- `ProcessingConfig`: Document processing settings
- `StorageConfig`: Storage backend settings
- `ModelConfig`: LLM and embedding model settings
- `CitationConfig`: Citation management settings
- `KnowledgeGraphConfig`: Knowledge graph settings

Key functions:
- `create_config()`: Configuration factory
- `validate_system_requirements()`: System validation
- `setup_environment()`: Environment setup