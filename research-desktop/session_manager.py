#!/usr/bin/env python3
"""
Session management for PDF processing sessions.
Stores session metadata and manages session persistence.
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

# Import the existing storage classes
from storage.neo4j.storage import Neo4jStorage

class SessionManager:
    def __init__(self):
        self.neo4j_storage = Neo4jStorage()
    
    def create_session(self, session_name: str = None) -> Dict[str, Any]:
        """
        Create a new processing session.
        
        Args:
            session_name: Optional custom session name
            
        Returns:
            Dict with session info
        """
        try:
            session_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # Generate session name if not provided
            if not session_name:
                session_name = f"Session {timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            session_data = {
                "id": session_id,
                "name": session_name,
                "created": timestamp.isoformat(),
                "last_updated": timestamp.isoformat(),
                "document_count": 0,
                "processing_count": 0,
                "status": "active"
            }
            
            # Store session in Neo4j
            with self.neo4j_storage.driver.session() as db_session:
                db_session.run("""
                    CREATE (s:ProcessingSession {
                        id: $id,
                        name: $name,
                        created: datetime($created),
                        last_updated: datetime($last_updated),
                        document_count: $document_count,
                        processing_count: $processing_count,
                        status: $status
                    })
                """, **session_data)
            
            print(f"✅ Created session: {session_name} ({session_id})")
            return {
                "success": True,
                "session": session_data
            }
            
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all processing sessions ordered by last_updated.
        
        Returns:
            List of session dictionaries
        """
        try:
            with self.neo4j_storage.driver.session() as db_session:
                result = db_session.run("""
                    MATCH (s:ProcessingSession)
                    OPTIONAL MATCH (s)-[:CONTAINS]->(d:Document)
                    RETURN s,
                           count(d) as actual_document_count
                    ORDER BY s.last_updated DESC
                """)
                
                sessions = []
                for record in result:
                    session_node = record["s"]
                    actual_count = record["actual_document_count"]
                    
                    session_data = {
                        "id": session_node["id"],
                        "name": session_node["name"],
                        "created": session_node["created"].isoformat() if session_node["created"] else "",
                        "last_updated": session_node["last_updated"].isoformat() if session_node["last_updated"] else "",
                        "document_count": actual_count,
                        "processing_count": session_node.get("processing_count", 0),
                        "status": session_node.get("status", "active")
                    }
                    sessions.append(session_data)
                
                return sessions
                
        except Exception as e:
            print(f"❌ Error loading sessions: {e}")
            return []
    
    def get_session_documents(self, session_id: str, lightweight: bool = False) -> List[Dict[str, Any]]:
        """
        Get all documents in a specific session.
        
        Args:
            session_id: Session ID
            lightweight: If True, returns minimal data for list view performance
            
        Returns:
            List of document dictionaries
        """
        try:
            with self.neo4j_storage.driver.session() as db_session:
                if lightweight:
                    # Lightweight query for list view - no full_text, minimal references/figures/tables
                    result = db_session.run("""
                        MATCH (s:ProcessingSession {id: $session_id})-[:CONTAINS]->(d:Document)
                        RETURN d.id as id,
                               d.title as title,
                               d.file_name as file_name,
                               d.path as path,
                               d.original_path as original_path,
                               d.original_filename as original_filename,
                               d.file_renamed as file_renamed,
                               d.created as created,
                               d.success as success,
                               d.error as error,
                               d.content_length as content_length,
                               d.abstract as abstract,
                               d.authors as authors,
                               d.keywords as keywords,
                               d.references_count as references_count,
                               d.figures_count as figures_count,
                               d.tables_count as tables_count
                        ORDER BY d.created DESC
                    """, session_id=session_id)
                    
                    documents = []
                    for record in result:
                        # Convert datetime objects to ISO strings
                        created_str = ""
                        if record.get("created"):
                            if hasattr(record["created"], 'isoformat'):
                                created_str = record["created"].isoformat()
                            else:
                                created_str = str(record["created"])
                        
                        documents.append({
                            "id": record["id"],
                            "title": record.get("title", "Untitled"),
                            "file_name": record.get("file_name", ""),
                            "path": record.get("path", ""),
                            "original_path": record.get("original_path"),
                            "original_filename": record.get("original_filename"),
                            "file_renamed": record.get("file_renamed", False),
                            "created": created_str,
                            "success": record.get("success", False),
                            "error": record.get("error", ""),
                            "content_length": record.get("content_length", 0),
                            "full_text": "",  # Empty for performance
                            "abstract": record.get("abstract", ""),
                            "authors": record.get("authors", []),
                            "keywords": record.get("keywords", []),
                            "references_count": record.get("references_count", 0),
                            "figures_count": record.get("figures_count", 0),
                            "tables_count": record.get("tables_count", 0),
                            "references": [],  # Empty for performance
                            "figures": [],     # Empty for performance
                            "tables": []       # Empty for performance
                        })
                    
                    return documents
                else:
                    # Full query with all data
                    result = db_session.run("""
                        MATCH (s:ProcessingSession {id: $session_id})-[:CONTAINS]->(d:Document)
                        OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                        OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                        OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                        RETURN d,
                               collect(DISTINCT r) as references,
                               collect(DISTINCT f) as figures,
                               collect(DISTINCT t) as tables
                        ORDER BY d.created DESC
                    """, session_id=session_id)
                
                documents = []
                for record in result:
                    doc = record["d"]
                    references = [dict(r) for r in record["references"] if r is not None]
                    figures = [dict(f) for f in record["figures"] if f is not None]
                    tables = [dict(t) for t in record["tables"] if t is not None]
                    
                    # Convert datetime objects to ISO strings
                    created_str = ""
                    if doc.get("created"):
                        if hasattr(doc["created"], 'isoformat'):
                            created_str = doc["created"].isoformat()
                        else:
                            created_str = str(doc["created"])
                    
                    documents.append({
                        "id": doc["id"],
                        "title": doc.get("title", "Untitled"),
                        "file_name": doc.get("file_name", ""),
                        "path": doc.get("path", ""),
                        "original_path": doc.get("original_path"),
                        "original_filename": doc.get("original_filename"),
                        "file_renamed": doc.get("file_renamed", False),
                        "created": created_str,
                        "success": doc.get("success", False),
                        "error": doc.get("error", ""),
                        "content_length": doc.get("content_length", 0),
                        "full_text": doc.get("full_text", ""),
                        "abstract": doc.get("abstract", ""),
                        "authors": doc.get("authors", []),
                        "keywords": doc.get("keywords", []),
                        "references_count": doc.get("references_count", 0),
                        "figures_count": doc.get("figures_count", 0),
                        "tables_count": doc.get("tables_count", 0),
                        "references": references,
                        "figures": figures,
                        "tables": tables
                    })
                
                return documents
                
        except Exception as e:
            print(f"❌ Error loading session documents: {e}")
            return []
    
    def add_document_to_session(self, session_id: str, document_id: str) -> Dict[str, Any]:
        """
        Add a document to a session.
        
        Args:
            session_id: Session ID
            document_id: Document ID
            
        Returns:
            Dict with operation status
        """
        try:
            with self.neo4j_storage.driver.session() as db_session:
                # Create relationship between session and document
                db_session.run("""
                    MATCH (s:ProcessingSession {id: $session_id})
                    MATCH (d:Document {id: $document_id})
                    MERGE (s)-[:CONTAINS]->(d)
                    SET s.last_updated = datetime()
                """, session_id=session_id, document_id=document_id)
                
                # Update document count
                db_session.run("""
                    MATCH (s:ProcessingSession {id: $session_id})
                    MATCH (s)-[:CONTAINS]->(d:Document)
                    WITH s, count(d) as doc_count
                    SET s.document_count = doc_count
                """, session_id=session_id)
            
            return {"success": True}
            
        except Exception as e:
            print(f"❌ Error adding document to session: {e}")
            return {"success": False, "error": str(e)}
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update session metadata.
        
        Args:
            session_id: Session ID
            updates: Dictionary of fields to update
            
        Returns:
            Dict with operation status
        """
        try:
            # Build SET clause dynamically
            set_clauses = ["s.last_updated = datetime()"]
            params = {"session_id": session_id}
            
            for key, value in updates.items():
                if key in ["name", "status"]:
                    set_clauses.append(f"s.{key} = ${key}")
                    params[key] = value
            
            query = f"""
                MATCH (s:ProcessingSession {{id: $session_id}})
                SET {', '.join(set_clauses)}
                RETURN s
            """
            
            with self.neo4j_storage.driver.session() as db_session:
                result = db_session.run(query, **params)
                if result.single():
                    return {"success": True}
                else:
                    return {"success": False, "error": "Session not found"}
            
        except Exception as e:
            print(f"❌ Error updating session: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_session(self, session_id: str, delete_documents: bool = False) -> Dict[str, Any]:
        """
        Delete a session and optionally its documents.
        
        Args:
            session_id: Session ID
            delete_documents: Whether to delete associated documents
            
        Returns:
            Dict with operation status
        """
        try:
            with self.neo4j_storage.driver.session() as db_session:
                if delete_documents:
                    # Delete session and all associated documents
                    result = db_session.run("""
                        MATCH (s:ProcessingSession {id: $session_id})
                        OPTIONAL MATCH (s)-[:CONTAINS]->(d:Document)
                        OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                        OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                        OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                        DETACH DELETE s, d, r, f, t
                        RETURN count(d) as deleted_docs
                    """, session_id=session_id)
                    
                    record = result.single()
                    deleted_docs = record["deleted_docs"] if record else 0
                    
                    # Also delete text vectors
                    db_session.run("""
                        MATCH (v:TextVector {vector_type: 'grobid_content'})
                        WHERE v.document_id IN [d_id IN ['session_' + $session_id] | d_id]
                        DELETE v
                    """, session_id=session_id)
                    
                    return {
                        "success": True,
                        "deleted_documents": deleted_docs,
                        "message": f"Deleted session and {deleted_docs} documents"
                    }
                else:
                    # Delete only session, keep documents
                    db_session.run("""
                        MATCH (s:ProcessingSession {id: $session_id})
                        DETACH DELETE s
                    """, session_id=session_id)
                    
                    return {
                        "success": True,
                        "deleted_documents": 0,
                        "message": "Deleted session, kept documents"
                    }
            
        except Exception as e:
            print(f"❌ Error deleting session: {e}")
            return {"success": False, "error": str(e)}
    
    def get_document_details(self, document_id: str) -> Dict[str, Any]:
        """
        Get full details for a specific document including full text and all relations.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dict with full document details
        """
        try:
            with self.neo4j_storage.driver.session() as db_session:
                result = db_session.run("""
                    MATCH (d:Document {id: $document_id})
                    OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                    OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                    OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                    RETURN d,
                           collect(DISTINCT r) as references,
                           collect(DISTINCT f) as figures,
                           collect(DISTINCT t) as tables
                """, document_id=document_id)
                
                record = result.single()
                if not record:
                    return {"success": False, "error": "Document not found"}
                
                doc = record["d"]
                references = [dict(r) for r in record["references"] if r is not None]
                figures = [dict(f) for f in record["figures"] if f is not None]
                tables = [dict(t) for t in record["tables"] if t is not None]
                
                return {
                    "success": True,
                    "title": doc.get("title", "Untitled"),
                    "filePath": doc.get("path", ""),
                    "fullText": doc.get("full_text", ""),
                    "abstract": doc.get("abstract", ""),
                    "authors": doc.get("authors", []),
                    "keywords": doc.get("keywords", []),
                    "content_length": doc.get("content_length", 0),
                    "references": references,
                    "figures": figures,
                    "tables": tables
                }
                
        except Exception as e:
            print(f"❌ Error loading document details: {e}")
            return {"success": False, "error": str(e)}

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a specific document and all its related data.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dict with operation status
        """
        try:
            with self.neo4j_storage.driver.session() as db_session:
                # Delete document and all its relationships and related nodes
                result = db_session.run("""
                    MATCH (d:Document {id: $document_id})
                    OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                    OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                    OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                    DETACH DELETE d, r, f, t
                    RETURN count(d) as deleted_count
                """, document_id=document_id)
                
                record = result.single()
                deleted_count = record["deleted_count"] if record else 0
                
                if deleted_count == 0:
                    return {"success": False, "error": "Document not found"}
                
                # Also delete any text vectors for this document
                db_session.run("""
                    MATCH (v:TextVector)
                    WHERE v.document_id = $document_id
                    DELETE v
                """, document_id=document_id)
                
                return {
                    "success": True,
                    "message": f"Document {document_id} deleted successfully"
                }
                
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python session_manager.py <command> [args]")
        print("Commands:")
        print("  create [session_name]")
        print("  list")
        print("  get <session_id>")
        print("  add <session_id> <document_id>")
        print("  update <session_id> <field=value> [field=value...]")
        print("  delete <session_id> [--with-docs]")
        print("  get-details <document_id>")
        sys.exit(1)
    
    manager = SessionManager()
    command = sys.argv[1]
    
    if command == "create":
        session_name = sys.argv[2] if len(sys.argv) > 2 else None
        result = manager.create_session(session_name)
        print(json.dumps(result, indent=2))
    
    elif command == "list":
        sessions = manager.get_all_sessions()
        print(json.dumps(sessions, indent=2))
    
    elif command == "get" and len(sys.argv) >= 3:
        session_id = sys.argv[2]
        documents = manager.get_session_documents(session_id)
        print(json.dumps(documents, indent=2))
    
    elif command == "add" and len(sys.argv) >= 4:
        session_id = sys.argv[2]
        document_id = sys.argv[3]
        result = manager.add_document_to_session(session_id, document_id)
        print(json.dumps(result, indent=2))
    
    elif command == "update" and len(sys.argv) >= 4:
        session_id = sys.argv[2]
        updates = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                key, value = arg.split("=", 1)
                updates[key] = value
        result = manager.update_session(session_id, updates)
        print(json.dumps(result, indent=2))
    
    elif command == "delete" and len(sys.argv) >= 3:
        session_id = sys.argv[2]
        delete_docs = "--with-docs" in sys.argv
        result = manager.delete_session(session_id, delete_docs)
        print(json.dumps(result, indent=2))
    
    elif command == "get-details" and len(sys.argv) >= 3:
        document_id = sys.argv[2]
        result = manager.get_document_details(document_id)
        print(json.dumps(result, indent=2))
    
    else:
        print("Invalid command or arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()