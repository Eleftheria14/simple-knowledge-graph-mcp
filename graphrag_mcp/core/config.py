"""
Configuration Management System for GraphRAG MCP Toolkit

Provides comprehensive configuration management for all system components
including sequential processing, storage, models, citations, and knowledge graphs.
Supports environment variables, validation, and development/production profiles.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


# =============================================================================
# Base Configuration Classes
# =============================================================================

class BaseConfig(BaseSettings):
    """Base configuration class with common settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment and deployment settings
    environment: Literal["development", "production", "testing"] = Field(
        default="development",
        description="Deployment environment"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Base directories
    project_root: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Project root directory"
    )
    
    data_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "data",
        description="Data storage directory"
    )
    
    cache_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "cache",
        description="Cache storage directory"
    )
    
    logs_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "logs",
        description="Logs directory"
    )
    
    @validator('project_root', 'data_dir', 'cache_dir', 'logs_dir', pre=True)
    def validate_paths(cls, v):
        """Validate and create directories if they don't exist"""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v


# =============================================================================
# Processing Configuration
# =============================================================================

class ProcessingConfig(BaseConfig):
    """Configuration for sequential document processing"""
    
    # Processing modes
    processing_mode: Literal["sequential", "parallel", "adaptive"] = Field(
        default="sequential",
        description="Document processing mode"
    )
    
    max_concurrent_documents: int = Field(
        default=3,
        description="Maximum concurrent documents in parallel mode"
    )
    
    batch_size: int = Field(
        default=10,
        description="Batch size for document processing"
    )
    
    # Document processing settings
    chunk_size: int = Field(
        default=800,
        description="Text chunk size for document splitting"
    )
    
    chunk_overlap: int = Field(
        default=100,
        description="Overlap between text chunks"
    )
    
    max_file_size_mb: int = Field(
        default=50,
        description="Maximum file size in MB"
    )
    
    supported_formats: List[str] = Field(
        default_factory=lambda: [".pdf", ".txt", ".md", ".docx"],
        description="Supported document formats"
    )
    
    # Validation and timeout settings
    validation_enabled: bool = Field(
        default=True,
        description="Enable comprehensive validation"
    )
    
    entity_extraction_timeout: int = Field(
        default=120,
        description="Timeout for entity extraction in seconds"
    )
    
    document_processing_timeout: int = Field(
        default=300,
        description="Timeout for document processing in seconds"
    )
    
    max_retry_attempts: int = Field(
        default=3,
        description="Maximum retry attempts for failed operations"
    )
    
    retry_delay: float = Field(
        default=1.0,
        description="Delay between retry attempts in seconds"
    )
    
    # Error handling
    error_handling_mode: Literal["strict", "lenient", "skip"] = Field(
        default="lenient",
        description="Error handling mode for processing failures"
    )
    
    skip_corrupted_files: bool = Field(
        default=True,
        description="Skip corrupted or unreadable files"
    )
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        if v < 100 or v > 4000:
            raise ValueError('chunk_size must be between 100 and 4000')
        return v
    
    @validator('chunk_overlap')
    def validate_chunk_overlap(cls, v, values):
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError('chunk_overlap must be less than chunk_size')
        return v
    
    @validator('max_file_size_mb')
    def validate_max_file_size(cls, v):
        if v < 1 or v > 500:
            raise ValueError('max_file_size_mb must be between 1 and 500')
        return v
    
    @validator('max_concurrent_documents')
    def validate_max_concurrent(cls, v):
        if v < 1 or v > 20:
            raise ValueError('max_concurrent_documents must be between 1 and 20')
        return v


# =============================================================================
# Storage Configuration
# =============================================================================

class ChromaDBConfig(BaseModel):
    """ChromaDB-specific configuration"""
    
    # Database settings
    persist_directory: Path = Field(
        default_factory=lambda: Path.cwd() / "chroma_db",
        description="ChromaDB persistence directory"
    )
    
    collection_name: str = Field(
        default="graphrag_documents",
        description="Default collection name"
    )
    
    # Performance settings
    batch_size: int = Field(
        default=100,
        description="Batch size for ChromaDB operations"
    )
    
    max_batch_size: int = Field(
        default=1000,
        description="Maximum batch size for bulk operations"
    )
    
    # Index settings
    index_type: Literal["flat", "hnsw", "ivf"] = Field(
        default="hnsw",
        description="Vector index type"
    )
    
    hnsw_m: int = Field(
        default=16,
        description="HNSW index M parameter"
    )
    
    hnsw_ef_construction: int = Field(
        default=200,
        description="HNSW index ef_construction parameter"
    )
    
    # Maintenance settings
    auto_cleanup: bool = Field(
        default=True,
        description="Enable automatic cleanup of old entries"
    )
    
    cleanup_interval_days: int = Field(
        default=30,
        description="Cleanup interval in days"
    )
    
    @validator('persist_directory', pre=True)
    def validate_persist_directory(cls, v):
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v


