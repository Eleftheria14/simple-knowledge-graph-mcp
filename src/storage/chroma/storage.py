"""ChromaDB storage manager for text and citations."""
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import config
from storage.embedding import EmbeddingService

class ChromaDBStorage:
    """Handle text storage operations in ChromaDB with embeddings."""
    
    def __init__(self):
        """Initialize ChromaDB and embedding service."""
        self.client = chromadb.PersistentClient(
            path=config.CHROMADB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=config.CHROMADB_COLLECTION
        )
        self.embedding_service = EmbeddingService()
    
    
    def store_vectors(
        self,
        contents: List[str],
        vector_ids: List[str], 
        metadatas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Store any type of content as vectors in ChromaDB."""
        if not contents:
            return {"vectors_stored": 0}
        
        # Generate embeddings for all content
        embeddings = self.embedding_service.encode_texts(contents)
        
        # Store in ChromaDB
        self.collection.add(
            documents=contents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=vector_ids
        )
        
        return {
            "vectors_stored": len(contents),
            "document_id": metadatas[0].get("document_id") if metadatas else None
        }
    
    def clear_collection(self):
        """Clear all data from the collection."""
        self.client.delete_collection(config.CHROMADB_COLLECTION)
        self.collection = self.client.get_or_create_collection(
            name=config.CHROMADB_COLLECTION
        )