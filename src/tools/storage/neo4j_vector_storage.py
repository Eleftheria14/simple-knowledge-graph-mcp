"""Neo4j vector storage tool for LangChain agents."""
from typing import List, Dict, Any
import uuid
from datetime import datetime
from langchain_core.tools import tool

from storage.neo4j import Neo4jStorage

@tool
def store_vectors(content: str, document_info: Dict[str, Any], chunk_size: int = 500, overlap: int = 50) -> Dict[str, Any]:
    """
    Store text content as searchable vectors in Neo4j knowledge graph.
    
    Automatically chunks long content and generates embeddings for semantic search.
    
    Args:
        content: Text content to store and embed
        document_info: Document metadata (title, type, path, etc.)
        chunk_size: Size of text chunks (default: 500 characters)
        overlap: Overlap between chunks (default: 50 characters)
        
    Returns:
        Dictionary with storage results and vector count
    """
    try:
        print(f"📦 Storing vectors for document: {document_info.get('title', 'Unknown')}")
        print(f"📊 Content length: {len(content)} chars, chunk size: {chunk_size}")
        
        # Initialize Neo4j storage
        neo4j_storage = Neo4jStorage()
        
        # Generate document ID if not provided
        document_id = document_info.get('id', str(uuid.uuid4()))
        document_title = document_info.get('title', 'Unknown Document')
        document_type = document_info.get('type', 'document')
        document_path = document_info.get('path', '')
        
        # Chunk the content
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at word boundaries
            if end < len(content):
                # Look for last space within next 50 chars to avoid breaking words
                space_pos = content.rfind(' ', end, min(end + 50, len(content)))
                if space_pos > start:
                    end = space_pos
            
            chunk_text = content[start:end].strip()
            if chunk_text:  # Only add non-empty chunks
                chunk_id += 1
                chunks.append({
                    'id': f"chunk_{chunk_id}",
                    'content': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'chunk_number': chunk_id
                })
            
            # Move start position with overlap
            start = max(start + 1, end - overlap)
        
        print(f"📄 Created {len(chunks)} text chunks")
        
        # Store each chunk as a vector in Neo4j
        stored_count = 0
        failed_count = 0
        
        for chunk in chunks:
            vector_id = f"{document_id}_{chunk['id']}"
            
            # Prepare metadata for this chunk
            metadata = {
                'document_id': document_id,
                'document_title': document_title,
                'document_type': document_type,
                'document_path': document_path,
                'chunk_id': chunk['id'],
                'chunk_number': chunk['chunk_number'],
                'start_position': chunk['start_pos'],
                'end_position': chunk['end_pos'],
                'chunk_size': len(chunk['content']),
                'stored_at': datetime.now().isoformat(),
                'vector_type': 'text_chunk'
            }
            
            # Store in Neo4j with automatic embedding generation
            try:
                result = neo4j_storage.store_text_vector(
                    content=chunk['content'],
                    vector_id=vector_id,
                    metadata=metadata
                )
                
                if result.get('success'):
                    stored_count += 1
                    print(f"  ✅ Stored chunk {chunk['chunk_number']}: {len(chunk['content'])} chars")
                else:
                    failed_count += 1
                    print(f"  ❌ Failed chunk {chunk['chunk_number']}: {result.get('error', 'Unknown error')}")
                    
            except Exception as chunk_error:
                failed_count += 1
                print(f"  ❌ Exception storing chunk {chunk['chunk_number']}: {chunk_error}")
        
        success_rate = stored_count / len(chunks) if chunks else 0
        
        result = {
            'success': stored_count > 0,
            'message': f"Stored {stored_count}/{len(chunks)} text chunks as vectors",
            'document_id': document_id,
            'document_title': document_title,
            'total_chunks': len(chunks),
            'chunks_stored': stored_count,
            'chunks_failed': failed_count,
            'success_rate': round(success_rate, 2),
            'chunk_size': chunk_size,
            'overlap': overlap,
            'content_length': len(content)
        }
        
        if stored_count > 0:
            print(f"✅ Vector storage completed: {stored_count} chunks stored")
        else:
            print(f"❌ Vector storage failed: no chunks stored successfully")
            
        return result
        
    except Exception as e:
        print(f"❌ Error in store_vectors: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to store vectors in Neo4j',
            'chunks_stored': 0,
            'chunks_failed': 0
        }

def register_vector_storage_tools(mcp, neo4j_storage: 'Neo4jStorage'):
    """Register vector storage tools with MCP server (for backwards compatibility)"""
    
    @mcp.tool()
    def store_vectors_mcp(
        content: str,
        document_info: Dict[str, Any], 
        chunk_size: int = 500,
        overlap: int = 50
    ) -> Dict[str, Any]:
        """MCP wrapper for store_vectors tool"""
        return store_vectors.invoke({
            'content': content,
            'document_info': document_info,
            'chunk_size': chunk_size,
            'overlap': overlap
        })