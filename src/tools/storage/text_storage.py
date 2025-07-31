"""Text storage tool for MCP knowledge graph using Neo4j vector storage."""
from typing import List, Dict, Any
import uuid
from datetime import datetime
from fastmcp import FastMCP
from pydantic import BaseModel

from storage.neo4j import Neo4jStorage

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
    """Represents any type of data to be stored as vectors in Neo4j.
    
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
    
def register_text_tools(mcp: FastMCP, neo4j_storage: Neo4jStorage):
    """Register vector storage tools with the MCP server."""
    
    @mcp.tool()
    def store_vectors(
        vectors: List[VectorData],
        document_info: DocumentInfo
    ) -> Dict[str, Any]:
        """
        Store any type of content as vectors in Neo4j.
        
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
            
            # Store vectors in Neo4j with embeddings
            stored_count = 0
            for vector in vectors:
                vector_id = f"{document_info.id}_{vector.id}"
                
                # Prepare metadata
                metadata = {
                    "document_id": document_info.id,
                    "document_title": document_info.title,
                    "document_type": document_info.type,
                    "vector_type": vector.type,
                    "vector_id": vector.id,
                    "stored_at": datetime.now().isoformat(),
                    **vector.properties
                }
                
                # Store vector in Neo4j (will handle embedding generation)
                result = neo4j_storage.store_text_vector(
                    content=vector.content,
                    vector_id=vector_id,
                    metadata=metadata
                )
                
                if result.get("success"):
                    stored_count += 1
            
            return {
                "success": True,
                "message": f"Stored {stored_count} vectors of types: {set(v.type for v in vectors)}",
                "document_id": document_info.id,
                "vectors_stored": stored_count,
                "vector_types": list(set(v.type for v in vectors))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store vectors"
            }