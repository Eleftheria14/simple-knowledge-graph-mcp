#!/usr/bin/env python3
"""
HTTP API server for research-desktop app.
Bridges frontend HTTP requests to existing backend storage and processing tools.
"""
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the backend src directory to Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

# Add current directory for backend utils
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# FastAPI for HTTP server
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import existing backend tools
from storage.neo4j.storage import Neo4jStorage
from storage.neo4j.query import Neo4jQuery
from processor.tools.grobid_tool import grobid_extract
from session_manager import SessionManager

# Initialize storage and session manager
neo4j_storage = Neo4jStorage()
neo4j_query = Neo4jQuery()
session_manager = SessionManager()

app = FastAPI(title="Research Desktop API", version="1.0.0")

# Enable CORS for the Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class DocumentStoreRequest(BaseModel):
    grobid_result: dict
    file_path: str
    session_id: Optional[str] = None

class SessionCreateRequest(BaseModel):
    name: Optional[str] = None

class SessionDeleteRequest(BaseModel):
    delete_documents: bool = False

class GrobidProcessRequest(BaseModel):
    file_path: str

class EntityExtractionRequest(BaseModel):
    extraction_mode: str = "academic"
    chunking_strategy: str = "hierarchical"
    template: Optional[dict] = None

# Document Management Endpoints
@app.post("/api/documents")
async def store_document(request: DocumentStoreRequest):
    """Store a GROBID-processed document."""
    try:
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Extract metadata
        metadata = request.grobid_result.get("metadata", {})
        title = metadata.get("title", "Untitled Document")
        authors = metadata.get("authors", [])
        abstract = metadata.get("abstract", "")
        keywords = metadata.get("keywords", [])
        
        # Extract references, figures, tables with field mapping
        references = metadata.get("references", [])
        if not references:
            references = request.grobid_result.get("citations", [])
        
        figures = metadata.get("figures", [])
        if not figures:
            figures = request.grobid_result.get("figures", [])
            
        tables = metadata.get("tables", [])
        if not tables:
            tables = request.grobid_result.get("tables", [])
        
        content = request.grobid_result.get("content", "")
        
        # Use existing storage function
        from store_grobid_document import store_complete_grobid_result
        
        storage_result = store_complete_grobid_result(
            grobid_result=request.grobid_result,
            file_path=request.file_path,
            rename_file=True
        )
        
        # Add to session if specified
        if request.session_id and storage_result.get("success"):
            try:
                session_manager.add_document_to_session(
                    request.session_id, 
                    storage_result.get("document_id")
                )
            except Exception as e:
                print(f"Warning: Failed to link document to session: {e}")
        
        return {
            "success": storage_result.get("success", False),
            "document_id": storage_result.get("document_id"),
            "stored": storage_result.get("stored", {}),
            "storage_result": storage_result,
            "session_id": request.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def get_documents():
    """Get all documents."""
    try:
        from store_grobid_document import load_grobid_documents
        documents = load_grobid_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents")
async def clear_documents():
    """Clear all documents."""
    try:
        from store_grobid_document import clear_all_grobid_documents
        result = clear_all_grobid_documents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{document_id}")
async def get_document_details(document_id: str):
    """Get details for a specific document."""
    try:
        result = session_manager.get_document_details(document_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document."""
    try:
        result = session_manager.delete_document(document_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Session Management Endpoints
@app.post("/api/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new session."""
    try:
        result = session_manager.create_session(request.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def get_sessions():
    """Get all sessions."""
    try:
        sessions = session_manager.get_all_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}/documents")
async def get_session_documents(session_id: str):
    """Get documents in a specific session."""
    try:
        documents = session_manager.get_session_documents(session_id)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: SessionDeleteRequest):
    """Delete a session."""
    try:
        result = session_manager.delete_session(session_id, request.delete_documents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Processing Endpoints
@app.post("/api/process-grobid")
async def process_grobid(request: GrobidProcessRequest):
    """Process a PDF with GROBID."""
    try:
        result = grobid_extract.invoke({"file_path": request.file_path})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/{document_id}/extract-entities")
async def extract_entities(document_id: str, request: EntityExtractionRequest):
    """Extract entities from a document."""
    try:
        # Get document details
        doc_result = session_manager.get_document_details(document_id)
        
        if not doc_result.get("success"):
            raise HTTPException(status_code=404, detail="Document not found")
        
        full_text = doc_result.get("fullText", "")
        if not full_text:
            raise HTTPException(status_code=400, detail="No document content found")
        
        # For now, return a simple response - full entity extraction would require 
        # the complete LLM integration which is complex
        return {
            "success": True,
            "message": f"Entity extraction requested for document {document_id}",
            "document_id": document_id,
            "extraction_mode": request.extraction_mode,
            "chunking_strategy": request.chunking_strategy,
            "document_length": len(full_text),
            "entities_found": 0,  # Placeholder
            "relationships_found": 0  # Placeholder
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🚀 Starting Research Desktop API Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📖 API docs at: http://localhost:8001/docs")
    print("🔧 Make sure Neo4j is running for storage operations")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")