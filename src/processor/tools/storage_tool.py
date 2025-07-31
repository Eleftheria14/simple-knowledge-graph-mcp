"""Neo4j storage integration tool for LangGraph"""
from typing import Dict, Any, List
from langchain_core.tools import tool

# Import existing storage classes
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from storage.neo4j import Neo4jStorage

@tool
def store_in_neo4j(
    entities: List[Dict[str, Any]], 
    relationships: List[Dict[str, Any]], 
    text_chunks: List[Dict[str, Any]],
    document_info: Dict[str, Any]
) -> str:
    """
    Store extracted entities, relationships, and text chunks in Neo4j knowledge graph.
    
    Args:
        entities: List of entity dictionaries with name, type, properties
        relationships: List of relationship dictionaries with source, target, type
        text_chunks: List of text chunks for vector storage
        document_info: Document metadata (title, type, path, etc.)
        
    Returns:
        Status message about storage operation
    """
    try:
        # Initialize storage (reuse existing MCP storage logic)
        neo4j_storage = Neo4jStorage()
        
        stored_entities = 0
        stored_relationships = 0  
        stored_vectors = 0
        
        print(f"💾 Storing {len(entities)} entities, {len(relationships)} relationships, {len(text_chunks)} text chunks...")
        
        # Store entities using the correct method
        try:
            entity_result = neo4j_storage.store_entities(entities, document_info)
            stored_entities = entity_result.get('entities_created', 0)
            stored_relationships = entity_result.get('relationships_created', 0)
        except Exception as e:
            print(f"Warning: Failed to store entities: {e}")
        
        # Store text vectors
        for i, chunk in enumerate(text_chunks):
            try:
                vector_id = f"{document_info.get('title', 'doc')}_{i}"
                result = neo4j_storage.store_text_vector(
                    content=chunk.get('content', ''),
                    vector_id=vector_id,
                    metadata={
                        **document_info,
                        'chunk_index': i,
                        'chunk_size': len(chunk.get('content', '')),
                        'document_id': document_info.get('id', 'unknown'),
                        'document_title': document_info.get('title', 'unknown'),
                        'vector_type': 'text_chunk',
                        'stored_at': document_info.get('created', 'unknown')
                    }
                )
                if result.get('success'):
                    stored_vectors += 1
            except Exception as e:
                print(f"Warning: Failed to store text chunk {i}: {e}")
        
        success_message = (
            f"✅ Successfully stored: {stored_entities} entities, "
            f"{stored_relationships} relationships, {stored_vectors} text vectors"
        )
        
        print(success_message)
        return success_message
        
    except Exception as e:
        error_message = f"❌ Error storing in Neo4j: {str(e)}"
        print(error_message)
        return error_message

# Test function
def test_storage_tool():
    """Test the Neo4j storage tool"""
    print("Neo4j storage tool created successfully")
    print("Tool name:", store_in_neo4j.name)
    print("Tool description:", store_in_neo4j.description)
    
    # Test with sample data
    sample_entities = [
        {"id": "test_entity", "name": "Test Entity", "type": "concept", "confidence": 0.9}
    ]
    sample_relationships = []
    sample_chunks = [
        {"content": "This is a test chunk of text for storage."}
    ]
    sample_doc_info = {"title": "Test Document", "type": "test"}
    
    try:
        result = store_in_neo4j(sample_entities, sample_relationships, sample_chunks, sample_doc_info)
        print("Test result:", result)
    except Exception as e:
        print("Test error (expected without Neo4j connection):", e)

if __name__ == "__main__":
    test_storage_tool()