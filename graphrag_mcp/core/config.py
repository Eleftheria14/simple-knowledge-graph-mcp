"""
Simple Configuration for GraphRAG MCP Toolkit

Core settings for PDF processing, citations, and MCP server.
"""

import os
from pathlib import Path
from typing import Literal, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class ModelConfig(BaseModel):
    """Model configuration with multi-provider support"""
    # Provider selection
    provider: Literal["ollama", "openai", "anthropic", "groq", "together", "local_api"] = Field(
        default="ollama", 
        description="LLM provider"
    )
    
    # Model names by provider
    llm_model: str = Field(default="llama3.1:8b", description="LLM model name")
    embedding_model: str = Field(default="nomic-embed-text", description="Embedding model")
    
    # API configuration
    api_key: str = Field(default="", description="API key for cloud providers")
    base_url: str = Field(default="", description="Custom API base URL")
    
    # Model parameters
    temperature: float = Field(default=0.1, description="LLM temperature")
    max_context: int = Field(default=4096, description="Maximum context length")
    max_predict: int = Field(default=1024, description="Maximum prediction length")
    batch_size: int = Field(default=32, description="Embedding batch size")
    
    # Provider-specific settings
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    timeout: int = Field(default=300, description="Request timeout in seconds")


class StorageConfig(BaseModel):
    """Storage configuration"""
    class ChromaDBConfig(BaseModel):
        persist_directory: str = Field(default="chroma_graph_db", description="ChromaDB path")
        collection_name: str = Field(default="graphrag_citations", description="Collection name")
    
    class Neo4jConfig(BaseModel):
        uri: str = Field(default="bolt://localhost:7687", description="Neo4j URI")
        username: str = Field(default="neo4j", description="Neo4j username")
        password: str = Field(default="password", description="Neo4j password")
        database: str = Field(default="neo4j", description="Neo4j database")
    
    chromadb: ChromaDBConfig = Field(default_factory=ChromaDBConfig)
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)


class ProcessingConfig(BaseModel):
    """Processing configuration"""
    # Chunking parameters
    optimal_chunk_size: int = Field(default=370000, description="Optimal chunk size for LLM context")
    chunk_overlap: int = Field(default=25000, description="Chunk overlap")
    chunk_separators: List[str] = Field(
        default=["\n\n\n", "\n\n", "\n", ". ", " ", ""], 
        description="Chunk separators in priority order"
    )
    processing_mode: str = Field(default="sequential", description="Processing mode")
    
    # Context window settings
    context_window: int = Field(default=400000, description="LLM context window size")
    output_buffer: int = Field(default=30000, description="Buffer space for output")
    
    # Timeout settings
    small_content_timeout: int = Field(default=30, description="Timeout for small content")
    medium_content_timeout: int = Field(default=60, description="Timeout for medium content")
    large_content_timeout: int = Field(default=180, description="Timeout for large content")
    max_processing_timeout: int = Field(default=600, description="Maximum timeout")
    
    # Retry configuration
    max_json_parse_retries: int = Field(default=2, description="Max JSON parsing retries")
    max_consecutive_failures: int = Field(default=3, description="Max consecutive failures")


class ExtractionConfig(BaseModel):
    """Entity extraction configuration"""
    # Quality thresholds
    min_entities_expected: int = Field(default=15, description="Minimum entities expected")
    max_entities_expected: int = Field(default=50, description="Maximum entities expected")
    
    # Confidence thresholds
    min_entity_confidence: float = Field(default=0.7, description="Minimum entity confidence")
    min_citation_confidence: float = Field(default=0.5, description="Minimum citation confidence")
    min_relationship_confidence: float = Field(default=0.6, description="Minimum relationship confidence")
    
    # Feature toggles
    enable_entity_enhancement: bool = Field(default=False, description="Enable entity enhancement")
    enable_graphiti_sync: bool = Field(default=False, description="Enable Graphiti sync")
    enable_relationship_extraction: bool = Field(default=True, description="Enable relationship extraction")
    
    # Custom extraction prompt
    entity_extraction_prompt: str = Field(
        default="""TASK: Extract entities and citations from this academic document.

FOCUS ON:
- Authors and researchers
- Key concepts and theories  
- Methods and technologies
- Organizations and institutions
- Important measurements and materials

EXTRACT 15-30 entities for literature review quality.

CONTENT: {content}

Return ONLY this JSON:

{{
  "entities": [
    {{
      "id": "entity_1",
      "name": "Entity Name",
      "type": "concept"
    }}
  ],
  "citations": [
    {{
      "text": "Author et al. (2023)",
      "authors": ["Author"],
      "year": 2023
    }}
  ],
  "relationships": []
}}""",
        description="Entity extraction prompt template"
    )


class PerformanceConfig(BaseModel):
    """Performance and hardware-specific configuration"""
    # Mac-specific optimizations
    mac_thermal_throttle_delay: int = Field(default=0, description="Mac thermal throttle delay")
    mac_memory_limit_gb: int = Field(default=8, description="Mac memory limit in GB")
    enable_mac_optimizations: bool = Field(default=True, description="Enable Mac optimizations")
    
    # Performance monitoring
    enable_performance_logging: bool = Field(default=True, description="Enable performance logging")
    enable_entity_count_warnings: bool = Field(default=True, description="Enable entity count warnings")
    log_level: str = Field(default="INFO", description="Logging level")


