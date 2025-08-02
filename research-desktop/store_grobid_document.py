#!/usr/bin/env python3
"""
Store complete GROBID document results in Neo4j using existing storage logic.
This script imports the backend storage implementation to properly store documents.
Includes file renaming functionality based on document metadata.
"""
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime

# Add the backend src directory to Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

# Add current directory for backend utils
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the existing storage classes
from storage.neo4j.storage import Neo4jStorage

# Import file operations utilities
from backend_utils.file_operations import rename_file_with_title

# Import session manager
from session_manager import SessionManager

def store_complete_grobid_result(grobid_result: dict, file_path: str, rename_file: bool = True) -> dict:
    """
    Store the complete GROBID processing result in Neo4j.
    Optionally renames the file based on document metadata.
    
    Args:
        grobid_result: Complete result from GROBID processing
        file_path: Path to the original PDF file
        rename_file: Whether to rename file based on document title
        
    Returns:
        Dict with storage status and details
    """
    try:
        # Initialize Neo4j storage
        neo4j_storage = Neo4jStorage()
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Extract metadata for file renaming
        metadata = grobid_result.get("metadata", {})
        title = metadata.get("title", "")
        authors = metadata.get("authors", [])
        year = metadata.get("year", "")
        
        # Rename file if requested and title is available
        final_file_path = file_path
        rename_result = None
        
        if rename_file and title and title.strip():
            print(f"🏷️  Renaming file based on title: {title[:50]}...")
            rename_result = rename_file_with_title(
                file_path,
                title,
                authors,
                year,
                target_directory=None,  # Keep in same directory
                avoid_conflicts=True
            )
            
            if rename_result.get("success"):
                final_file_path = rename_result["new_path"]
                print(f"✅ File renamed: {Path(final_file_path).name}")
            else:
                print(f"⚠️  File rename failed: {rename_result.get('error', 'Unknown error')}")
                # Continue with original path
        elif not title or not title.strip():
            print("⚠️  No title found, keeping original filename")
        
        # Prepare document info (using final file path after potential rename)
        document_info = {
            "id": doc_id,
            "title": title or "Untitled Document",
            "path": final_file_path,
            "file_name": Path(final_file_path).name,
            "original_path": file_path if final_file_path != file_path else None,
            "original_filename": Path(file_path).name if final_file_path != file_path else None,
            "processing_method": "GROBID",
            "created": datetime.now().isoformat(),
            "success": grobid_result.get("success", False),
            "error": grobid_result.get("error", ""),
            "content_length": len(grobid_result.get("content", "")),
            "metadata": grobid_result.get("metadata", {}),
            "file_renamed": rename_result.get("success", False) if rename_result else False
        }
        
        # Store document node with complete metadata
        with neo4j_storage.driver.session() as session:
            # Extract data arrays first to calculate counts
            references = grobid_result.get("metadata", {}).get("references", [])
            if not references:
                references = grobid_result.get("citations", [])
            
            figures = grobid_result.get("metadata", {}).get("figures", [])
            if not figures:
                figures = grobid_result.get("figures", [])
                
            tables = grobid_result.get("metadata", {}).get("tables", [])
            if not tables:
                tables = grobid_result.get("tables", [])

            # Create comprehensive document node
            session.run("""
                MERGE (d:Document {id: $doc_id})
                SET d.title = $title,
                    d.path = $path,
                    d.file_name = $file_name,
                    d.original_path = $original_path,
                    d.original_filename = $original_filename,
                    d.file_renamed = $file_renamed,
                    d.processing_method = $processing_method,
                    d.created = datetime($created),
                    d.success = $success,
                    d.error = $error,
                    d.content_length = $content_length,
                    d.full_text = $full_text,
                    d.abstract = $abstract,
                    d.keywords = $keywords,
                    d.authors = $authors,
                    d.journal = $journal,
                    d.references_count = $references_count,
                    d.figures_count = $figures_count,
                    d.tables_count = $tables_count
            """, 
                doc_id=doc_id,
                title=document_info["title"],
                path=final_file_path,
                file_name=document_info["file_name"],
                original_path=document_info["original_path"],
                original_filename=document_info["original_filename"],
                file_renamed=document_info["file_renamed"],
                processing_method="GROBID",
                created=document_info["created"],
                success=grobid_result.get("success", False),
                error=grobid_result.get("error", ""),
                content_length=len(grobid_result.get("content", "")),
                full_text=grobid_result.get("content", ""),
                abstract=grobid_result.get("metadata", {}).get("abstract", ""),
                keywords=grobid_result.get("metadata", {}).get("keywords", []),
                authors=[a.get("name", a) if isinstance(a, dict) else a 
                        for a in grobid_result.get("metadata", {}).get("authors", [])],
                journal=(grobid_result.get("metadata", {}).get("journal", "") or 
                        grobid_result.get("metadata", {}).get("venue", "") or 
                        grobid_result.get("metadata", {}).get("publication", "")),
                references_count=len(references),
                figures_count=len(figures),
                tables_count=len(tables)
            )
            
            references_stored = 0
            figures_stored = 0
            tables_stored = 0
            
            # Store references as separate nodes
            for i, ref in enumerate(references):
                ref_id = f"{doc_id}_ref_{i}"
                session.run("""
                    CREATE (r:Reference {
                        id: $ref_id,
                        document_id: $doc_id,
                        index: $index,
                        title: $title,
                        authors: $authors,
                        journal: $journal,
                        year: $year
                    })
                    WITH r
                    MATCH (d:Document {id: $doc_id})
                    CREATE (d)-[:HAS_REFERENCE]->(r)
                """,
                    ref_id=ref_id,
                    doc_id=doc_id,
                    index=i,
                    title=ref.get("title", ""),
                    authors=ref.get("authors", []),
                    journal=ref.get("journal", ""),
                    year=ref.get("year", "")
                )
                references_stored += 1
            
            # Store figures as separate nodes
            for i, figure in enumerate(figures):
                fig_id = f"{doc_id}_fig_{i}"
                session.run("""
                    CREATE (f:Figure {
                        id: $fig_id,
                        document_id: $doc_id,
                        index: $index,
                        caption: $caption,
                        type: $type
                    })
                    WITH f
                    MATCH (d:Document {id: $doc_id})
                    CREATE (d)-[:HAS_FIGURE]->(f)
                """,
                    fig_id=fig_id,
                    doc_id=doc_id,
                    index=i,
                    caption=figure.get("caption", ""),
                    type=figure.get("type", "figure")
                )
                figures_stored += 1
            
            # Store tables as separate nodes
            # Check both metadata.tables and top-level tables field
            tables = grobid_result.get("metadata", {}).get("tables", [])
            if not tables:
                tables = grobid_result.get("tables", [])
            for i, table in enumerate(tables):
                table_id = f"{doc_id}_table_{i}"
                session.run("""
                    CREATE (t:Table {
                        id: $table_id,
                        document_id: $doc_id,
                        index: $index,
                        caption: $caption,
                        content: $content,
                        type: $type
                    })
                    WITH t
                    MATCH (d:Document {id: $doc_id})
                    CREATE (d)-[:HAS_TABLE]->(t)
                """,
                    table_id=table_id,
                    doc_id=doc_id,
                    index=i,
                    caption=table.get("caption", ""),
                    content=table.get("content", ""),
                    type=table.get("type", "table")
                )
                tables_stored += 1
        
        # Store full text as vectors using existing vector storage
        content = grobid_result.get("content", "")
        vectors_stored = 0
        
        if content:
            # Chunk the content for vector storage
            chunk_size = 1000
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunk_content = content[i:i + chunk_size]
                chunks.append({
                    "content": chunk_content,
                    "index": i // chunk_size,
                    "start_pos": i,
                    "end_pos": min(i + chunk_size, len(content))
                })
            
            for chunk in chunks:
                try:
                    vector_id = f"{doc_id}_chunk_{chunk['index']}"
                    result = neo4j_storage.store_text_vector(
                        content=chunk["content"],
                        vector_id=vector_id,
                        metadata={
                            **document_info,
                            "chunk_index": chunk["index"],
                            "start_pos": chunk["start_pos"],
                            "end_pos": chunk["end_pos"],
                            "vector_type": "grobid_content"
                        }
                    )
                    if result.get("success"):
                        vectors_stored += 1
                except Exception as e:
                    print(f"Warning: Failed to store vector chunk {chunk['index']}: {e}")
        
        result = {
            "success": True,
            "document_id": doc_id,
            "stored": {
                "document": 1,
                "references": references_stored,
                "figures": figures_stored,
                "tables": tables_stored,
                "text_vectors": vectors_stored
            },
            "file_rename": rename_result if rename_result else {"success": False, "message": "No rename attempted"},
            "metadata": document_info
        }
        
        print(f"✅ Stored complete GROBID result: {document_info['file_name']}")
        print(f"   📄 Document: {document_info['title']}")
        print(f"   📚 References: {references_stored}")
        print(f"   🖼️  Figures: {figures_stored}")
        print(f"   📊 Tables: {tables_stored}")
        print(f"   🔍 Text vectors: {vectors_stored}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error storing GROBID result: {e}")
        return {
            "success": False,
            "error": str(e),
            "document_id": None
        }

