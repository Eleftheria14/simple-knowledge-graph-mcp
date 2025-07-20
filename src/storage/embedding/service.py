"""Local embedding service using sentence-transformers."""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import config

class EmbeddingService:
    """Generate embeddings locally without API calls."""
    
    def __init__(self):
        """Initialize embedding model."""
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts, 
            batch_size=config.EMBEDDING_BATCH_SIZE,
            show_progress_bar=False
        )
        return embeddings
    
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text."""
        return self.encode_texts([text])[0]