class Neo4jConfig(BaseModel):
    """Neo4j-specific configuration"""
    
    # Connection settings
    uri: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j connection URI"
    )
    
    username: str = Field(
        default="neo4j",
        description="Neo4j username"
    )
    
    password: str = Field(
        default="password",
        description="Neo4j password"
    )
    
    database: str = Field(
        default="neo4j",
        description="Neo4j database name"
    )
    
    # Connection pool settings
    max_connections: int = Field(
        default=100,
        description="Maximum connection pool size"
    )
    
    connection_timeout: int = Field(
        default=30,
        description="Connection timeout in seconds"
    )
    
    max_transaction_retry_time: int = Field(
        default=30,
        description="Maximum transaction retry time in seconds"
    )
    
    # Performance settings
    batch_size: int = Field(
        default=1000,
        description="Batch size for Neo4j operations"
    )
    
    max_batch_size: int = Field(
        default=5000,
        description="Maximum batch size for bulk operations"
    )
    
    # Index settings
    auto_create_indexes: bool = Field(
        default=True,
        description="Automatically create indexes for entities"
    )
    
    index_properties: List[str] = Field(
        default_factory=lambda: ["id", "name", "type"],
        description="Properties to index automatically"
    )
    
    # Maintenance settings
    enable_statistics: bool = Field(
        default=True,
        description="Enable database statistics collection"
    )
    
    @validator('uri')
    def validate_uri(cls, v):
        if not v.startswith(('bolt://', 'neo4j://', 'bolt+s://', 'neo4j+s://')):
            raise ValueError('Neo4j URI must start with bolt://, neo4j://, bolt+s://, or neo4j+s://')
        return v


class StorageConfig(BaseConfig):
    """Unified storage configuration for ChromaDB and Neo4j"""
    
    # Storage backends
    chromadb_enabled: bool = Field(
        default=True,
        description="Enable ChromaDB storage"
    )
    
    neo4j_enabled: bool = Field(
        default=True,
        description="Enable Neo4j storage"
    )
    
    # Configuration objects
    chromadb: ChromaDBConfig = Field(
        default_factory=ChromaDBConfig,
        description="ChromaDB configuration"
    )
    
    neo4j: Neo4jConfig = Field(
        default_factory=Neo4jConfig,
        description="Neo4j configuration"
    )
    
    # Backup and recovery
    backup_enabled: bool = Field(
        default=True,
        description="Enable automatic backups"
    )
    
    backup_interval_hours: int = Field(
        default=24,
        description="Backup interval in hours"
    )
    
    backup_retention_days: int = Field(
        default=7,
        description="Backup retention period in days"
    )
    
    backup_directory: Path = Field(
        default_factory=lambda: Path.cwd() / "backups",
        description="Backup storage directory"
    )
    
    @validator('backup_directory', pre=True)
    def validate_backup_directory(cls, v):
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v


# =============================================================================
# Model Configuration
# =============================================================================

