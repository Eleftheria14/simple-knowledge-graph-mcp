"""Shared ChromaDB client to ensure single database instance."""
import chromadb
from chromadb.config import Settings
import config
import os

# Global shared client instance
_shared_client = None
_shared_collection = None

def get_shared_chromadb_client():
    """Get a shared ChromaDB client instance with robust error handling and UUID prevention."""
    global _shared_client, _shared_collection
    
    if _shared_client is None:
        try:
            # Ensure ChromaDB directory exists with proper permissions
            os.makedirs(config.CHROMADB_PATH, mode=0o755, exist_ok=True)
            
            # Use absolute path
            absolute_path = os.path.abspath(config.CHROMADB_PATH)
            
            # Verify directory is writable
            if not os.access(absolute_path, os.W_OK):
                raise PermissionError(f"ChromaDB directory not writable: {absolute_path}")
            
            # Allow ChromaDB to manage its own UUID directories
            # Removing UUID directories can cause "unable to open database file" errors
            
            # Create client with modern ChromaDB configuration
            _shared_client = chromadb.PersistentClient(
                path=absolute_path
            )
            
            # Always use get_or_create_collection for consistent collection reference
            _shared_collection = _shared_client.get_or_create_collection(
                name=config.CHROMADB_COLLECTION
            )
            
            # Get document count (don't fail if this has issues)
            try:
                count = _shared_collection.count()
            except Exception:
                count = 0  # Collection exists but count failed - that's ok
            
            # Add instance tracking for debugging
            client_id = id(_shared_client)
            collection_id = id(_shared_collection)
            
            print(f"🔧 ChromaDB Shared Client Initialized:")
            print(f"   Path: {absolute_path}")
            print(f"   Collection: {_shared_collection.name} (ID: {_shared_collection.id})")
            print(f"   Client instance ID: {client_id}")
            print(f"   Collection instance ID: {collection_id}")
            print(f"   Document count: {count}")
            print(f"   Directory contents: {os.listdir(absolute_path)}")
            
        except Exception as e:
            print(f"❌ ChromaDB initialization failed: {e}")
            print(f"   Path attempted: {config.CHROMADB_PATH}")
            print(f"   Path exists: {os.path.exists(config.CHROMADB_PATH)}")
            print(f"   Path writable: {os.access(config.CHROMADB_PATH, os.W_OK) if os.path.exists(config.CHROMADB_PATH) else 'N/A'}")
            
            # Reset globals on failure
            _shared_client = None
            _shared_collection = None
            raise
    
    return _shared_client, _shared_collection

def reset_shared_client():
    """Reset the shared client (used for testing or clearing)."""
    global _shared_client, _shared_collection
    
    # Simply reset client references without deleting UUID directories
    # ChromaDB manages these directories and deleting them causes database errors
    _shared_client = None
    _shared_collection = None