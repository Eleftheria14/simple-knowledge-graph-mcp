"""ChromaDB storage manager for text and citations."""
from typing import List, Dict, Any
from storage.embedding.docsgpt_embeddings import KnowledgeGraphEmbeddings
from .client import get_shared_chromadb_client

class ChromaDBStorage:
    """Handle text storage operations in ChromaDB with embeddings."""
    
    def __init__(self):
        """Initialize ChromaDB using shared client and embedding service."""
        self.client, self.collection = get_shared_chromadb_client()
        self.embedding_service = KnowledgeGraphEmbeddings()
        print(f"📝 ChromaDBStorage initialized with collection ID: {self.collection.id}")
        print(f"🧠 Using {self.embedding_service.dimension}D embeddings ({self.embedding_service.model_name})")
    
    
    def store_vectors(
        self,
        contents: List[str],
        vector_ids: List[str], 
        metadatas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Store any type of content as vectors in ChromaDB."""
        if not contents:
            return {"vectors_stored": 0}
        
        # Generate embeddings for all content using DocsGPT's system
        embeddings = self.embedding_service.encode_content(contents)
        
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
        import config
        from .client import reset_shared_client
        
        # Delete the collection
        self.client.delete_collection(config.CHROMADB_COLLECTION)
        
        # Reset the shared client to force recreation
        reset_shared_client()
        
        # Get fresh client and collection
        from .client import get_shared_chromadb_client
        self.client, self.collection = get_shared_chromadb_client()