class ModelConfig(BaseConfig):
    """Configuration for LLM and embedding models"""
    
    # Ollama settings
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL"
    )
    
    ollama_timeout: int = Field(
        default=120,
        description="Ollama request timeout in seconds"
    )
    
    # LLM model settings
    llm_model: str = Field(
        default="llama3.1:8b",
        description="Primary LLM model"
    )
    
    fallback_llm_model: str = Field(
        default="llama3.1:8b",
        description="Fallback LLM model"
    )
    
    temperature: float = Field(
        default=0.1,
        description="LLM temperature for consistency"
    )
    
    max_context: int = Field(
        default=32768,
        description="Maximum context length"
    )
    
    max_predict: int = Field(
        default=2048,
        description="Maximum prediction length"
    )
    
    # Embedding model settings
    embedding_model: str = Field(
        default="nomic-embed-text",
        description="Primary embedding model"
    )
    
    fallback_embedding_model: str = Field(
        default="nomic-embed-text",
        description="Fallback embedding model"
    )
    
    embedding_dimensions: int = Field(
        default=768,
        description="Embedding vector dimensions"
    )
    
    # Performance settings
    batch_size: int = Field(
        default=32,
        description="Batch size for model operations"
    )
    
    max_batch_size: int = Field(
        default=100,
        description="Maximum batch size for bulk operations"
    )
    
    # Caching settings
    enable_cache: bool = Field(
        default=True,
        description="Enable model response caching"
    )
    
    cache_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds"
    )
    
    cache_size: int = Field(
        default=1000,
        description="Maximum cache entries"
    )
    
    # Model health monitoring
    health_check_interval: int = Field(
        default=60,
        description="Health check interval in seconds"
    )
    
    max_consecutive_failures: int = Field(
        default=3,
        description="Maximum consecutive failures before fallback"
    )
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('temperature must be between 0.0 and 1.0')
        return v
    
    @validator('max_context', 'max_predict')
    def validate_token_limits(cls, v):
        if v < 1 or v > 100000:
            raise ValueError('Token limits must be between 1 and 100000')
        return v
    
    @validator('embedding_dimensions')
    def validate_embedding_dimensions(cls, v):
        if v < 1 or v > 2048:
            raise ValueError('Embedding dimensions must be between 1 and 2048')
        return v


# =============================================================================
# Citation Configuration
# =============================================================================

