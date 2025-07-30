"""
Enhanced configuration combining knowledge graph and DocsGPT patterns.

This module extends our simple config with DocsGPT's structured approach
while maintaining our knowledge graph focus.
"""
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class KnowledgeGraphSettings(BaseSettings):
    """Enhanced settings for knowledge graph system."""
    
    # === Core Knowledge Graph Settings ===
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j" 
    NEO4J_PASSWORD: str = "password"
    
    CHROMADB_PATH: str = "./chroma_db"
    CHROMADB_COLLECTION: str = "knowledge_graph"
    
    # === Embedding Configuration (DocsGPT Compatible) ===
    EMBEDDINGS_NAME: str = "huggingface_sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"  # Direct model name
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DIMENSION: int = 768  # MPNet dimension
    
    # === Processing Settings ===
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_ENTITIES_PER_DOCUMENT: int = 100
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # === Citation and Quality ===
    CITATION_STYLES: list = ["APA", "IEEE", "Nature", "MLA"]
    DEFAULT_CITATION_STYLE: str = "APA"
    MIN_CITATION_QUALITY: float = 0.6
    
    # === Integration Settings ===
    N8N_BASE_URL: str = "http://localhost:5678"
    MCP_SERVER_PORT: int = 3001
    DOCSGPT_API_URL: str = "http://localhost:7091"
    
    # === LLM Configuration (for future use) ===
    LLM_PROVIDER: str = "knowledge_graph"  # Custom provider
    DEFAULT_MAX_HISTORY: int = 150
    MAX_RESULTS_PER_QUERY: int = 10
    
    # === Storage Configuration ===
    STORAGE_TYPE: str = "hybrid"  # neo4j + chromadb
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24
    
    # === Security ===
    API_KEY_REQUIRED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = KnowledgeGraphSettings()

# Compatibility functions for existing code
def get_neo4j_config() -> Dict[str, str]:
    """Get Neo4j connection configuration."""
    return {
        "uri": settings.NEO4J_URI,
        "username": settings.NEO4J_USERNAME, 
        "password": settings.NEO4J_PASSWORD
    }

def get_embedding_config() -> Dict[str, Any]:
    """Get embedding configuration."""
    return {
        "model_name": settings.EMBEDDING_MODEL,
        "embeddings_name": settings.EMBEDDINGS_NAME,
        "batch_size": settings.EMBEDDING_BATCH_SIZE,
        "dimension": settings.EMBEDDING_DIMENSION
    }

def get_chromadb_config() -> Dict[str, str]:
    """Get ChromaDB configuration."""
    return {
        "path": settings.CHROMADB_PATH,
        "collection": settings.CHROMADB_COLLECTION
    }