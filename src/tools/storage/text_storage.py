"""Text storage tool for MCP knowledge graph."""
from typing import List, Dict, Any
import uuid
from datetime import datetime
from fastmcp import FastMCP
from pydantic import BaseModel

from storage.chroma import ChromaDBStorage
# from utils.coverage_validation import check_coverage_before_storage

# Data models

class DocumentInfo(BaseModel):
    """Metadata about the source document for provenance tracking.
    
    Example:
    {"title": "Machine Learning Review", "type": "research_paper", 
     "path": "/papers/ml_review.pdf", "doi": "10.xxx/xxx"}
    """
    title: str  # Document title or filename
    type: str = "document"  # Document type: research_paper, book, article, etc.
    id: str = None  # Optional unique document ID (auto-generated if not provided)
    path: str = None  # Optional file path or URL
    doi: str = None  # Digital Object Identifier for academic papers
    journal: str = None  # Journal name for academic papers
    year: int = None  # Publication year
    citation_preview: str = None  # Formatted citation preview

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
        vectors: List[Dict[str, Any]],
        document_info: Dict[str, Any]
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
            # Debug: Show collection info at start of storage
            print(f"🔧 store_vectors using collection ID: {chromadb_storage.collection.id}")
            print(f"🔧 Collection name: {chromadb_storage.collection.name}")
            
            # Validate input data format
            if not vectors:
                return {"success": False, "error": "No vectors provided", "message": "Vector list is empty"}
            
            # Generate document ID if not provided
            doc_id = document_info.get('id') or str(uuid.uuid4())
            
            # Validate and prepare content for embedding
            contents = []
            vector_ids = []
            metadatas = []
            
            for i, vector in enumerate(vectors):
                if not isinstance(vector, dict):
                    return {"success": False, "error": f"Vector {i} is not a dict: {type(vector)}", "message": "Invalid vector format"}
                
                # Ensure required fields exist
                if 'id' not in vector or not vector['id']:
                    return {"success": False, "error": f"Vector {i} missing or null 'id' field: {vector}", "message": "Vector ID required"}
                
                if 'content' not in vector or not vector['content']:
                    return {"success": False, "error": f"Vector {i} missing 'content' field: {vector}", "message": "Vector content required"}
                
                contents.append(vector['content'])
                vector_ids.append(f"{doc_id}_{vector['id']}")
                
                # Prepare metadata with enhanced citation info
                metadata = {
                    "document_id": doc_id,
                    "document_title": document_info.get('title', 'Untitled Document'),
                    "document_type": document_info.get('type', 'document'),
                    "vector_type": vector.get('type', 'unknown'),
                    "vector_id": vector['id'],
                    "stored_at": datetime.now().isoformat(),
                    **vector.get('properties', {})
                }
                
                # Add citation metadata if available
                for field in ['doi', 'journal', 'year', 'citation_preview']:
                    if field in document_info and document_info[field] is not None:
                        metadata[field] = document_info[field]
                    
                metadatas.append(metadata)
            
            # Store in ChromaDB with embeddings
            result = chromadb_storage.store_vectors(
                contents,
                vector_ids,
                metadatas
            )
            
            # Prepare response
            vector_types = set(v.get('type', 'unknown') for v in vectors)
            response = {
                "success": True,
                "message": f"Stored {result['vectors_stored']} vectors of types: {vector_types}",
                "document_id": result["document_id"],
                "debug_info": {
                    "collection_id": chromadb_storage.collection.id,
                    "collection_name": chromadb_storage.collection.name,
                    "client_id": id(chromadb_storage.client)
                },
                **result
            }
            
            # Add basic quality note
            if len(vectors) >= 20:
                response["message"] += " ✅ Good chunk quantity for comprehensive coverage."
            elif len(vectors) < 10:
                response["message"] += " ⚠️ NOTICE: Low chunk count - ensure complete paper coverage."
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store vectors"
            }
    