def load_grobid_documents() -> list:
    """
    Load all stored GROBID documents from Neo4j.
    
    Returns:
        List of document dictionaries
    """
    try:
        neo4j_storage = Neo4jStorage()
        
        with neo4j_storage.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)
                WHERE d.processing_method = 'GROBID'
                OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                RETURN d,
                       collect(DISTINCT r) as references,
                       collect(DISTINCT f) as figures,
                       collect(DISTINCT t) as tables
                ORDER BY d.created DESC
            """)
            
            documents = []
            for record in result:
                doc = record["d"]
                references = [dict(r) for r in record["references"] if r is not None]
                figures = [dict(f) for f in record["figures"] if f is not None]
                tables = [dict(t) for t in record["tables"] if t is not None]
                
                documents.append({
                    "id": doc["id"],
                    "title": doc.get("title", "Untitled"),
                    "file_name": doc.get("file_name", ""),
                    "path": doc.get("path", ""),
                    "original_path": doc.get("original_path"),
                    "original_filename": doc.get("original_filename"),
                    "file_renamed": doc.get("file_renamed", False),
                    "created": str(doc.get("created", "")),
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
        print(f"❌ Error loading documents: {e}")
        return []

def clear_all_grobid_documents() -> dict:
    """
    Clear all GROBID documents and related data from Neo4j.
    
    Returns:
        Dict with operation status and counts
    """
    try:
        neo4j_storage = Neo4jStorage()
        
        with neo4j_storage.driver.session() as session:
            # Count what we're about to delete
            count_result = session.run("""
                MATCH (d:Document {processing_method: 'GROBID'})
                OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                OPTIONAL MATCH (v:TextVector {vector_type: 'grobid_content'})
                RETURN count(DISTINCT d) as docs,
                       count(DISTINCT r) as refs, 
                       count(DISTINCT f) as figs,
                       count(DISTINCT t) as tables,
                       count(DISTINCT v) as vectors
            """)
            
            counts = count_result.single()
            docs_count = counts["docs"]
            refs_count = counts["refs"]
            figs_count = counts["figs"]
            tables_count = counts["tables"]
            vectors_count = counts["vectors"]
            
            if docs_count == 0:
                return {
                    "success": True,
                    "message": "No GROBID documents found to clear",
                    "deleted": {
                        "documents": 0,
                        "references": 0,
                        "figures": 0,
                        "tables": 0,
                        "text_vectors": 0
                    }
                }
            
            # Delete all GROBID-related data
            session.run("""
                MATCH (d:Document {processing_method: 'GROBID'})
                OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                DETACH DELETE d, r, f, t
            """)
            
            # Delete GROBID text vectors
            session.run("""
                MATCH (v:TextVector {vector_type: 'grobid_content'})
                DELETE v
            """)
            
            result = {
                "success": True,
                "message": f"Successfully cleared all GROBID data",
                "deleted": {
                    "documents": docs_count,
                    "references": refs_count, 
                    "figures": figs_count,
                    "tables": tables_count,
                    "text_vectors": vectors_count
                }
            }
            
            print(f"🗑️  Cleared GROBID data:")
            print(f"   📄 Documents: {docs_count}")
            print(f"   📚 References: {refs_count}")
            print(f"   🖼️  Figures: {figs_count}")
            print(f"   📊 Tables: {tables_count}")
            print(f"   🔍 Text vectors: {vectors_count}")
            
            return result
            
    except Exception as e:
        print(f"❌ Error clearing GROBID documents: {e}")
        return {
            "success": False,
            "error": str(e),
            "deleted": {
                "documents": 0,
                "references": 0,
                "figures": 0, 
                "tables": 0,
                "text_vectors": 0
            }
        }

def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python store_grobid_document.py <command> [args]")
        print("Commands:")
        print("  store --json-file <json_file_path> <file_path> [--session-id=<id>] [--no-rename]")
        print("  store <grobid_result_json> <file_path> [--session-id=<id>] [--no-rename]  (legacy)")
        print("  load [--session-id=<id>]")
        print("  clear")
        print("  sessions")
        print("  create-session [session_name]")
        print("Options:")
        print("  --json-file       Read GROBID result from file (avoids E2BIG error)")
        print("  --no-rename       Don't rename file based on document title")
        print("  --session-id=<id> Store/load in specific session")
        sys.exit(1)
    
    command = sys.argv[1]
    session_manager = SessionManager()
    
    # Extract session ID from args
    session_id = None
    for arg in sys.argv:
        if arg.startswith("--session-id="):
            session_id = arg.split("=", 1)[1]
            break
    
    if command == "store":
        # Handle different argument patterns
        if "--json-file" in sys.argv:
            # New pattern: store --json-file <temp_file_path> <original_file_path>
            json_file_idx = sys.argv.index("--json-file")
            if json_file_idx + 2 < len(sys.argv):
                json_file_path = sys.argv[json_file_idx + 1]
                file_path = sys.argv[json_file_idx + 2]
            else:
                print(json.dumps({"success": False, "error": "Missing arguments for --json-file"}))
                return
        elif len(sys.argv) >= 4:
            # Legacy pattern: store <grobid_result_json> <file_path>
            grobid_result_json = sys.argv[2]
            file_path = sys.argv[3]
            json_file_path = None
        else:
            print(json.dumps({"success": False, "error": "Insufficient arguments for store command"}))
            return
        
        # Check for rename option
        rename_file = "--no-rename" not in sys.argv
        
        try:
            # Load JSON data from file or command line
            if json_file_path:
                # Read from temporary file
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        grobid_result = json.load(f)
                except FileNotFoundError:
                    print(json.dumps({"success": False, "error": f"Temporary JSON file not found: {json_file_path}"}))
                    return
                except IOError as e:
                    print(json.dumps({"success": False, "error": f"Failed to read temporary JSON file: {e}"}))
                    return
            else:
                # Parse from command line (legacy)
                grobid_result = json.loads(grobid_result_json)
                
            result = store_complete_grobid_result(grobid_result, file_path, rename_file)
            
            # Add to session if specified
            if session_id and result.get("success"):
                session_manager.add_document_to_session(session_id, result["document_id"])
                result["session_id"] = session_id
            
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print(json.dumps({"success": False, "error": f"Invalid JSON: {e}"}))
    
    elif command == "load":
        if session_id:
            documents = session_manager.get_session_documents(session_id)
        else:
            documents = load_grobid_documents()
        print(json.dumps(documents, indent=2))
    
    elif command == "clear":
        result = clear_all_grobid_documents()
        print(json.dumps(result, indent=2))
    
    elif command == "sessions":
        sessions = session_manager.get_all_sessions()
        print(json.dumps(sessions, indent=2))
    
    elif command == "create-session":
        session_name = sys.argv[2] if len(sys.argv) > 2 else None
        result = session_manager.create_session(session_name)
        print(json.dumps(result, indent=2))
    
    else:
        print("Invalid command or arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()