"""Unified embedding service using DocsGPT's embedding system."""
from typing import List
import numpy as np
import sys
import os

# Add DocsGPT path to import their embedding system
docsgpt_path = os.path.join(os.path.dirname(__file__), "../../../docsgpt-source/application")
sys.path.insert(0, docsgpt_path)

from vectorstore.base import EmbeddingsSingleton
import config

class UnifiedEmbeddingService:
    """Use DocsGPT's embedding system with your knowledge graph."""
    
    def __init__(self):
        """Initialize using DocsGPT's embedding singleton."""
        # Use DocsGPT's MPNet model for higher quality
        self.embeddings = EmbeddingsSingleton.get_instance(
            "huggingface_sentence-transformers/all-mpnet-base-v2"
        )
        self.dimension = self.embeddings.dimension
        print(f"🧠 Unified embedding service initialized with {self.dimension}D vectors")
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts using DocsGPT's system."""
        if not texts:
            return np.array([])
        
        # Use DocsGPT's embedding method
        embeddings = self.embeddings.embed_documents(texts)
        return np.array(embeddings)
    
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text."""
        embedding = self.embeddings.embed_query(text)
        return np.array(embedding)
    
    def encode_query(self, query: str) -> np.ndarray:
        """Generate embedding for search query (alias for consistency)."""
        return self.encode_text(query)