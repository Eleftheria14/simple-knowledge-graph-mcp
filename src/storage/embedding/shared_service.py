"""Shared embedding service for both DocsGPT and Knowledge Graph systems."""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class SharedEmbeddingService:
    """Singleton embedding service shared between systems."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            # Use the same model as DocsGPT for consistency
            print("🧠 Initializing shared MPNet embedding model...")
            self._model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
            self.dimension = self._model.get_sentence_embedding_dimension()
            print(f"✅ Shared embedding service ready ({self.dimension}D vectors)")
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        if not texts:
            return np.array([])
        
        embeddings = self._model.encode(
            texts, 
            batch_size=32,
            show_progress_bar=False
        )
        return embeddings
    
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text."""
        return self.encode_texts([text])[0]
    
    def embed_query(self, query: str) -> List[float]:
        """DocsGPT-compatible interface."""
        return self.encode_text(query).tolist()
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """DocsGPT-compatible interface."""
        return self.encode_texts(documents).tolist()

# Global instance
shared_embeddings = SharedEmbeddingService()