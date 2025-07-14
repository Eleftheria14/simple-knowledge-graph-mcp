# GraphRAG MCP Toolkit API Reference

This document provides comprehensive API documentation for the GraphRAG MCP Toolkit.

## 📋 Table of Contents

1. [Core Components](#core-components)
2. [Template System](#template-system)
3. [MCP Server API](#mcp-server-api)
4. [CLI Interface](#cli-interface)
5. [Configuration](#configuration)
6. [Python API](#python-api)

## 🔧 Core Components

### DocumentProcessor

Handles PDF parsing and content extraction with support for multiple document formats.

```python
from graphrag_mcp.core import DocumentProcessor, ProcessingConfig, DocumentData

class DocumentProcessor:
    def __init__(self, config: ProcessingConfig = None):
        """Initialize document processor with configuration."""
        
    def process_document(self, file_path: str) -> DocumentData:
        """Process a single document into structured data."""
        
    def extract_text(self, file_path: str) -> str:
        """Extract raw text from PDF or other document formats."""
        
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract document metadata including title, authors, citations."""

# Factory function
def create_document_processor(llm_model: str = "llama3.1:8b") -> DocumentProcessor:
    """Create document processor with default configuration."""
```

### AdvancedAnalyzer

GraphRAG-compatible document analysis with enhanced entity extraction.

```python
from graphrag_mcp.core import AdvancedAnalyzer, AnalysisConfig, CorpusDocument

class AdvancedAnalyzer:
    def __init__(self, config: AnalysisConfig = None):
        """Initialize advanced analyzer with configuration."""
        
    def analyze_for_corpus(self, 
                          file_path: str, 
                          domain_schema: Optional[Dict[str, str]] = None) -> CorpusDocument:
        """Analyze document for corpus inclusion with rich metadata."""
        
    def extract_entities(self, 
                        content: str, 
                        domain_guidance: Optional[Dict[str, str]] = None) -> Dict[str, List[str]]:
        """Extract entities using unconstrained approach with domain guidance."""
        
    def build_knowledge_graph(self, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Build knowledge graph from extracted entities and relationships."""

# Factory function
def create_advanced_analyzer() -> AdvancedAnalyzer:
    """Create advanced analyzer with default configuration."""
```

### ChatEngine

Interactive document exploration with hybrid RAG + knowledge graph retrieval.

```python
from graphrag_mcp.core import ChatEngine, ChatConfig, ChatResponse

class ChatEngine:
    def __init__(self, config: ChatConfig = None):
        """Initialize chat engine with configuration."""
        
    def chat(self, query: str, context: Optional[str] = None) -> ChatResponse:
        """Process user query with context and return structured response."""
        
    def search_semantic(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Semantic search across documents using embeddings."""
        
    def get_entities(self) -> Dict[str, List[str]]:
        """Get extracted entities from processed documents."""

# Factory function
def create_chat_engine() -> ChatEngine:
    """Create chat engine with default configuration."""
```

### OllamaEngine

Local LLM inference engine with health monitoring and embedding support.

```python
from graphrag_mcp.core import OllamaEngine, OllamaConfig

class OllamaEngine:
    def __init__(self, config: OllamaConfig = None):
        """Initialize Ollama engine with configuration."""
        
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate LLM response with optional parameters."""
        
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts using nomic-embed-text."""
        
    def check_health(self) -> Dict[str, Any]:
        """Check Ollama server health and available models."""

# Factory function
def create_ollama_engine(llm_model: str = "llama3.1:8b", 
                        embedding_model: str = "nomic-embed-text") -> OllamaEngine:
    """Create Ollama engine with specified models."""
```

## 🎨 Template System

### BaseTemplate

Abstract base class for all templates.

```python
from graphrag_mcp.templates import BaseTemplate, TemplateConfig

class BaseTemplate(ABC):
    def __init__(self):
        """Initialize template."""
        
    @abstractmethod
    def get_template_config(self) -> TemplateConfig:
        """Get template configuration."""
        
    @abstractmethod
    def get_entity_schema(self) -> Dict[str, str]:
        """Get entity schema for processing."""
        
    @abstractmethod
    def get_relationship_schema(self) -> List[Dict[str, Any]]:
        """Get relationship schema."""
        
    @abstractmethod
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions."""
```

### TemplateRegistry

Central registry for template management.

```python
from graphrag_mcp.templates import template_registry

class TemplateRegistry:
    def register(self, name: str, template_class: type):
        """Register template class."""
        
    def get_template(self, name: str) -> BaseTemplate:
        """Get template instance."""
        
    def list_templates(self) -> List[str]:
        """List available templates."""
        
    def get_template_info(self, name: str) -> Dict[str, Any]:
        """Get template information."""
```

### AcademicTemplate

Academic domain template implementation.

```python
from graphrag_mcp.templates import AcademicTemplate

class AcademicTemplate(BaseTemplate):
    def get_entity_schema(self) -> Dict[str, str]:
        """Get academic entity schema."""
        return {
            "academic": "Extract all entities focusing on research-related information"
        }
        
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get academic MCP tools."""
        return [
            {
                "name": "query_papers",
                "description": "Search and query papers in corpus",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
            # ... more tools
        ]
```

## 🌐 MCP Server API

### UniversalMCPServer

Universal MCP server for all domains with template switching capabilities.

```python
from graphrag_mcp.mcp import UniversalMCPServer, create_universal_server

class UniversalMCPServer:
    def __init__(self, 
                 name: str = "GraphRAG Universal Assistant",
                 template_name: str = "academic"):
        """Initialize universal MCP server with template."""
        
    async def run_server(self, 
                        transport: str = "stdio",
                        host: str = "localhost", 
                        port: int = 8080):
        """Run MCP server with specified transport."""
        
    def switch_template(self, template_name: str):
        """Switch to different domain template."""
        
    def get_server_status(self) -> Dict[str, Any]:
        """Get comprehensive server status."""

# Factory functions
def create_universal_server(template_name: str = "academic") -> UniversalMCPServer:
    """Create universal MCP server with specified template."""

async def run_universal_server_cli(template_name: str = "academic", 
                                  transport: str = "stdio"):
    """Run universal MCP server from CLI."""
```

### Core MCP Tools

#### list_templates
```python
async def list_templates(ctx: Context) -> Dict[str, Any]:
    """List all available domain templates."""
    return {
        "available_templates": {...},
        "current_template": "academic",
        "total_templates": 1
    }
```

#### switch_template
```python
async def switch_template(template_name: str, ctx: Context) -> Dict[str, Any]:
    """Switch to different domain template."""
    return {
        "success": True,
        "message": f"Switched to {template_name}",
        "current_template": template_name
    }
```

#### server_status
```python
async def server_status(ctx: Context) -> Dict[str, Any]:
    """Get comprehensive server status."""
    return {
        "server_name": "GraphRAG Universal Assistant",
        "current_template": "academic",
        "loaded_documents": 10,
        "ollama_status": {...}
    }
```

#### load_document_collection
```python
async def load_document_collection(collection_path: str, 
                                  collection_name: str, 
                                  ctx: Context) -> Dict[str, Any]:
    """Load and process document collection."""
    return {
        "success": True,
        "collection_name": collection_name,
        "documents_processed": 10,
        "entities_extracted": 150
    }
```

#### search_documents
```python
async def search_documents(query: str, 
                          collection_name: Optional[str] = None,
                          ctx: Context = None) -> Dict[str, Any]:
    """Search across loaded documents."""
    return {
        "success": True,
        "query": query,
        "results": [...],
        "total_matches": 5
    }
```

### Academic MCP Tools

#### query_papers
```python
async def query_papers(query: str, 
                      entity_filter: str = None, 
                      limit: int = 10) -> Dict[str, Any]:
    """Search and query papers in corpus."""
    return {
        "query": query,
        "results": [...],
        "total_matches": 15
    }
```

#### find_citations
```python
async def find_citations(claim: str, 
                        context: str = None) -> Dict[str, Any]:
    """Find citations for claims."""
    return {
        "claim": claim,
        "supporting_documents": [...],
        "evidence_count": 5
    }
```

#### research_gaps
```python
async def research_gaps(domain: str, 
                       depth: str = "surface") -> Dict[str, Any]:
    """Identify research gaps."""
    return {
        "domain": domain,
        "identified_gaps": [...],
        "recommendations": [...]
    }
```

## 💻 CLI Interface

### Main CLI App

```python
from graphrag_mcp.cli import cli_app
import typer

app = typer.Typer(
    name="graphrag-mcp",
    help="GraphRAG MCP Toolkit - Create domain-specific AI assistants"
)

@app.command()
def create(name: str, template: str = "academic"):
    """Create new domain-specific assistant."""
    
@app.command()
def add_documents(project: str, paths: List[str]):
    """Add documents to project."""
    
@app.command()
def process(project: str, force: bool = False):
    """Process documents into knowledge graphs."""
    
@app.command()
def serve(project: str, port: int = 8080):
    """Start MCP server for project."""
    
@app.command()
def status(project: Optional[str] = None):
    """Show system and project status."""
```

### CLI State Management

```python
from pydantic import BaseModel
from pathlib import Path

class CLIState(BaseModel):
    current_project: Optional[str] = None
    config_dir: Path = Path.home() / ".graphrag-mcp"
    projects_dir: Path = Path.home() / ".graphrag-mcp" / "projects"
    templates_dir: Path = Path.home() / ".graphrag-mcp" / "templates"
```

## ⚙️ Configuration

### Environment Variables

```bash
# Ollama configuration
OLLAMA_HOST=localhost:11434
OLLAMA_LLM_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# MCP server settings
GRAPHRAG_MCP_PORT=8080
GRAPHRAG_MCP_HOST=localhost
GRAPHRAG_MCP_CONFIG_DIR=~/.graphrag-mcp

# Processing settings
GRAPHRAG_MCP_MAX_ENTITIES=100
GRAPHRAG_MCP_CHUNK_SIZE=1000
GRAPHRAG_MCP_OVERLAP=200
```

### Project Configuration

```python
from pydantic import BaseModel
from typing import Dict, Any, List

class ProjectConfig(BaseModel):
    name: str
    template: str
    created_date: str
    version: str
    documents: List[str]
    mcp_server: Dict[str, Any]
    processing: Dict[str, Any]
```

Example `config.json`:
```json
{
  "name": "my-research",
  "template": "academic",
  "created_date": "2024-01-01",
  "version": "0.1.0",
  "documents": ["paper1.pdf", "paper2.pdf"],
  "mcp_server": {
    "port": 8080,
    "host": "localhost",
    "enabled": true
  },
  "processing": {
    "max_entities": 100,
    "citation_extraction": true,
    "entity_linking": true
  }
}
```

## 🐍 Python API

### Direct Usage

```python
from graphrag_mcp import (
    DocumentProcessor, 
    AdvancedAnalyzer, 
    UniversalMCPServer,
    template_registry
)

# Process document
processor = DocumentProcessor()
doc_data = processor.process_document("paper.pdf")

# Analyze for corpus
analyzer = AdvancedAnalyzer()
corpus_doc = analyzer.analyze_for_corpus("paper.pdf")

# Create MCP server
server = UniversalMCPServer(name="My Research Assistant")
await server.run_server()

# Use templates
academic_template = template_registry.get_template("academic")
tools = academic_template.get_mcp_tools()
```

### Programmatic Project Management

```python
from graphrag_mcp.cli.main import CLIState
from pathlib import Path
import json

# Create project programmatically
def create_project(name: str, template: str = "academic"):
    cli_state = CLIState()
    project_dir = cli_state.projects_dir / name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "name": name,
        "template": template,
        "created_date": "2024-01-01",
        "version": "0.1.0",
        "documents": [],
        "mcp_server": {"port": 8080, "host": "localhost", "enabled": False}
    }
    
    with open(project_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return project_dir

# Add documents programmatically
def add_documents_to_project(project_name: str, document_paths: List[str]):
    cli_state = CLIState()
    project_dir = cli_state.projects_dir / project_name
    docs_dir = project_dir / "documents"
    docs_dir.mkdir(exist_ok=True)
    
    for doc_path in document_paths:
        doc_path_obj = Path(doc_path)
        dest = docs_dir / doc_path_obj.name
        dest.write_bytes(doc_path_obj.read_bytes())
```

### Custom Template Creation

```python
from graphrag_mcp.templates import BaseTemplate, TemplateConfig, EntityConfig, MCPToolConfig

class CustomTemplate(BaseTemplate):
    def get_template_config(self) -> TemplateConfig:
        return TemplateConfig(
            name="Custom Domain",
            description="Custom template for my domain",
            domain="custom",
            version="1.0.0",
            entities=[
                EntityConfig(
                    name="custom_guidance",
                    description="Extract everything relevant to custom domain",
                    max_entities=999,
                    examples=["example1", "example2"]
                )
            ],
            relationships=[],
            mcp_tools=[
                MCPToolConfig(
                    name="custom_tool",
                    description="Custom domain tool",
                    parameters={
                        "query": {"type": "string", "description": "Query parameter"}
                    },
                    implementation="custom_implementation"
                )
            ]
        )
    
    def get_entity_schema(self) -> Dict[str, str]:
        return {
            "custom": "Extract all entities relevant to custom domain"
        }
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "custom_tool",
                "description": "Custom domain tool",
                "parameters": {
                    "query": {"type": "string", "description": "Query parameter"}
                }
            }
        ]

# Register custom template
template_registry.register("custom", CustomTemplate)
```

## 🔍 Error Handling

### Common Exceptions

```python
from graphrag_mcp.core.exceptions import (
    DocumentProcessingError,
    TemplateNotFoundError,
    OllamaConnectionError,
    MCPServerError
)

try:
    processor = DocumentProcessor()
    doc_data = processor.process_document("paper.pdf")
except DocumentProcessingError as e:
    logger.error(f"Document processing failed: {e}")
except OllamaConnectionError as e:
    logger.error(f"Ollama connection failed: {e}")
```

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Component-specific logging
logger = logging.getLogger('graphrag_mcp')
logger.setLevel(logging.DEBUG)
```

---

**For more examples and usage patterns, see the [Usage Guide](USAGE_GUIDE.md) and [examples](../examples/) directory.**