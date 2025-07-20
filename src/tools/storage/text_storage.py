"""Text storage tool for MCP knowledge graph."""
from typing import List, Dict, Any
import uuid
from datetime import datetime
from fastmcp import FastMCP
from pydantic import BaseModel

from storage.chroma import ChromaDBStorage

# Data models

class DocumentInfo(BaseModel):
    """Metadata about the source document for provenance tracking.
    
    Example:
    {"title": "Machine Learning Review", "type": "research_paper", 
     "path": "/papers/ml_review.pdf"}
    """
    title: str  # Document title or filename
    type: str = "document"  # Document type: research_paper, book, article, etc.
    id: str = None  # Optional unique document ID (auto-generated if not provided)
    path: str = None  # Optional file path or URL

class VectorData(BaseModel):
    """Represents any type of data to be stored as vectors in ChromaDB.
    
    Examples:
    - Entity embeddings: {"id": "transformer_2017", "content": "Transformer Architecture", 
                         "type": "entity", "properties": {"domain": "NLP"}}
    - Text chunks: {"id": "chunk_1", "content": "The transformer model...", 
                   "type": "text_chunk", "properties": {"section": "methodology"}}
    """
    id: str  # Unique identifier
    content: str  # Text content to embed
    type: str  # Type: entity, text_chunk, relationship, concept, etc.
    properties: Dict[str, Any] = {}  # Additional metadata
    
def register_text_tools(mcp: FastMCP, chromadb_storage: ChromaDBStorage):
    """Register vector storage tools with the MCP server."""
    
    @mcp.tool()
    def store_vectors(
        vectors: List[VectorData],
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """
        Store any type of content as vectors in ChromaDB.
        
        Args:
            vectors: List of content items to embed and store
            document_info: Document metadata for provenance tracking
        
        Returns:
            Success status and counts of stored vectors
        """
        try:
            # Generate document ID if not provided
            if not document_info.id:
                document_info.id = str(uuid.uuid4())
            
            # Prepare content for embedding
            contents = [vector.content for vector in vectors]
            vector_ids = [f"{document_info.id}_{vector.id}" for vector in vectors]
            
            # Prepare metadata
            metadatas = []
            for vector in vectors:
                metadata = {
                    "document_id": document_info.id,
                    "document_title": document_info.title,
                    "document_type": document_info.type,
                    "vector_type": vector.type,
                    "vector_id": vector.id,
                    "stored_at": datetime.now().isoformat(),
                    **vector.properties
                }
                metadatas.append(metadata)
            
            # Store in ChromaDB with embeddings
            result = chromadb_storage.store_vectors(
                contents,
                vector_ids,
                metadatas
            )
            
            return {
                "success": True,
                "message": f"Stored {result['vectors_stored']} vectors of types: {set(v.type for v in vectors)}",
                "document_id": result["document_id"],
                **result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store vectors"
            }
    
