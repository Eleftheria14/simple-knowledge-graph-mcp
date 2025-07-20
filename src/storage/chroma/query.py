"""ChromaDB query manager for semantic search and retrieval."""
from typing import List, Dict, Any
from storage.embedding import EmbeddingService
from .client import get_shared_chromadb_client

class ChromaDBQuery:
    """Handle query operations in ChromaDB with semantic search."""
    
    def __init__(self):
        """Initialize ChromaDB using shared client and embedding service."""
        self.client, self.collection = get_shared_chromadb_client()
        self.embedding_service = EmbeddingService()
        print(f"🔍 ChromaDBQuery initialized with collection ID: {self.collection.id}")
    
    def query_similar_text(
        self, 
        query: str, 
        n_results: int = 5,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Query similar text using semantic search."""
        # Get fresh collection reference to avoid stale cache
        _, collection = get_shared_chromadb_client()
        
        # Generate query embedding
        query_embedding = self.embedding_service.encode_text(query)
        
        # Search ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            include=["documents", "metadatas", "distances"] if include_metadata else ["documents"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            result = {
                "text": results["documents"][0][i],
                "distance": results["distances"][0][i],
            }
            if include_metadata and results["metadatas"]:
                result["metadata"] = results["metadatas"][0][i]
            formatted_results.append(result)
        
        return formatted_results
    
    def get_citations_for_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get citations related to a specific topic."""
        results = self.query_similar_text(topic, n_results=limit)
        
        citations = []
        for result in results:
            metadata = result.get("metadata", {})
            result_citations = metadata.get("citations", [])
            for citation in result_citations:
                if citation not in citations:  # Avoid duplicates
                    citations.append({
                        **citation,
                        "relevance_score": 1 - result["distance"],  # Convert distance to relevance
                        "context": result["text"][:200] + "..."
                    })
        
        return citations[:limit]