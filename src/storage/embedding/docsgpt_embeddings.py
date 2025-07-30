"""
DocsGPT embedding system extracted for knowledge graph use.

This module contains the embedding classes from DocsGPT, adapted for use
in our knowledge graph system without external dependencies.
"""
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import config

class EmbeddingsWrapper:
    """Wrapper for sentence-transformers models with DocsGPT interface."""
    
    def __init__(self, model_name: str, *args, **kwargs):
        """Initialize sentence transformer model."""
        self.model = SentenceTransformer(
            model_name, 
            config_kwargs={'allow_dangerous_deserialization': True}, 
            *args, 
            **kwargs
        )
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"🧠 Loaded embedding model: {model_name} ({self.dimension}D)")

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query string."""
        return self.model.encode(query).tolist()
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        return self.model.encode(documents).tolist()
    
    def __call__(self, text):
        """Allow direct calling with string or list."""
        if isinstance(text, str):
            return self.embed_query(text)
        elif isinstance(text, list):
            return self.embed_documents(text)
        else:
            raise ValueError("Input must be a string or a list of strings")


class EmbeddingsSingleton:
    """Singleton pattern for managing embedding model instances."""
    
    _instances: Dict[str, EmbeddingsWrapper] = {}

    @staticmethod
    def get_instance(embeddings_name: str, *args, **kwargs) -> EmbeddingsWrapper:
        """Get or create embedding instance."""
        if embeddings_name not in EmbeddingsSingleton._instances:
            EmbeddingsSingleton._instances[embeddings_name] = EmbeddingsSingleton._create_instance(
                embeddings_name, *args, **kwargs
            )
        return EmbeddingsSingleton._instances[embeddings_name]

    @staticmethod
    def _create_instance(embeddings_name: str, *args, **kwargs) -> EmbeddingsWrapper:
        """Factory for creating embedding instances."""
        
        # Predefined model configurations
        embeddings_factory = {
            # High-quality models
            "huggingface_sentence-transformers/all-mpnet-base-v2": 
                lambda: EmbeddingsWrapper("sentence-transformers/all-mpnet-base-v2"),
            "huggingface_sentence-transformers-all-mpnet-base-v2": 
                lambda: EmbeddingsWrapper("sentence-transformers/all-mpnet-base-v2"),
            
            # Lightweight models  
            "huggingface_sentence-transformers/all-MiniLM-L6-v2":
                lambda: EmbeddingsWrapper("sentence-transformers/all-MiniLM-L6-v2"),
                
            # Specialized models
            "huggingface_hkunlp/instructor-large": 
                lambda: EmbeddingsWrapper("hkunlp/instructor-large"),
        }

        if embeddings_name in embeddings_factory:
            return embeddings_factory[embeddings_name](*args, **kwargs)
        else:
            # Default: treat as direct model name
            return EmbeddingsWrapper(embeddings_name, *args, **kwargs)

    @staticmethod
    def clear_instances():
        """Clear all cached instances (useful for testing)."""
        EmbeddingsSingleton._instances.clear()


class KnowledgeGraphEmbeddings:
    """High-level interface for knowledge graph embeddings."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize with specified model or use config default."""
        if model_name is None:
            # Use DocsGPT's high-quality model by default
            model_name = "huggingface_sentence-transformers/all-mpnet-base-v2"
        
        self.embeddings = EmbeddingsSingleton.get_instance(model_name)
        self.model_name = model_name
        
    def encode_entities(self, entities: List[str]) -> List[List[float]]:
        """Generate embeddings for entity names/descriptions."""
        return self.embeddings.embed_documents(entities)
    
    def encode_relationships(self, relationships: List[str]) -> List[List[float]]:
        """Generate embeddings for relationship descriptions."""
        return self.embeddings.embed_documents(relationships)
    
    def encode_content(self, content: List[str]) -> List[List[float]]:
        """Generate embeddings for text content."""
        return self.embeddings.embed_documents(content)
    
    def encode_query(self, query: str) -> List[float]:
        """Generate embedding for search query."""
        return self.embeddings.embed_query(query)
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.embeddings.dimension