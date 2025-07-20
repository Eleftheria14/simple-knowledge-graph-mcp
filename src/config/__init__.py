"""Configuration management."""
from .settings import *

# Re-export all settings for clean imports
__all__ = [
    "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD",
    "CHROMADB_PATH", "CHROMADB_COLLECTION", 
    "EMBEDDING_MODEL", "EMBEDDING_BATCH_SIZE",
    "CITATION_STYLES"
]