class GraphRAGConfig(BaseModel):
    """Enhanced configuration for GraphRAG MCP Toolkit with environment variable support"""
    
    model: ModelConfig = Field(default_factory=ModelConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    # Citation settings
    default_citation_style: Literal["APA", "IEEE", "Nature", "MLA"] = Field(
        default="APA", 
        description="Default citation style"
    )
    
    # MCP settings
    mcp_server_name: str = Field(default="GraphRAG Research Assistant", description="MCP server name")
    
    @classmethod
    def from_env(cls) -> "GraphRAGConfig":
        """Load configuration from environment variables"""
        return cls(
            model=ModelConfig(
                provider=os.getenv("OLLAMA_PROVIDER", "ollama"),
                llm_model=os.getenv("OLLAMA_LLM_MODEL", "llama3.1:8b"),
                embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
                api_key=os.getenv("OLLAMA_API_KEY", ""),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.1")),
                max_context=int(os.getenv("OLLAMA_CONTEXT_WINDOW", "400000")),
                max_predict=int(os.getenv("OLLAMA_MAX_TOKENS", "4096")),
                batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "10")),
                ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                timeout=int(os.getenv("LARGE_CONTENT_TIMEOUT", "180"))
            ),
            storage=StorageConfig(
                chromadb=StorageConfig.ChromaDBConfig(
                    persist_directory=os.getenv("CHROMADB_PERSIST_DIR", "chroma_graph_db"),
                    collection_name=os.getenv("CHROMADB_COLLECTION_NAME", "graphrag_citations")
                ),
                neo4j=StorageConfig.Neo4jConfig(
                    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                    username=os.getenv("NEO4J_USERNAME", "neo4j"),
                    password=os.getenv("NEO4J_PASSWORD", "password"),
                    database=os.getenv("NEO4J_DATABASE", "neo4j")
                )
            ),
            processing=ProcessingConfig(
                optimal_chunk_size=int(os.getenv("OPTIMAL_CHUNK_SIZE", "370000")),
                chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "25000")),
                chunk_separators=os.getenv("CHUNK_SEPARATORS", "\\n\\n\\n,\\n\\n,\\n,. , ,").split(","),
                processing_mode=os.getenv("PROCESSING_MODE", "sequential"),
                context_window=int(os.getenv("OLLAMA_CONTEXT_WINDOW", "400000")),
                output_buffer=int(os.getenv("OLLAMA_OUTPUT_BUFFER", "30000")),
                small_content_timeout=int(os.getenv("SMALL_CONTENT_TIMEOUT", "30")),
                medium_content_timeout=int(os.getenv("MEDIUM_CONTENT_TIMEOUT", "60")),
                large_content_timeout=int(os.getenv("LARGE_CONTENT_TIMEOUT", "180")),
                max_processing_timeout=int(os.getenv("MAX_PROCESSING_TIMEOUT", "600")),
                max_json_parse_retries=int(os.getenv("MAX_JSON_PARSE_RETRIES", "2")),
                max_consecutive_failures=int(os.getenv("MAX_CONSECUTIVE_FAILURES", "3"))
            ),
            extraction=ExtractionConfig(
                min_entities_expected=int(os.getenv("MIN_ENTITIES_EXPECTED", "15")),
                max_entities_expected=int(os.getenv("MAX_ENTITIES_EXPECTED", "50")),
                min_entity_confidence=float(os.getenv("MIN_ENTITY_CONFIDENCE", "0.7")),
                min_citation_confidence=float(os.getenv("MIN_CITATION_CONFIDENCE", "0.5")),
                min_relationship_confidence=float(os.getenv("MIN_RELATIONSHIP_CONFIDENCE", "0.6")),
                enable_entity_enhancement=os.getenv("ENABLE_ENTITY_ENHANCEMENT", "false").lower() == "true",
                enable_graphiti_sync=os.getenv("ENABLE_GRAPHITI_SYNC", "false").lower() == "true",
                enable_relationship_extraction=os.getenv("ENABLE_RELATIONSHIP_EXTRACTION", "true").lower() == "true",
                entity_extraction_prompt=os.getenv("ENTITY_EXTRACTION_PROMPT", ExtractionConfig().entity_extraction_prompt)
            ),
            performance=PerformanceConfig(
                mac_thermal_throttle_delay=int(os.getenv("MAC_THERMAL_THROTTLE_DELAY", "0")),
                mac_memory_limit_gb=int(os.getenv("MAC_MEMORY_LIMIT_GB", "8")),
                enable_mac_optimizations=os.getenv("ENABLE_MAC_OPTIMIZATIONS", "true").lower() == "true",
                enable_performance_logging=os.getenv("ENABLE_PERFORMANCE_LOGGING", "true").lower() == "true",
                enable_entity_count_warnings=os.getenv("ENABLE_ENTITY_COUNT_WARNINGS", "true").lower() == "true",
                log_level=os.getenv("LOG_LEVEL", "INFO")
            ),
            default_citation_style=os.getenv("DEFAULT_CITATION_STYLE", "APA"),
            mcp_server_name=os.getenv("MCP_SERVER_NAME", "GraphRAG Research Assistant")
        )