class CitationConfig(BaseConfig):
    """Configuration for citation management"""
    
    # Citation styles
    default_style: Literal["APA", "IEEE", "Nature", "MLA", "Chicago"] = Field(
        default="APA",
        description="Default citation style"
    )
    
    supported_styles: List[str] = Field(
        default_factory=lambda: ["APA", "IEEE", "Nature", "MLA", "Chicago"],
        description="Supported citation styles"
    )
    
    # Citation tracking
    track_usage: bool = Field(
        default=True,
        description="Track citation usage statistics"
    )
    
    track_context: bool = Field(
        default=True,
        description="Track citation context and confidence"
    )
    
    auto_generate_keys: bool = Field(
        default=True,
        description="Automatically generate citation keys"
    )
    
    # Citation validation
    validate_citations: bool = Field(
        default=True,
        description="Validate citation completeness"
    )
    
    require_doi: bool = Field(
        default=False,
        description="Require DOI for citations"
    )
    
    require_year: bool = Field(
        default=True,
        description="Require publication year"
    )
    
    # Citation storage
    storage_format: Literal["json", "bibtex", "ris", "endnote"] = Field(
        default="json",
        description="Citation storage format"
    )
    
    citations_file: Path = Field(
        default_factory=lambda: Path.cwd() / "citations.json",
        description="Citations storage file"
    )
    
    backup_citations: bool = Field(
        default=True,
        description="Backup citations automatically"
    )
    
    # Bibliography generation
    bibliography_style: Dict[str, Any] = Field(
        default_factory=lambda: {
            "include_abstracts": False,
            "include_urls": True,
            "include_dois": True,
            "sort_by": "author",
            "group_by": "year"
        },
        description="Bibliography generation settings"
    )
    
    # Citation matching
    fuzzy_matching: bool = Field(
        default=True,
        description="Enable fuzzy matching for citations"
    )
    
    similarity_threshold: float = Field(
        default=0.8,
        description="Similarity threshold for citation matching"
    )
    
    # Usage analytics
    analytics_enabled: bool = Field(
        default=True,
        description="Enable citation usage analytics"
    )
    
    analytics_retention_days: int = Field(
        default=365,
        description="Analytics data retention period"
    )
    
    @validator('similarity_threshold')
    def validate_similarity_threshold(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('similarity_threshold must be between 0.0 and 1.0')
        return v
    
    @validator('citations_file', pre=True)
    def validate_citations_file(cls, v):
        if isinstance(v, str):
            v = Path(v)
        v.parent.mkdir(parents=True, exist_ok=True)
        return v


# =============================================================================
# Knowledge Graph Configuration
# =============================================================================

class KnowledgeGraphConfig(BaseConfig):
    """Configuration for knowledge graph management"""
    
    # Entity extraction settings
    entity_extraction_enabled: bool = Field(
        default=True,
        description="Enable entity extraction"
    )
    
    entity_types: List[str] = Field(
        default_factory=lambda: [
            "PERSON", "ORGANIZATION", "LOCATION", "CONCEPT",
            "TECHNOLOGY", "METHOD", "DATASET", "METRIC"
        ],
        description="Supported entity types"
    )
    
    min_entity_confidence: float = Field(
        default=0.7,
        description="Minimum confidence threshold for entities"
    )
    
    max_entities_per_document: int = Field(
        default=100,
        description="Maximum entities per document"
    )
    
    # Relationship extraction settings
    relationship_extraction_enabled: bool = Field(
        default=True,
        description="Enable relationship extraction"
    )
    
    relationship_types: List[str] = Field(
        default_factory=lambda: [
            "RELATED_TO", "PART_OF", "USED_BY", "CREATED_BY",
            "INFLUENCES", "DEPENDS_ON", "COMPETES_WITH", "EXTENDS"
        ],
        description="Supported relationship types"
    )
    
    min_relationship_confidence: float = Field(
        default=0.6,
        description="Minimum confidence threshold for relationships"
    )
    
    max_relationships_per_document: int = Field(
        default=200,
        description="Maximum relationships per document"
    )
    
    # Graph construction settings
    enable_graph_validation: bool = Field(
        default=True,
        description="Enable graph structure validation"
    )
    
    enable_duplicate_detection: bool = Field(
        default=True,
        description="Enable duplicate entity detection"
    )
    
    merge_similar_entities: bool = Field(
        default=True,
        description="Merge similar entities automatically"
    )
    
    entity_similarity_threshold: float = Field(
        default=0.85,
        description="Similarity threshold for entity merging"
    )
    
    # Graph analytics
    compute_centrality: bool = Field(
        default=True,
        description="Compute node centrality metrics"
    )
    
    compute_communities: bool = Field(
        default=True,
        description="Compute community structures"
    )
    
    analytics_batch_size: int = Field(
        default=1000,
        description="Batch size for graph analytics"
    )
    
    # Performance settings
    parallel_processing: bool = Field(
        default=True,
        description="Enable parallel graph processing"
    )
    
    max_parallel_workers: int = Field(
        default=4,
        description="Maximum parallel workers for graph processing"
    )
    
    # Visualization settings
    enable_visualization: bool = Field(
        default=True,
        description="Enable graph visualization"
    )
    
    visualization_layout: Literal["spring", "circular", "hierarchical", "force"] = Field(
        default="spring",
        description="Default graph layout algorithm"
    )
    
    max_nodes_for_visualization: int = Field(
        default=500,
        description="Maximum nodes for visualization"
    )
    
    @validator('min_entity_confidence', 'min_relationship_confidence', 'entity_similarity_threshold')
    def validate_confidence_thresholds(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Confidence thresholds must be between 0.0 and 1.0')
        return v
    
    @validator('max_entities_per_document', 'max_relationships_per_document')
    def validate_max_per_document(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Maximum per document values must be between 1 and 1000')
        return v


# =============================================================================
# Unified Configuration Management
# =============================================================================

class GraphRAGConfig(BaseConfig):
    """Unified configuration for the entire GraphRAG MCP system"""
    
    # Component configurations
    processing: ProcessingConfig = Field(
        default_factory=ProcessingConfig,
        description="Document processing configuration"
    )
    
    storage: StorageConfig = Field(
        default_factory=StorageConfig,
        description="Storage backends configuration"
    )
    
    model: ModelConfig = Field(
        default_factory=ModelConfig,
        description="LLM and embedding models configuration"
    )
    
    citation: CitationConfig = Field(
        default_factory=CitationConfig,
        description="Citation management configuration"
    )
    
    knowledge_graph: KnowledgeGraphConfig = Field(
        default_factory=KnowledgeGraphConfig,
        description="Knowledge graph configuration"
    )
    
    # System-wide settings
    system_name: str = Field(
        default="GraphRAG MCP Toolkit",
        description="System name for identification"
    )
    
    version: str = Field(
        default="1.0.0",
        description="System version"
    )
    
    # Performance monitoring
    enable_monitoring: bool = Field(
        default=True,
        description="Enable system monitoring"
    )
    
    monitoring_interval: int = Field(
        default=30,
        description="Monitoring interval in seconds"
    )
    
    # Security settings
    enable_security: bool = Field(
        default=True,
        description="Enable security features"
    )
    
    max_request_size: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        description="Maximum request size in bytes"
    )
    
    rate_limit_requests: int = Field(
        default=100,
        description="Rate limit per minute"
    )
    
    # Configuration persistence
    config_file: Path = Field(
        default_factory=lambda: Path.cwd() / "graphrag_config.json",
        description="Configuration file path"
    )
    
    auto_save_config: bool = Field(
        default=True,
        description="Automatically save configuration changes"
    )
    
    @validator('config_file', pre=True)
    def validate_config_file(cls, v):
        if isinstance(v, str):
            v = Path(v)
        v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @model_validator(mode='after')
    def validate_consistency(self):
        """Validate configuration consistency across components"""
        # Validate storage consistency
        if self.storage.chromadb_enabled:
            if not self.model.embedding_model:
                raise ValueError('ChromaDB enabled but no embedding model configured')
        
        # Validate citation consistency
        if self.citation.default_style not in self.citation.supported_styles:
            raise ValueError('Default citation style not in supported styles')
        
        return self
    
    def save_config(self, file_path: Optional[Path] = None) -> None:
        """Save configuration to file"""
        if file_path is None:
            file_path = self.config_file
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.model_dump(), f, indent=2, default=str)
            logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    @classmethod
    def load_config(cls, file_path: Optional[Path] = None) -> 'GraphRAGConfig':
        """Load configuration from file"""
        if file_path is None:
            file_path = Path.cwd() / "graphrag_config.json"
        
        if not file_path.exists():
            logger.info(f"Configuration file {file_path} not found, using defaults")
            return cls()
        
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Convert string paths back to Path objects
            def convert_paths(obj):
                if isinstance(obj, dict):
                    return {k: convert_paths(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_paths(item) for item in obj]
                elif isinstance(obj, str) and ('_dir' in str(obj) or '_file' in str(obj) or 'directory' in str(obj)):
                    return Path(obj)
                return obj
            
            config_data = convert_paths(config_data)
            
            logger.info(f"Configuration loaded from {file_path}")
            return cls(**config_data)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            return cls()
    
    def get_profile(self, profile_name: str) -> 'GraphRAGConfig':
        """Get configuration profile (development/production)"""
        if profile_name == "development":
            return self._get_development_profile()
        elif profile_name == "production":
            return self._get_production_profile()
        elif profile_name == "testing":
            return self._get_testing_profile()
        else:
            raise ValueError(f"Unknown profile: {profile_name}")
    
    def _get_development_profile(self) -> 'GraphRAGConfig':
        """Get development configuration profile"""
        config = self.model_copy(deep=True)
        config.environment = "development"
        config.debug = True
        config.log_level = "DEBUG"
        config.enable_monitoring = True
        config.processing.validation_enabled = True
        config.processing.error_handling_mode = "strict"
        config.storage.backup_enabled = False
        config.model.enable_cache = True
        config.citation.validate_citations = True
        config.knowledge_graph.enable_graph_validation = True
        return config
    
    def _get_production_profile(self) -> 'GraphRAGConfig':
        """Get production configuration profile"""
        config = self.model_copy(deep=True)
        config.environment = "production"
        config.debug = False
        config.log_level = "INFO"
        config.enable_monitoring = True
        config.processing.validation_enabled = True
        config.processing.error_handling_mode = "lenient"
        config.storage.backup_enabled = True
        config.model.enable_cache = True
        config.citation.validate_citations = True
        config.knowledge_graph.enable_graph_validation = True
        return config
    
    def _get_testing_profile(self) -> 'GraphRAGConfig':
        """Get testing configuration profile"""
        config = self.model_copy(deep=True)
        config.environment = "testing"
        config.debug = True
        config.log_level = "DEBUG"
        config.enable_monitoring = False
        config.processing.validation_enabled = False
        config.processing.error_handling_mode = "skip"
        config.storage.backup_enabled = False
        config.model.enable_cache = False
        config.citation.validate_citations = False
        config.knowledge_graph.enable_graph_validation = False
        return config


# =============================================================================
# Configuration Factory and Utilities
# =============================================================================

def create_config(
    profile: str = "development",
    config_file: Optional[Path] = None,
    **overrides
) -> GraphRAGConfig:
    """
    Create a GraphRAG configuration with profile and overrides.
    
    Args:
        profile: Configuration profile (development/production/testing)
        config_file: Path to configuration file
        **overrides: Configuration overrides
        
    Returns:
        GraphRAGConfig instance
    """
    # Load base configuration
    if config_file and config_file.exists():
        config = GraphRAGConfig.load_config(config_file)
    else:
        config = GraphRAGConfig()
    
    # Apply profile
    config = config.get_profile(profile)
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            # Handle nested configuration
            parts = key.split('.')
            if len(parts) == 2:
                section, param = parts
                if hasattr(config, section):
                    section_config = getattr(config, section)
                    if hasattr(section_config, param):
                        setattr(section_config, param, value)
    
    # Auto-save if enabled
    if config.auto_save_config:
        config.save_config()
    
    return config


def validate_system_requirements(config: GraphRAGConfig) -> Dict[str, Any]:
    """
    Validate system requirements for the given configuration.
    
    Args:
        config: GraphRAGConfig instance
        
    Returns:
        Validation results dictionary
    """
    results = {
        "status": "success",
        "warnings": [],
        "errors": [],
        "requirements": {}
    }
    
    # Check Ollama connection
    try:
        import httpx
        response = httpx.get(f"{config.model.ollama_base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            results["requirements"]["ollama"] = "available"
        else:
            results["requirements"]["ollama"] = "unavailable"
            results["errors"].append(f"Ollama not responding at {config.model.ollama_base_url}")
    except Exception as e:
        results["requirements"]["ollama"] = "unavailable"
        results["errors"].append(f"Ollama connection failed: {e}")
    
    # Check Neo4j connection if enabled
    if config.storage.neo4j_enabled:
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(
                config.storage.neo4j.uri,
                auth=(config.storage.neo4j.username, config.storage.neo4j.password)
            )
            with driver.session() as session:
                session.run("RETURN 1")
            results["requirements"]["neo4j"] = "available"
            driver.close()
        except Exception as e:
            results["requirements"]["neo4j"] = "unavailable"
            results["warnings"].append(f"Neo4j connection failed: {e}")
    
    # Check ChromaDB directory
    if config.storage.chromadb_enabled:
        try:
            config.storage.chromadb.persist_directory.mkdir(parents=True, exist_ok=True)
            results["requirements"]["chromadb"] = "available"
        except Exception as e:
            results["requirements"]["chromadb"] = "unavailable"
            results["errors"].append(f"ChromaDB directory creation failed: {e}")
    
    # Check disk space
    import shutil
    try:
        total, used, free = shutil.disk_usage(config.data_dir)
        free_gb = free / (1024**3)
        if free_gb < 1:
            results["errors"].append(f"Insufficient disk space: {free_gb:.1f}GB free")
        elif free_gb < 5:
            results["warnings"].append(f"Low disk space: {free_gb:.1f}GB free")
        results["requirements"]["disk_space_gb"] = f"{free_gb:.1f}"
    except Exception as e:
        results["warnings"].append(f"Disk space check failed: {e}")
    
    # Set overall status
    if results["errors"]:
        results["status"] = "error"
    elif results["warnings"]:
        results["status"] = "warning"
    
    return results


# =============================================================================
# Environment Configuration
# =============================================================================

def setup_environment(config: GraphRAGConfig) -> None:
    """
    Set up the environment based on configuration.
    
    Args:
        config: GraphRAGConfig instance
    """
    # Set up logging
    import logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logs_dir / "graphrag.log"),
            logging.StreamHandler()
        ]
    )
    
    # Create directories
    config.data_dir.mkdir(parents=True, exist_ok=True)
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    config.logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    os.environ['GRAPHRAG_ENVIRONMENT'] = config.environment
    os.environ['GRAPHRAG_DEBUG'] = str(config.debug)
    os.environ['OLLAMA_BASE_URL'] = config.model.ollama_base_url
    
    logger.info(f"Environment setup complete for {config.environment} profile")


# =============================================================================
# Export Configuration Classes
# =============================================================================

__all__ = [
    # Configuration classes
    'GraphRAGConfig',
    'ProcessingConfig',
    'StorageConfig',
    'ModelConfig',
    'CitationConfig',
    'KnowledgeGraphConfig',
    'ChromaDBConfig',
    'Neo4jConfig',
    
    # Utility functions
    'create_config',
    'validate_system_requirements',
    'setup_environment',
]