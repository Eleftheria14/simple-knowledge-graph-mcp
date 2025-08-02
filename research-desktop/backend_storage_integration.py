#!/usr/bin/env python3
"""
Direct backend storage integration for Electron app.
Uses core backend storage classes instead of separate scripts.
"""
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the backend src directory to Python path
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))

# Import core backend storage classes
from storage.neo4j.storage import Neo4jStorage
from storage.neo4j.query import Neo4jQuery

class BackendStorageIntegration:
    """Direct integration with backend storage classes."""
    
    def __init__(self):
        self.neo4j_storage = Neo4jStorage()
        self.neo4j_query = Neo4jQuery()
    
    def store_grobid_document(self, grobid_result: dict, file_path: str, session_id: str = None) -> dict:
        """
        Store complete GROBID document using core backend storage.
        
        Args:
            grobid_result: GROBID processing result
            file_path: Path to the original PDF file
            session_id: Optional session ID to associate document with
            
        Returns:
            Dict with storage status and details
        """
        try:
            # Generate unique document ID
            doc_id = str(uuid.uuid4())
            
            # Extract metadata
            metadata = grobid_result.get("metadata", {})
            title = metadata.get("title", "Untitled Document")
            authors = metadata.get("authors", [])
            abstract = metadata.get("abstract", "")
            keywords = metadata.get("keywords", [])
            
            # Extract references, figures, tables
            references = metadata.get("references", [])
            if not references:
                references = grobid_result.get("citations", [])
            
            figures = metadata.get("figures", [])
            if not figures:
                figures = grobid_result.get("figures", [])
                
            tables = metadata.get("tables", [])
            if not tables:
                tables = grobid_result.get("tables", [])
            
            content = grobid_result.get("content", "")
            
            # Store document using core backend storage
            document_data = {
                "id": doc_id,
                "title": title,
                "path": file_path,
                "file_name": Path(file_path).name,
                "processing_method": "GROBID",
                "created": datetime.now().isoformat(),
                "success": grobid_result.get("success", False),
                "error": grobid_result.get("error", ""),
                "content_length": len(content),
                "full_text": content,
                "abstract": abstract,
                "keywords": keywords,
                "authors": [a.get("name", a) if isinstance(a, dict) else a for a in authors],
                "references_count": len(references),
                "figures_count": len(figures),
                "tables_count": len(tables)
            }
            
            # Use the store_entities tool functionality for document storage
            entities = [{
                "id": doc_id,
                "name": title,
                "type": "Document", 
                "properties": document_data
            }]
            
            # Store references as entities
            reference_entities = []
            for i, ref in enumerate(references):
                ref_id = f"{doc_id}_ref_{i}"
                reference_entities.append({
                    "id": ref_id,
                    "name": ref.get("title", f"Reference {i+1}"),
                    "type": "Reference",
                    "properties": {
                        "document_id": doc_id,
                        "index": i,
                        "title": ref.get("title", ""),
                        "authors": ref.get("authors", []),
                        "journal": ref.get("journal", ""),
                        "year": ref.get("year", "")
                    }
                })
            
            # Store figures as entities
            figure_entities = []
            for i, figure in enumerate(figures):
                fig_id = f"{doc_id}_fig_{i}"
                figure_entities.append({
                    "id": fig_id,
                    "name": f"Figure {i+1}",
                    "type": "Figure",
                    "properties": {
                        "document_id": doc_id,
                        "index": i,
                        "caption": figure.get("caption", ""),
                        "type": figure.get("type", "figure")
                    }
                })
            
            # Store tables as entities
            table_entities = []
            for i, table in enumerate(tables):
                table_id = f"{doc_id}_table_{i}"
                table_entities.append({
                    "id": table_id,
                    "name": f"Table {i+1}",
                    "type": "Table",
                    "properties": {
                        "document_id": doc_id,
                        "index": i,
                        "caption": table.get("caption", ""),
                        "content": table.get("content", ""),
                        "type": table.get("type", "table")
                    }
                })
            
            # Create relationships
            relationships = []
            
            # Document -> Reference relationships
            for ref_entity in reference_entities:
                relationships.append({
                    "source": doc_id,
                    "target": ref_entity["id"],
                    "type": "HAS_REFERENCE",
                    "properties": {}
                })
            
            # Document -> Figure relationships
            for fig_entity in figure_entities:
                relationships.append({
                    "source": doc_id,
                    "target": fig_entity["id"],
                    "type": "HAS_FIGURE",
                    "properties": {}
                })
            
            # Document -> Table relationships
            for table_entity in table_entities:
                relationships.append({
                    "source": doc_id,
                    "target": table_entity["id"],
                    "type": "HAS_TABLE",
                    "properties": {}
                })
            
            # Store all entities and relationships using core backend
            all_entities = entities + reference_entities + figure_entities + table_entities
            
            storage_result = self.neo4j_storage.store_entities(
                entities=all_entities,
                relationships=relationships
            )
            
            # Store full text as vectors
            vectors_stored = 0
            if content:
                # Chunk the content for vector storage
                chunk_size = 1000
                for i in range(0, len(content), chunk_size):
                    chunk_content = content[i:i + chunk_size]
                    vector_id = f"{doc_id}_chunk_{i // chunk_size}"
                    
                    try:
                        vector_result = self.neo4j_storage.store_text_vector(
                            content=chunk_content,
                            vector_id=vector_id,
                            metadata={
                                **document_data,
                                "chunk_index": i // chunk_size,
                                "start_pos": i,
                                "end_pos": min(i + chunk_size, len(content)),
                                "vector_type": "grobid_content"
                            }
                        )
                        if vector_result.get("success"):
                            vectors_stored += 1
                    except Exception as e:
                        print(f"Warning: Failed to store vector chunk {i // chunk_size}: {e}")
            
            # Handle session association if provided
            if session_id:
                # Store session relationship
                try:
                    session_rel_result = self.neo4j_storage.store_entities(
                        entities=[],
                        relationships=[{
                            "source": session_id,
                            "target": doc_id,
                            "type": "CONTAINS_DOCUMENT",
                            "properties": {"added": datetime.now().isoformat()}
                        }]
                    )
                except Exception as e:
                    print(f"Warning: Failed to link document to session: {e}")
            
            result = {
                "success": True,
                "document_id": doc_id,
                "stored": {
                    "document": 1,
                    "references": len(reference_entities),
                    "figures": len(figure_entities),
                    "tables": len(table_entities),
                    "text_vectors": vectors_stored
                },
                "storage_result": storage_result,
                "session_id": session_id
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_id": None
            }
    
    def load_documents(self, session_id: str = None) -> List[Dict[str, Any]]:
        """
        Load documents using core backend query functionality.
        
        Args:
            session_id: Optional session ID to filter documents
            
        Returns:
            List of document dictionaries
        """
        try:
            if session_id:
                # Query documents in specific session
                query = """
                MATCH (s:Session {id: $session_id})-[:CONTAINS_DOCUMENT]->(d:Document)
                OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
                OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
                OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
                RETURN d,
                       collect(DISTINCT r) as references,
                       collect(DISTINCT f) as figures,
                       collect(DISTINCT t) as tables
                ORDER BY d.created DESC
                """
                query_result = self.neo4j_query.execute_query(query, {"session_id": session_id})
            else:
                # Query all GROBID documents
                query = """
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
                """
                query_result = self.neo4j_query.execute_query(query)
            
            documents = []
            if query_result.get("success") and query_result.get("results"):
                for record in query_result["results"]:
                    doc = record.get("d", {})
                    references = [dict(r) for r in record.get("references", []) if r]
                    figures = [dict(f) for f in record.get("figures", []) if f]
                    tables = [dict(t) for t in record.get("tables", []) if t]
                    
                    documents.append({
                        "id": doc.get("id"),
                        "title": doc.get("title", "Untitled"),
                        "file_name": doc.get("file_name", ""),
                        "path": doc.get("path", ""),
                        "created": doc.get("created", ""),
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
            print(f"Error loading documents: {e}")
            return []
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """
        Clear all GROBID documents using core backend functionality.
        
        Returns:
            Dict with operation status and counts
        """
        try:
            # Query to count what we're deleting
            count_query = """
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
            """
            
            count_result = self.neo4j_query.execute_query(count_query)
            
            if not count_result.get("success") or not count_result.get("results"):
                return {
                    "success": True,
                    "message": "No documents found to clear",
                    "deleted": {"documents": 0, "references": 0, "figures": 0, "tables": 0, "text_vectors": 0}
                }
            
            counts = count_result["results"][0]
            docs_count = counts.get("docs", 0)
            
            if docs_count == 0:
                return {
                    "success": True,
                    "message": "No GROBID documents found to clear",
                    "deleted": {"documents": 0, "references": 0, "figures": 0, "tables": 0, "text_vectors": 0}
                }
            
            # Delete all GROBID-related data
            delete_query = """
            MATCH (d:Document {processing_method: 'GROBID'})
            OPTIONAL MATCH (d)-[:HAS_REFERENCE]->(r:Reference)
            OPTIONAL MATCH (d)-[:HAS_FIGURE]->(f:Figure)
            OPTIONAL MATCH (d)-[:HAS_TABLE]->(t:Table)
            DETACH DELETE d, r, f, t
            """
            
            delete_result = self.neo4j_query.execute_query(delete_query)
            
            # Delete text vectors
            vector_delete_query = """
            MATCH (v:TextVector {vector_type: 'grobid_content'})
            DELETE v
            """
            
            vector_delete_result = self.neo4j_query.execute_query(vector_delete_query)
            
            return {
                "success": True,
                "message": "Successfully cleared all GROBID data",
                "deleted": {
                    "documents": counts.get("docs", 0),
                    "references": counts.get("refs", 0),
                    "figures": counts.get("figs", 0),
                    "tables": counts.get("tables", 0),
                    "text_vectors": counts.get("vectors", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "deleted": {"documents": 0, "references": 0, "figures": 0, "tables": 0, "text_vectors": 0}
            }


def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command provided"}))
        return
    
    try:
        integration = BackendStorageIntegration()
        command = sys.argv[1]
        
        if command == "store" and len(sys.argv) >= 4:
            grobid_result_json = sys.argv[2]
            file_path = sys.argv[3]
            session_id = sys.argv[4] if len(sys.argv) > 4 else None
            
            grobid_result = json.loads(grobid_result_json)
            result = integration.store_grobid_document(grobid_result, file_path, session_id)
            print(json.dumps(result))
            
        elif command == "load":
            session_id = sys.argv[2] if len(sys.argv) > 2 else None
            documents = integration.load_documents(session_id)
            print(json.dumps(documents))
            
        elif command == "clear":
            result = integration.clear_all_documents()
            print(json.dumps(result))
            
        else:
            print(json.dumps({"success": False, "error": "Invalid command or arguments"}))
    
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


if __name__ == "__main__":
    main()